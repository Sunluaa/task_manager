"""README — актуальное описание проекта

Небольшая, но полная демонстрационная микросервисная система для управления задачами.

Состав: API Gateway, Auth, Tasks, Notifications, фронтенд (Vue) и вспомогательные компоненты (Redis, Postgres).

⚠️  **Требования:** Python 3.11 или 3.12 (3.13+ имеет проблемы совместимости с SQLAlchemy)
"""

# Быстрый старт

Запустить весь стек локально (Docker):

```bash
docker-compose up --build
```

После запуска:

- Frontend: http://localhost:3000
- API Gateway: http://localhost:8000

## Что внутри репозитория

- `api-gateway/` — FastAPI gateway
- `auth-service/` — аутентификация и пользователи
- `tasks-service/` — задачи, комментарии, история
- `notifications-service/` — уведомления и воркеры
- `frontend/` — Vue 3 + Vite приложение
- `shared_events/` — общие события/модели
- `kubernetes/` — манифесты K8s
- SQL инициализаторы: `init-auth-db.sql`, `init-tasks-db.sql`, `init-notifications-db.sql`, `init-db.sql`

## Сервисы и порты (по `docker-compose.yml`)

- API Gateway — 8000
- Auth Service — 8001
- Tasks Service — 8002
- Notifications Service — 8003
- Frontend — 3000
- Redis — 6379

Каждый сервис использует свою базу Postgres (контейнеры `postgres-auth`, `postgres-tasks`, `postgres-notifications`).

## Запуск отдельного сервиса (локально)

Пример для `auth-service`:

```bash
cd auth-service
python -m venv .venv
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

Аналогично для `tasks-service` и `notifications-service` (меняя порт и каталог).

## Переменные окружения

Ключевые переменные (используются в `docker-compose.yml` и сервисах):

- `DATABASE_URL` (postgres connection string)
- `REDIS_URL` (например, `redis://redis:6379/0`)
- `SECRET_KEY` (JWT/сессии)
- `PYTHONPATH` (в контейнерах настроен `/app:/shared`)

Для продакшна храните секреты в менеджере секретов и не храните их в репозитории.

## Тестирование

Запустить тесты из корня репозитория (требуется Python 3.11 или 3.12):

```bash
pytest -q
```

Или тесты конкретного сервиса, например:

```bash
pytest auth-service -q
```

Перед запуском тестов убедитесь, что установлены все зависимости:

```bash
pip install -r auth-service/requirements.txt
pip install -r tasks-service/requirements.txt
```

## Kubernetes

Манифесты находятся в `kubernetes/`. Быстрый пример:

```bash
kubectl create namespace task-management
kubectl apply -f kubernetes/
kubectl get pods -n task-management
```

Перед деплоем в production замените локальные базы и redis на управляемые сервисы и используйте Secrets.

## Полезные файлы

- `docker-compose.yml` — локальный стек
- `init-*.sql` — скрипты инициализации БД
- `kubernetes/` — K8s манифесты
- `pytest.ini` — конфигурация тестов

## Особенности реализации

- Отдельная БД на сервис (auth_db, tasks_db, notifications_db)
- Redis используется как очередь для уведомлений и взаимодействия между сервисами
- `notifications-service` содержит HTTP API и отдельный воркер (Dockerfile.worker)

---

Если нужно — могу подготовить `QUICKSTART.md`, `.env.example` или запустить тесты/сборку контейнеров.

sleep 30
docker-compose up
```

### Port уже в использовании
```bash
# Найти и убить процесс
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

### API недоступен
```bash
docker-compose logs api-gateway
docker-compose restart api-gateway
```

📖 **Подробно:** Смотрите [QUICKSTART.md](./QUICKSTART.md#-решение-проблем)

## 🧪 Тестирование

### Запуск тестов

Проект включает comprehensive pytest suite с 19+ тестами для backend сервисов:

**Linux/Mac:**
```bash
./run-tests.sh
```

**Windows:**
```bash
run-tests.bat
```

**Или напрямую:**
```bash
pytest auth-service/tests/ -v
pytest tasks-service/tests/ -v
```

### Покрытие тестов

- **Auth Service:** 9 тестов (регистрация, логин, верификация токена)
- **Tasks Service:** 10 тестов (CRUD, фильтрация, назначение работников)

📖 **Подробно:** Смотрите [TESTING.md](./TESTING.md)

## ☸️ Kubernetes

### Быстрое развертывание

Проект включает production-ready Kubernetes манифесты:

**Linux/Mac:**
```bash
./deploy-k8s.sh
```

**Windows:**
```bash
deploy-k8s.bat
```

### Содержит

- Namespace изоляция (task-management)
- StatefulSet для PostgreSQL с persistent storage (5Gi)
- Deployments для всех сервисов (2 replicas)
- LoadBalancer для внешнего доступа
- Ingress для HTTP routing
- HPA (Horizontal Pod Autoscaler) для auto-scaling
- PDB (Pod Disruption Budget) для высокой доступности
- Health probes (liveness + readiness)
- Resource requests и limits

### Локально (Minikube)

```bash
minikube start
./deploy-k8s.sh
minikube service frontend -n task-management
```

### В облаке (GKE, EKS)

```bash
kubectl apply -f kubernetes/
kubectl get pods -n task-management
kubectl logs -n task-management <pod-name>
```

📖 **Подробно:** Смотрите [KUBERNETES.md](./KUBERNETES.md)

## 📈 Масштабирование

### Горизонтальное

```bash
# Docker Compose
docker-compose up --scale tasks-service=3

# Kubernetes
kubectl scale deployment tasks-service --replicas=3
```

### Вертикальное

Увеличение ресурсов в kubernetes/deployment.yaml

## 🎓 Обучение

1. Начните с [QUICKSTART.md](./QUICKSTART.md)
2. Изучите [ARCHITECTURE.md](./ARCHITECTURE.md)
3. Разберитесь с [DEPLOYMENT.md](./DEPLOYMENT.md)
4. Изучите [TESTING.md](./TESTING.md)
5. Настройте [KUBERNETES.md](./KUBERNETES.md)
6. Читайте исходный код в каждом сервисе

## 📝 Лицензия

MIT

## ✉️ Контакты

Для вопросов или предложений создавайте Issue

---

**Версия:** 1.0.0 | **Updated:** 2024 | **Status:** Production Ready ✅
