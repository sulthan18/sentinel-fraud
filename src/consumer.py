

import json
import time
from kafka import KafkaConsumer
from config import get_kafka_config, TOPIC_NAME
from model.predictor import FraudPredictor
from database import init_db, insert_prediction


def create_consumer():
    """Initialize Kafka consumer."""
    kafka_config = get_kafka_config()
    
    # Consumer specific config
    config = kafka_config.copy()
    config['auto_offset_reset'] = 'earliest'
    config['enable_auto_commit'] = True
    config['group_id'] = 'sentinel-dashboard-group'
    
    print(f"🔌 Connecting consumer to: {config['bootstrap_servers']}")
    
    return KafkaConsumer(
        TOPIC_NAME,
        **config,
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

def consume_loop(callback=None):
    """
    Main consumption loop. 
    
    Args:
        callback: Optional function to call with each result (for UI updates)
    """
    print("\n📦 Initializing Database...")
    init_db()

    print("\n🔍 Initializing Fraud Predictor...")
    predictor = FraudPredictor()
    
    print("📡 Starting Consumer Loop...")
    consumer = create_consumer()
    
    try:
        for message in consumer:
            # Start timer for latency metric
            start_time = time.perf_counter()
            
            transaction = message.value
            
            # Run Inference
            result = predictor.predict(transaction)
            
            # Calculate Latency
            latency_ms = (time.perf_counter() - start_time) * 1000
            
            # Persist to SQLite
            insert_prediction(transaction, result, latency_ms)
            
            # Log to console
            label = "🚨 FRAUD" if result['is_fraud'] else "✅ Legit"
            print(f"\r📥 Processed | {label} | Prob: {result['fraud_probability']:.4f} | Latency: {latency_ms:.2f}ms", end="")
            
            if callback:
                callback({**transaction, **result, 'latency_ms': latency_ms})
                
    except KeyboardInterrupt:
        print("\n🛑 Consumer stopped")
    finally:
        consumer.close()

if __name__ == "__main__":
    consume_loop()
