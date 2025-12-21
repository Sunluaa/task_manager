# Разделение баз данных (Database per Service)

## Что было изменено

### 1. Архитектура БД
**Было:** Один контейнер PostgreSQL с тремя БД (auth_db, tasks_db, notifications_db)  
**Стало:** Три отдельных контейнера PostgreSQL, каждый с собственной БД

### 2. Контейнеры в docker-compose.yml
- `postgres-auth` → слушает на порту 5432 (auth_db)
- `postgres-tasks` → слушает на порту 5433 (tasks_db)  
- `postgres-notifications` → слушает на порту 5434 (notifications_db)

Каждый имеет:
- Собственный volume (postgres_auth_data, postgres_tasks_data, postgres_notifications_data)
- Независимые init-скрипты
- Отдельный healthcheck

### 3. Connection Strings
- **Auth Service:** `postgresql://postgres:postgres@postgres-auth:5432/auth_db` (docker) / `localhost:5432` (local)
- **Tasks Service:** `postgresql://postgres:postgres@postgres-tasks:5432/tasks_db` (docker) / `localhost:5433` (local)
- **Notifications Service:** `postgresql://postgres:postgres@postgres-notifications:5432/notifications_db` (docker) / `localhost:5434` (local)

### 4. Init-скрипты
Созданы отдельные файлы инициализации:
- `init-auth-db.sql` — таблица users
- `init-tasks-db.sql` — таблица tasks с индексами
- `init-notifications-db.sql` — таблица notifications с индексами

## Преимущества

✅ **Истинная автономия сервисов**
- Каждый сервис контролирует свою БД полностью
- Независимые обновления схемы без влияния на другие сервисы
- Возможность использовать разные типы БД (PostgreSQL, MongoDB и т.д.)

✅ **Масштабируемость**
- Каждую БД можно масштабировать независимо
- Разные SLA и требования к памяти для каждого сервиса

✅ **Отказоустойчивость**
- Падение одной БД не влияет на остальные сервисы
- Независимые backup'ы и восстановление

✅ **Миграции и версионирование**
- Миграции для одного сервиса не требуют координации
- Проще откатывать изменения

## Запуск

```bash
# Стартовать все контейнеры
docker-compose up -d

# Проверить состояние БД
docker-compose ps
docker-compose logs postgres-auth
docker-compose logs postgres-tasks
docker-compose logs postgres-notifications

# Подключиться к конкретной БД
psql postgresql://postgres:postgres@localhost:5432/auth_db
psql postgresql://postgres:postgres@localhost:5433/tasks_db
psql postgresql://postgres:postgres@localhost:5434/notifications_db
```

## Следующие шаги для полной микросервисной архитектуры

1. **Асинхронная коммуникация между сервисами**
   - Event-driven интеграция через Kafka/RabbitMQ/Redis Streams
   - Вместо синхронных HTTP вызовов

2. **Event Sourcing для синхронизации**
   - Вместо прямых обращений к чужим БД
   - Сервис публикует события (user_created, task_assigned и т.д.)

3. **Distributed Tracing**
   - OpenTelemetry для отслеживания запросов через микросервисы

4. **Saga Pattern**
   - Для транзакций между несколькими сервисами

5. **API Versioning**
   - /api/v1/, /api/v2/ для обратной совместимости

6. **Circuit Breaker**
   - Обработка сбоев при обращении между сервисами
