"""
Sentinel Commander - Streaming Dashboard (SQLite Edition)
Modern UI reading from real-time Database stream.
"""
import streamlit as st
import pandas as pd
import sqlite3
import time
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Sentinel Commander", page_icon="🦅", layout="wide", initial_sidebar_state="collapsed")

# --- 🎨 MODERN UI STYLING (Same as v3.0) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }
    .stApp { background-color: #050509; color: white; }
    
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 16px;
        backdrop-filter: blur(10px);
    }
    
    .hero-header {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #fff 30%, #6366f1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
</style>
""", unsafe_allow_html=True)

DB_PATH = "sentinel.db"

def load_data():
    try:
        conn = sqlite3.connect(DB_PATH)
        # Get last 2000 transactions
        df = pd.read_sql_query("SELECT * FROM transactions ORDER BY timestamp DESC LIMIT 2000", conn)
        conn.close()
        # Convert timestamp
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except:
        return pd.DataFrame()

# AUTO REFRESH LOGIC
if 'last_run' not in st.session_state:
    st.session_state.last_run = time.time()

# Header
c1, c2 = st.columns([3, 1])
with c1:
    st.markdown('<div class="hero-header">SENTINEL STREAM</div>', unsafe_allow_html=True)
    st.caption("Architecture: Producer ➔ ZeroMQ ➔ Consumer ➔ SQLite ➔ Dashboard")
with c2:
    st.markdown("""
    <div style="background: rgba(16, 185, 129, 0.2); border: 1px solid #10b981; color: #10b981; padding: 10px; border-radius: 12px; text-align: center; font-weight: 600;">
        ● STREAMING LIVE
    </div>
    """, unsafe_allow_html=True)

# LOAD DATA
df = load_data()

if not df.empty:
    m1, m2, m3, m4 = st.columns(4)
    
    total = len(df)
    fraud = df['is_fraud'].sum()
    rate = (fraud/total)*100
    avg_lat = df['latency_ms'].mean() if 'latency_ms' in df.columns else 0
    
    with m1: st.metric("Buffer Size", f"{total}", "Rows")
    with m2: st.metric("Fraud Detected", f"{fraud}", f"{rate:.1f}%")
    with m3: st.metric("Live Latency", f"{avg_lat:.1f}ms")
    with m4: st.metric("Status", "ACTIVE", "Consumer Running")
    
    # CHARTS
    tab1, tab2 = st.tabs(["🌩️ Live Monitor", "🚨 Fraud List"])
    
    with tab1:
        col_chart1, col_chart2 = st.columns([2, 1])
        with col_chart1:
            fig = px.scatter(df, x='timestamp', y='amount', color='is_fraud',
                             color_discrete_map={1: '#ef4444', 0: '#6366f1'},
                             size='amount', size_max=15, title="Transaction Stream")
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#cbd5e1")
            st.plotly_chart(fig, use_container_width=True)
            
        with col_chart2:
            fig2 = px.histogram(df, x='fraud_prob', nbins=20, title="Risk Distribution",
                                color_discrete_sequence=['#8b5cf6'])
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#cbd5e1")
            st.plotly_chart(fig2, use_container_width=True)
            
    with tab2:
        st.dataframe(df[df['is_fraud']==1].head(100), use_container_width=True)

else:
    st.info("Waiting for Consumer data... Run `python src/consumer.py`")

# Auto-rerun for streaming effect
time.sleep(1)
st.rerun()
