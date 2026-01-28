"""
Locust Load Test for Sentinel Inference API

Simulates high-volume inference traffic to test:
- API scalability
- HPA behavior
- Latency under load
- Model throughput
"""

import random
import json
from locust import HttpUser, task, between, events
import numpy as np


class FraudInferenceUser(HttpUser):
    """
    Simulates a user making fraud detection inference requests.
    """
    
    # Wait time between requests (in seconds)
    wait_time = between(0.1, 0.5)
    
    def on_start(self):
        """Initialize - check API health"""
        response = self.client.get("/health")
        if response.status_code != 200:
            print(f"⚠️  API health check failed: {response.status_code}")
    
    def generate_transaction(self):
        """
        Generate a synthetic transaction.
        Mimics the distribution of the Credit Card Fraud dataset.
        """
        # Random PCA components (V1-V28)
        v_features = {f'V{i}': np.random.randn() for i in range(1, 29)}
        
        # Transaction amount (log-normal distribution)
        amount = max(1.0, np.random.lognormal(mean=3.5, sigma=1.5))
        
        # Timestamp
        time = random.randint(0, 172800)  # 48 hours in seconds
        
        return {
            'time': time,
            'amount': round(amount, 2),
            **v_features
        }
    
    @task(10)
    def predict_single(self):
        """
        Single transaction prediction (most common use case).
        Weight: 10 (executed 10x more than batch)
        """
        transaction = self.generate_transaction()
        
        with self.client.post(
            "/predict",
            json=transaction,
            catch_response=True,
            name="/predict [single]"
        ) as response:
            if response.status_code == 200:
                result = response.json()
                # Validate response structure
                if 'fraud_probability' in result and 'is_fraud' in result:
                    response.success()
                else:
                    response.failure("Invalid response structure")
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(1)
    def predict_batch(self):
        """
        Batch prediction (less frequent, but tests bulk processing).
        Weight: 1
        """
        batch_size = random.randint(5, 20)
        transactions = [self.generate_transaction() for _ in range(batch_size)]
        
        with self.client.post(
            "/batch_predict",
            json={"transactions": transactions},
            catch_response=True,
            name=f"/batch_predict [size={batch_size}]"
        ) as response:
            if response.status_code == 200:
                result = response.json()
                if result.get('total_processed') == batch_size:
                    response.success()
                else:
                    response.failure("Incomplete batch processing")
            else:
                response.failure(f"HTTP {response.status_code}")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Print message when load test starts"""
    print("\n" + "="*60)
    print("🚀 SENTINEL INFERENCE LOAD TEST STARTED")
    print("="*60 + "\n")
    print(f"Host: {environment.host}")
    print(f"Users: Ramping up to target")
    print(f"Scenario: Mixed single + batch inference\n")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Print summary when load test completes"""
    print("\n" + "="*60)
    print("✅ LOAD TEST COMPLETED")
    print("="*60 + "\n")
    
    stats = environment.stats
    print(f"Total Requests: {stats.total.num_requests}")
    print(f"Total Failures: {stats.total.num_failures}")
    print(f"Avg Response Time: {stats.total.avg_response_time:.2f}ms")
    print(f"P50 Latency: {stats.total.get_response_time_percentile(0.5):.2f}ms")
    print(f"P95 Latency: {stats.total.get_response_time_percentile(0.95):.2f}ms")
    print(f"P99 Latency: {stats.total.get_response_time_percentile(0.99):.2f}ms")
    print(f"RPS: {stats.total.current_rps:.2f}\n")
