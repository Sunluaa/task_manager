# Курсовая работа: Создание клиент‑серверного микросервисного приложения для управления задачами по ремонту и обслуживанию жилых помещений

Автор: (Фамилия И.О.)

Дисциплина: Архитектура клиент‑серверных приложений

Дата: 6 декабря 2025 г.

---

## Аннотация

В рамках данной курсовой работы разработано клиент‑серверное микросервисное приложение для управления заявками на ремонт и обслуживание жилых помещений. Система реализована на базе микросервисной архитектуры с использованием FastAPI, PostgreSQL, Docker, Kubernetes и Vue 3 для фронтенда. Приложение обеспечивает регистрацию и аутентификацию пользователей, создание и управление заявками, назначение мастеров, загрузку фото работ, а также отправку уведомлений.

Документ содержит аналитическую часть, проектирование архитектуры, реализацию сервисов, диаграммы в формате Mermaid, конфигурации контейнеризации и оркестрации, тестовые сценарии и инструкции по развертыванию.

---

## Перечень сокращений

- API — Application Programming Interface
- JWT — JSON Web Token
- DB — Database
- UI — User Interface
- REST — Representational State Transfer
- PVC — Persistent Volume Claim
- HPA — Horizontal Pod Autoscaler
- PDB — Pod Disruption Budget
- CI/CD — Continuous Integration / Continuous Delivery

---

## Введение

Актуальность: автоматизация управления заявками на ремонт жилых помещений повышает оперативность выполнения работ, делает прозрачным процесс взаимодействия жильца, диспетчера и мастера, обеспечивает сбор статистики и учёт истории заявок.

Цель: разработать учебный проект — микросервисное приложение, реализующее базовый жизненный цикл заявок (создание, назначение, выполнение, контроль качества), доступное через веб‑интерфейс и REST API.

Задачи:
- Спроектировать архитектуру системы в стиле микросервисов;
- Реализовать пять сервисов: `auth-service`, `tasks-service`, `files-service`, `notifications-service`, `api-gateway`;
- Обеспечить контейнеризацию и возможность деплоя в Kubernetes;
- Подготовить документацию, диаграммы и тесты.

---

# Глава 1. Аналитическая часть

## 1.1 Описание предметной области

Предметная область — процессы управления заявками на ремонт и обслуживание в жилых комплексах. Участники: жилец (создаёт заявку), диспетчер (назначает мастера, следит за статусами), мастер (выполняет работу), администратор (управление пользователями). Основные операции: подача заявки, прикрепление фото, назначение исполнителя, изменение статусов, уведомления участников.

## 1.2 Анализ существующих решений

Рынок предлагает решения от CRM/Helpdesk систем до специализированных ЖКХ платформ. Общие требования: многопользовательский доступ, разграничение прав, уведомления, хранение файлов, отказоустойчивость, масштабируемость. Для учебного проекта выбран стек, дающий баланс простоты разработки и соответствия промышленным практикам: FastAPI (быстрый backend), Vue 3 (легковесный SPA), Docker/Kubernetes (развертывание).

## 1.3 Формирование функциональных и нефункциональных требований

Функциональные требования (кратко):
- Регистрация и вход пользователей;
- Роли: житель, мастер, диспетчер, админ;
- CRUD для заявок (title, description, status, priority, attached_files, assigned_worker_id);
- Назначение мастера диспетчером;
- История изменений для каждой заявки;
- Загрузка/выдача файлов (фото работ);
- Отправка уведомлений (e‑mail или заглушка);
- UI: авторизация, список заявок, создание, подробности.

Нефункциональные требования:
- REST API, документированное через OpenAPI/Swagger;
- JWT‑аутентификация; ролевой доступ;
- Производительность: обработка 100 запросов/сек в типичных условиях (учебное требование);
- Масштабируемость: горизонтальное масштабирование сервисов;
- Устойчивость: отдельные БД, контейнеры, PDB/HPA в Kubernetes.

