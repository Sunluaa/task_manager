# Полная структура проекта

## Директории и файлы

```
course2/
├── auth-service/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── controllers/
│   │   │   ├── __init__.py
│   │   │   └── auth_controller.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── user.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── user.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   └── auth_service.py
│   │   └── db/
│   │       ├── __init__.py
│   │       └── database.py
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .env
│   └── logging.yaml
│
├── tasks-service/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── controllers/
│   │   │   ├── __init__.py
│   │   │   └── task_controller.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── task.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── task.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   └── task_service.py
│   │   └── db/
│   │       ├── __init__.py
│   │       └── database.py
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env
│
├── notifications-service/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── controllers/
│   │   │   ├── __init__.py
│   │   │   └── notification_controller.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── notification.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── notification.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   └── notification_service.py
│   │   └── db/
│   │       ├── __init__.py
│   │       └── database.py
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env
│
├── analytics-service/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── controllers/
│   │   │   ├── __init__.py
│   │   │   └── analytics_controller.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── metric.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── metric.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   └── analytics_service.py
│   │   └── db/
│   │       ├── __init__.py
│   │       └── database.py
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env
│
├── api-gateway/
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── client.js
│   │   ├── stores/
│   │   │   ├── authStore.js
│   │   │   └── taskStore.js
│   │   ├── router/
│   │   │   └── index.js
│   │   ├── views/
│   │   │   ├── LoginView.vue
│   │   │   ├── DashboardView.vue
│   │   │   ├── MyTasksView.vue
│   │   │   ├── TasksView.vue
│   │   │   ├── TaskDetailView.vue
│   │   │   └── UsersView.vue
│   │   ├── App.vue
│   │   └── main.js
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── nginx.conf
│   ├── Dockerfile
│   ├── .env
│   └── .gitignore
│
├── kubernetes/
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── pvc.yaml
│   ├── postgres.yaml
│   ├── auth-service.yaml
│   ├── tasks-service.yaml
│   ├── notifications-service.yaml
│   ├── analytics-service.yaml
│   ├── api-gateway.yaml
│   ├── frontend.yaml
│   └── ingress.yaml
│
├── docker-compose.yml
├── init-db.sql
├── .gitignore
├── .dockerignore
├── README.md
├── DEPLOYMENT.md
├── ARCHITECTURE.md
└── PROJECT_STRUCTURE.md (этот файл)
```

## Технологический стек

### Backend
- **Runtime:** Python 3.11
- **Web Framework:** FastAPI 0.104.1
- **Server:** Uvicorn 0.24.0
- **ORM:** SQLAlchemy 2.0.23
- **Database:** PostgreSQL 15
- **Auth:** JWT (python-jose), bcrypt
- **Validation:** Pydantic 2.5.0
- **HTTP Client:** httpx 0.25.2

### Frontend
- **Framework:** Vue 3
- **State Management:** Pinia
- **Build Tool:** Vite
- **HTTP Client:** Axios
- **Styling:** CSS3

### Infrastructure
- **Containerization:** Docker
- **Orchestration:** Kubernetes
- **Reverse Proxy:** Nginx (для frontend)
- **Registry:** Docker Hub / Private Registry

## Функции системы

### Управление пользователями
✓ Регистрация
✓ Аутентификация (JWT)
✓ Разделение по ролям (admin, worker)
✓ Управление пользователями (admin)

### Управление задачами
✓ Создание задач (admin)
✓ Редактирование задач (admin)
✓ Удаление задач (admin)
✓ Назначение нескольких исполнителей
✓ Статусы: NEW, IN_PROGRESS, COMPLETED, REWORK
✓ Приоритеты: LOW, MEDIUM, HIGH, CRITICAL
✓ История всех изменений

### Комментарии и коммуникация
✓ Добавление комментариев
✓ Просмотр всех комментариев к задаче
✓ Отслеживание автора комментария
✓ Интеграция с историей

### Отслеживание выполнения
✓ Отметить выполнено (работник)
✓ Одобрение задачи (admin)
✓ Возврат на доработку (admin)
✓ Логирование всех операций

### Уведомления
✓ Создание уведомлений
✓ Отметить как прочитано
✓ История уведомлений
✓ Удаление уведомлений

### Аналитика (дополнительно)
✓ Статистика по задачам
✓ Метрики производительности работников
✓ История метрик

## Доступ по ролям

### Администратор (admin)
- ✓ Все операции создания/редактирования/удаления задач
- ✓ Назначение работников
- ✓ Одобрение/отказ выполнения
- ✓ Управление пользователями
- ✓ Просмотр аналитики
- ✓ Просмотр всех задач

### Работник (worker)
- ✓ Просмотр только назначенных задач
- ✓ Добавление комментариев
- ✓ Отметить свою часть как выполненную
- ✓ Просмотр истории задачи

