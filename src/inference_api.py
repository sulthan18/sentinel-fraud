"""
Sentinel Inference API - FastAPI ML Serving Layer

Production-grade REST API for fraud detection inference.
Designed for Kubernetes deployment with observability.
"""

import os
import time
from typing import Dict, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

from src.model.predictor import FraudPredictor


# Prometheus Metrics
PREDICTION_COUNTER = Counter(
    'sentinel_predictions_total',
    'Total number of predictions made',
    ['result']  # fraud/legitimate
)

PREDICTION_LATENCY = Histogram(
    'sentinel_prediction_latency_seconds',
    'Latency of prediction requests',
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
)

ERROR_COUNTER = Counter(
    'sentinel_errors_total',
    'Total number of errors',
    ['type']
)

MODEL_LOADED = Gauge(
    'sentinel_model_loaded',
    'Whether the model is loaded (1) or not (0)'
)


# Request/Response Models
class Transaction(BaseModel):
    """Single transaction for inference"""
    time: float = Field(..., description="Transaction timestamp")
    amount: float = Field(..., ge=0, description="Transaction amount")
    V1: float = 0.0
    V2: float = 0.0
    V3: float = 0.0
    V4: float = 0.0
    V5: float = 0.0
    V6: float = 0.0
    V7: float = 0.0
    V8: float = 0.0
    V9: float = 0.0
    V10: float = 0.0
    V11: float = 0.0
    V12: float = 0.0
    V13: float = 0.0
    V14: float = 0.0
    V15: float = 0.0
    V16: float = 0.0
    V17: float = 0.0
    V18: float = 0.0
    V19: float = 0.0
    V20: float = 0.0
    V21: float = 0.0
    V22: float = 0.0
    V23: float = 0.0
    V24: float = 0.0
    V25: float = 0.0
    V26: float = 0.0
    V27: float = 0.0
    V28: float = 0.0

    class Config:
        json_schema_extra = {
            "example": {
                "time": 12345.0,
                "amount": 150.50,
                "V1": -1.3598071336738,
                "V2": -0.0727811733098497,
                "V3": 2.53634673796914,
                "V4": 1.37815522427443,
                "V5": -0.338320769942518
                # ... truncated for brevity
            }
        }


class PredictionResponse(BaseModel):
    """Prediction result"""
    transaction_id: Optional[str] = None
    fraud_probability: float = Field(..., ge=0, le=1)
    is_fraud: bool
    anomaly_score: float
    is_anomaly: bool
    latency_ms: float
    model_version: str = "v1.0"


class BatchPredictionRequest(BaseModel):
    """Batch of transactions"""
    transactions: List[Transaction]


class BatchPredictionResponse(BaseModel):
    """Batch prediction results"""
    predictions: List[PredictionResponse]
    total_processed: int
    total_fraud: int
    avg_latency_ms: float


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    model_loaded: bool
    version: str


# Global predictor instance
predictor: Optional[FraudPredictor] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model on startup, cleanup on shutdown"""
    global predictor
    try:
        print("[INFO] Loading ML models...")
        predictor = FraudPredictor()
        MODEL_LOADED.set(1)
        print("[OK] Models loaded successfully")
    except Exception as e:
        print(f"[ERROR] Failed to load models: {e}")
        MODEL_LOADED.set(0)
        raise
    
    yield
    
    # Cleanup
    print("[INFO] Shutting down...")
    MODEL_LOADED.set(0)


# Initialize FastAPI
app = FastAPI(
    title="Sentinel Fraud Detection API",
    description="Production ML inference service for real-time fraud detection",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint for Kubernetes probes.
    Returns model loading status.
    """
    return HealthResponse(
        status="healthy" if predictor is not None else "unhealthy",
        model_loaded=predictor is not None,
        version="1.0.0"
    )


@app.get("/metrics", tags=["Observability"])
async def metrics():
    """
    Prometheus metrics endpoint.
    Exposes custom ML metrics for monitoring.
    """
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/predict", response_model=PredictionResponse, tags=["Inference"])
async def predict(transaction: Transaction):
    """
    Single transaction fraud prediction.
    
    Returns fraud probability, classification, and anomaly detection results.
    """
    if predictor is None:
        ERROR_COUNTER.labels(type='model_not_loaded').inc()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded"
        )
    
    start_time = time.time()
    
    try:
        # Convert Pydantic model to dict for predictor
        tx_dict = transaction.model_dump()
        
        # Run inference
        result = predictor.predict(tx_dict)
        
        # Calculate latency
        latency = (time.time() - start_time) * 1000  # ms
        
        # Update metrics
        PREDICTION_LATENCY.observe(time.time() - start_time)
        PREDICTION_COUNTER.labels(
            result='fraud' if result['is_fraud'] else 'legitimate'
        ).inc()
        
        return PredictionResponse(
            fraud_probability=result['fraud_probability'],
            is_fraud=result['is_fraud'],
            anomaly_score=result['anomaly_score'],
            is_anomaly=result['is_anomaly'],
            latency_ms=latency
        )
        
    except Exception as e:
        ERROR_COUNTER.labels(type='prediction_error').inc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


@app.post("/batch_predict", response_model=BatchPredictionResponse, tags=["Inference"])
async def batch_predict(request: BatchPredictionRequest):
    """
    Batch prediction endpoint for multiple transactions.
    More efficient for bulk scoring.
    """
    if predictor is None:
        ERROR_COUNTER.labels(type='model_not_loaded').inc()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded"
        )
    
    start_time = time.time()
    predictions = []
    fraud_count = 0
    
    try:
        for tx in request.transactions:
            tx_start = time.time()
            tx_dict = tx.model_dump()
            result = predictor.predict(tx_dict)
            tx_latency = (time.time() - tx_start) * 1000
            
            pred = PredictionResponse(
                fraud_probability=result['fraud_probability'],
                is_fraud=result['is_fraud'],
                anomaly_score=result['anomaly_score'],
                is_anomaly=result['is_anomaly'],
                latency_ms=tx_latency
            )
            predictions.append(pred)
            
            if result['is_fraud']:
                fraud_count += 1
            
            # Update metrics
            PREDICTION_COUNTER.labels(
                result='fraud' if result['is_fraud'] else 'legitimate'
            ).inc()
        
        total_latency = (time.time() - start_time) * 1000
        avg_latency = total_latency / len(request.transactions)
        
        PREDICTION_LATENCY.observe(time.time() - start_time)
        
        return BatchPredictionResponse(
            predictions=predictions,
            total_processed=len(predictions),
            total_fraud=fraud_count,
            avg_latency_ms=avg_latency
        )
        
    except Exception as e:
        ERROR_COUNTER.labels(type='batch_prediction_error').inc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch prediction failed: {str(e)}"
        )


@app.get("/", tags=["Info"])
async def root():
    """API information"""
    return {
        "service": "Sentinel Fraud Detection API",
        "version": "1.0.0",
        "description": "Production ML inference service",
        "endpoints": {
            "health": "/health",
            "metrics": "/metrics",
            "predict": "/predict",
            "batch_predict": "/batch_predict",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "src.inference_api:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
