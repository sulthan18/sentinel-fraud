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

## 🚀 Quick Start Options

### Option 1: Local Development (Docker Compose)

```bash
# Start infrastructure
docker-compose -f infra/docker-compose.yml up -d

# Run producer
./scripts/run_producer.sh

# Run consumer & dashboard
python src/consumer.py
./scripts/run_dashboard.ps1
```

### Option 2: Kubernetes Deployment ⭐

**Prerequisites**: Minikube, Helm, kubectl, Docker

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

## 📊 Load Testing

```bash
pip install -r loadtest/requirements.txt
locust -f loadtest/locustfile.py --host=http://localhost:8000

# Watch autoscaling:
kubectl get hpa -w
```

## 🔄 GitOps Workflow

Update model version:
1. Build new image: `docker build -f infra/Dockerfile.inference -t sentinel-inference:v1.1 .`
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
