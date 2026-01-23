

import sqlite3
import os
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'sentinel.db')

def init_db():
    """Initialize the SQLite database and create tables."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Predictions Table
    # Added latency_ms for performance tracking
    c.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT,
            amount REAL,
            fraud_probability REAL,
            is_fraud BOOLEAN,
            is_anomaly BOOLEAN,
            anomaly_score REAL,
            processing_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            latency_ms REAL
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"📦 Database initialized at: {DB_PATH}")

def insert_prediction(transaction, result, latency_ms):
    """
    Insert a prediction result into the database.
    
    Args:
        transaction (dict): The original transaction data
        result (dict): The prediction result from predictor
        latency_ms (float): End-to-end processing latency
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO predictions (
            transaction_id, amount, fraud_probability, 
            is_fraud, is_anomaly, anomaly_score, latency_ms
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        str(transaction.get('transaction_id', '')),
        float(transaction.get('amount', 0.0)),
        float(result['fraud_probability']),
        bool(result['is_fraud']),
        bool(result['is_anomaly']),
        float(result['anomaly_score']),
        float(latency_ms)
    ))
    
    conn.commit()
    conn.close()

def get_recent_predictions(limit=100):
    """Retrieve recent predictions for dashboard."""
    conn = sqlite3.connect(DB_PATH)
    # Return row objects for easier access
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute('''
        SELECT * FROM predictions 
        ORDER BY id DESC 
        LIMIT ?
    ''', (limit,))
    
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    return rows

def get_stats():
    """Get aggregated statistics."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN is_fraud = 1 THEN 1 ELSE 0 END) as fraud_count,
            AVG(latency_ms) as avg_latency
        FROM predictions
    ''')
    
    result = c.fetchone()
    conn.close()
    
    return {
        'total': result[0] if result[0] else 0,
        'fraud': result[1] if result[1] else 0,
        'avg_latency': result[2] if result[2] else 0.0
    }

if __name__ == "__main__":
    init_db()
