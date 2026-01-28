# Sentinel ML - Project Structure

## 📁 Clean Architecture Overview

```
Sentinel/
├── 📊 DATA LAYER
│   ├── data/                    # Training datasets
│   ├── models/                  # Trained ML models (.pkl)
│   └── sentinel.db              # SQLite database (runtime)
│
├── 🧠 ML CORE LAYER
│   └── src/
│       ├── model/
│       │   ├── predictor.py     # Fraud prediction engine
│       │   └── train.py         # Model training pipeline
│       └── config.py            # Configuration management
│
├── 🔄 STREAMING LAYER (Local Demo)
│   └── src/
│       ├── producer.py          # Data generator (ZeroMQ Publisher)
│       ├── consumer.py          # ML processor (ZeroMQ Subscriber)
│       └── dashboard.py         # Streamlit visualization
│
├── 🚀 API LAYER (K8s Deployment)
│   └── src/
│       └── inference_api.py     # FastAPI REST endpoint
│
├── ☸️ KUBERNETES LAYER
│   ├── helm/                    # Helm charts for deployment
│   ├── k8s/                     # Raw K8s manifests
│   │   ├── base/                # Core deployments
│   │   └── monitoring/          # Prometheus & Grafana
│   ├── argocd/                  # GitOps configuration
│   └── loadtest/                # Locust load testing
│
├── 🐳 INFRASTRUCTURE
│   └── infra/
│       ├── Dockerfile.inference # Container image
│       └── redpanda-compose.yml # Kafka broker (optional)
│
├── 🛠️ SCRIPTS & TOOLS
│   └── scripts/
│       ├── run_producer.bat     # Start data generator
│       ├── run_consumer.bat     # Start ML processor
│       ├── run_dashboard.ps1    # Start dashboard
│       ├── setup-k8s.ps1/sh     # K8s deployment automation
│       └── build-images.ps1/sh  # Container build scripts
│
└── 📚 DOCUMENTATION
    ├── README.md                # Project overview
    ├── DEMO.md                  # K8s auto-scaling demo guide
    └── TESTING.md               # Testing instructions
```

---

## 🏗️ Architecture Layers

### 1. **Local Streaming Mode** (Development)
```
Producer (ZMQ) → Consumer (ML Core) → SQLite → Dashboard (Streamlit)
```

**Use Case**: Local development, testing, demos without Docker  
**Tech**: Python, ZeroMQ, SQLite, Streamlit

### 2. **Kubernetes Mode** (Production)
```
Inference API → HPA → Prometheus → Grafana
     ↓
Load Balancer → Multiple Pods
```

**Use Case**: Production deployment, auto-scaling demo  
**Tech**: FastAPI, K8s, Helm, ArgoCD, Prometheus, Grafana

---

## 📦 Dependencies

| File | Purpose |
|------|---------|
| `requirements.txt` | Core ML dependencies (scikit-learn, pandas, joblib) |
| `requirements-api.txt` | API layer (FastAPI, uvicorn, prometheus-client) |
| `requirements-dashboard.txt` | Dashboard (streamlit, plotly) |

---

## 🚀 Quick Start

### Local Streaming Demo
```powershell
# Terminal 1
.\scripts\run_producer.bat

# Terminal 2
.\scripts\run_consumer.bat

# Terminal 3
.\scripts\run_dashboard.ps1
```

### Kubernetes Demo
```powershell
.\scripts\setup-k8s.ps1
```

---

## ✅ Clean Architecture Principles Applied

1. **Separation of Concerns**: ML core, streaming, API, and UI are decoupled
2. **Dependency Inversion**: Config layer manages all dependencies
3. **Single Responsibility**: Each module has one clear purpose
4. **DRY (Don't Repeat Yourself)**: Shared config, reusable models
5. **Open/Closed**: Easy to swap ZeroMQ → Kafka without changing ML core

---

## 🎯 What Makes This "Clean"?

- ✅ No circular dependencies
- ✅ Clear layer boundaries
- ✅ Technology-agnostic core (ML code doesn't know about ZeroMQ or FastAPI)
- ✅ Easy testing (each layer can be tested independently)
- ✅ Scalable (can add new streaming sources without touching ML core)

**This is production-ready ML Engineering! 🚀**
