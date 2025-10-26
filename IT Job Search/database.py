import aiosqlite
from typing import List, Optional
from datetime import datetime
from models import Job, Application, JobFilter

class Database:
    def __init__(self, db_path: str = "jobs.db"):
        self.db_path = db_path
    
    async def init_db(self):
        """Инициализация базы данных"""
        async with aiosqlite.connect(self.db_path) as db:
            # Таблица вакансий
            await db.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    company TEXT NOT NULL,
                    location TEXT NOT NULL,
                    experience TEXT,
                    salary TEXT,
                    description TEXT,
                    tags TEXT,
                    source TEXT,
                    posted_date TEXT,
                    contact_email TEXT,
                    contact_telegram TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(title, company, posted_date)
                )
            """)
            
            # Таблица откликов
            await db.execute("""
                CREATE TABLE IF NOT EXISTS applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    phone TEXT,
                    message TEXT,
                    resume_path TEXT,
                    status TEXT DEFAULT 'sent',
                    applied_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (job_id) REFERENCES jobs (id)
                )
            """)
            
            # Индексы для быстрого поиска
            await db.execute("CREATE INDEX IF NOT EXISTS idx_jobs_location ON jobs(location)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_jobs_title ON jobs(title)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_applications_job ON applications(job_id)")
            
            await db.commit()
            print("✅ База данных инициализирована")
    
    async def add_job(self, job: Job) -> Optional[int]:
        """Добавить вакансию"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    INSERT OR IGNORE INTO jobs 
                    (title, company, location, experience, salary, description, 
                     tags, source, posted_date, contact_email, contact_telegram)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    job.title, job.company, job.location, job.experience,
                    job.salary, job.description, ','.join(job.tags),
                    job.source, job.posted_date, job.contact_email,
                    job.contact_telegram
                ))
                await db.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"❌ Ошибка добавления вакансии: {e}")
            return None
    
    async def get_jobs(self, filters: JobFilter, limit: int = 50) -> List[Job]:
        """Получить вакансии с фильтрами"""
        query = "SELECT * FROM jobs WHERE 1=1"
        params = []
        
        if filters.search:
            query += " AND (title LIKE ? OR company LIKE ? OR description LIKE ?)"
            search_term = f"%{filters.search}%"
            params.extend([search_term, search_term, search_term])
        
        if filters.location and filters.location != "all":
            query += " AND location = ?"
            params.append(filters.location)
        
        if filters.position and filters.position != "all":
            query += " AND title LIKE ?"
            params.append(f"%{filters.position}%")
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                jobs = []
                for row in rows:
                    job_dict = dict(row)
                    job_dict['tags'] = job_dict['tags'].split(',') if job_dict['tags'] else []
                    jobs.append(Job(**job_dict))
                return jobs
    
    async def get_job_by_id(self, job_id: int) -> Optional[Job]:
        """Получить вакансию по ID"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    job_dict = dict(row)
                    job_dict['tags'] = job_dict['tags'].split(',') if job_dict['tags'] else []
                    return Job(**job_dict)
                return None
    
    async def add_application(self, application: Application) -> Optional[int]:
        """Добавить отклик"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    INSERT INTO applications 
                    (job_id, name, email, phone, message, resume_path, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    application.job_id, application.name, application.email,
                    application.phone, application.message, application.resume_path,
                    application.status
                ))
                await db.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"❌ Ошибка добавления отклика: {e}")
            return None
    
    async def get_applications(self, user_email: Optional[str] = None) -> List[Application]:
        """Получить список откликов"""
        query = "SELECT * FROM applications"
        params = []
        
        if user_email:
            query += " WHERE email = ?"
            params.append(user_email)
        
        query += " ORDER BY applied_date DESC"
        
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [Application(**dict(row)) for row in rows]
    
    async def get_application_by_id(self, application_id: int) -> Optional[Application]:
        """Получить отклик по ID"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM applications WHERE id = ?", 
                (application_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return Application(**dict(row)) if row else None
    
    async def update_application_status(self, application_id: int, status: str) -> bool:
        """Обновить статус отклика"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "UPDATE applications SET status = ? WHERE id = ?",
                    (status, application_id)
                )
                await db.commit()
                return True
        except Exception as e:
            print(f"❌ Ошибка обновления статуса: {e}")
            return False
    
    async def get_stats(self) -> dict:
        """Получить статистику"""
        async with aiosqlite.connect(self.db_path) as db:
            # Количество вакансий
            async with db.execute("SELECT COUNT(*) FROM jobs") as cursor:
                total_jobs = (await cursor.fetchone())[0]
            
            # Количество откликов
            async with db.execute("SELECT COUNT(*) FROM applications") as cursor:
                total_applications = (await cursor.fetchone())[0]
            
            # Вакансии по локациям
            async with db.execute("""
                SELECT location, COUNT(*) as count 
                FROM jobs 
                GROUP BY location
            """) as cursor:
                locations = await cursor.fetchall()
            
            # Статусы откликов
            async with db.execute("""
                SELECT status, COUNT(*) as count 
                FROM applications 
                GROUP BY status
            """) as cursor:
                statuses = await cursor.fetchall()
            
            return {
                "total_jobs": total_jobs,
                "total_applications": total_applications,
                "jobs_by_location": dict(locations),
                "applications_by_status": dict(statuses)
            }