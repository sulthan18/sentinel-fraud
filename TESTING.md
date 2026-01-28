# Container Build & Testing Guide

## Local Testing Options

### Option 1: Test API Components (No Container Required)

Test the inference API components locally without containers:

```bash
# Install dependencies
pip install -r requirements-api.txt

# Test predictor directly
python -c "from src.model.predictor import FraudPredictor; p = FraudPredictor(); print('OK')"
```

**Note**: Windows console encoding may cause issues with emoji characters in output. This is cosmetic and doesn't affect functionality.

---

### Option 2: Build Podman Images

#### Prerequisites

**Podman**:
```powershell
# Start Podman machine first
podman machine init
podman machine start

# Verify
podman info
```

#### Build Images

**Using PowerShell script** (recommended):
```powershell
.\scripts\build-images.ps1
```

**Manual build with Podman**:
```bash
podman build -f infra/Dockerfile.inference -t sentinel-inference:latest .
podman build -f infra/Dockerfile.consumer -t sentinel-consumer:latest .
```

---

### Option 3: Test Container Locally

#### Run Inference API Container

```bash
podman run -p 8000:8000 sentinel-inference:latest
```

Access:
- Swagger UI: http://localhost:8000/docs
- Health check: http://localhost:8000/health
- Metrics: http://localhost:8000/metrics

#### Test with curl

```powershell
# Health check
curl http://localhost:8000/health

# Prediction
curl -X POST http://localhost:8000/predict `
  -H "Content-Type: application/json" `
  -d '{"time": 12345, "amount": 150.5, "V1": -1.35, "V2": 0.5, ...}'
```

---

## Kubernetes Deployment Testing

### Quick Setup (All-in-One)

```powershell
# Windows
.\scripts\setup-k8s.ps1

# Linux/macOS
./scripts/setup-k8s.sh
```

This automatically:
1. Starts Minikube
2. Builds images
3. Deploys all services
4. Sets up monitoring

### Manual Testing Steps

#### 1. Start Minikube
```bash
minikube start --cpus=4 --memory=8192
minikube addons enable metrics-server
```

#### 2. Build and Load Images
```bash
# Set Podman env to Minikube
& minikube -p minikube podman-env --shell powershell | Invoke-Expression

# Build images
podman build -f infra/Dockerfile.inference -t sentinel-inference:latest .
```

#### 3. Deploy with Helm
```bash
helm install sentinel-ml ./helm/sentinel-ml
```

#### 4. Verify Deployment
```bash
kubectl get pods
kubectl get svc
kubectl get hpa
```

#### 5. Port-Forward and Test
```bash
kubectl port-forward svc/sentinel-ml-inference 8000:8000
# Visit http://localhost:8000/docs
```

---

## Troubleshooting

### Podman connection refused
**Error**: `unable to connect to Podman socket`

**Solution**:
```bash
podman machine init
podman machine start
podman info  # Verify it's running
```

### Python import errors locally
**Error**: `ModuleNotFoundError: No module named 'src'`

**Solution**:
- Use the test script: `python scripts/test_api_local.py`
- OR run from container (no import issues in containers)

### Emoji encoding errors (Windows)
**Error**: `UnicodeEncodeError: 'charmap' codec can't encode`

**Solution**:
- This is cosmetic, doesn't affect functionality
- Set `$env:PYTHONIOENCODING="utf-8"` in PowerShell
- OR ignore (containers don't have this issue)

---

## Validation Checklist

Before deploying to Kubernetes:

- [ ] ML models exist in `models/` directory (`.pkl` files)
- [ ] Dependencies installed (`pip install -r requirements-api.txt`)
- [ ] Podman is running
- [ ] Images build successfully
- [ ] API responds to health checks
- [ ] Inference returns predictions

For Kubernetes deployment:

- [ ] Minikube is running
- [ ] Images loaded into Minikube
- [ ] Helm chart deploys without errors
- [ ] Pods are in Running state
- [ ] HPA is configured
- [ ] Prometheus metrics are scraped

---

## Quick Commands Reference

```bash
# Local testing
pip install -r requirements-api.txt
python scripts/test_api_local.py

# Build images
.\scripts\build-images.ps1  # Windows
./scripts/build-images.sh   # Linux/macOS

# Deploy to K8s
.\scripts\setup-k8s.ps1     # Windows
./scripts/setup-k8s.sh      # Linux/macOS

# Check status
kubectl get pods
kubectl get hpa -w
kubectl logs -f deployment/sentinel-ml-inference

# Access services
kubectl port-forward svc/sentinel-ml-inference 8000:8000
kubectl port-forward svc/prometheus-grafana 3000:80 -n monitoring
```
