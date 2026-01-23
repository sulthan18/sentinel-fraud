# SentinelStream 🛡️

**Real-time Credit Card Fraud Detection Pipeline**

SentinelStream is a robust data engineering and machine learning system that detects fraudulent credit card transactions in real-time. It simulates a high-throughput transaction stream, processes data using Redpanda (Kafka), and applies ML inference (XGBoost/Isolation Forest) to flag anomalies instantly.

## 🌟 Key Features
-   **Real-time Ingestion**: Streams 10,000+ transactions/sec using Redpanda.
-   **Hybrid ML Engine**: Combines **XGBoost** (Supervised) and **Isolation Forest** (Unsupervised) for high-precision fraud detection.
-   **Low Latency**: End-to-end inference latency of **<10ms**.
-   **Live Dashboard**: Interactive Streamlit UI visualizing fraud rates, alerts, and system usage.
-   **Persistence**: SQLite integration for historical latency tracking and audit logs.

## 🛠️ Technology Stack
| Component | Technology |
| :--- | :--- |
| **Streaming** | Redpanda (Kafka Protocol) |
| **Containerization** | Podman / Docker |
| **Machine Learning** | XGBoost, Scikit-learn |
| **Backend** | Python 3.11, Kafka-Python |
| **Frontend** | Streamlit, Plotly |
| **Database** | SQLite |

## 🚀 Quick Start

### 1. Start Infrastructure
Launch the Redpanda broker:
```bash
podman-compose -f infra/docker-compose.yml up -d
```

### 2. Run Producer
Simulate live transaction traffic:
```bash
./scripts/run_producer.sh
```

### 3. Run Consumer & Dashboard
Start the inference engine and visualization:
```bash
# Terminal 1: Consumer (Backend)
python src/consumer.py

# Terminal 2: Dashboard (Frontend)
.\scripts\run_dashboard.ps1
```

## 📊 Performance Metrics
-   **Recall**: 84% (XGBoost) - Captures the majority of fraud cases.
-   **Precision-Recall AUC**: 0.865.
-   **Throughput**: scalable to 50+ tx/s per producer instance.

## 📂 Project Structure
-   `src/model`: ML training and inference logic.
-   `src/producer.py`: Data streaming simulator.
-   `src/consumer.py`: Real-time processing agent.
-   `src/dashboard.py`: User interface.
-   `data/`: dataset storage (ignored in git).
