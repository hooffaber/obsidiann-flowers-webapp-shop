# Быстрое развертывание для разработки на Windows 11

Инструкция по быстрому запуску проекта для разработки на Windows 11 с минимальным набором сервисов.

## Требования

- Docker Desktop for Windows
- Git
- Свободные порты: 8000 (API), 5432 (PostgreSQL), 6379 (Redis)

## Быстрый старт

### 1. Клонировать репозиторий (если еще не клонирован)

```bash
git clone <repository-url>
cd obsidiann-webapp-shop
```

### 2. Создать .env файл для backend

Создайте файл `backend/.env` со следующим содержимым:

```env
# Django Settings
SECRET_KEY=your-secret-key-for-development-only
DEBUG=true
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_HOST=postgres
DB_NAME=flower_shop
DB_USER=postgres
DB_PASSWORD=postgres
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# Celery
CELERY_BROKER_URL=redis://redis:6379/1

# CORS
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000

# Storage (local для разработки)
USE_S3=false

# Telegram Bot (опционально, можно оставить пустым)
TELEGRAM_BOT_TOKEN=
TELEGRAM_ADMIN_CHAT_ID=
```

### 3. Запустить упрощенную версию (БЕЗ Celery)

Используйте упрощенный docker-compose без фоновых задач:

```bash
docker compose -f docker-compose.dev-simple.yml up -d
```

Эта команда запустит только необходимые сервисы:
- API (Django backend) на порту 8000
- PostgreSQL на порту 5432
- Redis на порту 6379

### 4. Выполнить миграции и создать суперпользователя

```bash
# Войти в контейнер API
docker compose -f docker-compose.dev-simple.yml exec api bash

# Выполнить миграции
python manage.py migrate

# Создать суперпользователя
python manage.py createsuperuser

# Выйти из контейнера
exit
```

### 5. Проверить работу

- Backend API: http://localhost:8000/api/v1/
- Django Admin: http://localhost:8000/admin/
- API документация: http://localhost:8000/api/schema/swagger-ui/

## Полезные команды

### Просмотр логов

```bash
# Все сервисы
docker compose -f docker-compose.dev-simple.yml logs -f

# Только API
docker compose -f docker-compose.dev-simple.yml logs -f api

# Только БД
docker compose -f docker-compose.dev-simple.yml logs -f postgres
```

### Остановить сервисы

```bash
# Остановить без удаления данных
docker compose -f docker-compose.dev-simple.yml stop

# Остановить и удалить контейнеры (данные БД сохранятся)
docker compose -f docker-compose.dev-simple.yml down

# Остановить и удалить ВСЕ (включая данные БД)
docker compose -f docker-compose.dev-simple.yml down -v
```

### Перезапустить сервисы

```bash
# Перезапустить все
docker compose -f docker-compose.dev-simple.yml restart

# Перезапустить только API
docker compose -f docker-compose.dev-simple.yml restart api
```

### Пересобрать образы после изменений

```bash
# Пересобрать все образы
docker compose -f docker-compose.dev-simple.yml build

# Пересобрать только API
docker compose -f docker-compose.dev-simple.yml build api

# Пересобрать и запустить
docker compose -f docker-compose.dev-simple.yml up -d --build
```

### Выполнить команды Django

```bash
# Войти в контейнер
docker compose -f docker-compose.dev-simple.yml exec api bash

# Или выполнить команду напрямую
docker compose -f docker-compose.dev-simple.yml exec api python manage.py <command>
```

Примеры:
```bash
# Создать миграции
docker compose -f docker-compose.dev-simple.yml exec api python manage.py makemigrations

# Применить миграции
docker compose -f docker-compose.dev-simple.yml exec api python manage.py migrate

# Собрать статику
docker compose -f docker-compose.dev-simple.yml exec api python manage.py collectstatic --noinput

# Django shell
docker compose -f docker-compose.dev-simple.yml exec api python manage.py shell
```

### Работа с базой данных

