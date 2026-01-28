# SentinelStream 🛡️

**Production-Ready ML System: Real-time Fraud Detection on Kubernetes**

SentinelStream is a scalable machine learning system for real-time fraud detection, now featuring **production ML deployment** on Kubernetes with autoscaling, monitoring, and GitOps.

## 🌟 Key Features

### Core ML Capabilities
-   **Hybrid ML Engine**: XGBoost + Isolation Forest for high-precision fraud detection
-   **Real-time Inference API**: FastAPI service with <10ms latency
-   **Batch Processing**: Kafka-based consumer for stream processing

### Production ML Engineering
-   **Kubernetes Deployment**: Scalable inference with HPA (2-10 pods)
-   **GitOps with ArgoCD**: Automated deployments via Git
-   **Observability**: Prometheus + Grafana dashboards
-   **Load Tested**: 10,000+ req/s sustained throughput

## 🛠️ Technology Stack

| Component | Technology |
| :--- | :--- |
| **ML Models** | XGBoost, Isolation Forest |
| **Inference API** | FastAPI, Uvicorn |
| **Streaming** | Redpanda (Kafka) |
| **Orchestration** | Kubernetes, Helm |
| **GitOps** | ArgoCD |
| **Monitoring** | Prometheus, Grafana |
| **Load Testing** | Locust |
| **Containerization** | Podman |

## 🚀 Quick Start Options

### Option 1: Local Development (Docker Compose)

```bash
# Start infrastructure
podman-compose -f infra/docker-compose.yml up -d

# Run producer
./scripts/run_producer.sh

# Run consumer & dashboard
python src/consumer.py
./scripts/run_dashboard.ps1
```

### Option 2: Kubernetes Deployment ⭐

**Prerequisites**: Minikube, Helm, kubectl, Podman

**Automated setup:**
```powershell
# Windows
.\scripts\setup-k8s.ps1

# Linux/macOS
./scripts/setup-k8s.sh
```

**Access services:**
```bash
# Inference API
kubectl port-forward svc/sentinel-ml-inference 8000:8000
# → http://localhost:8000/docs

# Grafana Dashboard
kubectl port-forward svc/prometheus-grafana 3000:80 -n monitoring
# → http://localhost:3000 (admin/prom-operator)

# ArgoCD
kubectl port-forward svc/argocd-server 8080:443 -n argocd
# → http://localhost:8080
```


## 🎬 Killer Demo: Auto-Scaling Under Load

**See Kubernetes HPA in action!** Watch pods automatically scale from 2 → 10 under 10,000+ req/s.

```bash
# 1. Deploy to K8s
.\scripts\setup-k8s.ps1

# 2. Open Grafana
kubectl port-forward svc/prometheus-grafana 3000:80 -n monitoring

# 3. Port-forward API
kubectl port-forward svc/sentinel-ml-inference 8000:8000

# 4. Run load test
pip install -r loadtest/requirements.txt
locust -f loadtest/locustfile.py --host=http://localhost:8000

# 5. Watch magic happen!
kubectl get hpa -w  # See auto-scaling in real-time
```

**Expected**: System handles 10K+ req/s, pods scale 2→10, P95 latency <50ms

📖 **Full demo guide**: [DEMO.md](DEMO.md)

---

## 📊 Load Testing

```bash
pip install -r loadtest/requirements.txt
locust -f loadtest/locustfile.py --host=http://localhost:8000

# Watch autoscaling:
kubectl get hpa -w
```

## 🔄 GitOps Workflow

Update model version:
1. Build new image: `podman build -f infra/Dockerfile.inference -t sentinel-inference:v1.1 .`
2. Update `helm/sentinel-ml/values.yaml` with new tag
3. Commit and push → ArgoCD auto-deploys ✨

See [argocd/README.md](argocd/README.md) for details.

## 📈 Performance Metrics

**ML Model**: 84% recall, 0.865 PR-AUC  
**System**: 10K+ req/s, <50ms P95 latency, 2-10 pod autoscaling

## 📂 Project Structure

```
├── src/inference_api.py       # FastAPI ML serving
├── src/model/                 # ML logic
├── k8s/                       # Kubernetes manifests
├── helm/sentinel-ml/          # Helm chart
├── argocd/                    # GitOps config
├── loadtest/                  # Locust tests
└── scripts/                   # Deployment automation
```

Full documentation: See `implementation_plan.md`
