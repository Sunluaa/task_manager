# Task Management System - Микросервисная архитектура

Полнофункциональная система управления задачами по ремонту и обслуживанию помещений на микросервисной архитектуре с API Gateway.

**Status:** ✅ Полностью рабочая | **Python** 3.11+ | **Vue 3** | **FastAPI** | **PostgreSQL** | **Docker & Kubernetes**

## 📋 Содержание

- [Быстрый старт](#-быстрый-старт)
- [Архитектура](#-архитектура)
- [Функции](#-функции)
- [Технологический стек](#-технологический-стек)
- [API Endpoints](#-api-endpoints)
- [Развертывание](#-развертывание)
- [Тестирование](#-тестирование)
- [Kubernetes](#-kubernetes)
- [Документация](#-документация)

## 🚀 Быстрый старт

### За 5 минут до рабочей системы

```bash
cd course2
docker-compose up -d
```

Откройте http://localhost:3000

**Тестовые данные:**
- Email: `admin@admin.admin`
- Password: `admin`

✨ **БД создаются автоматически в контейнере!**

📖 **Полное руководство:** Смотрите [QUICKSTART.md](./QUICKSTART.md)

## 🏗️ Архитектура

### Микросервисы (3)

| Сервис | Порт | Ответственность |
|--------|------|-----------------|
| **Auth Service** | 8001 | Аутентификация, управление пользователями, JWT |
| **Tasks Service** | 8002 | Управление задачами, история, комментарии |
| **Notifications Service** | 8003 | Уведомления, логирование событий |

### API Gateway

**Выбор: FastAPI** (вместо Traefik)

**Обоснование:**
- ✅ Простота разработки и расширения
- ✅ Встроенная документация Swagger UI
- ✅ Гибкость middleware и маршрутизации
- ✅ Идеально для демонстрации и быстрого прототипирования
- ℹ️ Production: рекомендуется Traefik для большей производительности

**Маршруты:**
```
/api/auth/*          → auth-service:8001
/api/tasks/*         → tasks-service:8002
/api/notifications/* → notifications-service:8003
```

### База данных

**Подход:** Полиглот (отдельная БД для каждого сервиса)

| БД | Сервис | Таблицы |
|----|--------|---------|
| `auth_db` | Auth Service | users |
| `tasks_db` | Tasks Service | tasks, comments, history, worker_completions |
| `notifications_db` | Notifications Service | notifications |

**Обоснование:**
- ✅ Независимость и масштабируемость
- ✅ Автономность каждого сервиса
- ✅ Нет кросс-сервисных транзакций
- ✅ Легкая миграция сервисов

### Frontend

- **Vue 3** + **Pinia** + **Vite**
- Отдельные интерфейсы для администратора и работника
- Реал-тайм обновления через запросы
- JWT хранилище в localStorage

## ✨ Функции

### 👤 Управление пользователями

- ✅ Регистрация и аутентификация
- ✅ JWT токены с expiration
- ✅ Две роли: **администратор** и **работник**
- ✅ Управление пользователями (админ только)

### 📝 Управление задачами

- ✅ CRUD операции (админ)
- ✅ Статусы: NEW → IN_PROGRESS → COMPLETED / REWORK
- ✅ Приоритеты: LOW, MEDIUM, HIGH, CRITICAL
- ✅ Назначение нескольких исполнителей
- ✅ История всех изменений
- ✅ Система комментариев

### 📊 Отслеживание выполнения

- ✅ Рабочий отмечает выполнение своей части
- ✅ Задача завершена только когда все отметили выполнение
- ✅ Админ одобряет или возвращает на доработку
- ✅ Полная история событий

### 🔔 Уведомления

- ✅ Создание уведомлений
- ✅ Отметить прочитано
- ✅ История уведомлений

### 📈 Аналитика (бонус)

- ✅ Общая статистика по задачам
- ✅ Метрики производительности работников
- ✅ История метрик

## 🛠️ Технологический стек

### Backend
```
Python 3.11 + FastAPI + SQLAlchemy + PostgreSQL + Pydantic
```

- **Web Framework:** FastAPI 0.104.1
- **Server:** Uvicorn 0.24.0
- **ORM:** SQLAlchemy 2.0.23
- **Database:** PostgreSQL 15
- **Auth:** JWT (python-jose) + bcrypt
- **Validation:** Pydantic 2.5.0

### Frontend
```
Vue 3 + Pinia + Vite + Axios
```

- **Framework:** Vue 3
- **State Management:** Pinia
- **Build:** Vite
- **HTTP:** Axios

### Infrastructure
```
Docker + Docker Compose + Kubernetes + Nginx + Redis
```

- **Containerization:** Docker + Docker Compose
- **Orchestration:** Kubernetes (K8s)
- **Cache & Queue:** Redis 7
- **Reverse Proxy:** Nginx/Ingress
- **CI/CD Ready:** GitHub Actions compatible

## 🚀 Новые возможности

### 🔄 Async Notification Queue (Redis Integration)

Асинхронная обработка уведомлений через Redis с поддержкой retries и Dead Letter Queue.

- **Queue System:** Redis List-based с префиксами `queues:notifications` и `dlq:notifications`
- **Worker Pattern:** Отдельный процесс для обработки очереди
- **Retry Logic:** Автоматические повторные попытки (до 3 раз) перед перемещением в DLQ
- **Dead Letter Queue:** Хранение неудачных уведомлений для анализа
- **Async API:** Полная поддержка async/await через `aioredis` v2
- **Scalable:** Горизонтальное масштабирование worker'ов

📖 **Документация:** [REDIS_INTEGRATION.md](./REDIS_INTEGRATION.md)

## 🔌 API Endpoints

### Аутентификация
```
POST   /api/auth/register
POST   /api/auth/login → {access_token, user}
POST   /api/auth/verify
GET    /api/auth/users
CRUD   /api/auth/users/{id}
```

### Задачи
```
POST   /api/tasks/                    → Создать (admin)
GET    /api/tasks/                    → Список
GET    /api/tasks/{id}                → Получить
PUT    /api/tasks/{id}                → Обновить (admin)
DELETE /api/tasks/{id}                → Удалить (admin)
POST   /api/tasks/{id}/comments       → Добавить комментарий
GET    /api/tasks/{id}/comments       → Список комментариев
GET    /api/tasks/{id}/history        → История изменений
POST   /api/tasks/{id}/mark-completed → Отметить выполнено (worker)
POST   /api/tasks/{id}/approve        → Одобрить (admin)
POST   /api/tasks/{id}/return-rework  → Вернуть на доработку (admin)
```

### Уведомления
```
POST   /api/notifications/                    → Enqueue (async via Redis)
GET    /api/notifications/user/{id}           → Список
GET    /api/notifications/{id}                → Получить
PUT    /api/notifications/{id}/read           → Отметить прочитано
PUT    /api/notifications/user/{id}/read-all  → Отметить все прочитано
DELETE /api/notifications/{id}                → Удалить
GET    /api/notifications/user/{id}/unread-count → Количество непрочитанных
GET    /api/notifications/admin/queue-stats   → Статистика очереди (admin)
```

### Аналитика
```
GET    /api/analytics/dashboard
GET    /api/analytics/workers
POST   /api/analytics/task-metric
GET    /api/analytics/metrics-history
```

## 📦 Развертывание

### Docker Compose (Локально)

```bash
docker-compose up --build
```

**Доступно:**
- Frontend: http://localhost:3000
- API Gateway: http://localhost:8000
- Services: 8001-8004
- Redis: localhost:6379

**Новые сервисы:**
- `redis` - Redis для queue
- `notifications-worker` - Background worker для обработки очереди

### Kubernetes

```bash
# Создать namespace
kubectl create namespace task-management

# Применить Redis
kubectl apply -f kubernetes/02-redis.yaml

# Применить остальные конфиги
kubectl apply -f kubernetes/

# Проверить
kubectl get pods -n task-management
kubectl get services -n task-management
```

**Новые ресурсы в K8s:**
- StatefulSet `redis` с PersistentVolumeClaim (5Gi)
- Deployment `notifications-worker` (2 replicas)
- Service `redis-service` (headless)

**В production используйте:**
- Traefik вместо FastAPI Gateway
- Managed Redis (Azure Cache, AWS ElastiCache)
- Persistent storage для Redis
- Управляемые БД (RDS, Cloud SQL)
- Secrets Manager (Vault, AWS Secrets)
- ELK Stack для логирования
- Prometheus + Grafana для мониторинга

📖 **Подробный гайд:** Смотрите [DEPLOYMENT.md](./DEPLOYMENT.md)

## 📚 Документация

| Документ | Описание |
|----------|---------|
| [QUICKSTART.md](./QUICKSTART.md) | 🚀 Быстрый старт за 5 минут |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | 🏗️ Подробная архитектура системы |
| [DEPLOYMENT.md](./DEPLOYMENT.md) | 📦 Инструкции по развертыванию |
| [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md) | 📂 Структура проекта и файлов |

## 🔒 Безопасность

- ✅ JWT аутентификация с expiration
- ✅ bcrypt хеширование паролей
- ✅ CORS конфигурация
- ✅ Валидация данных (Pydantic)
- ✅ Role-Based Access Control (RBAC)
- ✅ Secrets в Kubernetes
- ✅ Логирование операций

## 🎯 Роли и доступ

### 👨‍💼 Администратор

**Меню:** 4 вкладки вверху
- Все задачи
- Новые (NEW)
- В процессе (IN_PROGRESS)
- Выполненные (COMPLETED)

**Может:**
- Создавать, редактировать, удалять задачи
- Назначать нескольких исполнителей
- Одобрять выполнение / возвращать на доработку
- Управлять пользователями
- Просматривать аналитику

### 👷 Работник

**Меню:** 1 кнопка
- Мои задачи

**Может:**
- Просматривать только свои задачи
- Отметить выполнение своей части
- Добавлять комментарии
- Просматривать историю

## 🗂️ Структура проекта

```
course2/
├── auth-service/           # Аутентификация
├── tasks-service/          # Управление задачами
├── notifications-service/  # Уведомления
├── analytics-service/      # Аналитика (bonus)
├── api-gateway/            # API Gateway
├── frontend/               # Vue 3 приложение
├── kubernetes/             # K8s манифесты
├── docker-compose.yml      # Docker Compose конфиг
├── QUICKSTART.md           # Быстрый старт
├── ARCHITECTURE.md         # Архитектура
├── DEPLOYMENT.md           # Деплой
└── README.md              # Этот файл
```

## 🚦 Health Check

Все сервисы поддерживают:
```bash
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
curl http://localhost:8004/health
```

## 📊 Мониторинг

```bash
# Статус контейнеров
docker-compose ps

# Логи
docker-compose logs -f service-name

# Использование ресурсов
docker stats
```

## 🤝 Интеграция сервисов

```
Frontend (Vue 3)
    ↓
API Gateway (FastAPI)
    ├─→ Auth Service (JWT)
    ├─→ Tasks Service (CRUD + History)
    ├─→ Notifications Service (Events)
    └─→ Analytics Service (Metrics)
    ↓
PostgreSQL (4 БД)
```

## 🔄 Жизненный цикл задачи

```
Admin создает         → NEW
    ↓
Assign workers
    ↓
Worker работает       → IN_PROGRESS
    ↓
Worker отметил выполнено
    ↓
Admin одобрил         → COMPLETED
    
или

Admin отклонил        → REWORK
    ↓
Worker работает снова...
```

## 🐛 Решение проблем

### БД недоступна
```bash
docker-compose restart postgres
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
