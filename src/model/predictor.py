"""
Model Predictor
Loads trained models and provides inference for transactions.
"""

import os
import joblib
import pandas as pd
import numpy as np

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODELS_DIR = os.path.join(BASE_DIR, 'models')


class FraudPredictor:
    def __init__(self):
        self.xgb_model = None
        self.iso_model = None
        self.scaler = None
        self.load_models()

    def load_models(self):
        """Load trained models from disk."""
        try:
            print(f"📂 Loading models from: {MODELS_DIR}")
            self.xgb_model = joblib.load(os.path.join(MODELS_DIR, 'xgboost_model.pkl'))
            self.iso_model = joblib.load(os.path.join(MODELS_DIR, 'isolation_forest.pkl'))
            self.scaler = joblib.load(os.path.join(MODELS_DIR, 'scaler.pkl'))
            print("✅ Models loaded successfully")
        except FileNotFoundError as e:
            print(f"❌ Error loading models: {e}")
            raise

    def preprocess(self, transaction):
        """
        Preprocess a single transaction dictionary for inference.
        Expected keys: V1-V28, Amount, Time
        """
        # Normalize keys (producer sends lowercase, model trained on TitleCase)
        # Create a new dict with correct casing
        normalized_tx = {
            'Time': float(transaction.get('time', transaction.get('Time', 0))),
            'Amount': float(transaction.get('amount', transaction.get('Amount', 0)))
        }
        
        # Add V1-V28
        for i in range(1, 29):
            col = f'V{i}'
            normalized_tx[col] = float(transaction.get(col, 0))
            
        # Create DataFrame with single row
        df = pd.DataFrame([normalized_tx])
        
        # Ensure correct column order (must match training data: Time, V1-V28, Amount)
        features = ['Time'] + [f'V{i}' for i in range(1, 29)] + ['Amount']
        
        # Select only feature columns
        df_features = df[features]
        
        # Scale features
        X_scaled = self.scaler.transform(df_features)
        return X_scaled

    def predict(self, transaction):
        """
        Run inference on a transaction.
        
        Returns:
            dict: {
                'fraud_probability': float (0-1),
                'is_fraud': bool,
                'anomaly_score': float,
                'is_anomaly': bool
            }
        """
        X = self.preprocess(transaction)
        
        # XGBoost Prediction (Supervised)
        xgb_prob = self.xgb_model.predict_proba(X)[0][1]
        xgb_pred = int(self.xgb_model.predict(X)[0])
        
        # Isolation Forest Prediction (Unsupervised)
        # predict returns -1 for outlier, 1 for inlier
        iso_raw = self.iso_model.predict(X)[0]
        iso_pred = 1 if iso_raw == -1 else 0
        iso_score = self.iso_model.decision_function(X)[0] 
        
        return {
            'fraud_probability': float(xgb_prob),
            'is_fraud': bool(xgb_pred),
            'anomaly_score': float(iso_score),
            'is_anomaly': bool(iso_pred)
        }
