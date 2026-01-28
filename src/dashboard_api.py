"""
Sentinel ML - Commander Dashboard v3.0 (Ultra Modern)
High-performance fraud detection visualization
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
    page_title="Sentinel AI - Fraud Command",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 🎨 ULTRA MODERN UI STYLING (CSS) ---
st.markdown("""
<style>
    /* Global Theme */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .stApp {
        background-color: #050509; /* Deep Black/Blue */
        background-image: radial-gradient(circle at 50% 0%, #1a1a2e 0%, #050509 70%);
    }

    /* Metric Cards - Neon Glow */
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 16px;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        border-color: #6366f1;
        box-shadow: 0 10px 30px -10px rgba(99, 102, 241, 0.3);
    }
    
    /* Custom Header */
    .hero-header {
        font-size: 4rem;
        font-weight: 800;
        letter-spacing: -2px;
        background: linear-gradient(135deg, #fff 30%, #6366f1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .hero-sub {
        font-size: 1.2rem;
        color: #94a3b8;
        font-weight: 300;
        margin-bottom: 2rem;
    }

    /* Primary Button - Glowing */
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        border-radius: 12px;
        transition: all 0.3s;
        box-shadow: 0 4px 14px 0 rgba(124, 58, 237, 0.4);
        width: 100%;
    }
    div.stButton > button:first-child:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 20px 0 rgba(124, 58, 237, 0.6);
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        background: rgba(255,255,255,0.02);
        padding: 10px 20px;
        border-radius: 20px;
        margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        font-size: 1rem;
        font-weight: 500;
        color: #64748b;
    }
    .stTabs [aria-selected="true"] {
        color: #fff;
        background: rgba(99, 102, 241, 0.1);
        border-radius: 10px;
    }
    
    /* Plotly Chart Container */
    .chart-container {
        background: rgba(20, 20, 30, 0.6);
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.05);
        padding: 20px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- 🛠️ FUNCTIONS ---

def generate_synthetic_transaction():
    """Optimized data generation"""
    is_fraud_sim = random.random() < 0.15 
    if is_fraud_sim:
        amount = random.uniform(500, 5000)
        hour = random.choice([1, 2, 3, 23, 0]) 
    else:
        amount = random.uniform(10, 500)
        hour = random.choice(range(8, 22))
    
    transaction = {
        "time": hour * 3600 + random.randint(0, 3600),
        "amount": round(amount, 2)
    }
    
    # Generate V1-V28 just enough for the model
    # We simulate V features
    for i in range(1, 29):
        transaction[f"V{i}"] = random.gauss(0, 4) if is_fraud_sim and i in [3,4,10,12,14,17] else random.gauss(0, 1)
            
    return transaction

@st.cache_resource
def get_session():
    return requests.Session()

def call_batch_api_fast(transactions):
    """Call Batch API efficiently"""
    try:
        session = get_session()
        response = session.post(f"{API_URL}/batch_predict", json={"transactions": transactions}, timeout=30)
        return response.json() if response.status_code == 200 else None
    except:
        return None

def check_api_health():
    try:
        requests.get(f"{API_URL}/health", timeout=0.5)
        return True
    except:
        return False

# --- 💾 STATE ---
if 'data' not in st.session_state:
    st.session_state.data = []
if 'metrics' not in st.session_state:
    st.session_state.metrics = {'total': 0, 'fraud': 0, 'amount': 0, 'latency': 0}

# --- 🖥️ UI SYSTEM ---

# Header Section
col_head, col_status = st.columns([3, 1])
with col_head:
    st.markdown('<div class="hero-header">SENTINEL AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Autonomous Fraud Detection System • Kubernetes Cluster</div>', unsafe_allow_html=True)

with col_status:
    if check_api_health():
        st.markdown("""
        <div style="background: rgba(16, 185, 129, 0.2); border: 1px solid #10b981; color: #10b981; padding: 10px; border-radius: 12px; text-align: center; font-weight: 600;">
            ● SYSTEM ONLINE
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: rgba(239, 68, 68, 0.2); border: 1px solid #ef4444; color: #ef4444; padding: 10px; border-radius: 12px; text-align: center; font-weight: 600;">
            ● SYSTEM OFFLINE
        </div>
        """, unsafe_allow_html=True)

