import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Get project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data')
CSV_PATH = os.path.join(DATA_DIR, 'creditcard.csv')


def load_data():
    """Load the credit card fraud dataset."""
    print(f"📂 Loading dataset from: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH)
    
    print(f"✅ Loaded {len(df):,} transactions")
    print(f"   Fraud cases: {df['Class'].sum():,} ({df['Class'].mean()*100:.2f}%)")
    print(f"   Legitimate: {(df['Class']==0).sum():,} ({(df['Class']==0).mean()*100:.2f}%)")
    
    return df


def preprocess_data(df, test_size=0.2, random_state=42):
    """
    Preprocess and split data into train/test sets.
    
    Args:
        df: Raw DataFrame
        test_size: Proportion for test set
        random_state: Random seed for reproducibility
        
    Returns:
        X_train, X_test, y_train, y_test, scaler
    """
    print(f"\n🔧 Preprocessing data...")
    
    # Separate features and target
    X = df.drop('Class', axis=1)
    y = df['Class']
    
    # Split into train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    
    print(f"   Train set: {len(X_train):,} samples")
    print(f"   Test set: {len(X_test):,} samples")
    
    # Scale features (important for Isolation Forest, less critical for XGBoost)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    print(f"✅ Preprocessing complete")
    
    return X_train_scaled, X_test_scaled, y_train, y_test, scaler


if __name__ == "__main__":
    # Quick test
    df = load_data()
    X_train, X_test, y_train, y_test, scaler = preprocess_data(df)
    print(f"\n✅ Data loader working correctly!")
    print(f"   Feature shape: {X_train.shape}")
