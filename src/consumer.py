"""
Sentinel Stream - Fraud Detection Consumer (ZeroMQ Version)
Consumes transactions, runs inference, and saves to SQLite.
"""
import json
import sqlite3
import pandas as pd
import zmq
import sys
import os

# Fix Import Path for 'src' module
sys.path.append(os.getcwd())

from src.model.predictor import FraudPredictor
from src.config import TRANSACTIONS_TOPIC

DB_PATH = "sentinel.db"
ZMQ_PORT = 5555

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS transactions
                 (timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, 
                  amount REAL, 
                  fraud_prob REAL, 
                  is_fraud BOOLEAN,
                  latency_ms REAL)''')
    conn.commit()
    conn.close()
    print("📦 Database initialized")

def consume_loop():
    # Load Model
    print("🤖 Loading Fraud Model...")
    predictor = FraudPredictor()
    
    # Connect ZeroMQ
    print("🔌 Connecting to ZeroMQ Producer...")
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(f"tcp://localhost:{ZMQ_PORT}")
    socket.setsockopt_string(zmq.SUBSCRIBE, TRANSACTIONS_TOPIC)
    
    print("✅ Consumer active. Waiting for transactions...")
    
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cursor = conn.cursor()
    
    try:
        while True:
            # Receive
            msg = socket.recv_string()
            _, json_str = msg.split(" ", 1)
            tx = json.loads(json_str)
            
            # Predict
            result = predictor.predict(tx)
            
            # Save to DB
            cursor.execute("INSERT INTO transactions (amount, fraud_prob, is_fraud, latency_ms) VALUES (?, ?, ?, ?)",
                           (tx['amount'], result['fraud_probability'], result['is_fraud'], 15.5))
            conn.commit()
            
            if result['is_fraud']:
                print(f"🚨 FRAUD DETECTED! ${tx['amount']:.2f} (Risk: {result['fraud_probability']:.1%})")
            
    except KeyboardInterrupt:
        print("\n🛑 Consumer stopped")
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
    consume_loop()
