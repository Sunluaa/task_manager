# Асинхронная интеграция микросервисов (Event-Driven Architecture)

## Обзор

Реализована **event-driven архитектура** для слабой связности между сервисами на основе **Redis Streams**. Это позволяет сервисам взаимодействовать асинхронно без прямых HTTP вызовов и зависимостей.

## Архитектура

```
┌─────────────────┐         ┌──────────────────┐
│  Auth Service   │────────▶│   Redis Streams  │
│ (user.created)  │         │  (Event Bus)     │
└─────────────────┘         └──────────────────┘
                                    △
                                    │
                            ┌───────┴────────┐
                            │                │
                    ┌───────▼────────┐  ┌───▼──────────┐
                    │ Tasks Service  │  │ Notifications│
                    │(task.created)  │  │   Consumer   │
                    └────────────────┘  │  (processes) │
                                        └──────────────┘
```

## События (Events)

### Типы событий

```python
class EventType(str, Enum):
    # Auth events
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"
    
    # Task events
    TASK_CREATED = "task.created"
    TASK_UPDATED = "task.updated"
    TASK_DELETED = "task.deleted"
    TASK_ASSIGNED = "task.assigned"
    TASK_COMPLETED = "task.completed"
    
    # Notification events
    NOTIFICATION_SENT = "notification.sent"
    NOTIFICATION_FAILED = "notification.failed"
```

## Поток данных

### 1. Создание задачи (Tasks Service)

**Синхронный вызов:**
```
HTTP POST /api/tasks/
  ├─ Сохрани в tasks_db
  └─ Опубликуй TASK_CREATED событие → Redis Streams
```

**Событие в Redis:**
```json
{
  "type": "task.created",
  "aggregate_id": "123",
  "aggregate_type": "task",
  "data": {
    "task_id": 123,
    "title": "Fix bug",
    "worker_ids": [2, 3]
  },
  "timestamp": "2025-01-15T10:30:00"
}
```

### 2. Потребление события (Notifications Service)

**Event Consumer Worker** слушает Redis Streams:

```
Redis Stream (events:task.created)
          │
          ▼
   Event Consumer
   (event_consumer_worker.py)
          │
          ├─ Обработай событие
          ├─ Создай уведомления в notifications_db
          └─ Подтверди обработку (ACK)
```

### 3. Обработка ошибок (Retry & DLQ)

```
                ┌─ Обработать событие
                │      ▼
Redis Stream ───┤   ✓ Успех → ACK, удалить
                │      ▼
                │   ✗ Ошибка → Retry
                │      │ (MAX=3)
                │      ├─ Retry 1
                │      ├─ Retry 2
                │      ├─ Retry 3
                │      │
                │      └─ Max retries ► DLQ (Dead Letter Queue)
                │
                └─ event_dlq (Redis Stream)
                      │
                      └─ Ручное переобработка
```

**Retry механизм:**
- Максимум 3 попытки обработки
- Каждая попытка повторно добавляется в stream
- После 3 попыток событие отправляется в DLQ

## Реализация

### Event Bus (`shared_events/event_bus.py`)

```python
# Публикация события
event_bus = get_event_bus()
event = Event(
    event_type=EventType.TASK_CREATED,
    aggregate_id=str(task_id),
    aggregate_type="task",
    data={...}
)
event_bus.publish(event)

# Подписка на события
event_bus.subscribe(EventType.TASK_CREATED, handle_task_created)

# Потребление с retry и DLQ
event_bus.consume_events(
    event_type=EventType.TASK_CREATED,
    consumer_group="notifications_service"
)
```

### Event Consumer (`notifications-service/event_consumer_worker.py`)

```python
consumer = NotificationEventConsumer(db_session_factory=SessionLocal)

# Обработчики регистрируются автоматически
# TASK_CREATED → создай уведомление для worker'ов
# TASK_UPDATED → создай уведомление для admin'а
# TASK_COMPLETED → создай уведомление для creator'а
```

## Redis Streams структура

### Обычные потоки (Streams)

```
events:task.created
  ├─ ID: 1705319400000-0
  │  data: {type, aggregate_id, data...}
  ├─ ID: 1705319401000-0
  │  data: {...}
  └─ ID: 1705319402000-0
     data: {...}

events:user.created
  └─ ID: 1705319403000-0
     data: {email, full_name, ...}
```

### Consumer Groups (для отслеживания обработки)

```
notifications:task.created
  ├─ Processed: event1, event2
  └─ Pending: event3 (retry count: 1)
```

### Dead Letter Queue (DLQ)

