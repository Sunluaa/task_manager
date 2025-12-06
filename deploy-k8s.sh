#!/bin/bash

echo "=== Task Management System - Kubernetes Deployment ==="
echo ""

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "Error: kubectl is not installed!"
    exit 1
fi

# Check cluster connection
kubectl cluster-info > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Error: Cannot connect to Kubernetes cluster!"
    echo "Please start Minikube or configure kubectl"
    exit 1
fi

echo "Connected to cluster: $(kubectl cluster-info | head -1)"
echo ""

# Apply manifests in order
echo "Applying namespace..."
kubectl apply -f kubernetes/00-namespace.yaml

echo "Applying config and secrets..."
kubectl apply -f kubernetes/01-configmap-secret.yaml

echo "Applying PostgreSQL..."
kubectl apply -f kubernetes/02-postgres.yaml

echo "Waiting for PostgreSQL to be ready (this may take 30-60 seconds)..."
kubectl wait --for=condition=ready pod -l app=postgres -n task-management --timeout=300s

echo "Applying Auth Service..."
kubectl apply -f kubernetes/03-auth-service.yaml

echo "Applying Tasks Service..."
kubectl apply -f kubernetes/04-tasks-service.yaml

echo "Applying Notifications Service..."
kubectl apply -f kubernetes/05-notifications-service.yaml

echo "Applying API Gateway..."
kubectl apply -f kubernetes/06-api-gateway.yaml

echo "Applying Frontend..."
kubectl apply -f kubernetes/07-frontend.yaml

echo "Applying Ingress..."
kubectl apply -f kubernetes/08-ingress.yaml

echo "Applying HPA..."
kubectl apply -f kubernetes/09-hpa.yaml

echo "Applying PDB..."
kubectl apply -f kubernetes/10-pdb.yaml

echo ""
echo "=== Deployment Status ==="
echo ""

echo "Waiting for deployments to be ready (timeout: 5 minutes)..."
kubectl wait --for=condition=available --timeout=300s deployment/auth-service -n task-management 2>/dev/null
kubectl wait --for=condition=available --timeout=300s deployment/tasks-service -n task-management 2>/dev/null
kubectl wait --for=condition=available --timeout=300s deployment/api-gateway -n task-management 2>/dev/null
kubectl wait --for=condition=available --timeout=300s deployment/frontend -n task-management 2>/dev/null

echo ""
echo "Resources in task-management namespace:"
kubectl get all -n task-management

echo ""
echo "=== Services ==="
kubectl get svc -n task-management

echo ""
echo "=== Deployment Complete ==="
echo ""

# Show access information
echo "Access information:"
if command -v minikube &> /dev/null; then
    MINIKUBE_IP=$(minikube ip)
    echo "Minikube IP: $MINIKUBE_IP"
    echo "Frontend: http://$MINIKUBE_IP:30000 (or use port-forward)"
    echo ""
    echo "For port forwarding:"
    echo "  kubectl port-forward svc/frontend 3000:3000 -n task-management"
    echo "  Then access: http://localhost:3000"
else
    echo "For port forwarding:"
    echo "  kubectl port-forward svc/frontend 3000:3000 -n task-management"
    echo "  kubectl port-forward svc/api-gateway 8000:8000 -n task-management"
    echo "Then access: http://localhost:3000"
fi

echo ""
echo "Check pod logs:"
echo "  kubectl logs -f deployment/auth-service -n task-management"
echo "  kubectl logs -f deployment/tasks-service -n task-management"
echo "  kubectl logs -f deployment/api-gateway -n task-management"
