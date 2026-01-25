# 🌸 Flower Shop - Telegram Web App

Полнофункциональный магазин цветов для Telegram с использованием Web App API.

## 📋 Содержание

- [Технологии](#технологии)
- [Требования](#требования)
- [Быстрый старт](#быстрый-старт)
- [Разработка](#разработка)
- [Производство](#производство)
- [API Документация](#api-документация)
- [Структура проекта](#структура-проекта)

## 🛠 Технологии

### Backend
- **Django 5.2** - основной фреймворк
- **Django REST Framework** - API
- **PostgreSQL 16** - база данных
- **Redis 7** - кеш и брокер сообщений
- **Celery** - фоновые задачи
- **Python Telegram Bot** - интеграция с Telegram

### Frontend
- **React 18** - UI библиотека
- **TypeScript** - типизация
- **Vite** - сборщик
- **TailwindCSS** - стилизация
- **Zustand** - управление состоянием
- **React Query** - работа с API

## ✅ Требования

- Docker 20.10+
- Docker Compose 2.0+
- Make (опционально, для удобства)

## 🚀 Быстрый старт

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd obsidiann-webapp-shop
```

### 2. Настройка переменных окружения

#### Backend

```bash
cd backend
cp .env.example .env
```

Отредактируйте файл `backend/.env`:

```env
# Django
SECRET_KEY=your-super-secret-key-change-me
DEBUG=true
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Database
DB_NAME=flower_shop
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=postgres
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/1

# Telegram Bot (получите токен у @BotFather)
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_BOT_USERNAME=your_bot_username
TELEGRAM_MINI_APP_URL=https://your-app-url.com

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

#### Frontend

```bash
cd ../frontend
cp .env.example .env
```

Отредактируйте файл `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000/api/v1
VITE_TELEGRAM_BOT_USERNAME=your_bot_username
```

### 3. Запуск приложения

#### Вариант 1: С использованием Make (рекомендуется)

```bash
# Вернитесь в корень проекта
cd ..

# Запуск всех сервисов
make up

# Применение миграций
make migrate

# Создание суперпользователя
make createsuperuser

# Просмотр логов
make logs
```

#### Вариант 2: Без Make

```bash
# Запуск всех сервисов
docker compose up -d

# Применение миграций
docker compose exec api python manage.py migrate

# Создание суперпользователя
docker compose exec api python manage.py createsuperuser

# Просмотр логов
docker compose logs -f
```

### 4. Доступ к приложению

- **Frontend (Web App)**: http://localhost:5173
- **Backend API**: http://localhost:8000/api/v1
- **Django Admin**: http://localhost:8000/admin
- **API Documentation**: http://localhost:8000/api/schema/swagger-ui/

## 💻 Разработка

### Полезные команды Make

```bash
make help            # Показать все доступные команды
make up              # Запустить все сервисы
make down            # Остановить все сервисы
make logs            # Показать логи всех сервисов
make logs-api        # Показать логи API
make logs-frontend   # Показать логи frontend
make build           # Собрать все образы
make rebuild         # Пересобрать и перезапустить
make restart         # Перезапустить сервисы
make migrate         # Применить миграции
make makemigrations  # Создать миграции
make shell           # Открыть Django shell
make dbshell         # Открыть PostgreSQL shell
make clean           # Удалить все контейнеры и образы
make reset-db        # Сбросить базу данных (ОСТОРОЖНО!)
```

### Настройка Telegram Bot

1. Создайте бота через [@BotFather](https://t.me/BotFather)
2. Получите токен бота и username
3. Настройте Web App:
   ```
   /mybots -> Выберите вашего бота -> Bot Settings -> Menu Button -> Edit Menu Button URL
   ```
4. Укажите URL: `https://your-domain.com` (в разработке можно использовать ngrok)

### Установка webhook

```bash
# Через Django management команду
docker compose exec api python manage.py setwebhook

# Или через Make
make shell
>>> from apps.bot.management.commands.setwebhook import Command
>>> Command().handle()
```

### Локальная разработка frontend (без Docker)

```bash
cd frontend

# Установка зависимостей
npm install

# Запуск dev сервера
npm run dev

# Линтинг
npm run lint

# Тесты
npm run test
```

### Локальная разработка backend (без Docker)

```bash
cd backend

# Установка uv (если еще не установлен)
pip install uv

# Установка зависимостей
uv sync --dev

# Запуск сервера
cd src
python manage.py runserver

# Запуск Celery worker
celery -A celery_app worker -l info

# Запуск Celery beat
celery -A celery_app beat -l info
```

## 🚢 Производство

### Запуск production версии

```bash
# С Make
make up-prod

# Без Make
docker compose -f docker-compose.prod.yml up -d
```

### Рекомендации для production

1. **Измените SECRET_KEY** в `.env`
2. **Установите DEBUG=false**
3. **Настройте ALLOWED_HOSTS** с вашим доменом
4. **Настройте HTTPS** (например, с Nginx + Let's Encrypt)
5. **Настройте S3/R2 для хранения медиа**:
   ```env
   USE_S3=true
   AWS_ACCESS_KEY_ID=your_key
   AWS_SECRET_ACCESS_KEY=your_secret
   AWS_STORAGE_BUCKET_NAME=your_bucket
   AWS_S3_ENDPOINT_URL=https://your-endpoint.com
   ```
6. **Настройте Sentry** для мониторинга ошибок:
   ```env
   SENTRY_DSN=your_sentry_dsn
   ```

## 📚 API Документация

### Основные эндпоинты

#### Аутентификация
- `POST /api/v1/auth/telegram/` - Авторизация через Telegram

#### Продукты
- `GET /api/v1/products/` - Список продуктов
- `GET /api/v1/products/{id}/` - Детали продукта
- `GET /api/v1/categories/` - Категории

#### Корзина
- `GET /api/v1/cart/` - Содержимое корзины
- `POST /api/v1/cart/add/` - Добавить в корзину
- `PUT /api/v1/cart/update/` - Обновить количество
- `DELETE /api/v1/cart/remove/` - Удалить из корзины

#### Заказы
- `GET /api/v1/orders/` - Список заказов
- `POST /api/v1/orders/` - Создать заказ
- `GET /api/v1/orders/{id}/` - Детали заказа

#### Избранное
- `GET /api/v1/favorites/` - Список избранного
- `POST /api/v1/favorites/` - Добавить в избранное
- `DELETE /api/v1/favorites/{id}/` - Удалить из избранного

Полная документация доступна по адресу: http://localhost:8000/api/schema/swagger-ui/

## 📁 Структура проекта

```
obsidiann-webapp-shop/
├── backend/                    # Django Backend
│   ├── src/
│   │   ├── apps/              # Django приложения
│   │   │   ├── analytics/     # Аналитика и статистика
│   │   │   ├── bot/           # Telegram бот
│   │   │   ├── cart/          # Корзина
│   │   │   ├── core/          # Базовые модели и утилиты
│   │   │   ├── orders/        # Заказы
│   │   │   ├── payments/      # Платежи
│   │   │   ├── products/      # Продукты и категории
│   │   │   └── users/         # Пользователи
│   │   ├── settings/          # Конфигурация Django
│   │   └── manage.py
│   ├── docker-compose.yml     # Docker Compose для разработки
│   ├── Dockerfile             # Production Dockerfile
│   └── pyproject.toml         # Python зависимости
│
├── frontend/                  # React Frontend
│   ├── src/
│   │   ├── components/        # React компоненты
│   │   ├── pages/            # Страницы приложения
│   │   ├── stores/           # Zustand stores
│   │   ├── hooks/            # Custom hooks
│   │   ├── lib/              # Утилиты и API
│   │   └── types/            # TypeScript типы
│   ├── public/               # Статические файлы
│   ├── package.json          # NPM зависимости
│   └── vite.config.ts        # Vite конфигурация
│
├── docker-compose.yml         # Основной Docker Compose
├── docker-compose.prod.yml    # Production Docker Compose
├── Makefile                   # Команды для разработки
└── README.md                  # Этот файл
```

## 🔧 Troubleshooting

### Проблемы с БД

```bash
# Сброс базы данных
make reset-db

# Или вручную
docker compose down -v
docker compose up -d postgres
docker compose exec api python manage.py migrate
```

### Проблемы с зависимостями

```bash
# Пересобрать образы
make rebuild

# Или
docker compose build --no-cache
docker compose up -d
```

### Проблемы с Telegram Bot

1. Проверьте правильность `TELEGRAM_BOT_TOKEN`
2. Убедитесь что webhook установлен: `make shell` → `setwebhook`
3. Проверьте доступность URL для Telegram (должен быть HTTPS в production)

### Просмотр логов

```bash
# Все логи
make logs

# Только API
make logs-api

# Только frontend
make logs-frontend

# Конкретный сервис
docker compose logs -f celery
```

## 📝 Лицензия

MIT

## 👥 Авторы

Ваше имя / Команда

---

**Документация последний раз обновлена:** Январь 2025