```
event_dlq
  ├─ ID: error-1
  │  original_id: 1705319400000-0
  │  error: "Connection timeout"
  │  failed_at: "2025-01-15T10:35:00"
  └─ ID: error-2
     original_id: 1705319401000-0
     error: "DB constraint violation"
```

## Использование в Services

### Auth Service (Публикация)

```python
# auth-service/app/services/auth_service.py

@staticmethod
def register_user(db: Session, user_create: UserCreate) -> User:
    db_user = User(...)
    db.add(db_user)
    db.commit()
    
    # Опубликуй событие
    event = Event(
        event_type=EventType.USER_CREATED,
        aggregate_id=str(db_user.id),
        aggregate_type="user",
        data={"email": db_user.email, "user_id": db_user.id}
    )
    event_bus.publish(event)
    
    return db_user
```

### Tasks Service (Публикация)

```python
# tasks-service/app/controllers/task_controller.py

@router.post("/", response_model=TaskResponse)
async def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    db_task = TaskService.create_task(db, ...)
    
    # Опубликуй событие
    event = Event(
        event_type=EventType.TASK_CREATED,
        aggregate_id=str(db_task.id),
        aggregate_type="task",
        data={"task_id": db_task.id, "title": db_task.title, ...}
    )
    event_bus.publish(event)
    
    return db_task
```

### Notifications Service (Потребление)

```python
# notifications-service/app/services/event_consumer.py

class NotificationEventConsumer:
    def _handle_task_created(self, event: Event):
        # Получи данные события
        task_data = event.data
        worker_ids = task_data.get("worker_ids", [])
        
        # Создай уведомления для worker'ов
        for worker_id in worker_ids:
            notification = Notification(
                user_id=worker_id,
                task_id=int(event.aggregate_id),
                message=f"New task: {task_data['title']}"
            )
            db.add(notification)
        
        db.commit()  # Если успех → будет ACK
        # Если исключение → будет retry
```

## Запуск

### Docker Compose

```bash
# Стартовать все сервисы
docker-compose up -d

# Проверить что все работает
docker-compose ps

# Смотреть логи event consumer'а
docker-compose logs -f event-consumer-worker
```

### Локально (для разработки)

```bash
# Терминал 1: Starten Auth Service
cd auth-service
python -m uvicorn main:app --reload --port 8001

# Терминал 2: Start Tasks Service
cd tasks-service
python -m uvicorn main:app --reload --port 8002

# Терминал 3: Start Notifications Service
cd notifications-service
python -m uvicorn main:app --reload --port 8003

# Терминал 4: Start Event Consumer Worker
cd notifications-service
python event_consumer_worker.py
```

## Redis CLI Commands

### Просмотр потоков

```bash
# Подключиться к Redis
redis-cli

# Просмотр потоков
XRANGE events:task.created - +

# Просмотр consumer groups
XINFO GROUPS events:task.created

# Просмотр DLQ
XRANGE event_dlq - +

# Статистика потока
XINFO STREAM events:task.created
```

### Управление DLQ

```bash
# Посмотреть ошибки
XRANGE event_dlq - +

# Переобработать сообщение из DLQ
# (через API: POST /admin/dlq/reprocess/{msg_id})

# Очистить DLQ
DEL event_dlq
```

## Преимущества Event-Driven Architecture

✅ **Слабая связность (Loose Coupling)**
- Сервисы не знают друг о друге напрямую
- Изменения в одном сервисе не ломают другие

✅ **Масштабируемость**
- Можно добавить новый consumer без изменения publisher'а
- Разные consumer'ы могут обрабатывать независимо

✅ **Отказоустойчивость**
- Если notification service вниз → события остаются в Redis
- Когда сервис восстановится → обработает накопившиеся события

✅ **Асинхронность**
- Publisher не ждёт consumer'а
- Быстрый ответ пользователю (~100ms вместо 500ms+ с синхронными вызовами)

✅ **Аудит и История**
- Redis Streams хранят всю историю событий
- Можно переиграть (replay) события если нужно

✅ **Dead Letter Queue для мониторинга**
- Ошибки централизованы в одном месте
- Легко видеть и исправлять проблемы

## Следующие шаги

1. **Распределённые транзакции (Saga Pattern)**
   - Для сложных операций через несколько сервисов

2. **API для управления DLQ**
   - `/admin/dlq` - просмотр ошибочных событий
   - `/admin/dlq/reprocess` - переобработка

3. **Monitoring & Alerting**
   - Metrics на Redis Streams (lag, processed rate)
   - Alerts если DLQ растёт

4. **Event Sourcing**
   - Хранить полную историю всех событий
   - Восстановление состояния из события

5. **Kafka вместо Redis Streams**
   - Для очень высокого объёма событий
   - Лучше потребление, лучше гарантии доставки
