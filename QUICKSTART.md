# 🚀 Быстрый старт

## За 5 минут до рабочей системы

### Требования

- Docker & Docker Compose

### Запуск (Очень просто!)

```bash
# 1. Переходим в папку проекта
cd course2

# 2. Запускаем все сервисы (БД создается автоматически!)
docker-compose up -d

# 3. Ждем 20-30 секунд инициализации

# 4. Открываем браузер
http://localhost:3000
```

**Данные для входа:**
- 📧 Email: `admin@admin.admin`
- 🔑 Password: `admin`

✨ **ВСЕ ГОТОВО!** БД автоматически создаются в контейнере при первом запуске.

### Альтернатива: Использование батника/скрипта

**Windows - двойной клик:**
```bash
init-databases.bat
```

**Linux/Mac:**
```bash
bash init-databases.sh
```

| Сервис | URL | Порт |
|--------|-----|------|
| Frontend | http://localhost:3000 | 3000 |
| API Gateway | http://localhost:8000 | 8000 |
| Auth Service | http://localhost:8001 | 8001 |
| Tasks Service | http://localhost:8002 | 8002 |
| Notifications Service | http://localhost:8003 | 8003 |
| Analytics Service | http://localhost:8004 | 8004 |
| PostgreSQL | localhost:5432 | 5432 |

## Первые шаги в приложении

### 👨‍💼 Вход как администратор

1. На странице логина введите:
   - Email: `admin@admin.admin`
   - Password: `admin`

2. Нажмите кнопку Login

### ➕ Создание первой задачи

1. На главной странице заполните форму:
   - **Title**: "Отремонтировать кровлю"
   - **Description**: "Заменить прокладку на балконе"
   - **Priority**: High

2. Нажмите "Create Task"

3. Задача появится в списке всех задач

### 📋 Просмотр и управление задачей

1. Нажмите на карточку задачи

2. В модальном окне:
   - Измените статус (New → In Progress → Completed)
   - Добавьте комментарий
   - Посмотрите историю изменений

### 👷 Роли и доступ

**Администратор:**
- Видит все задачи
- Может создавать, редактировать, удалять
- Может одобрять/отклонять выполнение
- 4 вкладки вверху: Все, Новые, В процессе, Выполненные

**Работник:**
- Видит только свои задачи
- Может отметить выполнение
- Может добавлять комментарии
- 1 кнопка: Мои задачи

## Остановка сервисов

```bash
# Остановить контейнеры
docker-compose down

# Остановить и удалить все данные
docker-compose down -v
```

## Просмотр логов

```bash
# Логи всех сервисов
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f auth-service
docker-compose logs -f tasks-service
docker-compose logs -f frontend

# Последние 50 строк
docker-compose logs --tail=50 auth-service
```

## Проверка статуса

```bash
# Статус всех контейнеров
docker-compose ps

# Посмотреть порты
docker-compose ps --format "table {{.Service}}\t{{.Ports}}"
```

## Решение проблем

### ❌ Ошибка подключения к БД

```bash
# Перезагрузить PostgreSQL
docker-compose restart postgres

# Подождать 30 секунд и заново запустить сервисы
docker-compose restart auth-service tasks-service notifications-service
```

### ❌ Port уже в использовании

```bash
# Освободить порт (на примере 3000)
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Mac/Linux
lsof -i :3000
kill -9 <PID>
```

### ❌ Frontend показывает ошибку 404

```bash
# Очистить кэш браузера (Ctrl+Shift+Del)
# или
docker-compose restart frontend
```

### ❌ API Gateway недоступен

```bash
# Проверить доступность сервисов
docker exec course2_api-gateway_1 curl http://auth-service:8001/health
docker exec course2_api-gateway_1 curl http://tasks-service:8002/health
```

## Проверка API через curl

### 1️⃣ Вход

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@admin.admin",
    "password": "admin"
  }'

# Ответ:
# {
#   "access_token": "eyJhbGc...",
#   "token_type": "bearer",
#   "user": {...}
# }
```

### 2️⃣ Получить токен

```bash
# Сохраним токен в переменную (Linux/Mac)
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@admin.admin",
    "password": "admin"
  }' | jq -r '.access_token')

echo $TOKEN
```

### 3️⃣ Создать задачу

```bash
curl -X POST http://localhost:8000/api/tasks/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "Test Task",
    "description": "This is a test",
    "priority": "high",
    "worker_ids": []
  }'
```

### 4️⃣ Получить все задачи

```bash
curl -X GET http://localhost:8000/api/tasks/ \
  -H "Authorization: Bearer $TOKEN"
```

### 5️⃣ Добавить комментарий

```bash
curl -X POST http://localhost:8000/api/tasks/1/comments \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"text": "Working on it"}'
```

## Важные команды

```bash
# Запустить все
docker-compose up -d

# Запустить определенный сервис
docker-compose up -d auth-service

# Пересобрать только определенный образ
docker-compose build --no-cache auth-service

# Масштабировать
docker-compose up --scale tasks-service=3

# Удалить все волюмы (осторожно!)
docker-compose down -v

# Посмотреть переменные окружения
docker-compose config

# Выполнить команду в контейнере
docker-compose exec auth-service bash

# Посмотреть использование памяти
docker stats
```

## Health Checks

Все сервисы имеют `/health` эндпоинт:

```bash
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
curl http://localhost:8004/health
```

## База данных

### Подключиться к PostgreSQL

```bash
# Через docker
docker exec -it course2_postgres_1 psql -U postgres

# SQL команды
\l              # Список БД
\c auth_db      # Подключиться к auth_db
\dt             # Список таблиц
SELECT * FROM users; # Запрос
```

### Backup БД

```bash
docker exec course2_postgres_1 pg_dump -U postgres auth_db > backup_auth.sql
```

### Restore БД

```bash
docker exec -i course2_postgres_1 psql -U postgres auth_db < backup_auth.sql
```

## Интеграция с IDE

### VS Code

1. Установить расширения:
   - Docker
   - Python
   - Vue - Official

2. Открыть папку проекта

3. Нажать F5 (Debug)

### PyCharm

1. Открыть папку проекта

2. Settings → Project → Python Interpreter

3. Добавить Docker интерпретатор

## Следующие шаги

📚 **Для подробного изучения:**
- Читайте `README.md` - общая информация
- Читайте `ARCHITECTURE.md` - архитектура системы
- Читайте `DEPLOYMENT.md` - деплой и настройка
- Читайте `PROJECT_STRUCTURE.md` - структура проекта

🚀 **Для deployment на production:**
- Используйте Kubernetes манифесты
- Настройте SSL/TLS
- Используйте Traefik вместо FastAPI Gateway
- Добавьте мониторинг

👨‍💻 **Для разработки:**
- Запустите отдельно каждый сервис
- Используйте dev режим Vite для frontend
- Используйте горячую перезагрузку Python

---

**Наслаждайтесь! 🎉**
