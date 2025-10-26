from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class Job(BaseModel):
    id: Optional[int] = None
    title: str
    company: str
    location: str
    experience: str
    salary: str
    description: str
    tags: List[str]
    source: str
    posted_date: str
    contact_email: str
    contact_telegram: str
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class Application(BaseModel):
    id: Optional[int] = None
    job_id: int
    name: str
    email: EmailStr
    phone: Optional[str] = None
    message: str
    resume_path: str
    status: str = "sent"  # sent, viewed, rejected, accepted
    applied_date: datetime
    
    class Config:
        from_attributes = True

class JobFilter(BaseModel):
    search: Optional[str] = None
    location: Optional[str] = None
    position: Optional[str] = None
    experience_min: Optional[int] = None
    experience_max: Optional[int] = None

class TelegramMessage(BaseModel):
    """Модель сообщения из Telegram"""
    message_id: int
    channel: str
    text: str
    date: datetime
    
class ParsedJob(BaseModel):
    """Распарсенная вакансия из Telegram"""
    raw_text: str
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    experience: Optional[str] = None
    salary: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = []
    contact_email: Optional[str] = None
    contact_telegram: Optional[str] = None