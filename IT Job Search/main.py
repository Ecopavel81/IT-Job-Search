from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
import uvicorn
from datetime import datetime
import asyncio

from database import Database
from telegram_parser import TelegramParser
from email_service import EmailService
from models import Job, Application, JobFilter

app = FastAPI(title="Job Search System API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация сервисов
db = Database()
telegram_parser = TelegramParser()
email_service = EmailService()

# Фоновая задача для парсинга
async def parse_telegram_channels():
    """Парсинг Telegram каналов каждые 10 минут"""
    # Проверяем, настроены ли Telegram credentials
    if not telegram_parser.api_id or not telegram_parser.api_hash or not telegram_parser.phone:
        print("⚠️ Telegram credentials не настроены. Парсинг отключен.")
        print("   Для включения парсинга настройте TELEGRAM_API_ID, TELEGRAM_API_HASH и TELEGRAM_PHONE в .env")
        return
    
    while True:
        try:
            print("🔍 Начинаю парсинг Telegram каналов...")
            channels = [
                "revacancy_global",
                "datasciencejobs"
            ]
            
            for channel in channels:
                jobs = await telegram_parser.parse_channel(channel)
                for job in jobs:
                    await db.add_job(job)
                print(f"✅ Канал {channel}: найдено {len(jobs)} новых вакансий")
            
            await asyncio.sleep(600)  # 10 минут
        except Exception as e:
            print(f"❌ Ошибка парсинга: {e}")
            await asyncio.sleep(60)

@app.on_event("startup")
async def startup_event():
    """Запуск при старте приложения"""
    await db.init_db()
    # Запускаем фоновую задачу парсинга
    asyncio.create_task(parse_telegram_channels())
    print("🚀 Сервер запущен")

@app.get("/")
async def root():
    return {"message": "Job Search System API", "status": "running"}

@app.get("/api/jobs", response_model=List[Job])
async def get_jobs(
    search: Optional[str] = None,
    location: Optional[str] = None,
    position: Optional[str] = None,
    limit: int = 50
):
    """Получить список вакансий с фильтрами"""
    try:
        filters = JobFilter(
            search=search,
            location=location,
            position=position
        )
        jobs = await db.get_jobs(filters, limit)
        return jobs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/jobs/{job_id}", response_model=Job)
async def get_job(job_id: int):
    """Получить конкретную вакансию"""
    job = await db.get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Вакансия не найдена")
    return job

@app.post("/api/applications")
async def create_application(
    job_id: int = Form(...),
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(None),
    message: str = Form(...),
    resume: UploadFile = File(...)
):
    """Создать отклик на вакансию"""
    try:
        # Проверяем существование вакансии
        job = await db.get_job_by_id(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Вакансия не найдена")
        
        # Проверяем тип файла
        if not resume.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Только PDF файлы")
        
        # Сохраняем резюме
        resume_content = await resume.read()
        resume_path = f"uploads/resumes/{job_id}_{datetime.now().timestamp()}_{resume.filename}"
        
        with open(resume_path, "wb") as f:
            f.write(resume_content)
        
        # Создаём отклик
        application = Application(
            job_id=job_id,
            name=name,
            email=email,
            phone=phone,
            message=message,
            resume_path=resume_path,
            status="sent",
            applied_date=datetime.now()
        )
        
        application_id = await db.add_application(application)
        
        # Отправляем email работодателю
        await email_service.send_application_email(
            job=job,
            application=application,
            resume_path=resume_path
        )
        
        return {
            "status": "success",
            "application_id": application_id,
            "message": "Отклик успешно отправлен"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/applications", response_model=List[Application])
async def get_applications(user_email: Optional[str] = None):
    """Получить список откликов"""
    try:
        applications = await db.get_applications(user_email)
        return applications
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/applications/{application_id}", response_model=Application)
async def get_application(application_id: int):
    """Получить конкретный отклик"""
    application = await db.get_application_by_id(application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Отклик не найден")
    return application

@app.put("/api/applications/{application_id}/status")
async def update_application_status(
    application_id: int,
    status: str
):
    """Обновить статус отклика"""
    try:
        success = await db.update_application_status(application_id, status)
        if not success:
            raise HTTPException(status_code=404, detail="Отклик не найден")
        return {"status": "success", "message": "Статус обновлён"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/parse/trigger")
async def trigger_parse():
    """Запустить парсинг вручную"""
    try:
        asyncio.create_task(parse_telegram_channels())
        return {"status": "success", "message": "Парсинг запущен"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_stats():
    """Получить статистику"""
    try:
        stats = await db.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)