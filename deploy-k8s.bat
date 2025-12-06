@echo off
REM Task Management System - Kubernetes Deployment (Windows)

echo === Task Management System - Kubernetes Deployment ===
echo.

REM Check if kubectl is installed
kubectl version --client >nul 2>&1
if errorlevel 1 (
    echo Error: kubectl is not installed!
    exit /b 1
)

REM Check cluster connection
kubectl cluster-info >nul 2>&1
if errorlevel 1 (
    echo Error: Cannot connect to Kubernetes cluster!
    echo Please start Minikube or configure kubectl
    exit /b 1
)

echo Connected to cluster.
echo.

REM Apply manifests in order
echo Applying namespace...
kubectl apply -f kubernetes/00-namespace.yaml

echo Applying config and secrets...
kubectl apply -f kubernetes/01-configmap-secret.yaml

echo Applying PostgreSQL...
kubectl apply -f kubernetes/02-postgres.yaml

echo Waiting for PostgreSQL to be ready...
kubectl wait --for=condition=ready pod -l app=postgres -n task-management --timeout=300s

echo Applying services...
kubectl apply -f kubernetes/03-auth-service.yaml
kubectl apply -f kubernetes/04-tasks-service.yaml
kubectl apply -f kubernetes/05-notifications-service.yaml
kubectl apply -f kubernetes/06-api-gateway.yaml
kubectl apply -f kubernetes/07-frontend.yaml

echo Applying Ingress...
kubectl apply -f kubernetes/08-ingress.yaml

echo Applying HPA...
kubectl apply -f kubernetes/09-hpa.yaml

echo Applying PDB...
kubectl apply -f kubernetes/10-pdb.yaml

echo.
echo === Deployment Status ===
echo.
echo Resources:
kubectl get all -n task-management

echo.
echo === Deployment Complete ===
echo.
echo For port forwarding:
echo   kubectl port-forward svc/frontend 3000:3000 -n task-management
echo.
echo Then access: http://localhost:3000
echo.
echo Check logs:
echo   kubectl logs -f deployment/auth-service -n task-management
