# Quick Start Guide - Running Sentinel ML System

## Option 1: Test Inference API Locally (No Container Required) ⭐

### Step 1: Install Dependencies
```powershell
pip install -r requirements-api.txt
```

### Step 2: Start the Inference API
```powershell
# From project root
python -m uvicorn src.inference_api:app --host 0.0.0.0 --port 8000 --reload
```

### Step 3: Access the API
- **Swagger UI**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Metrics**: http://localhost:8000/metrics

### Step 4: Test Prediction

#### Via Browser (Swagger UI)
1. Go to http://localhost:8000/docs
2. Click on `/predict` endpoint
3. Click "Try it out"
4. Use this sample JSON:
```json
{
  "time": 12345.0,
  "amount": 150.50,
  "V1": -1.35, "V2": 0.5, "V3": 1.2, "V4": -0.8,
  "V5": 0.3, "V6": -0.9, "V7": 1.1, "V8": -0.4,
  "V9": 0.7, "V10": -1.0, "V11": 0.6, "V12": -0.2,
  "V13": 0.9, "V14": -0.5, "V15": 0.4, "V16": -0.7,
  "V17": 0.8, "V18": -0.3, "V19": 1.3, "V20": -1.1,
  "V21": 0.2, "V22": -0.6, "V23": 1.0, "V24": -0.1,
  "V25": 0.5, "V26": -0.8, "V27": 0.3, "V28": -0.4
}
```
5. Click "Execute"
6. See the fraud prediction result!

#### Via PowerShell (curl)
```powershell
curl -X POST "http://localhost:8000/predict" `
  -H "Content-Type: application/json" `
  -d '{
    "time": 12345,
    "amount": 150.5,
    "V1": -1.35, "V2": 0.5, "V3": 1.2, "V4": -0.8,
    "V5": 0.3, "V6": -0.9, "V7": 1.1, "V8": -0.4,
    "V9": 0.7, "V10": -1.0, "V11": 0.6, "V12": -0.2,
    "V13": 0.9, "V14": -0.5, "V15": 0.4, "V16": -0.7,
    "V17": 0.8, "V18": -0.3, "V19": 1.3, "V20": -1.1,
    "V21": 0.2, "V22": -0.6, "V23": 1.0, "V24": -0.1,
    "V25": 0.5, "V26": -0.8, "V27": 0.3, "V28": -0.4
  }'
```

**Expected Response:**
```json
{
  "fraud_probability": 0.234,
  "is_fraud": false,
  "anomaly_score": -0.156,
  "risk_level": "low",
  "model_version": "v1.0"
}
```

---

## Option 2: Run with Podman Containers

### Prerequisites
```powershell
# Fix Podman machine (if not running)
podman machine stop
podman machine rm
podman machine init --cpus 4 --memory 4096
podman machine start
```

### Build Images
```powershell
.\scripts\build-images.ps1
```

### Run Inference Container
```powershell
podman run -p 8000:8000 sentinel-inference:latest
```

Then access: http://localhost:8000/docs

---

## Option 3: Full Kubernetes Deployment

### Prerequisites
- Minikube installed
- kubectl installed
- Podman machine running

### Deploy Everything
```powershell
.\scripts\setup-k8s.ps1
```

This will:
1. ✅ Start Minikube
2. ✅ Build & load images
3. ✅ Deploy Prometheus + Grafana
4. ✅ Deploy ArgoCD
5. ✅ Deploy Sentinel ML
6. ✅ Configure monitoring

### Access Services

#### 1. Inference API
```powershell
kubectl port-forward svc/sentinel-ml-inference 8000:8000
```
Visit: http://localhost:8000/docs

#### 2. Grafana Dashboard
```powershell
kubectl port-forward svc/prometheus-grafana 3000:80 -n monitoring
```
Visit: http://localhost:3000
- Username: `admin`
- Password: `prom-operator`

Look for dashboard: "Sentinel ML: Fraud Detection Performance"

#### 3. ArgoCD
```powershell
kubectl port-forward svc/argocd-server 8080:443 -n argocd
```
Visit: http://localhost:8080
- Username: `admin`
- Password: 
```powershell
kubectl get secret argocd-initial-admin-secret -n argocd -o jsonpath="{.data.password}" | base64 -d
```

#### 4. Check Deployment Status
```powershell
# Check pods
kubectl get pods

# Check HPA
kubectl get hpa

# Check services
kubectl get svc

# Watch HPA autoscaling
kubectl get hpa -w
```

---

## Option 4: Load Testing

### Prerequisites
```powershell
pip install -r loadtest/requirements.txt
```

### Run Load Test
```powershell
# Make sure API is running (Option 1, 2, or 3)
# Then in a new terminal:

locust -f loadtest/locustfile.py --host=http://localhost:8000
```

### Access Locust UI
Visit: http://localhost:8089

**Recommended settings:**
- Number of users: 100
- Spawn rate: 10
- Duration: 5 minutes

**What to watch:**
- In another terminal: `kubectl get hpa -w` (see autoscaling)
- In Grafana: Real-time metrics
- In Locust: Throughput and response times

---

## 🎯 Quick Demo Flow

**5-Minute Demo:**

1. **Start API** (30 seconds):
   ```powershell
   python -m uvicorn src.inference_api:app --port 8000
   ```

2. **Open Swagger** (30 seconds):
   - Go to http://localhost:8000/docs
   - Show interactive API documentation

3. **Test Prediction** (1 minute):
   - Use `/predict` endpoint
   - Show fraud detection in action

4. **Check Metrics** (1 minute):
   - Visit http://localhost:8000/metrics
   - Show Prometheus metrics

5. **Explain Architecture** (2 minutes):
   - Show code structure
   - Explain ML model integration
   - Discuss Kubernetes deployment

---

## 🐛 Troubleshooting

### API won't start
**Error**: `ModuleNotFoundError: No module named 'fastapi'`
```powershell
pip install -r requirements-api.txt
```

### Podman issues
```powershell
podman machine stop
podman machine start
podman info  # Verify
```

### Minikube issues
```powershell
minikube stop
minikube delete
minikube start --cpus=4 --memory=8192
```

### Port already in use
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill it
taskkill /PID <PID> /F
```

---

## 📸 What You'll See

### Swagger UI
- Interactive API documentation
- Try out endpoints live
- See request/response schemas

### Grafana Dashboard
- Real-time inference metrics
- CPU/Memory usage graphs
- HPA scaling visualization
- Fraud detection rate

### Locust Load Test
- Requests per second chart
- Response time distribution
- Success/failure rates

---

## ✅ Success Indicators

You know it's working when:
- ✅ API responds to `/health` with 200 OK
- ✅ Predictions return fraud_probability values
- ✅ Metrics show at `/metrics`
- ✅ Pods are in "Running" status
- ✅ HPA shows current/desired replicas
- ✅ Grafana displays metrics

---

## 🎬 Next Steps

After testing:
1. Record screen demo (Swagger UI + Grafana)
2. Take screenshots for portfolio
3. Document performance results
4. Create Pull Request to main branch
