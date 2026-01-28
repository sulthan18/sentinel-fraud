# Load Testing with Locust

Stress test the Sentinel inference API to validate scalability and HPA behavior.

## Requirements

```bash
pip install locust numpy
```

## Running Load Tests

### 1. Local Testing (before K8s deployment)

Start the inference API locally:
```bash
python src/inference_api.py
```

Run Locust:
```bash
locust -f loadtest/locustfile.py --host=http://localhost:8000
```

Open browser: http://localhost:8089

### 2. Kubernetes Load Test

Port-forward the inference service:
```bash
kubectl port-forward svc/sentinel-ml-inference 8000:8000
```

Run headless load test:
```bash
locust -f loadtest/locustfile.py \
  --host=http://localhost:8000 \
  --headless \
  --users 100 \
  --spawn-rate 10 \
  --run-time 5m
```

### 3. High-Volume Test (10,000+ req/s target)

**⚠️ Run this only in K8s with HPA enabled**

```bash
locust -f loadtest/locustfile.py \
  --host=http://localhost:8000 \
  --headless \
  --users 500 \
  --spawn-rate 50 \
  --run-time 10m
```

## Test Scenarios

### Light Load (Baseline)
- **Users**: 10
- **Spawn Rate**: 2/sec
- **Duration**: 2 minutes
- **Expected**: Stable latency, no scaling

### Medium Load (Trigger HPA)
- **Users**: 100
- **Spawn Rate**: 10/sec
- **Duration**: 5 minutes
- **Expected**: CPU rises → HPA adds pods → latency stabilizes

### Heavy Load (Stress Test)
- **Users**: 500
- **Spawn Rate**: 50/sec
- **Duration**: 10 minutes
- **Expected**: Rapid scaling to max replicas, sustained high throughput

## Monitoring During Load Test

Open these in separate terminals/tabs:

**1. Watch HPA:**
```bash
kubectl get hpa -w
```

**2. Watch Pods:**
```bash
kubectl get pods -l app=sentinel-ml-inference -w
```

**3. Grafana Dashboard:**
```bash
kubectl port-forward svc/grafana 3000:3000 -n monitoring
# Open http://localhost:3000
```

**4. Prometheus:**
```bash
kubectl port-forward svc/prometheus 9090:9090 -n monitoring
# Check: sentinel_predictions_total
```

## Success Criteria

✅ **Throughput**: Sustain 10,000+ req/s  
✅ **Latency**: P95 < 100ms under load  
✅ **Scaling**: HPA scales from 2 → 10 pods  
✅ **Error Rate**: < 1% failures  
✅ **Stability**: No pod crashes or OOM kills

## Recording the Test

To create a demo video:

1. Start screen recording tool (OBS, Windows Game Bar)
2. Split screen: Grafana dashboard + terminal with HPA watch
3. Start load test
4. Narrate: "Watch CPU increase... HPA adding pods... Latency stable..."
5. Stop after 5-10 minutes
6. Show final metrics in Locust summary
