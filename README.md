# SentinelStream 🛡️

**Real-time Credit Card Fraud Detection System**

SentinelStream is an end-to-end data engineering and machine learning pipeline designed to detect fraudulent transactions in real-time.

## 🚀 Architecture
1.  **Producer**: Streams transaction data from CSV to Redpanda (Kafka-compatible).
2.  **Infrastructure**: Docker/Podman containers for Redpanda.
3.  **Brain**: XGBoost & Isolation Forest models trained on `creditcard.csv`.
4.  **Consumer**: Real-time inference engine using trained models.
5.  **Dashboard**: Streamlit UI for live monitoring and alerts.
6.  **Persistence**: SQLite database for latency tracking and historical analysis.

## 🛠️ Tech Stack
-   **Streaming**: Redpanda (Kafka)
-   **Containerization**: Podman / Docker
-   **ML Models**: XGBoost, Isolation Forest, Scikit-learn
-   **Backend**: Python (Kafka-Python, Pandas)
-   **Frontend**: Streamlit
-   **Database**: SQLite

## 🏃‍♂️ Quick Start

### 1. Start Infrastructure
```bash
podman-compose -f infra/docker-compose.yml up -d
```

### 2. Run Producer (Data Stream)
```bash
./scripts/run_producer.sh
```

### 3. Run Consumer (Inference)
```bash
python src/consumer.py
```

### 4. Launch Dashboard
```powershell
.\scripts\run_dashboard.ps1
```

## 📊 Performance
-   **Throughput**: 50+ tx/s (Configurable)
-   **Latency**: ~5-10ms per inference
-   **Accuracy**: 84% Recall (XGBoost)
