1. Установка:
bash# Клонируйте проект
git clone <your-repo>
cd job-search-system

# Установите зависимости
pip install --upgrade pip
pip install -r requirements.txt

# Настройте переменные окружения
cp .env.example .env
nano .env  # Заполните ваши данные

2. Получите Telegram API credentials:

Перейдите на https://my.telegram.org/apps
Войдите через свой телефон
Создайте новое приложение
Скопируйте api_id и api_hash в .env

3. Настройте Gmail для отправки писем:
bash# В .env укажите:
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password  # НЕ обычный пароль!
Как получить App Password для Gmail:

Включите 2FA: https://myaccount.google.com/security
Создайте App Password: https://myaccount.google.com/apppasswords
Скопируйте сгенерированный пароль в .env

4. Запустите backend:
bashpython main.py
При первом запуске Telegram попросит код подтверждения - введите его.
5. Проверьте работу:
bash# API документация
http://localhost:8000/docs

# Проверка здоровья
curl http://localhost:8000/

# Статистика
curl http://localhost:8000/api/stats
🐳 Запуск через Docker:
bash# Соберите и запустите
docker-compose up -d

# Проверьте логи
docker-compose logs -f backend

# Остановите
docker-compose down
📊 API примеры использования:
Получить вакансии:
bash# Все вакансии
curl http://localhost:8000/api/jobs

# С фильтрами
curl "http://localhost:8000/api/jobs?location=Dubai&position=ML%20Engineer&search=python"
Создать отклик:
bashcurl -X POST http://localhost:8000/api/applications \
  -F "job_id=1" \
  -F "name=Паел Гунин" \
  -F "email=pavelgun08@mail.ru" \
  -F "phone=+79614095295" \
  -F "telegram=@ecopavel81" \
  -F "message=Хочу работать у вас!" \
  -F "resume=@/path/to/resume.pdf"
Получить мои отклики:
bashcurl "http://localhost:8000/api/applications?user_email=ivan@example.com"

🔄 Интеграция Frontend с Backend:
Обновите файл React компонента, добавив реальные API вызовы:
javascript// В начале компонента
const API_URL = 'http://localhost:8000/api';

// Загрузка вакансий
useEffect(() => {
  const fetchJobs = async () => {
    try {
      const response = await fetch(`${API_URL}/jobs`);
      const data = await response.json();
      setJobs(data);
      setFilteredJobs(data);
    } catch (error) {
      console.error('Error fetching jobs:', error);
    }
  };
  
  fetchJobs();
}, []);

// Отправка отклика
const handleApplicationSubmit = async () => {
  const formData = new FormData();
  formData.append('job_id', selectedJob.id);
  formData.append('name', applicationForm.name);
  formData.append('email', applicationForm.email);
  formData.append('phone', applicationForm.phone);
  formData.append('message', applicationForm.message);
  formData.append('resume', applicationForm.resume);
  
  try {
    const response = await fetch(`${API_URL}/applications`, {
      method: 'POST',
      body: formData
    });
    
    if (response.ok) {
      showNotification('Отклик успешно отправлен!');
      // Обновить список откликов
    }
  } catch (error) {
    showNotification('Ошибка отправки отклика', 'error');
  }
};
🎨 Дополнительные возможности для расширения:
1. Добавить PostgreSQL вместо SQLite:
python# requirements.txt
asyncpg==0.29.0

# database.py
import asyncpg

class Database:
    async def init_db(self):
        self.pool = await asyncpg.create_pool(
            'postgresql://user:pass@localhost/jobsdb'
        )
2. Добавить Redis для кэширования:
python# requirements.txt
redis==5.0.1

# cache.py
import redis.asyncio as redis

class Cache:
    def __init__(self):
        self.redis = redis.from_url('redis://localhost')
    
    async def get_jobs(self, filters):
        key = f"jobs:{filters}"
        cached = await self.redis.get(key)
        if cached:
            return json.loads(cached)
        return None
3. Добавить Celery для фоновых задач:
python# requirements.txt
celery==5.3.4

# tasks.py
from celery import Celery

app = Celery('tasks', broker='redis://localhost')

@app.task
def parse_telegram_channels():
    # Парсинг в фоне
    pass
4. Добавить WebSocket для real-time обновлений:
python# main.py
from fastapi import WebSocket

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        # Отправляем новые вакансии
        await websocket.send_json({"new_jobs": jobs})
5. Добавить аутентификацию пользователей:
python# requirements.txt
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# auth.py
from jose import jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"])

def create_access_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm="HS256")
📈 Мониторинг и логирование:
Добавить логирование:
python# main.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
Добавить метрики (Prometheus):
python# requirements.txt
prometheus-fastapi-instrumentator==6.1.0

# main.py
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
🔒 Production настройки:
1. HTTPS через Nginx:
nginx# /etc/nginx/sites-available/job-search
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location / {
        root /var/www/job-search;
        try_files $uri $uri/ /index.html;
    }
}
2. Systemd service:
ini# /etc/systemd/system/job-search.service
[Unit]
Description=Job Search System
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/app/job-search
ExecStart=/usr/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target
3. Rate limiting:
python# requirements.txt
slowapi==0.1.9

# main.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/applications")
@limiter.limit("5/minute")
async def create_application():
    pass
```

## 🎯 Итоговая структура проекта:
```
job-search-system/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── database.py          # DB operations
│   ├── telegram_parser.py   # Telegram parsing
│   ├── email_service.py     # Email sending
│   ├── models.py            # Data models
│   ├── config.py            # Settings
│   ├── requirements.txt     # Dependencies
│   ├── .env.example         # Env template
│   ├── Dockerfile          # Docker config
│   └── docker-compose.yml  # Compose config
├── frontend/
│   ├── index.html          # React app
│   └── api.js              # API calls
├── uploads/
│   └── resumes/            # PDF resumes
├── README.md               # Documentation
└── jobs.db                 # SQLite database