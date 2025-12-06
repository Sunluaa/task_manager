# Архитектура системы управления задачами

## Общее описание

Микросервисная система для управления задачами по ремонту и обслуживанию помещений. Включает 4 микросервиса + API Gateway + Frontend.

## Выбор компонентов

### 1. API Gateway: FastAPI вместо Traefik

**Обоснование выбора:**

| Параметр | FastAPI | Traefik |
|----------|---------|---------|
| Сложность настройки | Низкая | Высокая |
| Гибкость логики маршрутизации | Высокая | Средняя |
| Встроенная документация API | Да (Swagger UI) | Нет |
| Возможность добавления middleware | Да (полная) | Ограничена |
| Контроль над трансформацией запросов | Да | Частично |
| Production-ready | Да, с оптимизацией | Да |
| Масштабируемость | Отличная | Отличная |

**Вывод:** FastAPI выбран для демонстрации и разработки благодаря гибкости и простоте добавления функций. В production рекомендуется Traefik с более высокой производительностью и встроенными возможностями Kubernetes.

### 2. Архитектура БД: Полиглот

**Используется:** PostgreSQL с отдельными БД для каждого сервиса

**Базы данных:**
- `auth_db` - Аутентификация и управление пользователями
- `tasks_db` - Задачи, комментарии, история
- `notifications_db` - Уведомления и логирование

**Обоснование полиглота:**

1. **Масштабируемость:** Каждый сервис может оптимизировать свою схему
2. **Независимость:** Обновления схемы не требуют координации
3. **Производительность:** Нет кросс-сервисных транзакций
4. **Надежность:** Отказ одной БД не влияет на другие сервисы
5. **Миграция:** Легко мигрировать отдельный сервис на другой стек

## Микросервисы

### 1. Auth Service (порт 8001)

**Ответственность:**
- Аутентификация пользователей
- Управление ролями и доступом
- JWT токены
- Управление пользователями

**Таблицы:**
```
users:
  - id (PK)
  - email (UNIQUE)
  - password_hash
  - full_name
  - role (ENUM: admin, worker)
  - is_active
  - created_at, updated_at
```

**Ключевые операции:**
- POST /auth/register - Регистрация
- POST /auth/login - Вход (выдает JWT)
- POST /auth/verify - Проверка токена
- CRUD операции над пользователями

### 2. Tasks Service (порт 8002)

**Ответственность:**
- Управление задачами
- История изменений
- Система комментариев
- Отслеживание выполнения

**Таблицы:**
```
tasks:
  - id (PK)
  - title
  - description
  - status (ENUM: new, in_progress, completed, rework)
  - priority (ENUM: low, medium, high, critical)
  - created_by (FK -> users)
  - created_at, updated_at

comments:
  - id (PK)
  - task_id (FK)
  - user_id
  - text
  - created_at

history:
  - id (PK)
  - task_id (FK)
  - event_type (ENUM: created, status_changed, assigned, etc)
  - user_id
  - details (JSON)
  - created_at

worker_completions:
  - id (PK)
  - task_id (FK)
  - worker_id
  - completed_at

task_workers (M2M):
  - task_id (FK)
  - worker_id
```

**Жизненный цикл задачи:**

```
NEW → IN_PROGRESS → COMPLETED
         ↓
      REWORK → IN_PROGRESS
```

**Правила:**
- Задача может быть создана только администратором
- Один администратор может назначить задачу нескольким рабочим
- Все рабочие должны отметить выполнение для завершения
- Администратор может вернуть на доработку в любой момент
- История отслеживает все события

### 3. Notifications Service (порт 8003)

**Ответственность:**
- Управление уведомлениями пользователей
- Отслеживание прочитанных уведомлений
- История событий

**Таблицы:**
```
notifications:
  - id (PK)
  - user_id
  - title
  - message
  - is_read
  - created_at
  - read_at
```

**Интеграция:**
- Создается при назначении задачи
- Создается при комментарии
- Создается при одобрении/отказе

### 4. Notifications Service (порт 8003)

**Ответственность:**
- Отправка уведомлений о событиях
- Логирование событий системы
- Оповещение пользователей об изменениях

## API Gateway

**Функциональность:**
- Маршрутизация запросов к микросервисам
- CORS обработка
- Трансформация заголовков
- Логирование запросов
- Обработка ошибок

