"""
CICIDS2017 Parquet Dataset Loader
Loads and merges Parquet files for the 4 required attack classes.
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from config.config import (
    BENIGN_FILE, BRUTEFORCE_FILE, DDOS_FILE, WEBATTACKS_FILE,
    ATTACK_CLASSES
)


class CICIDS2017Loader:
    """Load and prepare CICIDS2017 dataset from Parquet files."""
    
    def __init__(self):
        self.benign_df = None
        self.bruteforce_df = None
        self.ddos_df = None
        self.webattacks_df = None
        self.merged_df = None
        
    def load_parquet_files(self):
        """Load all required Parquet files."""
        print("Loading CICIDS2017 Parquet files...")
        
        # Load Benign traffic
        print(f"  Loading {BENIGN_FILE.name}...")
        self.benign_df = pd.read_parquet(BENIGN_FILE)
        self.benign_df['attack_type'] = 'Benign'
        print(f"    Loaded {len(self.benign_df):,} benign samples")
        
        # Load Brute Force attacks
        print(f"  Loading {BRUTEFORCE_FILE.name}...")
        self.bruteforce_df = pd.read_parquet(BRUTEFORCE_FILE)
        self.bruteforce_df['attack_type'] = 'Brute Force'
        print(f"    Loaded {len(self.bruteforce_df):,} brute force samples")
        
        # Load DDoS attacks
        print(f"  Loading {DDOS_FILE.name}...")
        self.ddos_df = pd.read_parquet(DDOS_FILE)
        self.ddos_df['attack_type'] = 'DDoS'
        print(f"    Loaded {len(self.ddos_df):,} DDoS samples")
        
        # Load Web Attacks (use ALL web attacks)
        print(f"  Loading {WEBATTACKS_FILE.name}...")
        self.webattacks_df = pd.read_parquet(WEBATTACKS_FILE)
        self.webattacks_df['attack_type'] = 'Web Attack'
        print(f"    Loaded {len(self.webattacks_df):,} web attack samples (SQLi + XSS + Web Brute Force)")
        
        print("\n✓ All Parquet files loaded successfully")
        
    def merge_datasets(self):
        """Merge all dataframes into a single unified dataset."""
        print("\nMerging datasets...")
        
        # Concatenate all dataframes
        self.merged_df = pd.concat([
            self.benign_df,
            self.bruteforce_df,
            self.ddos_df,
            self.webattacks_df
        ], ignore_index=True)
        
        print(f"✓ Merged dataset shape: {self.merged_df.shape}")
        print(f"  Total samples: {len(self.merged_df):,}")
        print(f"  Total features: {self.merged_df.shape[1] - 1}")  # -1 for attack_type column
        
    def get_dataset_statistics(self):
        """Display comprehensive dataset statistics."""
        if self.merged_df is None:
            raise ValueError("Dataset not loaded. Call load_parquet_files() and merge_datasets() first.")
        
        print("\n" + "="*60)
        print("DATASET STATISTICS")
        print("="*60)
        
        # Class distribution
        print("\nClass Distribution:")
        class_counts = self.merged_df['attack_type'].value_counts()
        for attack_type, count in class_counts.items():
            percentage = (count / len(self.merged_df)) * 100
            print(f"  {attack_type:20s}: {count:>10,} ({percentage:>5.2f}%)")
        
        print(f"\n  {'Total':20s}: {len(self.merged_df):>10,} (100.00%)")
        
        # Feature information
        print(f"\nFeature Information:")
        print(f"  Total features: {self.merged_df.shape[1] - 1}")  # -1 for attack_type
        
        # Data types
        print(f"\nData Types:")
        dtype_counts = self.merged_df.dtypes.value_counts()
        for dtype, count in dtype_counts.items():
            print(f"  {str(dtype):20s}: {count} columns")
        
        # Missing values
        print(f"\nMissing Values:")
        missing = self.merged_df.isnull().sum()
        missing_cols = missing[missing > 0]
        if len(missing_cols) > 0:
            print(f"  Columns with missing values: {len(missing_cols)}")
            for col, count in missing_cols.items():
                percentage = (count / len(self.merged_df)) * 100
                print(f"    {col:30s}: {count:>8,} ({percentage:>5.2f}%)")
        else:
            print(f"  No missing values found ✓")
        
        # Duplicates
        duplicates = self.merged_df.duplicated().sum()
        print(f"\nDuplicate Rows: {duplicates:,}")
        
        print("="*60 + "\n")
        
        return {
            'total_samples': len(self.merged_df),
            'total_features': self.merged_df.shape[1] - 1,
            'class_distribution': class_counts.to_dict(),
            'missing_values': missing_cols.to_dict() if len(missing_cols) > 0 else {},
            'duplicates': int(duplicates)
        }
    
    def get_merged_dataset(self):
        """Return the merged dataset."""
        if self.merged_df is None:
            raise ValueError("Dataset not loaded. Call load_parquet_files() and merge_datasets() first.")
        return self.merged_df
    
    def save_merged_dataset(self, output_path):
        """Save merged dataset to Parquet file."""
        if self.merged_df is None:
            raise ValueError("Dataset not loaded. Call load_parquet_files() and merge_datasets() first.")
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"\nSaving merged dataset to {output_path}...")
        self.merged_df.to_parquet(output_path, index=False)
        print(f"✓ Dataset saved successfully")


def main():
    """Main function to demonstrate dataset loading."""
    loader = CICIDS2017Loader()
    
    # Load Parquet files
    loader.load_parquet_files()
    
    # Merge datasets
    loader.merge_datasets()
    
    # Get statistics
    stats = loader.get_dataset_statistics()
    
    # Optionally save merged dataset
    # loader.save_merged_dataset("data/merged_cicids2017.parquet")
    
    return loader


if __name__ == "__main__":
    loader = main()
