"""
Sentinel Stream - Transaction Producer (ZeroMQ Version)
Generates synthetic transaction data and sends to ZeroMQ (No Docker required).
"""
import json
import time
import random
import zmq
import sys
import os

# Fix Import Path
sys.path.append(os.getcwd())

from src.config import TRANSACTIONS_TOPIC

# ZeroMQ Config
ZMQ_PORT = 5555

def create_producer():
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind(f"tcp://*:{ZMQ_PORT}")
    print(f"✅ Bound to ZeroMQ port {ZMQ_PORT}")
    return socket

def generate_transaction():
    """Generate fake transaction data"""
    is_fraud = random.random() < 0.1
    
    if is_fraud:
        amount = random.uniform(1000, 5000)
        hour = random.choice([0, 1, 2, 3, 23])
    else:
        amount = random.uniform(10, 500)
        hour = random.choice(range(8, 22))
        
    tx = {
        "time": hour * 3600 + random.randint(0, 3600),
        "amount": round(amount, 2)
    }
    
    # V1-V28 features
    for i in range(1, 29):
        tx[f"V{i}"] = random.gauss(0, 3 if is_fraud else 1)
        
    return tx

def produce_loop(speed=0.01): # Fast 100 tx/sec
    producer = create_producer()
    print(f"🚀 Producer started! emitting events...")
    
    try:
        count = 0
        while True:
            tx = generate_transaction()
            producer.send_string(f"{TRANSACTIONS_TOPIC} {json.dumps(tx)}")
            count += 1
            if count % 100 == 0:
                print(f"Sent {count} transactions...", end='\r')
            time.sleep(speed)
    except KeyboardInterrupt:
        print("\n🛑 Producer stopped")

if __name__ == "__main__":
    produce_loop()
