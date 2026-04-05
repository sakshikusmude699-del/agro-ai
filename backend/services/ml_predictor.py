"""
ML Crop Prediction Service.
Loads the trained Random Forest model and returns ranked crop recommendations.
"""

import os
import numpy as np
import joblib
from pathlib import Path

# Path to saved model artifacts
MODEL_DIR = Path(__file__).parent.parent.parent / "ml" / "artifacts"
MODEL_PATH = MODEL_DIR / "crop_model.pkl"
ENCODER_PATH = MODEL_DIR / "label_encoder.pkl"
SCALER_PATH = MODEL_DIR / "scaler.pkl"

# Crop rotation compatibility map
# Key: previous crop → Value: list of rotation-friendly next crops
ROTATION_MAP = {
    "rice":        ["wheat", "mustard", "chickpea", "lentil"],
    "wheat":       ["rice", "maize", "cotton", "sugarcane"],
    "maize":       ["wheat", "soybean", "groundnut", "sunflower"],
    "cotton":      ["wheat", "chickpea", "lentil", "mustard"],
    "sugarcane":   ["wheat", "mustard", "soybean"],
    "chickpea":    ["rice", "maize", "cotton", "wheat"],
    "lentil":      ["rice", "maize", "wheat"],
    "groundnut":   ["maize", "cotton", "sorghum", "wheat"],
    "soybean":     ["wheat", "maize", "cotton", "sunflower"],
    "tomato":      ["beans", "lettuce", "carrot", "spinach"],
    "potato":      ["tomato", "beans", "peas", "corn"],
    "mungbean":    ["rice", "wheat", "maize"],
    "blackgram":   ["rice", "wheat", "maize"],
    "kidneybeans": ["maize", "rice", "wheat"],
    "pigeonpeas":  ["rice", "wheat", "maize", "cotton"],
    "mothbeans":   ["rice", "wheat"],
    "mango":       ["banana", "papaya"],
    "banana":      ["papaya", "mango"],
    "grapes":      ["wheat", "maize"],
    "watermelon":  ["maize", "wheat"],
    "muskmelon":   ["maize", "wheat"],
    "apple":       ["wheat", "maize"],
    "orange":      ["banana", "papaya"],
    "papaya":      ["banana", "mango"],
    "coconut":     ["banana", "papaya"],
    "coffee":      ["banana", "papaya"],
    "jute":        ["rice", "wheat"],
}

# Human-readable crop descriptions for recommendations
CROP_REASONS = {
    "rice": "High humidity and rainfall suit paddy cultivation well.",
    "wheat": "Cool temperature and moderate rainfall ideal for wheat.",
    "maize": "Warm climate and good phosphorus levels favor maize growth.",
    "cotton": "High potassium and warm weather support cotton fiber development.",
    "sugarcane": "Moist soil and warm temperature great for sugarcane yield.",
    "chickpea": "Low moisture and neutral pH suit chickpea perfectly.",
    "lentil": "Cool weather and moderate nutrients favor lentil growth.",
    "groundnut": "Sandy soil and warm weather ideal for groundnut.",
    "soybean": "Rich nitrogen and warm temperatures support soybean.",
    "mungbean": "Warm, moderately moist conditions favor mung bean.",
    "blackgram": "Warm, humid conditions with good drainage suit black gram.",
    "kidneybeans": "Moderate climate with good nitrogen levels favor kidney beans.",
    "pigeonpeas": "Drought-tolerant crop suitable for your dry conditions.",
    "mothbeans": "Extremely drought-tolerant, suits your soil profile.",
    "mango": "Warm climate and good drainage favor mango orchards.",
    "banana": "Humid, warm conditions with rich potassium ideal for banana.",
    "grapes": "Well-drained soil and warm climate suit grape cultivation.",
    "watermelon": "Sandy loam with high temperature perfect for watermelon.",
    "muskmelon": "Warm, dry climate with good drainage suits muskmelon.",
    "apple": "Cool climate and well-drained soil favor apple cultivation.",
    "orange": "Subtropical climate with moderate rainfall ideal for citrus.",
    "papaya": "Warm climate and high potassium support papaya growth.",
    "coconut": "Coastal, warm, humid conditions suit coconut palms.",
    "coffee": "High humidity, moderate temperature, and shade ideal for coffee.",
    "jute": "Alluvial soil and high humidity favor jute cultivation.",
    "pomegranate": "Dry, warm climate and well-drained soil suit pomegranate.",
    "default": "Soil and weather conditions are well-matched for this crop.",
}


def _load_model():
    """Load model, encoder, and scaler from disk."""
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model not found at {MODEL_PATH}. "
            "Run `python ml/train.py` first to train the model."
        )
    model = joblib.load(MODEL_PATH)
    encoder = joblib.load(ENCODER_PATH)
    scaler = joblib.load(SCALER_PATH)
    return model, encoder, scaler


def predict_crops(
    nitrogen: float,
    phosphorus: float,
    potassium: float,
    temperature: float,
    humidity: float,
    ph: float,
    rainfall: float,
    previous_crop: str = None,
    top_n: int = 3,
) -> dict:
    """
    Predict top N crops and apply crop rotation logic.

    Returns:
        {
          "recommendations": [...],       # top N rotation-friendly crops
          "previous_crop_option": {...},  # previous crop as optional suggestion
        }
    """
    model, encoder, scaler = _load_model()

    # Scale input features
    features = np.array([[nitrogen, phosphorus, potassium,
                          temperature, humidity, ph, rainfall]])
    features_scaled = scaler.transform(features)

    # Get probability distribution over all classes
    probas = model.predict_proba(features_scaled)[0]
    classes = encoder.classes_

    # Rank all crops by confidence
    ranked = sorted(
        zip(classes, probas), key=lambda x: x[1], reverse=True
    )

    prev = previous_crop.lower().strip() if previous_crop else None
    rotation_friendly = ROTATION_MAP.get(prev, []) if prev else []

    recommendations = []
    previous_crop_option = None

    for crop_name, confidence in ranked:
        crop_lower = crop_name.lower()

        # Build recommendation object
        rec = {
            "crop": crop_name,
            "confidence": round(float(confidence) * 100, 1),
            "is_rotation_friendly": crop_lower in rotation_friendly,
            "reason": CROP_REASONS.get(crop_lower, CROP_REASONS["default"]),
        }

        # Skip same crop as previous (add as optional at end)
        if prev and crop_lower == prev:
            previous_crop_option = {
                **rec,
                "reason": f"You previously grew {crop_name}. "
                           "Growing same crop repeatedly may reduce yield.",
                "is_rotation_friendly": False,
            }
            continue

        # Prioritize rotation-friendly crops
        if len(recommendations) < top_n:
            recommendations.append(rec)

        if len(recommendations) >= top_n:
            break

    # If not enough rotation-friendly crops, pad with best remaining
    if len(recommendations) < top_n:
        for crop_name, confidence in ranked:
            if len(recommendations) >= top_n:
                break
            if not any(r["crop"] == crop_name for r in recommendations):
                if not (prev and crop_name.lower() == prev):
                    recommendations.append({
                        "crop": crop_name,
                        "confidence": round(float(confidence) * 100, 1),
                        "is_rotation_friendly": False,
                        "reason": CROP_REASONS.get(
                            crop_name.lower(), CROP_REASONS["default"]
                        ),
                    })

    return {
        "recommendations": recommendations,
        "previous_crop_option": previous_crop_option,
    }
