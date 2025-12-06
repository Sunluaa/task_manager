# Kubernetes Развёртывание

## Требования

- Kubernetes кластер (minikube, Docker Desktop K8s, kind, или облако)
- `kubectl` установлен и настроен
- Docker образы построены и доступны

## Структура манифестов

```
kubernetes/
├── 00-namespace.yaml          # Namespace для приложения
├── 01-configmap-secret.yaml   # ConfigMap и Secrets
├── 02-postgres.yaml           # PostgreSQL StatefulSet + Service
├── 03-auth-service.yaml       # Auth Service Deployment + Service
├── 04-tasks-service.yaml      # Tasks Service Deployment + Service
├── 05-notifications-service.yaml  # Notifications Service Deployment + Service
├── 06-api-gateway.yaml        # API Gateway Deployment + Service (LoadBalancer)
├── 07-frontend.yaml           # Frontend Deployment + Service (LoadBalancer)
├── 08-ingress.yaml            # Ingress для маршрутизации
├── 09-hpa.yaml               # Horizontal Pod Autoscaler
└── 10-pdb.yaml               # Pod Disruption Budget
```

## Развёртывание на Kubernetes

### 1. Локальное тестирование с Minikube

```bash
# Запустить миникуб
minikube start --cpus=4 --memory=4096

# Загрузить Docker образы
minikube image load course2-auth-service:latest
minikube image load course2-tasks-service:latest
minikube image load course2-notifications-service:latest
minikube image load course2-api-gateway:latest
minikube image load course2-frontend:latest
```

### 2. Применение манифестов

```bash
# Применить все манифесты по порядку
kubectl apply -f kubernetes/00-namespace.yaml
kubectl apply -f kubernetes/01-configmap-secret.yaml
kubectl apply -f kubernetes/02-postgres.yaml

# Подождать пока PostgreSQL запустится
kubectl wait --for=condition=ready pod -l app=postgres -n task-management --timeout=300s

# Применить микросервисы
kubectl apply -f kubernetes/03-auth-service.yaml
kubectl apply -f kubernetes/04-tasks-service.yaml
kubectl apply -f kubernetes/05-notifications-service.yaml
kubectl apply -f kubernetes/06-api-gateway.yaml
kubectl apply -f kubernetes/07-frontend.yaml

# Применить Ingress и HPA
kubectl apply -f kubernetes/08-ingress.yaml
kubectl apply -f kubernetes/09-hpa.yaml
kubectl apply -f kubernetes/10-pdb.yaml

# Или всё сразу
kubectl apply -f kubernetes/
```

### 3. Проверка статуса

```bash
# Список всех ресурсов в namespace
kubectl get all -n task-management

# Статус Pods
kubectl get pods -n task-management
kubectl describe pod <pod-name> -n task-management

# Логи сервиса
kubectl logs -f <pod-name> -n task-management

# Статус Services
kubectl get svc -n task-management

# Статус Deployments
kubectl get deploy -n task-management -w

# Статус HPA
kubectl get hpa -n task-management
```

### 4. Доступ к приложению (с Minikube)

```bash
# Получить IP адрес Minikube
minikube ip

# Port forward для frontend
kubectl port-forward svc/frontend 3000:3000 -n task-management

# Port forward для API Gateway
kubectl port-forward svc/api-gateway 8000:8000 -n task-management

# Открыть Minikube dashboard
minikube dashboard
```

Затем откройте в браузере: `http://localhost:3000`

### 5. Масштабирование

```bash
# Мануальное масштабирование
kubectl scale deployment auth-service --replicas=3 -n task-management

# HPA автоматически масштабирует при нагрузке
# Минимум/максимум реплик настроены в 10-hpa.yaml

# Проверить статус HPA
kubectl get hpa -n task-management -w
```

## Облачное развёртывание

### Google Cloud (GKE)

```bash
# Создать кластер
gcloud container clusters create task-management --zone us-central1-a

# Установить контекст
gcloud container clusters get-credentials task-management --zone us-central1-a

# Применить манифесты
kubectl apply -f kubernetes/

# Получить IP LoadBalancer
kubectl get svc -n task-management
```

### Amazon AWS (EKS)

```bash
# Требуется AWS CLI и eksctl

# Создать кластер
eksctl create cluster --name task-management --region us-east-1

# Применить манифесты
kubectl apply -f kubernetes/
```

## Отладка и мониторинг

```bash
# Проверить события в namespace
kubectl get events -n task-management

# Смотреть логи сервиса в реальном времени
kubectl logs -f deployment/auth-service -n task-management

# Получить информацию о ресурсах
kubectl top nodes
kubectl top pods -n task-management

# Войти в контейнер
kubectl exec -it <pod-name> -n task-management -- sh

# Port forward для базы данных (если нужно подключиться извне)
kubectl port-forward svc/postgres 5432:5432 -n task-management
```

## Удаление ресурсов

```bash
# Удалить namespace (удаляет все ресурсы)
kubectl delete namespace task-management

# Удалить конкретный ресурс
kubectl delete deployment auth-service -n task-management
kubectl delete svc auth-service -n task-management
```

## Особенности конфигурации

- **StatefulSet для PostgreSQL**: сохраняет данные между перезаписями
- **HPA**: автоматическое масштабирование на основе CPU и памяти
- **PDB**: гарантирует минимум доступных подов при обновлениях
- **Probes**: liveness и readiness для здоровья контейнеров
- **Resources**: requests и limits для управления ресурсами
- **LoadBalancer**: для API Gateway и Frontend (для облака требуется настройка)

## Продакшн конфигурация

Для продакшена рекомендуется:

1. Использовать правильные имена хостов вместо localhost
2. Настроить TLS/SSL сертификаты
3. Использовать управляемые базы данных (RDS, Cloud SQL)
4. Настроить мониторинг и логирование (Prometheus, ELK)
5. Использовать приватные реестры Docker (ECR, GCR)
6. Настроить RBAC для безопасности
7. Использовать Network Policies для ограничения трафика
