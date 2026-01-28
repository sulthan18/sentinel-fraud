# Sentinel ML K8s Setup Script - PowerShell
# Automated deployment for Minikube on Windows

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🚀 Sentinel ML Kubernetes Setup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Minikube is running
Write-Host "Checking Minikube status..." -ForegroundColor Yellow
try {
    $status = minikube status 2>$null
    Write-Host "✅ Minikube is running" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Minikube not running. Starting..." -ForegroundColor Yellow
    minikube start --cpus=4 --memory=8192 --driver=docker
}

# Enable metrics-server for HPA
Write-Host ""
Write-Host "📊 Enabling metrics-server..." -ForegroundColor Yellow
minikube addons enable metrics-server

# Build and load Docker images into Minikube
Write-Host ""
Write-Host "🐳 Building Docker images..." -ForegroundColor Yellow

# Set Docker environment to Minikube
& minikube -p minikube docker-env --shell powershell | Invoke-Expression

docker build -f infra\Dockerfile.inference -t sentinel-inference:latest .
docker build -f infra\Dockerfile.consumer -t sentinel-consumer:latest .

Write-Host "✅ Docker images built and loaded into Minikube" -ForegroundColor Green

# Install kube-prometheus-stack
Write-Host ""
Write-Host "📈 Installing Prometheus + Grafana..." -ForegroundColor Yellow
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

kubectl create namespace monitoring 2>$null

helm upgrade --install prometheus prometheus-community/kube-prometheus-stack `
    -f k8s\monitoring\prometheus-values.yaml `
    -n monitoring `
    --wait

Write-Host "✅ Monitoring stack deployed" -ForegroundColor Green

# Install ArgoCD
Write-Host ""
Write-Host "🔄 Installing ArgoCD..." -ForegroundColor Yellow
kubectl create namespace argocd 2>$null

kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

Write-Host "⏳ Waiting for ArgoCD to be ready..." -ForegroundColor Yellow
kubectl wait --for=condition=available --timeout=300s deployment/argocd-server -n argocd

Write-Host "✅ ArgoCD installed" -ForegroundColor Green

# Deploy Sentinel ML via Helm
Write-Host ""
Write-Host "🤖 Deploying Sentinel ML..." -ForegroundColor Yellow
helm upgrade --install sentinel-ml .\helm\sentinel-ml --wait

Write-Host "✅ Sentinel ML deployed" -ForegroundColor Green

# Apply ServiceMonitor
Write-Host ""
Write-Host "📡 Configuring Prometheus monitoring..." -ForegroundColor Yellow
kubectl apply -f k8s\monitoring\servicemonitor.yaml

Write-Host "✅ ServiceMonitor configured" -ForegroundColor Green

# Display access information
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access services:" -ForegroundColor White
Write-Host ""
Write-Host "1. Inference API:" -ForegroundColor Yellow
Write-Host "   kubectl port-forward svc/sentinel-ml-inference 8000:8000"
Write-Host "   http://localhost:8000/docs"
Write-Host ""
Write-Host "2. Grafana Dashboard:" -ForegroundColor Yellow
Write-Host "   kubectl port-forward svc/prometheus-grafana 3000:80 -n monitoring"
Write-Host "   http://localhost:3000 (admin/prom-operator)"
Write-Host ""
Write-Host "3. ArgoCD UI:" -ForegroundColor Yellow
Write-Host "   kubectl port-forward svc/argocd-server 8080:443 -n argocd"
Write-Host "   http://localhost:8080"
Write-Host "   Password: kubectl get secret argocd-initial-admin-secret -n argocd -o jsonpath=`"{.data.password}`" | base64 -d"
Write-Host ""
Write-Host "4. Watch HPA:" -ForegroundColor Yellow
Write-Host "   kubectl get hpa -w"
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "- Run load test: locust -f loadtest\locustfile.py --host=http://localhost:8000"
Write-Host ""
