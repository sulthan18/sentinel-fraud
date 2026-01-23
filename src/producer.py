"""
SentinelStream Producer
Real-time transaction streaming from CSV to Kafka/Redpanda

Features:
- FR-01: Replay capability (reads CSV row-by-row)
- FR-02: Rate limiting (configurable tx/sec)
- FR-03: JSON serialization
- FR-05: Network agnostic (Local/Cloud switch)
"""

import json
import time
import pandas as pd
from kafka import KafkaProducer
from kafka.errors import KafkaError
from config import get_kafka_config, TOPIC_NAME, RATE_LIMIT, CSV_PATH, print_config


def create_producer():
    """Initialize Kafka producer with current configuration."""
    kafka_config = get_kafka_config()
    
    producer = KafkaProducer(
        **kafka_config,
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        key_serializer=lambda k: k.encode('utf-8') if k else None,
        acks='all',
        retries=3,
    )
    return producer


def stream_transactions(producer, limit=None):
    """
    Stream transactions from CSV to Kafka topic.
    
    Args:
        producer: KafkaProducer instance
        limit: Optional max number of transactions to send (None = all)
    """
    print(f"\n📂 Loading dataset: {CSV_PATH}")
    
    # Read CSV in chunks for memory efficiency
    chunk_size = 10000
    total_sent = 0
    start_time = time.time()
    
    for chunk in pd.read_csv(CSV_PATH, chunksize=chunk_size):
        for idx, row in chunk.iterrows():
            if limit and total_sent >= limit:
                break
            
            # Create transaction record
            transaction = {
                "transaction_id": f"TX-{idx:08d}",
                "timestamp": time.time(),
                "time": float(row['Time']),
                "amount": float(row['Amount']),
                "class": int(row['Class']),  # 0 = legit, 1 = fraud
                # PCA features V1-V28
                **{f"V{i}": float(row[f'V{i}']) for i in range(1, 29)}
            }
            
            # Send to Kafka
            try:
                future = producer.send(
                    TOPIC_NAME,
                    key=transaction["transaction_id"],
                    value=transaction
                )
                # Don't block on every message, just track
                total_sent += 1
                
                # Progress indicator
                if total_sent % 100 == 0:
                    elapsed = time.time() - start_time
                    rate = total_sent / elapsed if elapsed > 0 else 0
                    fraud_label = "🚨 FRAUD" if transaction["class"] == 1 else "✅ Legit"
                    print(f"\r📤 Sent: {total_sent:,} | Rate: {rate:.1f} tx/s | Last: {fraud_label}", end="")
                
                # Rate limiting
                if RATE_LIMIT > 0:
                    time.sleep(1.0 / RATE_LIMIT)
                    
            except KafkaError as e:
                print(f"\n❌ Error sending message: {e}")
                
        if limit and total_sent >= limit:
            break
    
    # Flush remaining messages
    producer.flush()
    
    elapsed = time.time() - start_time
    print(f"\n\n✅ Streaming complete!")
    print(f"   Total sent: {total_sent:,} transactions")
    print(f"   Duration: {elapsed:.1f} seconds")
    print(f"   Avg rate: {total_sent/elapsed:.1f} tx/s")


def main():
    """Main entry point."""
    print_config()
    
    print("\n🔌 Connecting to broker...")
    try:
        producer = create_producer()
        print("✅ Connected successfully!\n")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n💡 Tip: Make sure Redpanda is running:")
        print("   wsl -d podman-machine-default podman ps")
        return
    
    try:
        # Stream with rate limiting (use limit=10000 for scale test)
        stream_transactions(producer, limit=10000)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    finally:
        producer.close()
        print("🔌 Producer closed")


if __name__ == "__main__":
    main()
