# SentinelStream Configuration
# Hybrid Architecture: Local (Redpanda) / Cloud (Upstash Kafka)

import os
from dotenv import load_dotenv

load_dotenv()

# Broker Mode: 'local' or 'cloud'
BROKER_MODE = os.getenv("BROKER_MODE", "local")

# Local Redpanda Configuration
LOCAL_BOOTSTRAP_SERVERS = os.getenv("LOCAL_BOOTSTRAP_SERVERS", "localhost:19092")

# Cloud (Upstash Kafka) Configuration
CLOUD_BOOTSTRAP_SERVERS = os.getenv("CLOUD_BOOTSTRAP_SERVERS", "")
CLOUD_SASL_USERNAME = os.getenv("CLOUD_SASL_USERNAME", "")
CLOUD_SASL_PASSWORD = os.getenv("CLOUD_SASL_PASSWORD", "")

# Topic Configuration
TOPIC_NAME = os.getenv("TOPIC_NAME", "transaction-stream")

# Producer Settings
RATE_LIMIT = int(os.getenv("RATE_LIMIT", "10"))  # Transactions per second
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "100"))  # Messages before flush

# Data Source
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
CSV_PATH = os.getenv("CSV_PATH", os.path.join(DATA_DIR, "creditcard.csv"))


def get_kafka_config():
    """Returns Kafka producer configuration based on BROKER_MODE."""
    if BROKER_MODE == "cloud":
        if not CLOUD_BOOTSTRAP_SERVERS:
            raise ValueError("CLOUD_BOOTSTRAP_SERVERS must be set for cloud mode")
        return {
            "bootstrap_servers": CLOUD_BOOTSTRAP_SERVERS,
            "security_protocol": "SASL_SSL",
            "sasl_mechanism": "SCRAM-SHA-256",
            "sasl_plain_username": CLOUD_SASL_USERNAME,
            "sasl_plain_password": CLOUD_SASL_PASSWORD,
        }
    else:
        return {
            "bootstrap_servers": LOCAL_BOOTSTRAP_SERVERS,
        }


def print_config():
    """Display current configuration."""
    print(f"╔══════════════════════════════════════════╗")
    print(f"║       SentinelStream Configuration       ║")
    print(f"╠══════════════════════════════════════════╣")
    print(f"║ Mode:       {BROKER_MODE.upper():>28} ║")
    if BROKER_MODE == "local":
        print(f"║ Broker:     {LOCAL_BOOTSTRAP_SERVERS:>28} ║")
    else:
        print(f"║ Broker:     {CLOUD_BOOTSTRAP_SERVERS[:28]:>28} ║")
    print(f"║ Topic:      {TOPIC_NAME:>28} ║")
    print(f"║ Rate Limit: {RATE_LIMIT:>25} tx/s ║")
    print(f"╚══════════════════════════════════════════╝")