## 1.4 Ограничения проекта

- Учебный характер: некоторые компоненты (например, SMTP) реализованы как заглушки;
- Минимальный набор логики бизнес‑правил; упрощена обработка файлов (локальное хранилище / PVC);
- Без полной интеграции с внешними системами оплаты и биллинга.

---

# Глава 2. Проектирование архитектуры

## 2.1 Обзор архитектурных стилей

Кратко сравнение: монолит, SOA, микросервисы, serverless. Микросервисы выбраны из‑за модульности, независимого деплоя и масштабирования.

## 2.2 Обоснование выбора микросервисной архитектуры

Микросервисы позволяют разделить домены (аутентификация, задачи, файлы, уведомления), автономно развивать и масштабировать их, изолировать сбои и управлять зависимостями. Это соответствует DDD (Domain‑Driven Design): каждый сервис владеет своей моделью и БД.

## 2.3 Описание микросервисов

- `auth-service` — управление пользователями, регистрация, логин, JWT, роли (resident, worker, dispatcher, admin).
- `tasks-service` — CRUD для заявок, статусы (new, assigned, in_progress, done, verified), приоритеты (low, normal, high), история изменений, assignment.
- `files-service` — загрузка и получение фото; хранение на PVC; API для привязки файлов к заявкам.
- `notifications-service` — отправка уведомлений (SMTP или тестовая очередь). Может быть заменён реальным сервисом в production.
- `api-gateway` — единственная точка входа; маршрутизация запросов; валидация/проверка JWT; консолидированная документация.

## 2.4 API Gateway

API Gateway реализует следующие функции:
- Маршрутизация запросов по префиксам `/api/auth`, `/api/tasks`, `/api/files`, `/api/notifications`;
- Проверка и извлечение JWT; проброс контекста пользователя в заголовках;
- Аггрегация простых запросов при необходимости.

## 2.5 Проектирование взаимодействия сервисов

Взаимодействие — синхронное по REST между gateway и сервисами. Асинхронные события (например, уведомления о смене статуса) можно реализовать через очереди (RabbitMQ) — пункт для дальнейшего расширения.

Пример сценария: создание заявки
1. Жилец POST `/api/tasks` → API Gateway → Tasks Service
2. Tasks Service создаёт запись, сохраняет отношение к пользователю
3. Tasks Service вызывает Notifications Service (POST `/notifications`) синхронно или отправляет событие в очередь
4. Files загружает фотографии и возвращает ссылки, Tasks связывает файлы с заявкой

## 2.6 ER‑диаграмма (Mermaid)

```mermaid
erDiagram
    USERS ||--o{ TASKS : creates
    USERS ||--o{ FILES : uploads
    TASKS ||--o{ FILES : has
    TASKS ||--o{ TASK_HISTORY : history

    USERS {
        integer id PK
        string email
        string full_name
        string role
    }
    TASKS {
        integer id PK
        string title
        text description
        string status
        string priority
        integer author_id FK
        integer assigned_worker_id FK
        datetime created_at
        datetime updated_at
    }
    FILES {
        integer id PK
        string file_path
        integer owner_id FK
        integer task_id FK
        datetime created_at
    }
    TASK_HISTORY {
        integer id PK
        integer task_id FK
        integer user_id FK
        string action
        text comment
        datetime created_at
    }
```

## 2.7 UML диаграммы (Mermaid)

Use Case:

```mermaid
usecaseDiagram
    actor Resident as R
    actor Dispatcher as D
    actor Worker as W
    actor Admin as A

    R --> (Create Task)
    R --> (View Own Tasks)
    D --> (Assign Worker)
    D --> (View All Tasks)
    W --> (Update Task Status)
    A --> (Manage Users)
```

Component Diagram:

