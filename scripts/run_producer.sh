#!/bin/bash
# Run producer inside the Podman container network

# Get container IP
# Put specific dist name if needed, or just use localhost if running inside the same VM
# But since we are likely running in 'Debian' or 'Ubuntu' (root@sulthanrafi18), 
# and Podman is in 'podman-machine-default', we need to reach across.
# The easiest way for WSL->WSL communication is often the bridge IP.
# Let's try to get it, or fallback.

CONTAINER_IP="172.21.6.242" # Fallback to known working IP
# Try to get dynamic if possible (this command might fail if not in the same dist)
# CONTAINER_IP=$(podman inspect sentinel-redpanda --format '{{.NetworkSettings.IPAddress}}' 2>/dev/null || echo "172.21.6.242")

# Set environment
export BROKER_MODE=local
export LOCAL_BOOTSTRAP_SERVERS="${CONTAINER_IP}:9092"
export TOPIC_NAME=transaction-stream
export RATE_LIMIT=10
export CSV_PATH=/mnt/c/Users/sulth/Sentinel/data/creditcard.csv

echo "🔌 Broker: $LOCAL_BOOTSTRAP_SERVERS"

# Run producer
cd /mnt/c/Users/sulth/Sentinel
pip3 install -q kafka-python pandas python-dotenv 2>/dev/null
python3 src/producer.py
