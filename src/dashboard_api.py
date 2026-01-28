"""
Sentinel ML - Streamlit Dashboard
Real-time fraud detection visualization consuming from Inference API
No Kafka/Docker required - runs standalone with API
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import random
import numpy as np

# API Configuration
API_URL = "http://localhost:8000"

# Page config
st.set_page_config(
    page_title="Sentinel ML - Fraud Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
</style>
""", unsafe_allow_html=True)


def generate_synthetic_transaction():
    """Generate synthetic transaction for testing"""
    # 90% legitimate, 10% potentially fraudulent
    is_fraud_sim = random.random() < 0.1
    
    if is_fraud_sim:
        # Fraudulent pattern: high amount, unusual time
        amount = random.uniform(500, 2000)
        hour = random.choice([2, 3, 4, 23, 0, 1])  # Unusual hours
    else:
        # Normal pattern
        amount = random.uniform(10, 300)
        hour = random.choice(range(9, 22))  # Business hours
    
    # Generate PCA components (V1-V28)
    transaction = {
        "time": hour * 3600 + random.randint(0, 3600),
        "amount": round(amount, 2)
    }
    
    # Add V1-V28 features (synthetic PCA components)
    for i in range(1, 29):
        if is_fraud_sim:
            # Outlier values for fraud
            transaction[f"V{i}"] = random.gauss(0, 3)
        else:
            # Normal distribution
            transaction[f"V{i}"] = random.gauss(0, 1)
    
    return transaction


def call_inference_api(transaction):
    """Call the inference API"""
    try:
        response = requests.post(
            f"{API_URL}/predict",
            json=transaction,
            timeout=5
        )
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        st.error(f"API Error: {e}")
        return None


