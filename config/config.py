"""
Configuration settings for the Multi-Vector IDS system.
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Dataset paths
DATASET_DIR = BASE_DIR / "cicids2017"
BENIGN_FILE = DATASET_DIR / "Benign-Monday-no-metadata.parquet"
BRUTEFORCE_FILE = DATASET_DIR / "Bruteforce-Tuesday-no-metadata.parquet"
DDOS_FILE = DATASET_DIR / "DDoS-Friday-no-metadata.parquet"
WEBATTACKS_FILE = DATASET_DIR / "WebAttacks-Thursday-no-metadata.parquet"

# Model paths
MODELS_DIR = BASE_DIR / "models"
MODEL_PATH = MODELS_DIR / "random_forest_model.pkl"
SCALER_PATH = MODELS_DIR / "scaler.pkl"
PCA_PATH = MODELS_DIR / "pca.pkl"

# Results paths
RESULTS_DIR = BASE_DIR / "results"
EVALUATION_REPORT = RESULTS_DIR / "evaluation_report.json"
CONFUSION_MATRIX_IMG = RESULTS_DIR / "confusion_matrix.png"

# Data processing parameters
ATTACK_CLASSES = {
    "Benign": 0,
    "DDoS": 1,
    "Brute Force": 2,
    "Web Attack": 3  # All WebAttacks (SQLi + XSS + Web Brute Force)
}

# Feature engineering parameters
TRAIN_TEST_SPLIT_RATIO = 0.2
RANDOM_STATE = 42
PCA_VARIANCE_THRESHOLD = 0.95  # Retain 95% variance (no component limit)

# Random Forest hyperparameters for tuning
RF_PARAM_GRID = {
    'n_estimators': [200, 300, 500],
    'max_depth': [20, 30, None],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4],
    'class_weight': ['balanced'],  # Handle class imbalance
    'random_state': [RANDOM_STATE]
}

# Cross-validation folds
CV_FOLDS = 5

# API settings
API_HOST = "0.0.0.0"
API_PORT = 8000
CORS_ORIGINS = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:3000",  # Alternative frontend
]

# Live capture settings
MAX_ALERTS_IN_MEMORY = 1000
FLOW_TIMEOUT = 2  # seconds - ultra-fast detection (2000ms)
PACKET_BUFFER_SIZE = 1000

# CSV export settings
CSV_EXPORT_DIR = BASE_DIR / "exports"
CSV_ROTATION_INTERVAL = "daily"  # daily, hourly, weekly
