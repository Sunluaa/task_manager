# Инструкции по запуску проекта

## Требования

### Для Docker Compose:
- Docker
- Docker Compose

### Для Kubernetes:
- Docker
- Kubernetes (minikube, Kind, или другой дистрибьютив)
- kubectl

### Для локальной разработки:
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+

## Запуск с Docker Compose

1. Перейти в корневую директорию проекта:
```bash
cd course2
```

2. Запустить все сервисы:
```bash
docker-compose up --build
```

3. Дождаться инициализации БД (примерно 30 секунд)

4. Открыть в браузере: http://localhost:3000

5. Для входа используйте:
   - Email: admin@admin.admin
   - Password: admin

## Запуск с Kubernetes

### Локально (minikube)

1. Запустить minikube:
```bash
minikube start
```

2. Переключиться на Docker daemon minikube:
```bash
eval $(minikube docker-env)
```

3. Собрать Docker образы:
```bash
docker-compose build
```

4. Применить Kubernetes манифесты:
```bash
kubectl apply -f kubernetes/
```

5. Проверить статус:
```bash
kubectl get pods
kubectl get services
```

6. Получить URL фронтенда:
```bash
minikube service frontend --url
```

или

```bash
minikube service api-gateway --url
```

### На облаке (AWS, GCP, Azure)

1. Убедиться, что кластер Kubernetes настроен
2. Загрузить Docker образы в реестр (ECR, GCR, ACR)
3. Обновить образы в манифестах (kubernetes/auth-service.yaml и т.д.)
4. Применить манифесты:
```bash
kubectl apply -f kubernetes/
```

## Локальная разработка

### Backend (каждый сервис отдельно)

1. Auth Service:
```bash
cd auth-service
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

2. Аналогично для tasks-service и notifications-service

### Frontend

1. Установить зависимости:
```bash
cd frontend
npm install
```

2. Запустить dev сервер:
```bash
npm run dev
```

3. Открыть: http://localhost:5173

## Архитектура и выбор API Gateway

### Почему FastAPI вместо Traefik?

| Критерий | FastAPI | Traefik |
|----------|---------|---------|
| Простота настройки | ✓✓✓ | ✓✓ |
| Легкость расширения | ✓✓✓ | ✓✓ |
| Производительность | ✓✓✓ | ✓✓✓ |
| Логирование | ✓✓✓ | ✓ |
| Встроенная документация | ✓✓✓ | ✗ |
| Контроль запросов | ✓✓✓ | ✓✓ |
| Деплой в контейнере | ✓✓ | ✓✓✓ |

**Вывод:** FastAPI выбран для демонстрационного проекта благодаря гибкости и простоте разработки, Traefik лучше для production на Kubernetes.

## Структура БД

### Отдельные базы для каждого микросервиса

**auth_db:**
- users (id, email, password_hash, full_name, role, is_active, created_at, updated_at)

**tasks_db:**
- tasks (id, title, description, status, priority, created_by, created_at, updated_at)
- comments (id, task_id, user_id, text, created_at)
- history (id, task_id, event_type, user_id, details, created_at)
- worker_completions (id, task_id, worker_id, completed_at)

**notifications_db:**
- notifications (id, user_id, title, message, is_read, created_at, read_at)

## API Endpoints

Все запросы идут через API Gateway на localhost:8000

### Аутентификация
```
POST /api/auth/register
POST /api/auth/login
POST /api/auth/verify
GET /api/auth/users
```

### Задачи
```
POST /api/tasks/
GET /api/tasks/
POST /api/tasks/{id}/comments
POST /api/tasks/{id}/mark-completed
POST /api/tasks/{id}/approve
```

### Уведомления
```
GET /api/notifications/user/{user_id}
PUT /api/notifications/{id}/read
```

## Решение проблем

### БД не подключается
```bash
# Проверить статус PostgreSQL
docker-compose ps postgres

# Посмотреть логи
docker-compose logs postgres

# Перезапустить
docker-compose restart postgres
```

### Сервисы не общаются
```bash
# Проверить сеть
docker network ls

# Проверить DNS
docker exec <service_name> ping <other_service>
```

### Frontend показывает ошибку 404
```bash
# Очистить кэш браузера
# Или перезагрузить фронтенд
docker-compose restart frontend
```

## Масштабирование

### Horizontal Scaling (Docker Compose)
```bash
docker-compose up --scale tasks-service=3 --scale auth-service=2
```

### Kubernetes Scaling
```bash
kubectl scale deployment auth-service --replicas=3
kubectl scale deployment tasks-service --replicas=3
```

## Monitoring

Все сервисы имеют health check endpoints:
```
GET /health
```

На Kubernetes это используется для liveness и readiness probes.

## Безопасность

- Используется JWT для аутентификации
- Пароли хешируются bcrypt
- Среды переменные через .env и Kubernetes secrets
- CORS настроен на конкретные источники (в production)

## Разработка новых функций

1. Добавить endpoint в контроллер (app/controllers/)
2. Добавить логику в сервис (app/services/)
3. Добавить схему Pydantic (app/schemas/)
4. Обновить тесты
5. Перестартовать сервис

## Деплой в production

1. Загрузить образы в реестр
2. Настроить SSL/TLS (nginx ingress)
3. Настроить базы данных (управляемые сервисы)
4. Включить логирование и мониторинг
5. Настроить backup для БД
