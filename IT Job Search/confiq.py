import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

class Settings:
    # API Settings
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', 8090))
    
    # Database
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/jobs.db')
    
    # Telegram
    TELEGRAM_API_ID = os.getenv('TELEGRAM_API_ID')
    TELEGRAM_API_HASH = os.getenv('TELEGRAM_API_HASH')
    TELEGRAM_PHONE = os.getenv('TELEGRAM_PHONE')
    
    # Channels to monitor
    TELEGRAM_CHANNELS = [
        'revacancy_global',
        'datasciencejobs'
    ]
    
    # Parsing settings
    PARSE_INTERVAL_MINUTES = int(os.getenv('PARSE_INTERVAL_MINUTES', 10))
    MESSAGES_LIMIT = int(os.getenv('MESSAGES_LIMIT', 100))
    DAYS_BACK = int(os.getenv('DAYS_BACK', 7))
    
    # SMTP Settings
    SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USER = os.getenv('SMTP_USER')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
    FROM_EMAIL = os.getenv('FROM_EMAIL', SMTP_USER)
    
    # Upload settings
    UPLOAD_DIR = os.getenv('UPLOAD_DIR', 'uploads/resumes')
    MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB
    
    # Job filtering
    PRIORITY_LOCATIONS = ['Dubai', 'Canada', 'Ireland', 'Serbia']
    TARGET_POSITIONS = ['ML Engineer', 'AI Developer', 'Data Scientist']
    TARGET_EXPERIENCE = ['2-3 years', '2-4 years', '3+ years']
    
    # Keywords for job detection
    JOB_KEYWORDS = [
        'ml engineer', 'machine learning engineer',
        'ai developer', 'artificial intelligence',
        'data scientist', 'deep learning',
        'mlops', 'computer vision', 'nlp'
    ]

settings = Settings()

# Создаём директории если их нет
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)