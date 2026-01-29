"""
Real-Time Prediction Engine
Loads trained model and makes predictions on extracted flow features.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import numpy as np
import pandas as pd
import joblib
from datetime import datetime
import threading
import queue

from config.config import MODEL_PATH, SCALER_PATH, PCA_PATH, ATTACK_CLASSES


class Predictor:
    """Real-time prediction engine for network flows."""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.pca = None
        self.is_loaded = False
        self.prediction_queue = queue.Queue()
        self.lock = threading.Lock()
        
        # Reverse mapping for attack classes
        self.class_names = {v: k for k, v in ATTACK_CLASSES.items()}
        
    def load_model_and_transformers(self):
        """Load trained model, scaler, and PCA transformer."""
        print("\nLoading model and transformers...")
        print("-" * 60)
        
        try:
            # Load model
            if not MODEL_PATH.exists():
                raise FileNotFoundError(f"Model not found at {MODEL_PATH}")
            
            self.model = joblib.load(MODEL_PATH)
            print(f"✓ Model loaded from {MODEL_PATH}")
            
            # Load scaler
            if not SCALER_PATH.exists():
                raise FileNotFoundError(f"Scaler not found at {SCALER_PATH}")
            
            self.scaler = joblib.load(SCALER_PATH)
            print(f"✓ Scaler loaded from {SCALER_PATH}")
            
            # Load PCA
            if not PCA_PATH.exists():
                raise FileNotFoundError(f"PCA not found at {PCA_PATH}")
            
            self.pca = joblib.load(PCA_PATH)
            print(f"✓ PCA loaded from {PCA_PATH}")
            print(f"  PCA components: {self.pca.n_components_}")
            
            self.is_loaded = True
            print("-" * 60)
            print("✓ All components loaded successfully\n")
            
        except Exception as e:
            print(f"❌ Error loading model/transformers: {e}")
            raise
    
    def predict_flow(self, flow_features, flow_key=None):
        """
        Predict attack type for a single flow.
        
        Args:
            flow_features: Dictionary of flow features
            flow_key: Optional flow identifier (src_ip, dst_ip, src_port, dst_port, protocol)
            
        Returns:
            Dictionary with prediction results
        """
        if not self.is_loaded:
            raise ValueError("Model not loaded. Call load_model_and_transformers() first.")
        
        try:
            # Convert features to DataFrame
            features_df = pd.DataFrame([flow_features])
            
            # Ensure all expected features are present (pad with zeros if missing)
            expected_features = self.scaler.feature_names_in_ if hasattr(self.scaler, 'feature_names_in_') else None
            if expected_features is not None:
                for feat in expected_features:
                    if feat not in features_df.columns:
                        features_df[feat] = 0
                
                # Reorder columns to match training
                features_df = features_df[expected_features]
            
            # Scale features
            features_scaled = self.scaler.transform(features_df)
            
            # Apply PCA
            features_pca = self.pca.transform(features_scaled)
            
            # Predict
            prediction = self.model.predict(features_pca)[0]
            probabilities = self.model.predict_proba(features_pca)[0]
            
            # Get attack type name
            attack_type = self.class_names.get(prediction, "Unknown")
            
            # Get confidence (probability of predicted class)
            confidence = probabilities[prediction]
            
            # Create result
            result = {
                'timestamp': datetime.now().isoformat(),
                'flow_key': flow_key,
                'attack_type': attack_type,
                'attack_class_id': int(prediction),
                'confidence': float(confidence),
                'probabilities': {
                    self.class_names[i]: float(prob) 
                    for i, prob in enumerate(probabilities)
                },
                'is_attack': attack_type != 'Benign'
            }
            
            return result
            
        except Exception as e:
            print(f"Error predicting flow: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'flow_key': flow_key,
                'attack_type': 'Error',
                'confidence': 0.0,
                'error': str(e)
            }
    
    def predict_batch(self, flows_features):
        """
        Predict attack types for multiple flows.
        
        Args:
            flows_features: List of (flow_key, features_dict) tuples
            
        Returns:
            List of prediction results
        """
        results = []
        
        for flow_key, features in flows_features:
            result = self.predict_flow(features, flow_key)
            results.append(result)
        
        return results
    
    def predict_async(self, flow_features, flow_key=None, callback=None):
        """
        Asynchronous prediction (non-blocking).
        
        Args:
            flow_features: Dictionary of flow features
            flow_key: Optional flow identifier
            callback: Optional callback function to call with result
        """
        def worker():
            result = self.predict_flow(flow_features, flow_key)
            if callback:
                callback(result)
            else:
                with self.lock:
                    self.prediction_queue.put(result)
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
    
    def get_prediction_results(self, max_results=10):
        """
        Get prediction results from queue.
        
        Args:
            max_results: Maximum number of results to return
            
        Returns:
            List of prediction results
        """
        results = []
        with self.lock:
            for _ in range(min(max_results, self.prediction_queue.qsize())):
                if not self.prediction_queue.empty():
                    results.append(self.prediction_queue.get())
        return results
    
    def get_model_info(self):
        """Get information about loaded model."""
        if not self.is_loaded:
            return {'loaded': False}
        
        return {
            'loaded': True,
            'model_type': type(self.model).__name__,
            'n_features_original': len(self.scaler.feature_names_in_) if hasattr(self.scaler, 'feature_names_in_') else 'Unknown',
            'n_features_pca': self.pca.n_components_,
            'attack_classes': list(self.class_names.values()),
            'model_path': str(MODEL_PATH)
        }


def main():
    """Demonstrate prediction engine."""
    print("Real-Time Prediction Engine Demo")
    print("="*60)
    
    # Initialize predictor
    predictor = Predictor()
    
    # Load model
    try:
        predictor.load_model_and_transformers()
    except Exception as e:
        print(f"\n❌ Cannot load model. Make sure to train the model first:")
        print(f"   python scripts/train_pipeline.py")
        return
    
    # Get model info
    info = predictor.get_model_info()
    print("\nModel Information:")
    print("-" * 60)
    print(f"  Model type: {info['model_type']}")
    print(f"  Original features: {info['n_features_original']}")
    print(f"  PCA features: {info['n_features_pca']}")
    print(f"  Attack classes: {', '.join(info['attack_classes'])}")
    print("-" * 60)
    
    # Create dummy features for testing
    print("\nTesting with dummy features...")
    dummy_features = {f'feature_{i}': np.random.rand() for i in range(78)}
    
    # Predict
    result = predictor.predict_flow(dummy_features, flow_key=('192.168.1.1', '8.8.8.8', 12345, 80, 6))
    
    print("\nPrediction Result:")
    print("-" * 60)
    print(f"  Attack Type: {result['attack_type']}")
    print(f"  Confidence: {result['confidence']*100:.2f}%")
    print(f"  Is Attack: {result['is_attack']}")
    print(f"\n  Probabilities:")
    for attack, prob in result['probabilities'].items():
        print(f"    {attack:20s}: {prob*100:>6.2f}%")
    print("-" * 60)


if __name__ == "__main__":
    main()