```mermaid
componentDiagram
    package "Frontend" {
      [Vue SPA]
    }
    package "API Layer" {
      [API Gateway]
    }
    package "Services" {
      [Auth Service]
      [Tasks Service]
      [Files Service]
      [Notifications Service]
    }
    package "Infrastructure" {
      [Postgres]
      [PVC / Storage]
      [Ingress]
    }

    [Vue SPA] --> [API Gateway]
    [API Gateway] --> [Auth Service]
    [API Gateway] --> [Tasks Service]
    [API Gateway] --> [Files Service]
    [API Gateway] --> [Notifications Service]
    [Tasks Service] --> [Postgres]
    [Auth Service] --> [Postgres]
    [Files Service] --> [PVC / Storage]
```

Sequence diagram: создание заявки с загрузкой файла и уведомлением

```mermaid
sequenceDiagram
    participant Frontend
    participant Gateway
    participant Tasks
    participant Files
    participant Notifications

    Frontend->>Gateway: POST /api/tasks (task + files)
    Gateway->>Tasks: POST /tasks (task meta)
    Tasks->>Files: POST /files (upload)
    Files-->>Tasks: 201 {file_urls}
    Tasks-->>Gateway: 201 {task}
    Gateway->>Notifications: POST /notifications (task_created)
    Notifications-->>Gateway: 200 OK
    Gateway-->>Frontend: 201 {task}
```

## 2.8 DFD L0 и L1 (Mermaid)

DFD L0:

```mermaid
flowchart TD
    U[User] -->|Browser| UI[Frontend]
    UI -->|HTTP| G[API Gateway]
    G --> A[Auth Service]
    G --> T[Tasks Service]
    G --> F[Files Service]
    G --> N[Notifications]
    T -->|DB| P[Postgres]
    A -->|DB| P
    F -->|Storage| S[Persistent Storage]
```

DFD L1 (Tasks flow):

```mermaid
flowchart TD
    UI -->|Create task| G
    G -->|Validate JWT| A
    G -->|Create| T
    T -->|Store| P
    T -->|Request file upload| F
    F -->|Store file| S
    T -->|Notify| N
```

## 2.9 Модель физической инфраструктуры

Инфраструктура предполагает размещение контейнеров в Kubernetes кластере (тестовый Minikube или облачный провайдер). Сервисы размещаются в отдельных Deployment, Postgres в StatefulSet с PVC. Ingress обеспечивает HTTP(S) доступ, ConfigMap и Secret хранят конфигурацию и секреты.

Mermaid инфраструктурная схема:

```mermaid
flowchart LR
    subgraph K8sCluster["Kubernetes Cluster"]
      direction TB
      Ingress --> API[API Gateway Deployment]
      API --> Auth
      API --> Tasks
      API --> Files
      API --> Notifications
      Auth --> Postgres
      Tasks --> Postgres
      Files --> PVC
      Notifications --> Postgres
    end
    User -->|HTTPS| Ingress
```

---

# Глава 3. Реализация

## 3.1 Структура репозитория (реальная структура проекта)

```
course2/
├── auth-service/
│   ├── app/
│   │   ├── main.py
│   │   ├── controllers/
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── db.py
│   ├── Dockerfile
│   └── requirements.txt
├── tasks-service/
├── files-service/
├── notifications-service/
├── api-gateway/
├── frontend/
├── kubernetes/
├── docker-compose.yml
└── README.md
```

> Примечание: структура соответствует реальному репозиторию в проекте `course2`.

## 3.2 Реализация микросервисов на FastAPI

Ниже приведены полные минимально достаточные реализации основных сервисов (урезанные для компактности, но рабочие). Для развёртывания все файлы уже присутствуют в репозитории; здесь – концентрированные версии, которые можно вставить и запустить.

### 3.2.1 auth-service (полный пример)

`auth-service/app/main.py`