**Маршруты:**
```
/api/auth/*      → auth-service:8001
/api/tasks/*     → tasks-service:8002
/api/notifications/* → notifications-service:8003
```

## Frontend

**Фреймворк:** Vue 3 + Pinia + Vite

**Структура:**
```
src/
  ├── api/
  │   └── client.js - HTTP клиент
  ├── components/ - Переиспользуемые компоненты
  ├── views/ - Страницы
  ├── stores/ - Pinia хранилище (authStore, taskStore)
  ├── router/ - Vue Router конфигурация
  └── App.vue - Главный компонент
```

**Роли и интерфейсы:**

**Администратор:**
- Верхнее меню с вкладками: Все задачи, Новые, В процессе, Выполненные
- Форма создания задачи
- Форма редактирования задачи
- Назначение исполнителей
- Просмотр комментариев и истории
- Одобрение/возврат на доработку
- Список и управление пользователями

**Работник:**
- Список только своих задач
- Кнопка отметить выполнено
- Просмотр истории
- Добавление комментариев
- Просмотр информации о задаче

## Безопасность

### JWT Аутентификация

```
POST /api/auth/login
Response: {
  access_token: "eyJhbGc...",
  token_type: "bearer",
  user: { id, email, role, ... }
}
```

**Клиент хранит токен:** localStorage

**Отправка:** Все запросы содержат `Authorization: Bearer <token>`

### Контроль доступа

```python
# На уровне контроллера
@app.get("/tasks")
def get_tasks(user_id: int, user_role: str):  # Из токена
    if user_role == "admin":
        return all_tasks
    else:
        return user_tasks
```

### Хеширование паролей

**Метод:** bcrypt

```python
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"])
hash = pwd_context.hash(password)
is_valid = pwd_context.verify(password, hash)
```

## Развертывание

### Docker Compose (Локально)

```bash
docker-compose up --build
```

**Сервисы:**
- PostgreSQL (5432)
- Auth Service (8001)
- Tasks Service (8002)
- Notifications Service (8003)
- API Gateway (8000)
- Frontend (3000)

### Kubernetes

**Объекты:**
- Deployment: Каждый сервис + PostgreSQL
- Service: ClusterIP для микросервисов, LoadBalancer для Gateway и Frontend
- ConfigMap: Конфигурация приложения
- Secret: Пароли и ключи
- PVC: Персистентное хранилище для БД
- Ingress: Маршрутизация HTTP

**Команды:**
```bash
kubectl apply -f kubernetes/
kubectl get pods
kubectl get services
```

## Масштабирование

### Горизонтальное

```bash
# Docker Compose
docker-compose up --scale tasks-service=3

# Kubernetes
kubectl scale deployment tasks-service --replicas=3
```

### Вертикальное

Ограничение ресурсов в Kubernetes:
```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

## Мониторинг

**Health Check Endpoints:**
- GET /health

**Логирование:**
- Все операции логируются
- Уровни: INFO, WARNING, ERROR

**Prometheus метрики:**
- Можно добавить `/metrics` эндпоинты

## Интеграция сервисов

### Асинхронные операции

В production рекомендуется добавить:
- RabbitMQ для очереди задач
- Redis для кэширования
- ELK Stack для логирования

### События

```
Task Created → Отправить уведомление рабочим
Task Completed → Обновить analytics
Task Approved → Отправить уведомление администратору
```

## Резервная копия

```bash
# PostgreSQL backup
docker exec course2_postgres_1 pg_dump -U postgres auth_db > auth_db.sql

# Restore
docker exec -i course2_postgres_1 psql -U postgres auth_db < auth_db.sql
```

## Производство

Перед деплоем в production:

1. ✅ Настроить SSL/TLS
2. ✅ Включить HTTPS
3. ✅ Настроить настоящую БД (RDS, Cloud SQL)
4. ✅ Использовать Traefik вместо FastAPI Gateway
5. ✅ Добавить Redis для сессий
6. ✅ Включить логирование (ELK, Datadog)
7. ✅ Настроить мониторинг (Prometheus, Grafana)
8. ✅ Автоматизировать backup
9. ✅ Настроить CI/CD (GitHub Actions, GitLab CI)
10. ✅ Использовать environment-specific конфиги

