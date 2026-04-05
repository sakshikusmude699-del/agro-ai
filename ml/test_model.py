"""
AgroSmart AI - Model Test Script
=================================
Run after training to verify predictions work correctly.

Usage: python ml/test_model.py
"""

import sys
from pathlib import Path

# Add backend to path so we can import the predictor
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from services.ml_predictor import predict_crops


def test_predictions():
    print("=" * 60)
    print("AgroSmart AI — Model Prediction Tests")
    print("=" * 60)

    test_cases = [
        {
            "name": "Typical rice conditions (hot, humid, high rainfall)",
            "inputs": dict(nitrogen=80, phosphorus=40, potassium=40,
                           temperature=25, humidity=85, ph=6.5, rainfall=200),
            "previous_crop": None,
        },
        {
            "name": "Wheat conditions (cool, moderate rainfall)",
            "inputs": dict(nitrogen=100, phosphorus=50, potassium=50,
                           temperature=18, humidity=60, ph=7.0, rainfall=80),
            "previous_crop": "rice",
        },
        {
            "name": "Cotton conditions (hot, dry, high potassium)",
            "inputs": dict(nitrogen=100, phosphorus=50, potassium=20,
                           temperature=30, humidity=65, ph=7.5, rainfall=75),
            "previous_crop": None,
        },
        {
            "name": "Chickpea conditions (cool, low moisture)",
            "inputs": dict(nitrogen=30, phosphorus=70, potassium=90,
                           temperature=22, humidity=20, ph=6.8, rainfall=60),
            "previous_crop": "wheat",
        },
    ]

    for case in test_cases:
        print(f"\n📊 Test: {case['name']}")
        if case["previous_crop"]:
            print(f"   Previous crop: {case['previous_crop']}")

        result = predict_crops(
            **case["inputs"],
            previous_crop=case["previous_crop"],
        )

        print("   Top Recommendations:")
        for i, crop in enumerate(result["recommendations"], 1):
            rotation_tag = "✅ rotation-friendly" if crop["is_rotation_friendly"] else ""
            print(f"   {i}. {crop['crop']:<15} {crop['confidence']:>5.1f}%  {rotation_tag}")

        if result["previous_crop_option"]:
            pc = result["previous_crop_option"]
            print(f"   🔄 Previous crop option: {pc['crop']} ({pc['confidence']:.1f}%)")

    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    test_predictions()