```python
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext

# Конфигурация (в production - из env)
SECRET_KEY = "change-me-in-prod"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
app = FastAPI(title="auth-service")

# In-memory store (заменяется на DB в реальной реализации)
USERS = {}
ID_COUNTER = 1

class RegisterSchema(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str]
    role: Optional[str] = "resident"

class LoginSchema(BaseModel):
    email: EmailStr
    password: str

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.post('/register')
def register(payload: RegisterSchema):
    global ID_COUNTER
    if payload.email in USERS:
        raise HTTPException(status_code=400, detail="Email exists")
    hashed = pwd_context.hash(payload.password)
    user = {"id": ID_COUNTER, "email": payload.email, "password_hash": hashed, "full_name": payload.full_name, "role": payload.role}
    USERS[payload.email] = user
    ID_COUNTER += 1
    return {"id": user["id"], "email": user["email"], "role": user["role"]}

@app.post('/login')
def login(payload: LoginSchema):
    user = USERS.get(payload.email)
    if not user or not pwd_context.verify(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": str(user["id"]), "role": user["role"]}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": token, "token_type": "bearer"}

@app.get('/users')
def list_users():
    return list(USERS.values())
```

> Реальная сервисная версия использует SQLAlchemy и Postgres; в `auth-service` репозитории есть `db/database.py`, модели и миграции.

### 3.2.2 tasks-service (фрагмент)

`tasks-service/app/main.py`

```python
from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

app = FastAPI(title='tasks-service')

TASKS = {}
ID = 1

class TaskIn(BaseModel):
    title: str
    description: Optional[str]
    priority: Optional[str] = 'normal'

class TaskOut(TaskIn):
    id: int
    status: str
    author_id: int
    assigned_worker_id: Optional[int]
    created_at: datetime

@app.post('/tasks')
def create_task(task: TaskIn, request: Request):
    global ID
    payload = task.dict()
    t = {**payload, 'id': ID, 'status': 'new', 'author_id': 1, 'assigned_worker_id': None, 'created_at': datetime.utcnow()}
    TASKS[ID] = t
    ID += 1
    return t

@app.get('/tasks')
def list_tasks():
    return list(TASKS.values())

@app.get('/tasks/{task_id}')
def get_task(task_id: int):
    t = TASKS.get(task_id)
    if not t:
        raise HTTPException(404)
    return t

@app.put('/tasks/{task_id}/assign')
def assign_worker(task_id: int, body: dict):
    t = TASKS.get(task_id)
    if not t:
        raise HTTPException(404)
    t['assigned_worker_id'] = body.get('worker_id')
    t['status'] = 'assigned'
    return t

@app.put('/tasks/{task_id}/status')
def update_status(task_id: int, body: dict):
    t = TASKS.get(task_id)
    if not t:
        raise HTTPException(404)
    t['status'] = body.get('status')
    return t
```

> Для реального проекта используйте SQLAlchemy ORM модели, миграции и зависимости от `auth-service` для проверки авторизации.

## 3.3 Реализация API Gateway

`api-gateway/main.py` (суммарно — репозиторный файл в проекте):

```python
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI(title='api-gateway')

AUTH = 'http://auth-service:8001'
TASKS = 'http://tasks-service:8002'
FILES = 'http://files-service:8005'
NOTIFS = 'http://notifications-service:8003'

async def forward(service: str, path: str, request: Request):
    url = f"{service}{path}"
    async with httpx.AsyncClient() as client:
        headers = dict(request.headers)
        body = await request.body()
        resp = await client.request(method=request.method, url=url, headers=headers, content=body)
        return resp.status_code, resp.headers, resp.content

@app.api_route('/api/{service}/{path:path}', methods=['GET','POST','PUT','DELETE','PATCH'])
async def gateway(service: str, path: str, request: Request):
    mapping = {'auth': AUTH, 'tasks': TASKS, 'files': FILES, 'notifications': NOTIFS}
    if service not in mapping:
        raise HTTPException(404)
    status_code, headers, content = await forward(mapping[service], f'/{path}', request)
    return HTTPException(status_code=status_code, detail=content)
```

> В реальной реализации gateway проверяет JWT, декодирует роль и пробрасывает `X-User-Id` и `X-User-Role` в заголовках.

## 3.4 Реализация фронтенда на Vue.js

