

import os
import joblib
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.metrics import classification_report, confusion_matrix, precision_recall_curve, auc
import xgboost as xgb

from loader import load_data, preprocess_data

# Output directory for trained models
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODELS_DIR = os.path.join(BASE_DIR, 'models')


def train_isolation_forest(X_train, y_train, X_test, y_test):
    """
    Train Isolation Forest (Unsupervised Anomaly Detection).
    
    Args:
        X_train, y_train: Training data
        X_test, y_test: Test data
        
    Returns:
        Trained model
    """
    print("\n" + "="*60)
    print("🌲 Training Isolation Forest (Unsupervised)")
    print("="*60)
    
    # Contamination = expected proportion of outliers (frauds)
    contamination = y_train.mean()
    
    model = IsolationForest(
        contamination=contamination,
        random_state=42,
        n_estimators=100,
        max_samples='auto',
        n_jobs=-1
    )
    
    print(f"   Contamination rate: {contamination:.4f}")
    print(f"   Training on {len(X_train):,} samples...")
    
    model.fit(X_train)
    
    # Predict (-1 for anomaly/fraud, 1 for normal)
    y_pred = model.predict(X_test)
    y_pred_binary = (y_pred == -1).astype(int)  # Convert to 0/1
    
    # Evaluation
    print(f"\n📊 Isolation Forest Results:")
    print(confusion_matrix(y_test, y_pred_binary))
    print(classification_report(y_test, y_pred_binary, target_names=['Legitimate', 'Fraud']))
    
    return model


def train_xgboost(X_train, y_train, X_test, y_test):
    """
    Train XGBoost Classifier (Supervised).
    
    Args:
        X_train, y_train: Training data
        X_test, y_test: Test data
        
    Returns:
        Trained model
    """
    print("\n" + "="*60)
    print("🚀 Training XGBoost (Supervised)")
    print("="*60)
    
    # Handle class imbalance with scale_pos_weight
    scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()
    
    model = xgb.XGBClassifier(
        max_depth=6,
        learning_rate=0.1,
        n_estimators=100,
        scale_pos_weight=scale_pos_weight,
        eval_metric='aucpr',  # Precision-Recall AUC (better for imbalanced data)
        random_state=42,
        n_jobs=-1
    )
    
    print(f"   Class imbalance ratio: {scale_pos_weight:.2f}:1")
    print(f"   Training on {len(X_train):,} samples...")
    
    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        verbose=False
    )
    
    # Predict
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    # Evaluation
    print(f"\n📊 XGBoost Results:")
    print(confusion_matrix(y_test, y_pred))
    print(classification_report(y_test, y_pred, target_names=['Legitimate', 'Fraud']))
    
    # Precision-Recall AUC
    precision, recall, _ = precision_recall_curve(y_test, y_pred_proba)
    pr_auc = auc(recall, precision)
    print(f"\n   PR-AUC Score: {pr_auc:.4f}")
    
    return model


def save_models(isolation_forest_model, xgboost_model, scaler):
    """Save trained models to disk."""
    os.makedirs(MODELS_DIR, exist_ok=True)
    
    print(f"\n💾 Saving models to: {MODELS_DIR}")
    
    joblib.dump(isolation_forest_model, os.path.join(MODELS_DIR, 'isolation_forest.pkl'))
    joblib.dump(xgboost_model, os.path.join(MODELS_DIR, 'xgboost_model.pkl'))
    joblib.dump(scaler, os.path.join(MODELS_DIR, 'scaler.pkl'))
    
    print(f"   ✅ isolation_forest.pkl")
    print(f"   ✅ xgboost_model.pkl")
    print(f"   ✅ scaler.pkl")


def main():
    """Main training pipeline."""
    print("╔" + "="*58 + "╗")
    print("║" + " "*10 + "SentinelStream: ML Model Training" + " "*15 + "║")
    print("╚" + "="*58 + "╝")
    
    # Load and preprocess data
    df = load_data()
    X_train, X_test, y_train, y_test, scaler = preprocess_data(df)
    
    # Train models
    iso_model = train_isolation_forest(X_train, y_train, X_test, y_test)
    xgb_model = train_xgboost(X_train, y_train, X_test, y_test)
    
    # Save models
    save_models(iso_model, xgb_model, scaler)
    
    print("\n" + "="*60)
    print("✅ Training Complete!")
    print("="*60)
    print("\nNext Steps:")
    print("1. Review model metrics above")
    print("2. Models saved in models/ directory")
    print("3. Ready for Phase 4: Consumer implementation")


if __name__ == "__main__":
    main()