## API Эндпоинты

### Аутентификация (/api/auth)
```
POST   /api/auth/register              - Регистрация
POST   /api/auth/login                 - Вход
POST   /api/auth/verify                - Проверка токена
GET    /api/auth/users                 - Список пользователей (admin)
GET    /api/auth/users/{id}            - Получить пользователя
PUT    /api/auth/users/{id}            - Обновить пользователя (admin)
DELETE /api/auth/users/{id}            - Удалить пользователя (admin)
GET    /api/auth/user-by-email/{email} - Получить по email
```

### Задачи (/api/tasks)
```
POST   /api/tasks/                     - Создать задачу (admin)
GET    /api/tasks/                     - Список всех задач
GET    /api/tasks/{id}                 - Получить задачу
PUT    /api/tasks/{id}                 - Обновить задачу (admin)
DELETE /api/tasks/{id}                 - Удалить задачу (admin)
POST   /api/tasks/{id}/comments        - Добавить комментарий
GET    /api/tasks/{id}/comments        - Получить комментарии
GET    /api/tasks/{id}/history         - Получить историю
POST   /api/tasks/{id}/mark-completed  - Отметить выполнено (worker)
POST   /api/tasks/{id}/approve         - Одобрить (admin)
POST   /api/tasks/{id}/return-rework   - Вернуть на доработку (admin)
GET    /api/tasks/worker/{id}/tasks    - Задачи работника
```

### Уведомления (/api/notifications)
```
POST   /api/notifications/                    - Создать уведомление
GET    /api/notifications/user/{id}           - Уведомления пользователя
GET    /api/notifications/{id}                - Получить уведомление
PUT    /api/notifications/{id}/read           - Отметить прочитано
PUT    /api/notifications/user/{id}/read-all  - Отметить все прочитано
DELETE /api/notifications/{id}                - Удалить уведомление
GET    /api/notifications/user/{id}/unread-count - Количество непрочитанных
```

### Аналитика (/api/analytics)
```
GET  /api/analytics/dashboard        - Общая статистика
GET  /api/analytics/workers          - Топ рабочих
POST /api/analytics/task-metric      - Записать метрику задач
POST /api/analytics/worker-metric    - Записать метрику работника
GET  /api/analytics/metrics-history  - История метрик
```

## Примеры использования

### Вход
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@admin.admin",
    "password": "admin"
  }'
```

### Создание задачи
```bash
curl -X POST http://localhost:8000/api/tasks/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "title": "Отремонтировать кровлю",
    "description": "Заменить прокладку на балконе",
    "priority": "high",
    "worker_ids": [2, 3]
  }'
```

### Добавление комментария
```bash
curl -X POST http://localhost:8000/api/tasks/1/comments \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"text": "Начал работу"}'
```

### Отметить выполнено
```bash
curl -X POST http://localhost:8000/api/tasks/1/mark-completed \
  -H "Authorization: Bearer <token>"
```

## Тестовые данные

**Администратор:**
- Email: admin@admin.admin
- Password: admin

Создается автоматически при запуске auth-service.

## Масштабирование

### Горизонтальное масштабирование

Каждый микросервис может масштабироваться независимо:

```bash
# Docker Compose
docker-compose up --scale tasks-service=3 --scale auth-service=2

# Kubernetes
kubectl scale deployment tasks-service --replicas=3
```

### Вертикальное масштабирование

Увеличение ресурсов в Kubernetes:

```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "1Gi"
    cpu: "1000m"
```

## Безопасность

✓ JWT токены с expiration
✓ bcrypt хеширование паролей
✓ CORS конфигурация
✓ Валидация данных (Pydantic)
✓ Разделение доступа по ролям (RBAC)
✓ Логирование операций
✓ Secrets в Kubernetes

## Production Readiness

В production необходимо:

1. **SSL/TLS:**
   - Использовать HTTPS
   - Let's Encrypt сертификаты
   - Nginx/Traefik для SSL termination

2. **Database:**
   - Использовать управляемые сервисы (RDS, Cloud SQL)
   - Автоматический backup
   - Репликация
   - Monitoring

3. **Logging:**
   - ELK Stack (Elasticsearch, Logstash, Kibana)
   - Datadog
   - CloudWatch

4. **Monitoring:**
   - Prometheus + Grafana
   - Health checks
   - Alerting

5. **CI/CD:**
   - GitHub Actions
   - GitLab CI
   - Automated testing
   - Automated deployment

6. **Secrets Management:**
   - HashiCorp Vault
   - AWS Secrets Manager
   - Kubernetes Secrets

## Лицензия

MIT

## Контакт

Для вопросов - создать issue в GitHub