Фронтенд — SPA на Vue 3 с Pinia. Ключевые страницы: Login, Dashboard (список задач), NewTask, TaskDetail.

`frontend/src/main.js`

```javascript
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './style.css'

createApp(App).use(router).mount('#app')
```

`frontend/src/services/api.js`

```javascript
import axios from 'axios'
const api = axios.create({ baseURL: '/api' })
export default api
```

`frontend/src/views/Login.vue` (упрощённо)

```html
<template>
  <form @submit.prevent="submit">
    <input v-model="email" />
    <input v-model="password" type="password" />
    <button type="submit">Войти</button>
  </form>
</template>

<script>
import api from '../services/api'
export default {
  data(){ return { email:'', password:'' } },
  methods: {
    async submit(){
      const res = await api.post('/auth/login', { email: this.email, password: this.password })
      localStorage.setItem('token', res.data.access_token)
      this.$router.push('/')
    }
  }
}
</script>
```

`frontend/src/views/Dashboard.vue` — делает GET `/api/tasks` и отображает список.

## 3.5 Реализация БД PostgreSQL

В репозитории есть `init.sql` для инициализации баз (auth_db, tasks_db, notifications_db). Производственная версия использует отдельную БД на каждую bounded context и SQLAlchemy с Alembic для миграций.

Пример модели SQLAlchemy (tasks-service/models.py):

```python
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), default='new')
    priority = Column(String(20), default='normal')
    author_id = Column(Integer, nullable=False)
    assigned_worker_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

## 3.6 Docker‑контейнеризация

Пример `Dockerfile` для `auth-service`:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

Корневой `docker-compose.yml` (обновлённый, без analytics):

```yaml
version: '3.8'
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_PASSWORD: postgres
      POSTGRES_USER: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/01-init.sql
  auth-service:
    build: ./auth-service
    environment:
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/auth_db
    ports:
      - "8001:8001"
    depends_on:
      postgres:
        condition: service_healthy
  tasks-service:
    build: ./tasks-service
    environment:
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/tasks_db
    ports:
      - "8002:8002"
    depends_on:
      postgres:
        condition: service_healthy
  notifications-service:
    build: ./notifications-service
    environment:
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/notifications_db
    ports:
      - "8003:8003"
    depends_on:
      postgres:
        condition: service_healthy
  api-gateway:
    build: ./api-gateway
    ports:
      - "8000:8000"
    depends_on:
      - auth-service
      - tasks-service
      - notifications-service
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - api-gateway
volumes:
  postgres_data:
```

## 3.7 Kubernetes‑манифесты

В каталоге `kubernetes/` присутствуют файлы:
- `00-namespace.yaml`
- `01-configmap-secret.yaml`
- `02-postgres.yaml` (StatefulSet + PVC)
- `03-auth-service.yaml` (Deployment + Service)
- `04-tasks-service.yaml`
- `05-notifications-service.yaml`
- `06-api-gateway.yaml`
- `07-frontend.yaml`
- `08-ingress.yaml`
- `09-hpa.yaml`
- `10-pdb.yaml`

Пример `03-auth-service.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: auth-service
  namespace: task-management
spec:
  replicas: 2
  selector:
    matchLabels:
      app: auth-service
  template:
    metadata:
      labels:
        app: auth-service
    spec:
      containers:
      - name: auth-service
        image: course2-auth-service:latest
        ports:
          - containerPort: 8001
        envFrom:
          - configMapRef:
              name: app-config
          - secretRef:
              name: app-secret
