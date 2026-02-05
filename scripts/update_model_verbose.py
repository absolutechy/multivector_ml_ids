"""
Quick script to update the existing model's verbose setting to 0.
This eliminates the parallel processing messages during predictions.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import joblib
from config.config import MODEL_PATH

print("Loading existing model...")
model = joblib.load(MODEL_PATH)

print(f"Current verbose setting: {model.verbose}")

# Update verbose to 0
model.verbose = 0

print(f"Updated verbose setting: {model.verbose}")

# Save the updated model
print(f"\nSaving updated model to {MODEL_PATH}...")
joblib.dump(model, MODEL_PATH)

print("✓ Model updated successfully!")
print("\nThe model will no longer produce verbose parallel processing messages during predictions.")
