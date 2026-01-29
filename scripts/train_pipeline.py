"""
End-to-End Training Pipeline
Executes the complete ML pipeline from data loading to model evaluation.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.data.dataset_loader import CICIDS2017Loader
from src.preprocessing.data_cleaner import DataCleaner
from src.preprocessing.feature_engineer import FeatureEngineer
from src.models.random_forest_trainer import RandomForestTrainer
from src.evaluation.evaluator import ModelEvaluator
from sklearn.model_selection import train_test_split
from config.config import TRAIN_TEST_SPLIT_RATIO, RANDOM_STATE
import time


def main():
    """Execute end-to-end training pipeline."""
    
    print("="*80)
    print(" "*20 + "MULTI-VECTOR IDS TRAINING PIPELINE")
    print("="*80)
    
    total_start_time = time.time()
    
    # Step 1: Load Dataset
    print("\n[STEP 1/6] Loading CICIDS2017 Dataset...")
    print("-" * 80)
    loader = CICIDS2017Loader()
    loader.load_parquet_files()
    loader.merge_datasets()
    stats = loader.get_dataset_statistics()
    df = loader.get_merged_dataset()
    
    # Step 2: Clean Dataset
    print("\n[STEP 2/6] Cleaning Dataset...")
    print("-" * 80)
    cleaner = DataCleaner(df)
    cleaner.handle_missing_values(strategy='drop')
    cleaner.remove_duplicates()
    cleaner.remove_infinite_values()
    cleaner.filter_attack_classes()
    
    # Balance classes - using undersampling for faster training
    # For production, you might want to use SMOTE or no balancing
    print("\nBalancing classes (undersampling to 100K samples per class for faster training)...")
    cleaner.balance_classes(method='undersample', target_samples=100000)
    
    cleaned_df = cleaner.get_cleaned_data()
    cleaning_summary = cleaner.get_cleaning_summary()
    
    # Step 3: Feature Engineering
    print("\n[STEP 3/6] Feature Engineering...")
    print("-" * 80)
    engineer = FeatureEngineer()
    X, y = engineer.prepare_features(cleaned_df)
    
    # Split data
    print(f"\nSplitting data (test size: {TRAIN_TEST_SPLIT_RATIO*100:.0f}%)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TRAIN_TEST_SPLIT_RATIO, random_state=RANDOM_STATE, stratify=y
    )
    print(f"  Training samples: {len(X_train):,}")
    print(f"  Test samples: {len(X_test):,}")
    
    # Normalize features
    X_train_scaled, X_test_scaled = engineer.normalize_features(X_train, X_test)
    
    # Apply PCA
    X_train_pca, X_test_pca = engineer.apply_pca(X_train_scaled, X_test_scaled)
    
    # Save transformers
    engineer.save_transformers()
    
    # Step 4: Train Random Forest
    print("\n[STEP 4/6] Training Random Forest Model...")
    print("-" * 80)
    trainer = RandomForestTrainer()
    
    # Set to True for hyperparameter tuning (takes longer)
    # Set to False for faster training with default params
    trainer.train_model(X_train_pca, y_train, tune_hyperparameters=False)
    
    # Step 5: Evaluate Model
    print("\n[STEP 5/6] Evaluating Model...")
    print("-" * 80)
    
    # Get predictions
    y_test_numeric = y_test.map({v: k for k, v in enumerate(y_test.unique())})
    y_pred, y_pred_proba = trainer.predict(X_test_pca)
    
    # Comprehensive evaluation
    evaluator = ModelEvaluator()
    evaluator.evaluate_comprehensive(y_test_numeric, y_pred, y_pred_proba)
    
    # Generate visualizations
    evaluator.plot_confusion_matrix()
    evaluator.plot_normalized_confusion_matrix()
    
    # Save evaluation report
    evaluator.save_evaluation_report()
    
    # Generate thesis tables
    evaluator.generate_thesis_tables()
    
    # Step 6: Save Model
    print("\n[STEP 6/6] Saving Model...")
    print("-" * 80)
    trainer.save_model()
    
    # Final Summary
    total_time = time.time() - total_start_time
    
    print("\n" + "="*80)
    print(" "*25 + "PIPELINE COMPLETED SUCCESSFULLY")
    print("="*80)
    print(f"\nTotal execution time: {total_time:.2f} seconds ({total_time/60:.2f} minutes)")
    print(f"\nKey Results:")
    print(f"  Dataset samples: {stats['total_samples']:,}")
    print(f"  Features (original): {stats['total_features']}")
    print(f"  Features (after PCA): {engineer.pca_components}")
    print(f"  Test accuracy: {evaluator.metrics['overall']['accuracy']*100:.2f}%")
    print(f"  F1-Score (macro): {evaluator.metrics['overall']['f1_macro']*100:.2f}%")
    
    # Check if accuracy meets target
    if evaluator.metrics['overall']['accuracy'] >= 0.95:
        print(f"\n✓ Target accuracy (≥95%) ACHIEVED!")
    else:
        print(f"\n⚠ Target accuracy (≥95%) NOT MET. Consider:")
        print(f"    - Enabling hyperparameter tuning")
        print(f"    - Using SMOTE for class balancing")
        print(f"    - Adjusting PCA variance threshold")
    
    print("="*80 + "\n")
    
    print("Next steps:")
    print("  1. Review evaluation report: results/evaluation_report.json")
    print("  2. Check confusion matrix: results/confusion_matrix.png")
    print("  3. Proceed to live capture implementation")
    print("\n")


if __name__ == "__main__":
    main()