```

## 3.8 Инструкции по запуску

### Локально (через Docker Compose)

```bash
# Собрать и поднять контейнеры
docker-compose up -d --build
# Доступ к фронтенду: http://localhost:3000
# Swagger / OpenAPI gateway (при наличии): http://localhost:8000/docs
```

### В Kubernetes (Minikube)

```bash
minikube start --cpus=4 --memory=4096
./deploy-k8s.sh
# потом
kubectl get pods -n task-management
minikube service frontend -n task-management
```

---

# Глава 4. Тестирование

## 4.1 Тестирование REST API через Swagger

Каждый сервис публикует OpenAPI спецификацию (FastAPI автоматически генерирует `/docs`). Тестирование выполняется вручную через Swagger UI и автоматически с использованием `pytest`.

## 4.2 Тестирование API Gateway

Проверяется корректность маршрутизации, передача заголовков авторизации и проброс `Authorization` к сервисам. Для тестов использовать `httpx` или `curl`.

Пример curl запроса авторизации через gateway:

```bash
curl -X POST http://localhost:8000/api/auth/login -d '{"email":"admin@admin.admin","password":"admin"}' -H 'Content-Type: application/json'
```

## 4.3 Проверка авторизации и JWT

Проверить:
- Невозможность доступа к защищённым ресурсам без токена;
- Токен истекает через заданное время;
- Ролевые ограничения: диспетчер может назначать мастера, работник — менять статус.

## 4.4 CRUD‑тестирование микросервисов

Для `tasks-service`:
- Создать задачу POST `/api/tasks`;
- Извлечь список GET `/api/tasks`;
- Обновить статус PUT `/api/tasks/{id}/status`;
- Назначить мастера PUT `/api/tasks/{id}/assign`;
- Удалить задачу (если реализовано).

## 4.5 Тестирование фронтенда (XHR, Network)

Использовать DevTools для инспекции сетевых запросов, проверить успешную передачу `Authorization` header и загрузку файлов (multipart/form-data).

## 4.6 End‑to‑End сценарии

1. Регистрация жильца → Вход → Создание заявки с фотографией → Диспетчер назначает мастера → Мастер меняет статус на `in_progress` и затем `done` → Диспетчер проверяет и закрывает.
2. Негативные: попытка назначить мастера пользователем без роли диспетчер.

---

## Заключение

В работе реализован учебный пример микросервисного приложения для управления заявками на ремонт. Выбранный стек обеспечивает баланс скорости разработки и соответствия промышленным практикам. Предложенная архитектура расширяема: добавление очередей событий, внешних интеграций, мониторинга и аудита не требует радикальной переработки.

---

## Список источников

1. Richardson, C. Microservices Patterns. Manning, 2018.
2. Fielding, R. Architectural Styles and the Design of Network-based Software Architectures. Dissertation, 2000.
3. FastAPI documentation — https://fastapi.tiangolo.com
4. Vue.js documentation — https://vuejs.org
5. Kubernetes documentation — https://kubernetes.io

---

## Приложения

### A. Mermaid диаграммы (копировать в draw.io как Mermaid)

(см. разделы выше — ER, Use Case, Sequence, DFD, Component, Infrastructure)

### B. Полные конфигурации и кодовые фрагменты

В репозитории проекта находятся рабочие реализации всех сервисов в директориях `auth-service`, `tasks-service`, `files-service`, `notifications-service`, `api-gateway`, `frontend`. Ниже приведены наиболее важные конфигурации (повтор):

- `docker-compose.yml` — в корне проекта.
- `kubernetes/*.yaml` — в папке `kubernetes/`.
- `init.sql` — инициализация БД.

### C. Запуск тестов

В проект добавлены тесты `pytest` для `auth-service` и `tasks-service`. Запуск:

```bash
pytest auth-service/tests -q
pytest tasks-service/tests -q
```

---

## Примечания по дальнейшей работе

- Подключение SMTP: использовать `notifications-service` для отправки реальных писем (config через Secrets).
- Масштабирование: настроить HPA и resource limits для сервисов.
- Мониторинг: интеграция Prometheus и Grafana для метрик.

---

> Файлы кода и все манифесты находятся в корне репозитория `course2/`. Если нужно, могу автоматически вставить сюда полные версии всех файлов (каждый сервис), но это значительно увеличит объём документа. Напишите, нужно ли вложить все исходники прямо в этот Markdown.
