"""
AgroSmart AI - Crop Recommendation Model Training Script
=========================================================
Dataset: Crop Recommendation Dataset (Kaggle)
  - Download from: https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset
  - Save as: ml/data/Crop_recommendation.csv

Features: N, P, K, temperature, humidity, ph, rainfall
Target:   label (crop name)

Run: python ml/train.py
"""

import os
import sys
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import joblib

# ─── Paths ────────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "data" / "Crop_recommendation.csv"
ARTIFACTS_DIR = BASE_DIR / "artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)


# ─── Generate Synthetic Data (if CSV not found) ───────────────────────────────

def generate_synthetic_data() -> pd.DataFrame:
    """
    Generate a synthetic crop recommendation dataset for demo/testing.
    Based on real agronomic ranges from research papers.
    """
    print("⚠️  Dataset not found. Generating synthetic training data...")

    np.random.seed(42)
    n = 2200  # 100 samples per crop

    crops = {
        "rice":        dict(N=(60,100), P=(30,60), K=(30,60), T=(22,27), H=(80,90), pH=(5.5,7.0), R=(150,300)),
        "wheat":       dict(N=(80,120), P=(30,60), K=(30,60), T=(15,22), H=(55,70), pH=(6.0,7.5), R=(60,100)),
        "maize":       dict(N=(80,130), P=(40,80), K=(20,50), T=(22,28), H=(55,75), pH=(5.8,7.5), R=(60,110)),
        "cotton":      dict(N=(80,140), P=(35,70), K=(10,40), T=(25,35), H=(55,75), pH=(6.0,8.0), R=(60,100)),
        "sugarcane":   dict(N=(90,140), P=(30,60), K=(30,70), T=(24,32), H=(65,80), pH=(6.0,7.5), R=(100,200)),
        "chickpea":    dict(N=(20,60),  P=(50,100),K=(70,120),T=(20,28), H=(14,25), pH=(5.8,7.5), R=(50,100)),
        "lentil":      dict(N=(20,60),  P=(50,100),K=(70,120),T=(18,26), H=(60,70), pH=(6.0,8.0), R=(35,75)),
        "groundnut":   dict(N=(20,40),  P=(50,80), K=(10,40), T=(25,30), H=(40,60), pH=(5.5,7.5), R=(50,100)),
        "soybean":     dict(N=(20,80),  P=(60,100),K=(10,40), T=(25,32), H=(55,75), pH=(6.0,7.5), R=(60,100)),
        "mungbean":    dict(N=(20,40),  P=(30,60), K=(10,40), T=(26,35), H=(60,80), pH=(6.2,7.5), R=(60,120)),
        "blackgram":   dict(N=(20,40),  P=(50,80), K=(10,40), T=(26,34), H=(60,80), pH=(6.0,7.5), R=(60,100)),
        "kidneybeans": dict(N=(20,50),  P=(50,100),K=(10,30), T=(18,26), H=(50,65), pH=(5.5,7.5), R=(100,200)),
        "pigeonpeas":  dict(N=(10,30),  P=(50,100),K=(10,50), T=(26,35), H=(30,70), pH=(5.5,7.0), R=(60,100)),
        "mothbeans":   dict(N=(10,30),  P=(30,60), K=(10,30), T=(28,38), H=(25,50), pH=(6.0,7.5), R=(30,60)),
        "mango":       dict(N=(10,40),  P=(10,60), K=(30,80), T=(24,35), H=(50,80), pH=(5.5,7.5), R=(50,100)),
        "banana":      dict(N=(80,120), P=(60,120),K=(50,120),T=(25,32), H=(70,90), pH=(6.0,7.5), R=(100,200)),
        "grapes":      dict(N=(10,40),  P=(60,100),K=(10,30), T=(25,35), H=(60,80), pH=(6.0,7.5), R=(60,100)),
        "watermelon":  dict(N=(90,130), P=(50,100),K=(40,100),T=(25,35), H=(70,90), pH=(6.0,7.5), R=(50,100)),
        "muskmelon":   dict(N=(80,120), P=(50,100),K=(40,100),T=(28,36), H=(70,90), pH=(6.0,7.5), R=(20,60)),
        "apple":       dict(N=(0,20),   P=(100,145),K=(130,205),T=(18,24),H=(90,95),pH=(5.5,7.0), R=(100,200)),
        "orange":      dict(N=(0,20),   P=(10,30), K=(10,30), T=(22,28), H=(80,90), pH=(6.0,7.5), R=(100,200)),
        "papaya":      dict(N=(40,80),  P=(50,100),K=(40,100),T=(25,35), H=(60,80), pH=(6.0,7.5), R=(100,200)),
        "coconut":     dict(N=(10,40),  P=(10,40), K=(30,80), T=(26,34), H=(75,95), pH=(5.5,7.0), R=(100,200)),
        "coffee":      dict(N=(60,120), P=(20,60), K=(40,100),T=(22,28), H=(60,80), pH=(5.8,6.5), R=(150,300)),
        "jute":        dict(N=(60,100), P=(30,80), K=(30,80), T=(24,36), H=(70,90), pH=(6.0,7.5), R=(150,300)),
        "pomegranate": dict(N=(10,40),  P=(10,60), K=(40,80), T=(26,35), H=(40,70), pH=(5.5,7.5), R=(40,80)),
    }

    rows = []
    for crop, params in crops.items():
        for _ in range(n // len(crops)):
            rows.append({
                "N":           np.random.uniform(*params["N"]),
                "P":           np.random.uniform(*params["P"]),
                "K":           np.random.uniform(*params["K"]),
                "temperature": np.random.uniform(*params["T"]),
                "humidity":    np.random.uniform(*params["H"]),
                "ph":          np.random.uniform(*params["pH"]),
                "rainfall":    np.random.uniform(*params["R"]),
                "label":       crop,
            })

    df = pd.DataFrame(rows)
    # Save generated data
    (BASE_DIR / "data").mkdir(exist_ok=True)
    df.to_csv(DATA_PATH, index=False)
    print(f"✅ Synthetic data saved to {DATA_PATH} ({len(df)} rows)")
    return df


# ─── Main Training Function ───────────────────────────────────────────────────

def train():
    """Load data, train Random Forest model, save artifacts."""

    # Load or generate dataset
    if DATA_PATH.exists():
        print(f"📂 Loading dataset from {DATA_PATH}")
        df = pd.read_csv(DATA_PATH)
    else:
        df = generate_synthetic_data()

    print(f"📊 Dataset: {len(df)} rows, {df['label'].nunique()} crops")
    print(f"   Crops: {sorted(df['label'].unique())}")

    # Features and target
    FEATURES = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
    X = df[FEATURES].values
    y = df["label"].values

    # Encode labels
    encoder = LabelEncoder()
    y_encoded = encoder.fit_transform(y)

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Train / test split (80/20)
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )

    # Train Random Forest
    print("\n🌲 Training Random Forest Classifier...")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        random_state=42,
        n_jobs=-1,
        class_weight="balanced",
    )
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\n✅ Model Accuracy: {accuracy * 100:.2f}%")
    print("\n📋 Classification Report:")
    print(classification_report(y_test, y_pred, target_names=encoder.classes_))

    # Feature importance
    importances = model.feature_importances_
    print("\n📈 Feature Importances:")
    for feat, imp in sorted(zip(FEATURES, importances), key=lambda x: -x[1]):
        print(f"   {feat:15s}: {imp:.4f}")

    # Save artifacts
    joblib.dump(model,   ARTIFACTS_DIR / "crop_model.pkl")
    joblib.dump(encoder, ARTIFACTS_DIR / "label_encoder.pkl")
    joblib.dump(scaler,  ARTIFACTS_DIR / "scaler.pkl")

    print(f"\n💾 Model artifacts saved to {ARTIFACTS_DIR}/")
    print("   - crop_model.pkl")
    print("   - label_encoder.pkl")
    print("   - scaler.pkl")
    print("\n🚀 Training complete! Your AgroSmart AI model is ready.")

    return accuracy


if __name__ == "__main__":
    train()
