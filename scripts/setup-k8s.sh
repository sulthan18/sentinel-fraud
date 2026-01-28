#!/bin/bash
# Sentinel ML K8s Setup Script
# Automated deployment for Minikube

set -e

echo "=========================================="
echo "🚀 Sentinel ML Kubernetes Setup"
echo "=========================================="
echo ""

# Check if Minikube is running
if ! minikube status &gt; /dev/null 2&gt;&1; then
    echo "⚠️  Minikube not running. Starting..."
    minikube start --cpus=4 --memory=8192 --driver=docker
else
    echo "✅ Minikube is running"
fi

# Enable metrics-server for HPA
echo ""
echo "📊 Enabling metrics-server..."
minikube addons enable metrics-server

# Build and load Docker images into Minikube
echo ""
echo "🐳 Building Docker images..."
eval $(minikube docker-env)

docker build -f infra/Dockerfile.inference -t sentinel-inference:latest .
docker build -f infra/Dockerfile.consumer -t sentinel-consumer:latest .

echo "✅ Docker images built and loaded into Minikube"

# Install kube-prometheus-stack
echo ""
echo "📈 Installing Prometheus + Grafana..."
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

kubectl create namespace monitoring || true

helm upgrade --install prometheus prometheus-community/kube-prometheus-stack \
    -f k8s/monitoring/prometheus-values.yaml \
    -n monitoring \
    --wait

echo "✅ Monitoring stack deployed"

# Install ArgoCD
echo ""
echo "🔄 Installing ArgoCD..."
kubectl create namespace argocd || true

kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

echo "⏳ Waiting for ArgoCD to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/argocd-server -n argocd

echo "✅ ArgoCD installed"

# Deploy Sentinel ML via Helm
echo ""
echo "🤖 Deploying Sentinel ML..."
helm upgrade --install sentinel-ml ./helm/sentinel-ml --wait

echo "✅ Sentinel ML deployed"

# Apply ServiceMonitor
echo ""
echo "📡 Configuring Prometheus monitoring..."
kubectl apply -f k8s/monitoring/servicemonitor.yaml

echo "✅ ServiceMonitor configured"

# Display access information
echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Access services:"
echo ""
echo "1. Inference API:"
echo "   kubectl port-forward svc/sentinel-ml-inference 8000:8000"
echo "   http://localhost:8000/docs"
echo ""
echo "2. Grafana Dashboard:"
echo "   kubectl port-forward svc/prometheus-grafana 3000:80 -n monitoring"
echo "   http://localhost:3000 (admin/prom-operator)"
echo ""
echo "3. ArgoCD UI:"
echo "   kubectl port-forward svc/argocd-server 8080:443 -n argocd"
echo "   http://localhost:8080"
echo "   Password: kubectl get secret argocd-initial-admin-secret -n argocd -o jsonpath=\"{.data.password}\" | base64 -d"
echo ""
echo "4. Watch HPA:"
echo "   kubectl get hpa -w"
echo ""
echo "Next steps:"
echo "- Run load test: locust -f loadtest/locustfile.py --host=http://localhost:8000"
echo ""