# 🚀 MAIN ACTION BUTTON (Full Width)
st.markdown("###") # spacer
if st.button("RUN SIMULATION - GENERATE 10,000 TRANSACTIONS 🚀"):
    with st.spinner("Processing High-Volume Data Stream..."):
        # 1. Generate Data Locally (Fast)
        batch_tx = [generate_synthetic_transaction() for _ in range(10000)]
        
        # 2. Call API Batch
        result = call_batch_api_fast(batch_tx)
        
        if result:
            predictions = result['predictions']
            
            # 3. Process Results
            new_data = []
            fraud_count = 0
            total_amount = 0
            latencies = []
            
            base_time = datetime.now()
            
            for idx, p in enumerate(predictions):
                # Spread timestamps for visualization
                t_offset = base_time - timedelta(minutes=random.randint(0, 15))
                new_data.append({
                    'timestamp': t_offset,
                    'amount': batch_tx[idx]['amount'],
                    'fraud_probability': p['fraud_probability'],
                    'is_fraud': p['is_fraud'],
                    'latency_ms': p['latency_ms'],
                    'anomaly_score': p['anomaly_score']
                })
                if p['is_fraud']: fraud_count += 1
                total_amount += batch_tx[idx]['amount']
                latencies.append(p['latency_ms'])
            
            # Update State
            st.session_state.data = new_data # Replace old data for demo clarity
            st.session_state.metrics = {
                'total': 10000,
                'fraud': fraud_count,
                'amount': total_amount,
                'latency': np.mean(latencies) if latencies else 0
            }
            st.rerun()
        else:
            st.error("Failed to connect to Inference API. Check if it's running!")

st.markdown("###") # spacer

# 📊 METRICS GRID
m = st.session_state.metrics
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("Total Transactions", f"{m['total']:,}", "Last Batch")
with c2:
    rate = (m['fraud'] / m['total'] * 100) if m['total'] > 0 else 0
    st.metric("Fraud Detected", f"{m['fraud']:,}", f"{rate:.2f}% Rate", delta_color="inverse")
with c3:
    st.metric("Processed Volume", f"${m['amount']/1000000:.2f}M", "USD")
with c4:
    st.metric("Avg Latency", f"{m['latency']:.2f}ms", "Real-time")

# 📉 VISUALIZATION
st.markdown("### System Analytics")

tab1, tab2 = st.tabs(["🌩️ Live Data Stream", "🔍 Forensics"])

df = pd.DataFrame(st.session_state.data)

with tab1:
    if not df.empty:
        col_chart1, col_chart2 = st.columns([2, 1])
        
        with col_chart1:
            # Time series Scatter
            fig = px.scatter(df, x='timestamp', y='amount', 
                             color='is_fraud',
                             color_discrete_map={True: '#ef4444', False: '#6366f1'},
                             size='amount',
                             size_max=15,
                             title="Transaction Velocity & Risk",
                             height=450)
            
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", 
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#cbd5e1",
                xaxis_showgrid=False,
                yaxis_showgrid=True,
                yaxis_gridcolor="rgba(255,255,255,0.05)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)
            
        with col_chart2:
            # Gauge Chart for Fraud Risk
            fraud_risk_score = rate # from metrics
            
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = fraud_risk_score,
                title = {'text': "Current Risk Level"},
                gauge = {
                    'axis': {'range': [None, 20]},
                    'bar': {'color': "#ef4444" if fraud_risk_score > 5 else "#6366f1"},
                    'steps': [
                        {'range': [0, 5], 'color': "rgba(16, 185, 129, 0.1)"},
                        {'range': [5, 20], 'color': "rgba(239, 68, 68, 0.1)"}],
                }
            ))
            fig_gauge.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#cbd5e1", height=300)
            st.plotly_chart(fig_gauge, use_container_width=True)
            
            # Latency Dist
            fig_hist = px.histogram(df, x='latency_ms', nbins=20, 
                                    title="Latency Distribution",
                                    color_discrete_sequence=['#10b981'])
            fig_hist.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", 
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#cbd5e1",
                height=150,
                margin=dict(l=20, r=20, t=30, b=20)
            )
            st.plotly_chart(fig_hist, use_container_width=True)

    else:
        st.info("System Ready. Press 'RUN SIMULATION' to visualize data.")

with tab2:
    if not df.empty:
        st.markdown("#### High Probability Fraud Alerts")
        # Filter high risk
        high_risk = df[df['fraud_probability'] > 0.8].sort_values('fraud_probability', ascending=False).head(100)
        
        st.dataframe(
            high_risk[['timestamp', 'amount', 'fraud_probability', 'is_fraud']],
            use_container_width=True,
            column_config={
                "fraud_probability": st.column_config.ProgressColumn(
                    "Confidence",
                    format="%.2f",
                    min_value=0,
                    max_value=1,
                ),
                "timestamp": st.column_config.DatetimeColumn("Detected At", format="D MMM HH:mm:ss"),
                "amount": st.column_config.NumberColumn("Value (USD)", format="$%.2f")
            }
        )
    else:
        st.write("No data available.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #475569; font-size: 0.8rem;">
    SECURE TERMINAL ACCESS • SENTINEL INC. • v3.0.0-build.2024
</div>
""", unsafe_allow_html=True)
