"""
Quick test script for inference API
Run from project root: python scripts/test_api_local.py
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.model.predictor import FraudPredictor
import json

print("=" * 60)
print("Testing Inference API Components")
print("=" * 60)

# Test 1: Load ML models
print("\n1. Loading ML models...")
try:
    predictor = FraudPredictor()
    print("   [OK] Models loaded successfully")
except Exception as e:
    print(f"   [FAIL] Failed: {e}")
    sys.exit(1)

# Test 2: Run inference
print("\n2. Testing inference...")
test_transaction = {
    'time': 12345.0,
    'amount': 150.50,
    **{f'V{i}': float(i * 0.1) for i in range(1, 29)}
}

try:
    result = predictor.predict(test_transaction)
    print(f"   [OK] Prediction completed")
    print(f"      Fraud Probability: {result['fraud_probability']:.4f}")
    print(f"      Is Fraud: {result['is_fraud']}")
    print(f"      Anomaly Score: {result['anomaly_score']:.4f}")
except Exception as e:
    print(f"   [FAIL] Failed: {e}")
    sys.exit(1)

# Test 3: Check API can import
print("\n3. Checking FastAPI imports...")
try:
    from fastapi import FastAPI
    from prometheus_client import Counter
    print("   [OK] All API dependencies available")
except Exception as e:
    print(f"   ❌ Missing dependency: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("[SUCCESS] All component tests passed!")
print("=" * 60)
print("\nReady for containerization and deployment.")
print("\nNext steps:")
print("  1. Build Docker/Podman images")
print("  2. Test containers locally")
print("  3. Deploy to Kubernetes")