```bash
# Подключиться к PostgreSQL
docker compose -f docker-compose.dev-simple.yml exec postgres psql -U postgres -d flower_shop

# Сделать бэкап БД
docker compose -f docker-compose.dev-simple.yml exec postgres pg_dump -U postgres flower_shop > backup.sql

# Восстановить из бэкапа
cat backup.sql | docker compose -f docker-compose.dev-simple.yml exec -T postgres psql -U postgres -d flower_shop
```

## Полная версия с Celery (для разработки фоновых задач)

Если нужно работать с фоновыми задачами (Celery), используйте полный docker-compose:

```bash
# Запустить все сервисы включая Celery Worker и Celery Beat
docker compose up -d

# Остановить
docker compose down
```

Полная версия включает:
- Frontend (React + Vite) на порту 5173
- API (Django) на порту 8000
- PostgreSQL на порту 5432
- Redis на порту 6379
- Celery Worker (фоновые задачи)
- Celery Beat (планировщик задач)

## Разработка без Docker (альтернатива)

Если хотите разрабатывать без Docker:

### Backend

1. Установите Python 3.12 и uv:
   ```bash
   pip install uv
   ```

2. Установите зависимости:
   ```bash
   cd backend
   uv sync
   ```

3. Настройте .env для локальной БД:
   ```env
   DB_HOST=localhost
   # ... остальные настройки
   ```

4. Запустите PostgreSQL и Redis локально или через Docker:
   ```bash
   docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=flower_shop postgres:16-alpine
   docker run -d -p 6379:6379 redis:7-alpine
   ```

5. Запустите Django:
   ```bash
   cd src
   python manage.py migrate
   python manage.py runserver
   ```

### Frontend

1. Установите Node.js (LTS версия)

2. Установите зависимости:
   ```bash
   cd frontend
   npm install
   ```

3. Запустите dev server:
   ```bash
   npm run dev
   ```

## Типичные проблемы

### Порты заняты

Если порты 8000, 5432 или 6379 уже используются:

```bash
# Проверить, что занимает порт
netstat -ano | findstr :8000

# Остановить процесс по PID
taskkill /PID <pid> /F
```

### Ошибка подключения к БД

Убедитесь, что PostgreSQL контейнер запущен:

```bash
docker compose -f docker-compose.dev-simple.yml ps
docker compose -f docker-compose.dev-simple.yml logs postgres
```

### Docker Desktop не запущен

Запустите Docker Desktop перед выполнением команд docker compose.

### Изменения в коде не применяются

В dev-режиме используется hot reload, но если не работает:

```bash
# Перезапустите API контейнер
docker compose -f docker-compose.dev-simple.yml restart api
```

### Ошибки миграций

```bash
# Сбросить миграции (ОСТОРОЖНО: удалит все данные)
docker compose -f docker-compose.dev-simple.yml down -v
docker compose -f docker-compose.dev-simple.yml up -d
docker compose -f docker-compose.dev-simple.yml exec api python manage.py migrate
```

## Структура проекта

```
obsidiann-webapp-shop/
├── backend/              # Django backend
│   ├── src/             # Исходный код Django
│   │   ├── apps/        # Django приложения
│   │   ├── settings/    # Настройки Django (модульные)
│   │   └── manage.py    # Django CLI
│   ├── Dockerfile       # Production образ
│   ├── Dockerfile.dev   # Development образ с hot reload
│   └── .env            # Переменные окружения
├── frontend/            # React + Vite frontend
├── docs/               # Документация
├── docker-compose.yml           # Полная версия для разработки
├── docker-compose.dev-simple.yml # Упрощенная версия (рекомендуется)
└── docker-compose.prod.yml      # Production версия
```

## Дальнейшие шаги

После успешного запуска:

1. Откройте Django Admin: http://localhost:8000/admin/
2. Войдите с учетными данными суперпользователя
3. Изучите API документацию: http://localhost:8000/api/schema/swagger-ui/
4. Начинайте разработку в `backend/src/apps/`

Изменения в коде автоматически применятся благодаря volume mounting и hot reload.
