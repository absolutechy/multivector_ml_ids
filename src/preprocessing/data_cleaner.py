"""
Data Cleaning Pipeline for CICIDS2017 Dataset
Handles missing values, duplicates, and class balancing.
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from sklearn.utils import resample
from imblearn.over_sampling import SMOTE
from config.config import ATTACK_CLASSES, RANDOM_STATE


class DataCleaner:
    """Clean and prepare dataset for training."""
    
    def __init__(self, df):
        """
        Initialize DataCleaner with dataset.
        
        Args:
            df: pandas DataFrame with 'attack_type' column
        """
        self.df = df.copy()
        self.original_shape = self.df.shape
        
    def handle_missing_values(self, strategy='drop', fill_value=0):
        """
        Handle missing values in the dataset.
        
        Args:
            strategy: 'drop' to remove rows, 'fill' to impute
            fill_value: value to use if strategy='fill'
        """
        print("\nHandling missing values...")
        missing_before = self.df.isnull().sum().sum()
        
        if missing_before == 0:
            print("  No missing values found ✓")
            return
        
        if strategy == 'drop':
            self.df = self.df.dropna()
            print(f"  Dropped rows with missing values")
        elif strategy == 'fill':
            # Fill numeric columns with fill_value, categorical with mode
            for col in self.df.columns:
                if self.df[col].dtype in ['float64', 'float32', 'int64', 'int32', 'int16', 'int8']:
                    self.df[col].fillna(fill_value, inplace=True)
                else:
                    self.df[col].fillna(self.df[col].mode()[0], inplace=True)
            print(f"  Filled {missing_before:,} missing values")
        
        missing_after = self.df.isnull().sum().sum()
        print(f"  Missing values after: {missing_after:,}")
        
    def remove_duplicates(self):
        """Remove duplicate rows."""
        print("\nRemoving duplicates...")
        duplicates_before = self.df.duplicated().sum()
        
        if duplicates_before == 0:
            print("  No duplicates found ✓")
            return
        
        self.df = self.df.drop_duplicates()
        print(f"  Removed {duplicates_before:,} duplicate rows")
        print(f"  Dataset shape: {self.df.shape}")
        
    def remove_infinite_values(self):
        """Replace infinite values with NaN and handle them."""
        print("\nHandling infinite values...")
        
        # Find numeric columns
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        inf_count = 0
        for col in numeric_cols:
            inf_mask = np.isinf(self.df[col])
            inf_count += inf_mask.sum()
            if inf_mask.any():
                # Replace inf with NaN, then fill with column max (for +inf) or min (for -inf)
                self.df.loc[inf_mask & (self.df[col] > 0), col] = self.df[col][~inf_mask].max()
                self.df.loc[inf_mask & (self.df[col] < 0), col] = self.df[col][~inf_mask].min()
        
        if inf_count == 0:
            print("  No infinite values found ✓")
        else:
            print(f"  Replaced {inf_count:,} infinite values")
    
    def filter_attack_classes(self):
        """Ensure only the 4 required attack classes are present."""
        print("\nFiltering attack classes...")
        classes_before = self.df['attack_type'].unique()
        
        # Keep only the 4 required classes
        valid_classes = list(ATTACK_CLASSES.keys())
        self.df = self.df[self.df['attack_type'].isin(valid_classes)]
        
        classes_after = self.df['attack_type'].unique()
        print(f"  Classes before: {len(classes_before)}")
        print(f"  Classes after: {len(classes_after)}")
        print(f"  Dataset shape: {self.df.shape}")
        
    def balance_classes(self, method='smote', target_samples=None):
        """
        Balance class distribution.
        
        Args:
            method: 'smote' for oversampling, 'undersample' for undersampling, 'none' for no balancing
            target_samples: target number of samples per class (for undersampling)
        """
        if method == 'none':
            print("\nSkipping class balancing (as requested)")
            return
        
        print(f"\nBalancing classes using {method.upper()}...")
        
        # Show distribution before
        class_dist_before = self.df['attack_type'].value_counts()
        print("\n  Distribution before balancing:")
        for attack_type, count in class_dist_before.items():
            print(f"    {attack_type:20s}: {count:>10,}")
        
        if method == 'undersample':
            # Undersample to the minority class or target_samples
            min_samples = class_dist_before.min() if target_samples is None else target_samples
            
            balanced_dfs = []
            for attack_type in ATTACK_CLASSES.keys():
                class_df = self.df[self.df['attack_type'] == attack_type]
                if len(class_df) > min_samples:
                    class_df = resample(class_df, n_samples=min_samples, random_state=RANDOM_STATE)
                balanced_dfs.append(class_df)
            
            self.df = pd.concat(balanced_dfs, ignore_index=True)
            
        elif method == 'smote':
            # SMOTE requires numeric features only
            # Separate features and labels
            X = self.df.drop('attack_type', axis=1)
            y = self.df['attack_type']
            
            # Convert attack_type to numeric labels
            y_numeric = y.map(ATTACK_CLASSES)
            
            # Select only numeric columns for SMOTE
            numeric_cols = X.select_dtypes(include=[np.number]).columns
            X_numeric = X[numeric_cols]
            
            # Apply SMOTE
            smote = SMOTE(random_state=RANDOM_STATE, k_neighbors=5)
            X_resampled, y_resampled = smote.fit_resample(X_numeric, y_numeric)
            
            # Convert back to DataFrame
            self.df = pd.DataFrame(X_resampled, columns=numeric_cols)
            
            # Map numeric labels back to attack types
            reverse_mapping = {v: k for k, v in ATTACK_CLASSES.items()}
            self.df['attack_type'] = y_resampled.map(reverse_mapping)
        
        # Show distribution after
        class_dist_after = self.df['attack_type'].value_counts()
        print("\n  Distribution after balancing:")
        for attack_type, count in class_dist_after.items():
            print(f"    {attack_type:20s}: {count:>10,}")
        
        print(f"\n  Final dataset shape: {self.df.shape}")
        
    def get_cleaned_data(self):
        """Return cleaned dataset."""
        return self.df
    
    def get_cleaning_summary(self):
        """Return summary of cleaning operations."""
        return {
            'original_shape': self.original_shape,
            'final_shape': self.df.shape,
            'rows_removed': self.original_shape[0] - self.df.shape[0],
            'class_distribution': self.df['attack_type'].value_counts().to_dict()
        }


def main():
    """Demonstrate data cleaning pipeline."""
    from src.data.dataset_loader import CICIDS2017Loader
    
    # Load dataset
    print("Loading dataset...")
    loader = CICIDS2017Loader()
    loader.load_parquet_files()
    loader.merge_datasets()
    df = loader.get_merged_dataset()
    
    # Clean dataset
    cleaner = DataCleaner(df)
    cleaner.handle_missing_values(strategy='drop')
    cleaner.remove_duplicates()
    cleaner.remove_infinite_values()
    cleaner.filter_attack_classes()
    
    # Balance classes (you can choose method)
    # cleaner.balance_classes(method='undersample', target_samples=100000)
    # cleaner.balance_classes(method='smote')
    cleaner.balance_classes(method='none')  # No balancing for now
    
    # Get cleaned data
    cleaned_df = cleaner.get_cleaned_data()
    summary = cleaner.get_cleaning_summary()
    
    print("\n" + "="*60)
    print("CLEANING SUMMARY")
    print("="*60)
    print(f"Original shape: {summary['original_shape']}")
    print(f"Final shape: {summary['final_shape']}")
    print(f"Rows removed: {summary['rows_removed']:,}")
    print("="*60 + "\n")
    
    return cleaned_df


if __name__ == "__main__":
    cleaned_data = main()
