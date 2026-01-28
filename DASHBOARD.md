# Streamlit Dashboard - Quick Start

## 🚀 Running the Dashboard (No Docker Required!)

### Step 1: Install Dependencies
```powershell
pip install -r requirements-dashboard.txt
```

### Step 2: Start Inference API
```powershell
# Terminal 1
python -m uvicorn src.inference_api:app --port 8000
```

### Step 3: Start Dashboard
```powershell
# Terminal 2
streamlit run src/dashboard_api.py
```

**Browser will auto-open**: http://localhost:8501

---

## 🎯 Features

- ✅ **Real-time fraud detection** - Generate and analyze transactions
- ✅ **Interactive visualization** - Plotly charts with animations
- ✅ **Auto-generation mode** - Simulate traffic (1-10 tx/sec)
- ✅ **Manual testing** - Test specific transaction amounts
- ✅ **No Kafka needed** - Direct API consumption
- ✅ **No Docker needed** - Pure Python

---

## 📊 Dashboard Sections

### 1. Real-Time Dashboard
- Fraud probability timeline
- Latency distribution histogram
- Fraud vs Legitimate pie chart
- Amount vs Risk scatter plot

### 2. Transaction Log
- Last 50 transactions table
- Color-coded fraud alerts
- Sortable columns

### 3. Analytics
- Statistical metrics
- P95 latency tracking
- Fraud detection rates

---

## 🎮 How to Use

1. **Check API Status** (sidebar) - Should show "✅ API Connected"
2. **Enable Auto-generate** - Toggle checkbox in sidebar
3. **Adjust Speed** - Use slider (1-10 transactions/sec)
4. **Watch Metrics Update** - See real-time graphs populate
5. **Manual Test** - Enter custom amount and click "Test Transaction"

---

## 🎬 Demo Flow

**5-Minute Demo:**
1. Start API (30s)
2. Start Dashboard (30s)
3. Enable auto-generation at 5 tx/sec (3min)
4. Show fraud detection in action
5. Test high-amount transaction → see fraud flag
6. Show analytics tab with statistics

**Perfect for portfolio recording!**

---

## 🔧 Customization

### Change Transaction Generation Patterns

Edit `generate_synthetic_transaction()` in `dashboard_api.py`:
```python
# Adjust fraud probability (currently 10%)
is_fraud_sim = random.random() < 0.1

# Modify amount ranges
amount = random.uniform(500, 2000)  # For fraud
amount = random.uniform(10, 300)    # For normal
```

### Change API Endpoint

Edit at top of `dashboard_api.py`:
```python
API_URL = "http://localhost:8000"  # Change if needed
```

---

## ✅ Success Checklist

- [ ] API running on port 8000
- [ ] Dashboard opens in browser
- [ ] "API Connected" shows green
- [ ] Can generate transactions manually
- [ ] Auto-generation works
- [ ] Graphs update in real-time
- [ ] Fraud alerts appear for high amounts

---

## 🎯 Why This Works Without Docker

**Traditional Setup:**
- ❌ Producer → Kafka → Consumer → Dashboard
- ❌ Needs Redpanda container  
- ❌ Needs Podman/Docker

**New Setup:**
- ✅ Dashboard → Inference API
- ✅ Generates synthetic data in Python
- ✅ Direct HTTP calls
- ✅ Zero container dependencies
- ✅ Works immediately!

---

## 📸 Screenshots to Take

1. Dashboard overview with all 4 metrics
2. Real-time graphs showing fraud spike
3. Transaction log with fraud alerts
4. Analytics tab with statistics
5. Manual test showing fraud detection

---

Perfect for demos without infrastructure hassle! 🎉
