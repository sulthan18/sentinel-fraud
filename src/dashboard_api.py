"""
Sentinel ML - Commander Dashboard
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

# Page config - MUST be the first Streamlit command
st.set_page_config(
    page_title="Sentinel Commander",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 🎨 PREMIUM UI STYLING ---
st.markdown("""
<style>
    /* Dark Theme & Glassmorphism */
    .stApp {
        background-color: #0e1117;
    }
    
    /* Metrics Cards */
    div[data-testid="metric-container"] {
        background-color: #1a1c24;
        border: 1px solid #2d2f36;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        border-color: #4f46e5;
    }
    
    /* Header */
    .main-header {
        font-family: 'Inter', sans-serif;
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #4f46e5 0%, #06b6d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        letter-spacing: -1px;
    }
    
    .status-badge {
        background-color: #059669;
        color: white;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 600;
        vertical-align: middle;
    }
    
    .status-badge-offline {
        background-color: #dc2626;
        color: white;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 600;
        vertical-align: middle;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #1a1c24;
        padding: 8px;
        border-radius: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 5px;
        color: #9ca3af;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4f46e5;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# --- 🛠️ HELPER FUNCTIONS ---

def generate_synthetic_transaction():
    """Generate a single optimized synthetic transaction"""
    is_fraud_sim = random.random() < 0.12  # slightly higher fraud rate for demo
    
    if is_fraud_sim:
        amount = random.uniform(500, 5000)
        hour = random.choice([1, 2, 3, 23, 0]) 
    else:
        amount = random.uniform(10, 500)
        hour = random.choice(range(8, 22))
    
    # Base transaction
    transaction = {
        "time": hour * 3600 + random.randint(0, 3600),
        "amount": round(amount, 2)
    }
    
    # V features
    for i in range(1, 29):
        # Optimized random generation (faster than gauss for simple mocks if needed, 
        # but keep gauss for model accuracy)
        if is_fraud_sim:
            transaction[f"V{i}"] = random.gauss(0, 4) if i in [3, 4, 10, 11, 12, 14, 17] else random.gauss(0, 1)
        else:
            transaction[f"V{i}"] = random.gauss(0, 1)
            
    return transaction

def call_inference_api(transaction):
    """Single API call"""
    try:
        response = requests.post(f"{API_URL}/predict", json=transaction, timeout=2)
        return response.json() if response.status_code == 200 else None
    except:
        return None

def call_batch_api(transactions):
    """🚀 HIGH SPEED BATCH CALL"""
    try:
        payload = {"transactions": transactions}
        response = requests.post(f"{API_URL}/batch_predict", json=payload, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Batch Error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Batch Connection Error: {e}")
        return None

def check_api_health():
    try:
        r = requests.get(f"{API_URL}/health", timeout=1)
        return r.status_code == 200
    except:
        return False

# --- 💾 SESSION STATE ---
if 'data' not in st.session_state:
    st.session_state.data = []
if 'total_count' not in st.session_state:
    st.session_state.total_count = 0 

# --- 📱 UI LAYOUT ---

# Top Bar Status
api_status = check_api_health()
status_html = f"""
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
    <div style="font-family: 'Inter'; font-weight: 600; color: #9ca3af;">🦅 SENTINEL COMMANDER v2.0</div>
    <div>
        <span class="{'status-badge' if api_status else 'status-badge-offline'}">
            {'● SYSTEM ONLINE' if api_status else '● SYSTEM OFFLINE'}
        </span>
    </div>
</div>
"""
st.markdown(status_html, unsafe_allow_html=True)

st.markdown('<div class="main-header">Fraud Detection Center</div>', unsafe_allow_html=True)

# 🚀 ACTION CENTER (Top Controls)
with st.container():
    c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
    
    with c1:
        st.markdown("### ⚡ Quick Actions")
        if st.button("🚀 Generate 10k Transactions (Batch)", type="primary", use_container_width=True):
            if not api_status:
                st.error("API Offline. Start uvicorn first!")
            else:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Generate 10 batches of 1000
                total_new = 0
                batch_size = 1000
                num_batches = 10
                
                start_time = time.time()
                
                for i in range(num_batches):
                    status_text.text(f"Generating Batch {i+1}/{num_batches}...")
                    
                    # 1. Create Data
                    batch_tx = [generate_synthetic_transaction() for _ in range(batch_size)]
                    
                    # 2. Call API
                    result = call_batch_api(batch_tx)
                    
                    if result:
                        predictions = result['predictions']
                        timestamp_now = datetime.now()
                        
                        # Add timestamps spread slightly for realism
                        new_rows = []
                        for idx, pred in enumerate(predictions):
                            # Add some random seconds so they don't all look identical time
                            t = timestamp_now - timedelta(seconds=random.randint(0, 300))
                            
                            row = {
                                'timestamp': t,
                                'amount': batch_tx[idx]['amount'],
                                'fraud_probability': pred['fraud_probability'],
                                'is_fraud': pred['is_fraud'],
                                'latency_ms': pred['latency_ms'],
                                'anomaly_score': pred['anomaly_score']
                            }
                            new_rows.append(row)
                        
                        st.session_state.data.extend(new_rows)
                        total_new += len(new_rows)
                    
                    progress_bar.progress((i + 1) / num_batches)
                
                end_time = time.time()
                duration = end_time - start_time
                st.session_state.total_count += total_new
                st.success(f"✅ Generated {total_new:,} transactions in {duration:.2f}s ({int(total_new/duration)} tx/s)")
                time.sleep(1)
                st.rerun()

    with c2:
        st.markdown("### 🧹 Management")
        if st.button("🗑️ Clear All Data", use_container_width=True):
            st.session_state.data = []
            st.session_state.total_count = 0
            st.rerun()

    with c3:
        st.markdown("### 🧪 Simulation")
        auto_run = st.toggle("Auto-Stream (10 tx/s)")
        if auto_run and api_status:
            # Generate small batch quickly
            tx = generate_synthetic_transaction()
            res = call_inference_api(tx)
            if res:
                st.session_state.data.append({
                    'timestamp': datetime.now(),
                    'amount': tx['amount'],
                    **res
                })
                st.session_state.total_count += 1
                time.sleep(0.1) # throttle slightly
                st.rerun()

# 📊 STATS OVERVIEW
df = pd.DataFrame(st.session_state.data)

if not df.empty:
    m1, m2, m3, m4 = st.columns(4)
    
    total_tx = len(df)
    fraud_tx = df['is_fraud'].sum()
    fraud_rate = (fraud_tx / total_tx) * 100
    avg_latency = df['latency_ms'].mean()
    total_volume = df['amount'].sum()
    
    with m1:
        st.metric("Total Traffic", f"{total_tx:,}", "Transactions")
    with m2:
        st.metric("Fraud Detected", f"{fraud_tx:,}", f"{fraud_rate:.2f}% Rate", delta_color="inverse")
    with m3:
        st.metric("System Latency", f"{avg_latency:.1f}ms", "P95 < 50ms")
    with m4:
        st.metric("Volume Processed", f"${total_volume:,.0f}", "USD")


st.divider()

# 📈 VISUALIZATION TABS
tab1, tab2, tab3 = st.tabs(["🌩️ Live Monitoring", "🔎 Investigation", "🔬 Model Metrics"])

with tab1:
    if not df.empty:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### 🌊 Transaction Velocity & Fraud Spikes")
            # Resample for cleaner graph if too many points
            chart_df = df.copy()
            chart_df = chart_df.sort_values('timestamp')
            
            # Simple line chart
            fig = px.scatter(chart_df, x='timestamp', y='amount', 
                             color='is_fraud', 
                             color_discrete_map={True: '#ef4444', False: '#10b981'},
                             title="Real-time Transaction Stream",
                             height=400)
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e5e7eb")
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.markdown("#### 🚨 Risk Distribution")
            fig2 = px.histogram(df, x='fraud_probability', nbins=20, 
                                title="Fraud Probability Histogram",
                                color_discrete_sequence=['#6366f1'])
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e5e7eb")
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Awaiting data stream... Click 'Generate 10k Transactions' to start.")

with tab2:
    if not df.empty:
        st.markdown("#### 📋 Suspicious Transactions (High Risk)")
        high_risk = df[df['fraud_probability'] > 0.5].sort_values('fraud_probability', ascending=False)
        
        st.dataframe(
            high_risk[['timestamp', 'amount', 'fraud_probability', 'is_fraud', 'anomaly_score']],
            use_container_width=True,
            column_config={
                "fraud_probability": st.column_config.ProgressColumn(
                    "Risk Score",
                    format="%.2f",
                    min_value=0,
                    max_value=1,
                ),
                "amount": st.column_config.NumberColumn(
                    "Amount",
                    format="$%.2f"
                )
            }
        )
    else:
        st.write("No high risk transactions found yet.")

with tab3:
    if not df.empty:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### ⚡ Latency Performance")
            fig_lat = px.line(df, y='latency_ms', title="API Response Time (ms)")
            fig_lat.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e5e7eb")
            st.plotly_chart(fig_lat, use_container_width=True)
        with c2:
            st.markdown("#### 🤖 Anomaly Scores")
            fig_anom = px.scatter(df, x='amount', y='anomaly_score', color='is_fraud',
                                  title="Isolation Forest Anomaly Map")
            fig_anom.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e5e7eb")
            st.plotly_chart(fig_anom, use_container_width=True)
