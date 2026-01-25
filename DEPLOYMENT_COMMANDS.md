# 🚀 Команды для развёртывания обновлений

## После git pull - применить изменения на сервере

### 1. Получить обновления с GitHub

```bash
cd /home/obsidiann-tg-shop
git pull origin main
```

### 2. Перезапустить контейнеры

```bash
# Вариант A: Пересоздать контейнеры (рекомендуется для изменений в коде Python)
docker compose down
docker compose up -d

# Вариант B: Просто перезапуск (если изменения незначительные)
docker compose restart api

# Вариант C: Force recreate (если не помогает вариант A)
docker compose up -d --force-recreate api
```

### 3. Применить миграции (если есть изменения в моделях)

```bash
# Проверить есть ли неприменённые миграции
docker compose exec api python manage.py showmigrations | grep "\[ \]"

# Применить миграции
docker compose exec api python manage.py migrate
```

### 4. Проверить что всё работает

```bash
# Проверить статус контейнеров
docker compose ps

# Посмотреть логи
docker compose logs api | tail -50

# Проверить API
curl http://localhost:8000/health/
```

---

## 🔒 Тестирование Telegram-only защиты

### Проверка 1: Статус защиты

```bash
docker compose exec api python manage.py telegram_protection status
```

**Ожидаемый результат:**
```
🔒 Telegram-only защита: ВКЛЮЧЕНА
   Доступ разрешён только из Telegram Mini App
```

### Проверка 2: Блокировка обычного браузера

```bash
# Попытка доступа без Telegram (должно вернуть 403)
curl -v http://localhost:8000/api/v1/products/ 2>&1 | grep -E "HTTP|error"
```

**Ожидаемый результат:**
```
< HTTP/1.1 403 Forbidden
{"error":"Telegram Required","message":"This application can only be accessed through Telegram Mini App"}
```

### Проверка 3: Доступ с JWT токеном

```bash
# Если у вас есть JWT токен - проверьте что он работает
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" http://localhost:8000/api/v1/products/
```

**Ожидаемый результат:** `200 OK` с данными товаров

### Проверка 4: Admin панель доступна

```bash
curl -I http://localhost:8000/admin/
```

**Ожидаемый результат:** `200 OK` или `302 Found` (редирект на login)

### Проверка 5: Из Telegram Mini App

1. Откройте бота в Telegram
2. Запустите Web App
3. Приложение должно загрузиться и показать товары
4. **Не должно быть ошибок 403**

### Проверка 6: Логи middleware

```bash
# Посмотреть что middleware пишет в логи
docker compose logs api | grep -i "telegram-only"
docker compose logs api | grep "Access denied" | tail -10
docker compose logs api | grep "JWT token" | tail -10
```

---

## 🐛 Troubleshooting

### Проблема: Защита не работает (доступ из браузера разрешён)

```bash
# 1. Проверьте переменную окружения
docker compose exec api env | grep ENFORCE_TELEGRAM_ONLY

# Должно быть: ENFORCE_TELEGRAM_ONLY=true

# 2. Если переменная не установлена - проверьте .env
cat backend/.env | grep ENFORCE_TELEGRAM_ONLY

# 3. Если в .env правильно, но в контейнере неправильно:
docker compose down
docker compose up -d

# 4. Проверьте логи запуска
docker compose logs api | grep "Telegram-only mode"
```

### Проблема: Из Telegram тоже не работает (403 ошибка)

```bash
# 1. Проверьте что TELEGRAM_BOT_TOKEN установлен
docker compose exec api env | grep TELEGRAM_BOT_TOKEN

# Должна быть длинная строка, не пустая!

# 2. Посмотрите логи ошибок
docker compose logs api | grep "Access denied" | tail -20

# 3. Проверьте что frontend отправляет initData
# В браузере откройте DevTools -> Network -> выберите запрос -> Headers
# Должен быть заголовок: X-Telegram-Init-Data: query_id=...
```

### Проблема: БД пропала после перезапуска

```bash
# 1. Проверьте volumes
docker volume ls | grep postgres

# 2. Если volume есть - проверьте его использование
docker compose config | grep volumes -A 5

# 3. Восстановите из бэкапа
gunzip < backups/latest_backup.sql.gz | docker compose exec -T postgres psql -U postgres -d flower_shop
```

---

## 📦 Полный цикл обновления

Используйте эти команды при каждом обновлении кода:

```bash
#!/bin/bash
# Скрипт для безопасного обновления

set -e  # Остановиться при ошибке

cd /home/obsidiann-tg-shop

echo "📦 1. Создаём бэкап БД..."
./backup-db.sh

echo "📥 2. Получаем обновления..."
git pull origin main

echo "🔨 3. Пересобираем контейнеры..."
docker compose down
docker compose up -d

echo "⏳ 4. Ждём запуска..."
sleep 10

echo "🗄️ 5. Применяем миграции..."
docker compose exec api python manage.py migrate

echo "✅ 6. Проверяем статус..."
docker compose ps
docker compose logs api | tail -20

echo "🎉 Обновление завершено!"
```

Сохраните этот скрипт как `update.sh` и используйте:

```bash
chmod +x update.sh
./update.sh
```

---

## 🔐 Управление защитой

### Включить защиту

```bash
# Через команду
docker compose exec api python manage.py telegram_protection enable
docker compose restart api

# ИЛИ вручную в .env
nano backend/.env
# Измените: ENFORCE_TELEGRAM_ONLY=true
docker compose restart api
```

### Выключить защиту (для разработки)

```bash
# Через команду
docker compose exec api python manage.py telegram_protection disable
docker compose restart api

# ИЛИ вручную в .env
nano backend/.env
# Измените: ENFORCE_TELEGRAM_ONLY=false
docker compose restart api
```

---

## 📊 Мониторинг

### Посмотреть логи в реальном времени

```bash
# Все сервисы
docker compose logs -f

# Только API
docker compose logs -f api

# Только ошибки
docker compose logs api | grep -i error

# Заблокированные запросы
docker compose logs api | grep "Access denied"
```

### Проверить использование ресурсов

```bash
# Использование CPU и памяти
docker stats

# Размер логов
docker compose logs api --tail 1000 | wc -l

# Размер volumes
docker system df -v
```
