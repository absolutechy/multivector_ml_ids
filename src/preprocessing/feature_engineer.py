"""
Feature Engineering Pipeline
Handles normalization, PCA, and feature selection.
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
import joblib
from config.config import (
    PCA_VARIANCE_THRESHOLD, SCALER_PATH, PCA_PATH, 
    MODELS_DIR, ATTACK_CLASSES
)


class FeatureEngineer:
    """Feature engineering and dimensionality reduction."""
    
    def __init__(self):
        self.scaler = MinMaxScaler()
        self.pca = None
        self.feature_names = None
        self.pca_components = None
        self.variance_retained = None
        
    def prepare_features(self, df):
        """
        Separate features and labels.
        
        Args:
            df: DataFrame with 'attack_type' column
            
        Returns:
            X: Feature matrix
            y: Labels
        """
        # Separate features and labels
        X = df.drop('attack_type', axis=1)
        y = df['attack_type']
        
        # Keep only numeric columns
        numeric_cols = X.select_dtypes(include=[np.number]).columns
        X = X[numeric_cols]
        
        self.feature_names = X.columns.tolist()
        
        print(f"\nFeature preparation:")
        print(f"  Total features: {len(self.feature_names)}")
        print(f"  Samples: {len(X):,}")
        
        return X, y
    
    def normalize_features(self, X_train, X_test=None):
        """
        Apply Min-Max normalization (0-1 scaling).
        
        Args:
            X_train: Training features
            X_test: Test features (optional)
            
        Returns:
            X_train_scaled, X_test_scaled (if X_test provided)
        """
        print("\nApplying Min-Max normalization...")
        
        # Fit scaler on training data
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_train_scaled = pd.DataFrame(X_train_scaled, columns=X_train.columns)
        
        print(f"  Scaled training data: {X_train_scaled.shape}")
        print(f"  Feature range: [0, 1]")
        
        if X_test is not None:
            X_test_scaled = self.scaler.transform(X_test)
            X_test_scaled = pd.DataFrame(X_test_scaled, columns=X_test.columns)
            print(f"  Scaled test data: {X_test_scaled.shape}")
            return X_train_scaled, X_test_scaled
        
        return X_train_scaled
    
    def apply_pca(self, X_train, X_test=None, variance_threshold=PCA_VARIANCE_THRESHOLD):
        """
        Apply PCA for dimensionality reduction.
        
        Args:
            X_train: Training features (already scaled)
            X_test: Test features (optional, already scaled)
            variance_threshold: Minimum variance to retain (default: 0.95)
            
        Returns:
            X_train_pca, X_test_pca (if X_test provided)
        """
        print(f"\nApplying PCA (target variance: {variance_threshold*100:.1f}%)...")
        
        # Initialize PCA
        self.pca = PCA(n_components=variance_threshold, random_state=42)
        
        # Fit and transform training data
        X_train_pca = self.pca.fit_transform(X_train)
        
        self.pca_components = self.pca.n_components_
        self.variance_retained = self.pca.explained_variance_ratio_.sum()
        
        print(f"  Original features: {X_train.shape[1]}")
        print(f"  PCA components: {self.pca_components}")
        print(f"  Variance retained: {self.variance_retained*100:.2f}%")
        print(f"  Dimensionality reduction: {X_train.shape[1]} → {self.pca_components}")
        
        # Show top components' variance
        print(f"\n  Top 10 components variance:")
        for i, var in enumerate(self.pca.explained_variance_ratio_[:10], 1):
            cumsum = self.pca.explained_variance_ratio_[:i].sum()
            print(f"    PC{i:2d}: {var*100:5.2f}% (cumulative: {cumsum*100:5.2f}%)")
        
        if X_test is not None:
            X_test_pca = self.pca.transform(X_test)
            return X_train_pca, X_test_pca
        
        return X_train_pca
    
    def save_transformers(self):
        """Save scaler and PCA transformers for inference."""
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        
        print("\nSaving transformers...")
        
        # Save scaler
        joblib.dump(self.scaler, SCALER_PATH)
        print(f"  ✓ Scaler saved to {SCALER_PATH}")
        
        # Save PCA
        if self.pca is not None:
            joblib.dump(self.pca, PCA_PATH)
            print(f"  ✓ PCA saved to {PCA_PATH}")
        
    def load_transformers(self):
        """Load saved transformers."""
        print("\nLoading transformers...")
        
        if SCALER_PATH.exists():
            self.scaler = joblib.load(SCALER_PATH)
            print(f"  ✓ Scaler loaded from {SCALER_PATH}")
        
        if PCA_PATH.exists():
            self.pca = joblib.load(PCA_PATH)
            self.pca_components = self.pca.n_components_
            self.variance_retained = self.pca.explained_variance_ratio_.sum()
            print(f"  ✓ PCA loaded from {PCA_PATH}")
            print(f"    Components: {self.pca_components}")
            print(f"    Variance retained: {self.variance_retained*100:.2f}%")
    
    def transform_new_data(self, X):
        """
        Transform new data using saved transformers.
        
        Args:
            X: New feature data
            
        Returns:
            Transformed data
        """
        # Scale
        X_scaled = self.scaler.transform(X)
        
        # Apply PCA if available
        if self.pca is not None:
            X_transformed = self.pca.transform(X_scaled)
        else:
            X_transformed = X_scaled
        
        return X_transformed
    
    def get_feature_importance_summary(self):
        """Return summary of feature engineering."""
        return {
            'original_features': len(self.feature_names) if self.feature_names else 0,
            'pca_components': self.pca_components,
            'variance_retained': self.variance_retained,
            'dimensionality_reduction_ratio': self.pca_components / len(self.feature_names) if self.feature_names else 0
        }


def main():
    """Demonstrate feature engineering pipeline."""
    from src.data.dataset_loader import CICIDS2017Loader
    from src.preprocessing.data_cleaner import DataCleaner
    from sklearn.model_selection import train_test_split
    from config.config import TRAIN_TEST_SPLIT_RATIO, RANDOM_STATE
    
    # Load and clean dataset
    print("Loading dataset...")
    loader = CICIDS2017Loader()
    loader.load_parquet_files()
    loader.merge_datasets()
    df = loader.get_merged_dataset()
    
    print("\nCleaning dataset...")
    cleaner = DataCleaner(df)
    cleaner.handle_missing_values(strategy='drop')
    cleaner.remove_duplicates()
    cleaner.remove_infinite_values()
    cleaner.filter_attack_classes()
    cleaner.balance_classes(method='none')
    cleaned_df = cleaner.get_cleaned_data()
    
    # Feature engineering
    engineer = FeatureEngineer()
    X, y = engineer.prepare_features(cleaned_df)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TRAIN_TEST_SPLIT_RATIO, random_state=RANDOM_STATE, stratify=y
    )
    
    print(f"\nTrain-test split:")
    print(f"  Training samples: {len(X_train):,}")
    print(f"  Test samples: {len(X_test):,}")
    
    # Normalize
    X_train_scaled, X_test_scaled = engineer.normalize_features(X_train, X_test)
    
    # Apply PCA
    X_train_pca, X_test_pca = engineer.apply_pca(X_train_scaled, X_test_scaled)
    
    # Save transformers
    engineer.save_transformers()
    
    # Get summary
    summary = engineer.get_feature_importance_summary()
    print("\n" + "="*60)
    print("FEATURE ENGINEERING SUMMARY")
    print("="*60)
    print(f"Original features: {summary['original_features']}")
    print(f"PCA components: {summary['pca_components']}")
    print(f"Variance retained: {summary['variance_retained']*100:.2f}%")
    print(f"Reduction ratio: {summary['dimensionality_reduction_ratio']*100:.2f}%")
    print("="*60 + "\n")
    
    return X_train_pca, X_test_pca, y_train, y_test


if __name__ == "__main__":
    X_train, X_test, y_train, y_test = main()