def check_api_health():
    """Check if API is running"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False


# Initialize session state
if 'predictions' not in st.session_state:
    st.session_state.predictions = []
if 'running' not in st.session_state:
    st.session_state.running = False
if 'total_transactions' not in st.session_state:
    st.session_state.total_transactions = 0
if 'total_fraud' not in st.session_state:
    st.session_state.total_fraud = 0


# Header
st.markdown('<div class="main-header">🛡️ Sentinel ML - Real-Time Fraud Detection</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Health Check
    api_healthy = check_api_health()
    if api_healthy:
        st.success("✅ API Connected")
    else:
        st.error("❌ API Offline")
        st.info("Start API: `python -m uvicorn src.inference_api:app --port 8000`")
    
    st.divider()
    
    # Controls
    st.header("🎮 Controls")
    
    transactions_per_sec = st.slider("Transactions/sec", 1, 10, 2)
    auto_generate = st.checkbox("Auto-generate transactions", value=False)
    
    if st.button("🔄 Clear History"):
        st.session_state.predictions = []
        st.session_state.total_transactions = 0
        st.session_state.total_fraud = 0
        st.rerun()
    
    st.divider()
    
    # Manual transaction test
    st.header("🧪 Manual Test")
    test_amount = st.number_input("Amount ($)", 10.0, 5000.0, 100.0)
    if st.button("🚀 Test Transaction"):
        tx = generate_synthetic_transaction()
        tx['amount'] = test_amount
        result = call_inference_api(tx)
        if result:
            st.session_state.predictions.append({
                'timestamp': datetime.now(),
                'amount': tx['amount'],
                **result
            })
            st.session_state.total_transactions += 1
            if result['is_fraud']:
                st.session_state.total_fraud += 1
            st.rerun()

# Main content
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="📊 Total Transactions",
        value=f"{st.session_state.total_transactions:,}",
        delta=f"{len(st.session_state.predictions)} in buffer"
    )

with col2:
    fraud_count = st.session_state.total_fraud
    st.metric(
        label="🚨 Fraud Detected",
        value=f"{fraud_count:,}",
        delta=f"{(fraud_count/max(st.session_state.total_transactions, 1)*100):.1f}%"
    )

with col3:
    if st.session_state.predictions:
        avg_latency = np.mean([p['latency_ms'] for p in st.session_state.predictions[-100:]])
        st.metric(
            label="⚡ Avg Latency",
            value=f"{avg_latency:.1f} ms",
            delta="P95 ready"
        )
    else:
        st.metric(label="⚡ Avg Latency", value="-- ms")

with col4:
    st.metric(
        label="🎯 Model Version",
        value="v1.0",
        delta="Active"
    )

st.divider()

# Tabs
tab1, tab2, tab3 = st.tabs(["📈 Real-Time Dashboard", "📋 Transaction Log", "📊 Analytics"])

with tab1:
    if len(st.session_state.predictions) > 0:
        df = pd.DataFrame(st.session_state.predictions[-100:])  # Last 100
        
        col_left, col_right = st.columns(2)
        
        with col_left:
            # Fraud probability over time
            st.subheader("🎯 Fraud Probability Timeline")
            fig = px.line(
                df,
                x='timestamp',
                y='fraud_probability',
                title='Fraud Probability Over Time',
                color_discrete_sequence=['#1f77b4']
            )
            fig.add_hline(y=0.5, line_dash="dash", line_color="red", 
                         annotation_text="Threshold")
            st.plotly_chart(fig, use_container_width=True)
            
            # Latency distribution
            st.subheader("⚡ Latency Distribution")
            fig = px.histogram(
                df,
                x='latency_ms',
                nbins=30,
                title='Response Time Distribution',
                color_discrete_sequence=['#2ca02c']
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col_right:
            # Fraud vs Legitimate
            st.subheader("🚨 Fraud Detection Results")
            fraud_counts = df['is_fraud'].value_counts()
            fig = go.Figure(data=[go.Pie(
                labels=['Legitimate', 'Fraud'],
                values=[
                    fraud_counts.get(False, 0),
                    fraud_counts.get(True, 0)
                ],
                hole=0.4,
                marker_colors=['#2ca02c', '#d62728']
            )])
            fig.update_layout(title='Transaction Classification')
            st.plotly_chart(fig, use_container_width=True)
            
            # Amount vs Probability scatter
            st.subheader("💰 Amount vs Fraud Risk")
            fig = px.scatter(
                df,
                x='amount',
                y='fraud_probability',
                color='is_fraud',
                size='anomaly_score',
                title='Transaction Amount vs Fraud Probability',
                color_discrete_map={True: '#d62728', False: '#2ca02c'},
                labels={'is_fraud': 'Fraud Detected'}
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("👆 Generate transactions using the sidebar controls or enable auto-generation!")

with tab2:
    st.subheader("📋 Recent Transactions")
    if st.session_state.predictions:
        df = pd.DataFrame(st.session_state.predictions[-50:])  # Last 50
        df_display = df[['timestamp', 'amount', 'fraud_probability', 'is_fraud', 'latency_ms']].copy()
        df_display['timestamp'] = df_display['timestamp'].dt.strftime('%H:%M:%S')
        df_display['fraud_probability'] = df_display['fraud_probability'].apply(lambda x: f"{x:.1%}")
        df_display['amount'] = df_display['amount'].apply(lambda x: f"${x:.2f}")
        df_display['latency_ms'] = df_display['latency_ms'].apply(lambda x: f"{x:.1f}ms")
        df_display['is_fraud'] = df_display['is_fraud'].apply(lambda x: "🚨 FRAUD" if x else "✅ OK")
        
        st.dataframe(
            df_display.sort_values('timestamp', ascending=False),
            use_container_width=True,
            height=400
        )
    else:
        st.info("No transactions yet. Start generating to see data!")

with tab3:
    st.subheader("📊 Statistical Analytics")
    
    if len(st.session_state.predictions) >= 10:
        df = pd.DataFrame(st.session_state.predictions)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Mean Fraud Probability", f"{df['fraud_probability'].mean():.1%}")
            st.metric("Max Fraud Probability", f"{df['fraud_probability'].max():.1%}")
            st.metric("Fraud Detection Rate", f"{(df['is_fraud'].sum() / len(df)):.1%}")
        
        with col2:
            st.metric("Mean Latency", f"{df['latency_ms'].mean():.2f} ms")
            st.metric("P95 Latency", f"{df['latency_ms'].quantile(0.95):.2f} ms")
            st.metric("Total Anomalies", f"{df['is_anomaly'].sum()}")
    else:
        st.info("Need at least 10 transactions for analytics")

# Auto-generate transactions
if auto_generate and api_healthy:
    placeholder = st.empty()
    
    with placeholder.container():
        st.info(f"🔄 Auto-generating {transactions_per_sec} transactions/sec...")
        
        for _ in range(transactions_per_sec):
            tx = generate_synthetic_transaction()
            result = call_inference_api(tx)
            
            if result:
                st.session_state.predictions.append({
                    'timestamp': datetime.now(),
                    'amount': tx['amount'],
                    **result
                })
                st.session_state.total_transactions += 1
                if result['is_fraud']:
                    st.session_state.total_fraud += 1
        
        time.sleep(1)
        st.rerun()

# Footer
st.divider()
st.caption("🛡️ Sentinel ML - Production Fraud Detection System | Powered by FastAPI + XGBoost + Isolation Forest")
