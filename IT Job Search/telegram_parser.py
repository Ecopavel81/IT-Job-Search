from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from typing import List
import re
import os
from datetime import datetime, timedelta
from models import Job

class TelegramParser:
    def __init__(self):
        # Получаем credentials из переменных окружения
        self.api_id = os.getenv('TELEGRAM_API_ID')
        self.api_hash = os.getenv('TELEGRAM_API_HASH')
        self.phone = os.getenv('TELEGRAM_PHONE')
        
        self.client = None
        self.keywords = [
            'ml engineer', 'machine learning', 'data scientist',
            'ai developer', 'artificial intelligence', 'deep learning'
        ]
        self.priority_locations = ['dubai', 'canada', 'ireland', 'serbia']
    
    async def connect(self):
        """Подключение к Telegram"""
        if not self.client:
            self.client = TelegramClient('session', self.api_id, self.api_hash)
            await self.client.start(phone=self.phone)
            print("✅ Подключено к Telegram")
    
    async def parse_channel(self, channel_username: str) -> List[Job]:
        """Парсинг канала Telegram"""
        await self.connect()
        
        jobs = []
        try:
            # Получаем сущность канала
            entity = await self.client.get_entity(channel_username)
            
            # Получаем последние 100 сообщений за последние 7 дней
            offset_date = datetime.now() - timedelta(days=7)
            
            messages = await self.client(GetHistoryRequest(
                peer=entity,
                offset_id=0,
                offset_date=offset_date,
                add_offset=0,
                limit=100,
                max_id=0,
                min_id=0,
                hash=0
            ))
            
            for message in messages.messages:
                if not message.message:
                    continue
                
                text = message.message.lower()
                
                # Проверяем, содержит ли сообщение ключевые слова
                if any(keyword in text for keyword in self.keywords):
                    job = self._parse_job_from_text(
                        message.message, 
                        channel_username,
                        message.date
                    )
                    if job:
                        jobs.append(job)
            
            print(f"📊 Канал {channel_username}: найдено {len(jobs)} вакансий")
            
        except Exception as e:
            print(f"❌ Ошибка парсинга канала {channel_username}: {e}")
        
        return jobs
    
    def _parse_job_from_text(self, text: str, source: str, date: datetime) -> Job:
        """Парсинг вакансии из текста сообщения"""
        try:
            # Извлекаем заголовок (первая строка или жирный текст)
            lines = text.split('\n')
            title = self._extract_title(lines)
            
            # Извлекаем компанию
            company = self._extract_company(text)
            
            # Извлекаем локацию
            location = self._extract_location(text)
            
            # Извлекаем опыт работы
            experience = self._extract_experience(text)
            
            # Извлекаем зарплату
            salary = self._extract_salary(text)
            
            # Извлекаем описание (первые 200 символов без первых строк)
            description = self._extract_description(lines)
            
            # Извлекаем теги/навыки
            tags = self._extract_tags(text)
            
            # Извлекаем контакты
            contact_email = self._extract_email(text)
            contact_telegram = self._extract_telegram(text)
            
            if not title or not company:
                return None
            
            return Job(
                title=title,
                company=company,
                location=location or "Remote",
                experience=experience or "2-3 years",
                salary=salary or "Competitive",
                description=description,
                tags=tags,
                source=f"t.me/{source}",
                posted_date=date.strftime('%Y-%m-%d'),
                contact_email=contact_email or f"jobs@{company.lower().replace(' ', '')}.com",
                contact_telegram=contact_telegram or f"@{source}"
            )
            
        except Exception as e:
            print(f"❌ Ошибка парсинга текста: {e}")
            return None
    
    def _extract_title(self, lines: List[str]) -> str:
        """Извлечь название должности"""
        # Ищем строки с ключевыми словами позиций
        position_keywords = ['engineer', 'developer', 'scientist', 'analyst']
        
        for line in lines[:5]:  # Проверяем первые 5 строк
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in position_keywords):
                # Очищаем от эмодзи и лишних символов
                clean_line = re.sub(r'[^\w\s-]', '', line).strip()
                if len(clean_line) > 5:
                    return clean_line[:100]
        
        return lines[0][:100] if lines else "Unknown Position"
    
    def _extract_company(self, text: str) -> str:
        """Извлечь название компании"""
        # Паттерны для поиска компании
        patterns = [
            r'[Cc]ompany[:\s]+([A-Z][A-Za-z0-9\s&]+)',
            r'[Кк]омпания[:\s]+([А-ЯA-Z][А-Яа-яA-Za-z0-9\s&]+)',
            r'@([A-Za-z0-9_]+)',  # Telegram username
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()[:100]
        
        return "Unknown Company"
    
    def _extract_location(self, text: str) -> str:
        """Извлечь локацию"""
        text_lower = text.lower()
        
        # Проверяем приоритетные локации
        for location in self.priority_locations:
            if location in text_lower:
                return location.capitalize()
        
        # Паттерны для других локаций
        location_patterns = [
            r'[Ll]ocation[:\s]+([A-Za-z\s,]+)',
            r'[Лл]окация[:\s]+([А-Яа-яA-Za-z\s,]+)',
            r'🌍\s*([A-Za-z\s,]+)',
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()[:50]
        
        return None
    
    def _extract_experience(self, text: str) -> str:
        """Извлечь требуемый опыт"""
        patterns = [
            r'(\d+[-–]\d+)\s*(?:years?|лет)',
            r'(?:experience|опыт)[:\s]+(\d+[-–]\d+)',
            r'(\d+\+)\s*(?:years?|лет)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1) + " years"
        
        return None
    
    def _extract_salary(self, text: str) -> str:
        """Извлечь зарплату"""
        patterns = [
            r'([\$€£]\d+[kK]?[-–]\d+[kK]?)',
            r'(\d+[kK]?[-–]\d+[kK]?\s*(?:USD|EUR|GBP|CAD))',
            r'[Ss]alary[:\s]+([\$€£]\d+[kK]?[-–]\d+[kK]?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_description(self, lines: List[str]) -> str:
        """Извлечь описание"""
        # Берём строки со 2-й по 5-ю, объединяем
        description_lines = [line for line in lines[1:6] if len(line) > 20]
        description = ' '.join(description_lines)
        return description[:500] if description else "No description available"
    
    def _extract_tags(self, text: str) -> List[str]:
        """Извлечь технологии/навыки"""
        # Список популярных технологий
        tech_keywords = [
            'python', 'pytorch', 'tensorflow', 'keras', 'scikit-learn',
            'r', 'sql', 'nosql', 'docker', 'kubernetes', 'aws', 'azure',
            'gcp', 'spark', 'hadoop', 'nlp', 'computer vision', 'mlops',
            'git', 'linux', 'tableau', 'power bi', 'airflow'
        ]
        
        text_lower = text.lower()
        found_tags = []
        
        for keyword in tech_keywords:
            if keyword in text_lower:
                found_tags.append(keyword.title())
        
        # Ограничиваем до 6 тегов
        return found_tags[:6] if found_tags else ['Python', 'Machine Learning']
    
    def _extract_email(self, text: str) -> str:
        """Извлечь email"""
        pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        match = re.search(pattern, text)
        return match.group(0) if match else None
    
    def _extract_telegram(self, text: str) -> str:
        """Извлечь Telegram username"""
        pattern = r'@([a-zA-Z0-9_]{5,32})'
        matches = re.findall(pattern, text)
        return f"@{matches[0]}" if matches else None
    
    async def close(self):
        """Закрыть соединение"""
        if self.client:
            await self.client.disconnect()
            print("👋 Отключено от Telegram")