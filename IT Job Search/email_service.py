import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os
from typing import Optional
from models import Job, Application

class EmailService:
    def __init__(self):
        # Настройки SMTP из переменных окружения
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_user = os.getenv('SMTP_USER')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.from_email = os.getenv('FROM_EMAIL', self.smtp_user)
    
    async def send_application_email(
        self, 
        job: Job, 
        application: Application, 
        resume_path: str
    ) -> bool:
        """Отправить отклик на вакансию работодателю"""
        try:
            # Создаём multipart сообщение
            message = MIMEMultipart()
            message['From'] = self.from_email
            message['To'] = job.contact_email
            message['Subject'] = f"Отклик на вакансию: {job.title} - {application.name}"
            
            # Тело письма
            body = self._create_email_body(job, application)
            message.attach(MIMEText(body, 'html'))
            
            # Прикрепляем резюме
            if os.path.exists(resume_path):
                with open(resume_path, 'rb') as f:
                    resume_attachment = MIMEApplication(f.read(), _subtype='pdf')
                    resume_attachment.add_header(
                        'Content-Disposition', 
                        'attachment', 
                        filename=os.path.basename(resume_path)
                    )
                    message.attach(resume_attachment)
            
            # Отправляем письмо
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                start_tls=True,
                username=self.smtp_user,
                password=self.smtp_password
            )
            
            print(f"✅ Отклик отправлен на {job.contact_email}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка отправки email: {e}")
            return False
    
    def _create_email_body(self, job: Job, application: Application) -> str:
        """Создать HTML тело письма"""
        return f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #4F46E5;
                    color: white;
                    padding: 20px;
                    border-radius: 8px 8px 0 0;
                }}
                .content {{
                    background-color: #f9fafb;
                    padding: 20px;
                    border-radius: 0 0 8px 8px;
                }}
                .info-block {{
                    background-color: white;
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 6px;
                    border-left: 4px solid #4F46E5;
                }}
                .label {{
                    font-weight: bold;
                    color: #4F46E5;
                }}
                .message-box {{
                    background-color: white;
                    padding: 15px;
                    margin: 15px 0;
                    border-radius: 6px;
                    border: 1px solid #e5e7eb;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>🎯 Новый отклик на вакансию</h2>
                    <p>{job.title} в {job.company}</p>
                </div>
                
                <div class="content">
                    <div class="info-block">
                        <p><span class="label">👤 Имя кандидата:</span> {application.name}</p>
                        <p><span class="label">📧 Email:</span> <a href="mailto:{application.email}">{application.email}</a></p>
                        {f'<p><span class="label">📱 Телефон:</span> {application.phone}</p>' if application.phone else ''}
                    </div>
                    
                    <div class="info-block">
                        <p><span class="label">💼 Вакансия:</span> {job.title}</p>
                        <p><span class="label">🏢 Компания:</span> {job.company}</p>
                        <p><span class="label">📍 Локация:</span> {job.location}</p>
                        <p><span class="label">📅 Дата публикации:</span> {job.posted_date}</p>
                    </div>
                    
                    <div class="message-box">
                        <p class="label">💬 Сопроводительное письмо:</p>
                        <p style="white-space: pre-wrap;">{application.message}</p>
                    </div>
                    
                    <p style="margin-top: 20px; color: #6b7280; font-size: 14px;">
                        📎 Резюме кандидата прикреплено к этому письму в формате PDF.
                    </p>
                    
                    <hr style="margin: 20px 0; border: none; border-top: 1px solid #e5e7eb;">
                    
                    <p style="color: #6b7280; font-size: 12px; text-align: center;">
                        Это письмо отправлено автоматически из системы поиска вакансий<br>
                        Источник вакансии: {job.source}
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
    
    async def send_confirmation_email(self, application: Application, job: Job) -> bool:
        """Отправить подтверждение кандидату"""
        try:
            message = MIMEMultipart()
            message['From'] = self.from_email
            message['To'] = application.email
            message['Subject'] = f"Ваш отклик на вакансию {job.title} отправлен"
            
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #4F46E5;">✅ Ваш отклик успешно отправлен!</h2>
                    
                    <p>Здравствуйте, {application.name}!</p>
                    
                    <p>Ваш отклик на вакансию <strong>{job.title}</strong> в компании 
                    <strong>{job.company}</strong> успешно отправлен работодателю.</p>
                    
                    <div style="background-color: #f3f4f6; padding: 15px; border-radius: 6px; margin: 20px 0;">
                        <p><strong>📧 Email работодателя:</strong> {job.contact_email}</p>
                        <p><strong>💬 Telegram:</strong> {job.contact_telegram}</p>
                    </div>
                    
                    <p>Работодатель свяжется с вами в ближайшее время, если ваша кандидатура 
                    будет интересна.</p>
                    
                    <p style="color: #6b7280; font-size: 14px; margin-top: 30px;">
                        Удачи в поиске работы!<br>
                        Команда системы поиска вакансий
                    </p>
                </div>
            </body>
            </html>
            """
            
            message.attach(MIMEText(body, 'html'))
            
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                start_tls=True,
                username=self.smtp_user,
                password=self.smtp_password
            )
            
            print(f"✅ Подтверждение отправлено на {application.email}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка отправки подтверждения: {e}")
            return False
    
    async def send_status_update(
        self, 
        application: Application, 
        job: Job, 
        new_status: str
    ) -> bool:
        """Уведомить кандидата об изменении статуса"""
        try:
            status_messages = {
                'viewed': 'Ваше резюме просмотрено работодателем',
                'accepted': '🎉 Поздравляем! Ваша кандидатура заинтересовала работодателя',
                'rejected': 'К сожалению, работодатель выбрал другого кандидата'
            }
            
            message = MIMEMultipart()
            message['From'] = self.from_email
            message['To'] = application.email
            message['Subject'] = f"Обновление статуса отклика на {job.title}"
            
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #4F46E5;">Обновление статуса вашего отклика</h2>
                    
                    <p>Здравствуйте, {application.name}!</p>
                    
                    <div style="background-color: #f3f4f6; padding: 15px; border-radius: 6px; margin: 20px 0;">
                        <p><strong>Вакансия:</strong> {job.title}</p>
                        <p><strong>Компания:</strong> {job.company}</p>
                        <p><strong>Статус:</strong> {status_messages.get(new_status, new_status)}</p>
                    </div>
                    
                    <p>Спасибо за использование нашего сервиса!</p>
                </div>
            </body>
            </html>
            """
            
            message.attach(MIMEText(body, 'html'))
            
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                start_tls=True,
                username=self.smtp_user,
                password=self.smtp_password
            )
            
            print(f"✅ Уведомление о статусе отправлено на {application.email}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка отправки уведомления: {e}")
            return False