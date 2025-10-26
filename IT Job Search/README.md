# 🚀 Система автоматического поиска вакансий ML/AI/DS

Автоматическая система для поиска вакансий в Telegram-каналах с возможностью прямого отклика на позиции.

## 📋 Возможности

- ✅ **Автоматический парсинг** Telegram-каналов каждые 10 минут
- 🔍 **Умная фильтрация** по должностям, локациям и опыту
- 📧 **Автоматическая отправка** откликов работодателям
- 📎 **Прикрепление PDF резюме**
- 📊 **Отслеживание статусов** откликов
- 🔔 **Email уведомления** для кандидатов

## 🛠 Технологии

**Backend:**
- FastAPI - современный async веб-фреймворк
- SQLite (aiosqlite) - база данных
- Telethon - Telegram API клиент
- aiosmtplib - отправка email

**Frontend:**
- React + Hooks
- TailwindCSS
- Lucide Icons

## 📦 Установка

### 1. Клонируйте репозиторий

```bash
git clone <repository-url>
cd job-search-system
```

### 2. Установите зависимости

```bash
pip install -r requirements.txt
```

### 3. Настройте переменные окружения

Скопируйте `.env.example` в `.env` и заполните:

```bash
cp .env.example .env
nano .env
```

**Необходимые настройки:**

#### Telegram API
1. Перейдите на https://my.telegram.org/apps
2. Создайте приложение
3. Получите `api_id` и `api_hash`
4. Укажите свой номер телефона

#### Email (для Gmail)
1. Включите двухфакторную аутентификацию
2. Создайте "Пароль приложения": https://myaccount.google.com/apppasswords
3. Используйте этот пароль в `SMTP_PASSWORD`

### 4. Создайте структуру директорий

```bash
mkdir -p uploads/resumes
```

## 🚀 Запуск

### Backend

```bash
python main.py
```

Сервер запустится на `http://localhost:8090`

API документация доступна на `http://localhost:8090/docs`

### Frontend

Откройте `index.html` в браузере или используйте любой веб-сервер:

```bash
# Простой HTTP сервер
python -m http.server 3000
```

Затем откройте `http://localhost:3000`

## 📚 API Endpoints

### Вакансии

- `GET /api/jobs` - Получить список вакансий
  - Query параметры: `search`, `location`, `position`, `limit`
- `GET /api/jobs/{job_id}` - Получить вакансию по ID

### Отклики

- `POST /api/applications` - Создать отклик
  - Form data: `job_id`, `name`, `email`, `phone`, `message`, `resume` (PDF)
- `GET /api/applications` - Получить список откликов
  - Query параметры: `user_email`
- `GET /api/applications/{id}` - Получить отклик по ID
- `PUT /api/applications/{id}/status` - Обновить статус отклика

### Парсинг

- `POST /api/parse/trigger` - Запустить парсинг вручную
- `GET /api/stats` - Получить статистику

## 🔧 Структура проекта

```
job-search-system/
├── main.py              # FastAPI приложение
├── database.py          # Работа с БД
├── telegram_parser.py   # Парсинг Telegram
├── email_service.py     # Отправка email
├── models.py            # Pydantic модели
├── config.py            # Настройки
├── requirements.txt     # Зависимости
├── .env.example         # Пример переменных окружения
├── README.md           # Документация
├── index.html          # Frontend
└── uploads/
    └── resumes/        # Загруженные резюме
```

## 🎯 Настройка каналов

По умолчанию мониторятся каналы:
- `t.me/revacancy_global`
- `t.me/datasciencejobs`

Чтобы добавить свои каналы, отредактируйте `config.py`:

```python
TELEGRAM_CHANNELS = [
    'revacancy_global',
    'datasciencejobs',
    'your_channel_name'  # Добавьте свой
]
```

## 🔍 Как работает парсинг

1. Система подключается к Telegram через Telethon
2. Каждые 10 минут сканирует указанные каналы
3. Ищет сообщения с ключевыми словами (ML Engineer, Data Scientist и т.д.)
4. Извлекает структурированную информацию:
   - Название должности
   - Компания
   - Локация (приоритет: Dubai, Canada, Ireland, Serbia)
   - Опыт работы (фокус на 2-3 года)
   - Зарплата
   - Контакты
5. Сохраняет в БД (избегая дубликатов)

## 📧 Процесс отклика

1. Кандидат выбирает вакансию
2. Заполняет форму и прикрепляет PDF резюме
3. Система отправляет email работодателю с:
   - Контактными данными кандидата
   - Сопроводительным письмом
   - Прикреплённым резюме
4. Кандидат получает подтверждение на email
5. Отклик сохраняется в БД со статусом "sent"

## 🔐 Безопасность

- ✅ Все пароли в `.env` файле (не коммитить!)
- ✅ Валидация типов файлов (только PDF)
- ✅ Ограничение размера файлов (10 MB)
- ✅ SQL injection защита через параметризованные запросы
- ✅ CORS настроен для production

## 🐛 Troubleshooting

### Ошибка подключения к Telegram

```
Error: Could not connect to Telegram
```

**Решение:**
1. Проверьте `TELEGRAM_API_ID` и `TELEGRAM_API_HASH`
2. Убедитесь что номер телефона указан в международном формате (+...)
3. При первом запуске введите код подтверждения из Telegram

### Ошибка отправки email

```
Error: SMTP authentication failed
```

**Решение:**
1. Для Gmail используйте "Пароль приложения", не обычный пароль
2. Проверьте что двухфакторная аутентификация включена
3. Убедитесь что SMTP_HOST и SMTP_PORT правильные

### База данных заблокирована

```
Error: database is locked
```

**Решение:**
- SQLite не поддерживает множественные писатели
- Перезапустите приложение
- Для production используйте PostgreSQL

## 📈 Расширение функционала

### Добавить новый канал

1. Отредактируйте `config.py`:
```python
TELEGRAM_CHANNELS.append('new_channel_name')
```

2. Перезапустите сервер

### Изменить частоту парсинга

В `main.py` измените:
```python
await asyncio.sleep(600)  # 600 секунд = 10 минут
```

### Добавить новые фильтры

1. Добавьте поле в `JobFilter` в `models.py`
2. Обновите SQL запрос в `database.py`
3. Добавьте UI элемент во frontend

## 📝 Лицензия

MIT License

## 🤝 Поддержка

Если возникли вопросы или проблемы:
1. Проверьте документацию
2. Посмотрите логи сервера
3. Создайте issue в репозитории

---

Удачи в поиске работы! 🎯