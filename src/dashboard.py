
import time
import pandas as pd
import plotly.express as px
import streamlit as st

# Import modules
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database import init_db, get_stats, get_recent_predictions

# Page Config
st.set_page_config(
    page_title="SentinelStream | Fraud Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .reportview-container {
        background: #0e1117;
    }
    .stDataFrame {
        border: 1px solid #41424b;
    }
</style>
""", unsafe_allow_html=True)

# Initialize DB
init_db()

# --- Sidebar ---
st.sidebar.title("🛡️ SentinelStream")
st.sidebar.markdown("---")

# Refresh rate
refresh_rate = st.sidebar.slider("Refresh Rate (seconds)", 1, 10, 2)
st.sidebar.markdown("---")
st.sidebar.info("💡 Consumer must be running separately to populate data.")

# --- Main Layout ---
st.title("Real-Time Transaction Monitor")

col1, col2, col3, col4, col5 = st.columns(5)

# Fetch latest stats from DB
stats = get_stats()
total = stats['total']
fraud = stats['fraud']
avg_latency = stats['avg_latency']
rate = (fraud / total * 100) if total > 0 else 0

# Display metrics
col1.metric("Processed", f"{total:,}")
col2.metric("Fraud Detected", f"{fraud:,}", delta_color="inverse")
col3.metric("Fraud Rate", f"{rate:.2f}%")
col4.metric("Avg Latency", f"{avg_latency:.2f} ms")
col5.metric("System Status", "🟢 ACTIVE")

# Placeholders for charts
row2_col1, row2_col2 = st.columns([2, 1])

with row2_col1:
    st.subheader("Live Transaction Feed")
    
    # Fetch recent rows for Table
    rows = get_recent_predictions(limit=20)
    if rows:
        df = pd.DataFrame(rows)
        
        # Format for display
        df['Time'] = pd.to_datetime(df['processing_time']).dt.strftime('%H:%M:%S')
        df['Amount'] = df['amount'].apply(lambda x: f"${x:.2f}")
        df['Prob'] = df['fraud_probability'].apply(lambda x: f"{x:.4f}")
        df['Latency'] = df['latency_ms'].apply(lambda x: f"{x:.1f}ms")
        df['Status'] = df['is_fraud'].apply(lambda x: '🚨 FRAUD' if x else '✅ OK')
        
        st.dataframe(
            df[['Time', 'transaction_id', 'Amount', 'Status', 'Prob', 'Latency']], 
            height=400,
            hide_index=True
        )
    else:
        st.info("No transactions yet. Make sure the consumer is running.")

with row2_col2:
    st.subheader("System Performance")
    
    # Update Chart (Latency)
    chart_rows = get_recent_predictions(limit=50)
    if chart_rows:
        df_chart = pd.DataFrame(chart_rows)
        # Reverse to show chronological order left-to-right
        df_chart = df_chart.iloc[::-1].reset_index(drop=True)
        
        fig = px.line(
            df_chart, 
            y='latency_ms', 
            title="Inference Latency (ms)",
            markers=True
        )
        fig.update_layout(yaxis_title="Latency (ms)", xaxis_title="Transaction Stream")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Waiting for data...")

# Auto-refresh
time.sleep(refresh_rate)
st.rerun()

