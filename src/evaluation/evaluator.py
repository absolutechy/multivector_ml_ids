"""
Model Evaluator
Comprehensive evaluation metrics and visualizations for thesis documentation.
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import json
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_curve, auc
)
import matplotlib.pyplot as plt
import seaborn as sns

from config.config import (
    ATTACK_CLASSES, RESULTS_DIR, EVALUATION_REPORT, CONFUSION_MATRIX_IMG
)


class ModelEvaluator:
    """Comprehensive model evaluation and visualization."""
    
    def __init__(self):
        self.metrics = {}
        self.confusion_mat = None
        self.class_names = list(ATTACK_CLASSES.keys())
        
    def evaluate_comprehensive(self, y_true, y_pred, y_pred_proba=None):
        """
        Perform comprehensive evaluation.
        
        Args:
            y_true: True labels (numeric)
            y_pred: Predicted labels (numeric)
            y_pred_proba: Prediction probabilities (optional)
        """
        print("\n" + "="*60)
        print("COMPREHENSIVE MODEL EVALUATION")
        print("="*60)
        
        # Overall metrics
        accuracy = accuracy_score(y_true, y_pred)
        precision_macro = precision_score(y_true, y_pred, average='macro')
        recall_macro = recall_score(y_true, y_pred, average='macro')
        f1_macro = f1_score(y_true, y_pred, average='macro')
        
        precision_weighted = precision_score(y_true, y_pred, average='weighted')
        recall_weighted = recall_score(y_true, y_pred, average='weighted')
        f1_weighted = f1_score(y_true, y_pred, average='weighted')
        
        print(f"\nOverall Metrics:")
        print(f"  Accuracy:           {accuracy*100:.2f}%")
        print(f"\n  Macro Average:")
        print(f"    Precision:        {precision_macro*100:.2f}%")
        print(f"    Recall:           {recall_macro*100:.2f}%")
        print(f"    F1-Score:         {f1_macro*100:.2f}%")
        print(f"\n  Weighted Average:")
        print(f"    Precision:        {precision_weighted*100:.2f}%")
        print(f"    Recall:           {recall_weighted*100:.2f}%")
        print(f"    F1-Score:         {f1_weighted*100:.2f}%")
        
        # Per-class metrics
        precision_per_class = precision_score(y_true, y_pred, average=None)
        recall_per_class = recall_score(y_true, y_pred, average=None)
        f1_per_class = f1_score(y_true, y_pred, average=None)
        
        print(f"\nPer-Class Metrics:")
        print(f"  {'Class':<20s} {'Precision':>10s} {'Recall':>10s} {'F1-Score':>10s}")
        print(f"  {'-'*20} {'-'*10} {'-'*10} {'-'*10}")
        
        for i, class_name in enumerate(self.class_names):
            print(f"  {class_name:<20s} {precision_per_class[i]*100:>9.2f}% {recall_per_class[i]*100:>9.2f}% {f1_per_class[i]*100:>9.2f}%")
        
        # Confusion matrix
        self.confusion_mat = confusion_matrix(y_true, y_pred)
        
        # Store metrics
        self.metrics = {
            'overall': {
                'accuracy': float(accuracy),
                'precision_macro': float(precision_macro),
                'recall_macro': float(recall_macro),
                'f1_macro': float(f1_macro),
                'precision_weighted': float(precision_weighted),
                'recall_weighted': float(recall_weighted),
                'f1_weighted': float(f1_weighted)
            },
            'per_class': {}
        }
        
        for i, class_name in enumerate(self.class_names):
            self.metrics['per_class'][class_name] = {
                'precision': float(precision_per_class[i]),
                'recall': float(recall_per_class[i]),
                'f1_score': float(f1_per_class[i])
            }
        
        print("\n" + "="*60)
        
    def plot_confusion_matrix(self, save_path=None):
        """
        Plot and save confusion matrix.
        
        Args:
            save_path: Path to save the plot (default: CONFUSION_MATRIX_IMG)
        """
        if self.confusion_mat is None:
            raise ValueError("Confusion matrix not computed. Call evaluate_comprehensive() first.")
        
        if save_path is None:
            save_path = CONFUSION_MATRIX_IMG
        
        # Create figure
        plt.figure(figsize=(10, 8))
        
        # Plot heatmap
        sns.heatmap(
            self.confusion_mat, 
            annot=True, 
            fmt='d', 
            cmap='Blues',
            xticklabels=self.class_names,
            yticklabels=self.class_names,
            cbar_kws={'label': 'Count'}
        )
        
        plt.title('Confusion Matrix - Multi-Vector Attack Detection', fontsize=14, fontweight='bold')
        plt.xlabel('Predicted Label', fontsize=12)
        plt.ylabel('True Label', fontsize=12)
        plt.tight_layout()
        
        # Save
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"\n✓ Confusion matrix saved to {save_path}")
        plt.close()
        
    def plot_normalized_confusion_matrix(self, save_path=None):
        """Plot normalized confusion matrix (percentages)."""
        if self.confusion_mat is None:
            raise ValueError("Confusion matrix not computed. Call evaluate_comprehensive() first.")
        
        if save_path is None:
            save_path = RESULTS_DIR / "confusion_matrix_normalized.png"
        
        # Normalize
        cm_normalized = self.confusion_mat.astype('float') / self.confusion_mat.sum(axis=1)[:, np.newaxis]
        
        # Create figure
        plt.figure(figsize=(10, 8))
        
        # Plot heatmap
        sns.heatmap(
            cm_normalized, 
            annot=True, 
            fmt='.2%', 
            cmap='Blues',
            xticklabels=self.class_names,
            yticklabels=self.class_names,
            cbar_kws={'label': 'Percentage'}
        )
        
        plt.title('Normalized Confusion Matrix - Multi-Vector Attack Detection', fontsize=14, fontweight='bold')
        plt.xlabel('Predicted Label', fontsize=12)
        plt.ylabel('True Label', fontsize=12)
        plt.tight_layout()
        
        # Save
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✓ Normalized confusion matrix saved to {save_path}")
        plt.close()
        
    def save_evaluation_report(self, save_path=None):
        """
        Save evaluation metrics to JSON file for thesis documentation.
        
        Args:
            save_path: Path to save the report (default: EVALUATION_REPORT)
        """
        if not self.metrics:
            raise ValueError("Metrics not computed. Call evaluate_comprehensive() first.")
        
        if save_path is None:
            save_path = EVALUATION_REPORT
        
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        
        # Add confusion matrix to report
        report = {
            'metrics': self.metrics,
            'confusion_matrix': self.confusion_mat.tolist() if self.confusion_mat is not None else None,
            'class_names': self.class_names
        }
        
        with open(save_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n✓ Evaluation report saved to {save_path}")
        
    def generate_thesis_tables(self):
        """Generate formatted tables for thesis documentation."""
        if not self.metrics:
            raise ValueError("Metrics not computed. Call evaluate_comprehensive() first.")
        
        print("\n" + "="*60)
        print("THESIS-READY TABLES")
        print("="*60)
        
        # Table 1: Overall Performance
        print("\nTable 1: Overall Model Performance")
        print("-" * 60)
        print(f"{'Metric':<25s} {'Value':>15s}")
        print("-" * 60)
        print(f"{'Accuracy':<25s} {self.metrics['overall']['accuracy']*100:>14.2f}%")
        print(f"{'Precision (Macro)':<25s} {self.metrics['overall']['precision_macro']*100:>14.2f}%")
        print(f"{'Recall (Macro)':<25s} {self.metrics['overall']['recall_macro']*100:>14.2f}%")
        print(f"{'F1-Score (Macro)':<25s} {self.metrics['overall']['f1_macro']*100:>14.2f}%")
        print(f"{'Precision (Weighted)':<25s} {self.metrics['overall']['precision_weighted']*100:>14.2f}%")
        print(f"{'Recall (Weighted)':<25s} {self.metrics['overall']['recall_weighted']*100:>14.2f}%")
        print(f"{'F1-Score (Weighted)':<25s} {self.metrics['overall']['f1_weighted']*100:>14.2f}%")
        print("-" * 60)
        
        # Table 2: Per-Class Performance
        print("\nTable 2: Per-Class Performance Metrics")
        print("-" * 80)
        print(f"{'Attack Type':<20s} {'Precision':>15s} {'Recall':>15s} {'F1-Score':>15s}")
        print("-" * 80)
        for class_name, metrics in self.metrics['per_class'].items():
            print(f"{class_name:<20s} {metrics['precision']*100:>14.2f}% {metrics['recall']*100:>14.2f}% {metrics['f1_score']*100:>14.2f}%")
        print("-" * 80)
        
        print("\n" + "="*60)


def main():
    """Demonstrate model evaluation."""
    # This would typically be called after training
    # For demonstration, we'll create dummy data
    
    # Simulate predictions (replace with actual model predictions)
    np.random.seed(42)
    n_samples = 1000
    y_true = np.random.randint(0, 4, n_samples)
    y_pred = y_true.copy()
    # Add some errors
    error_indices = np.random.choice(n_samples, size=50, replace=False)
    y_pred[error_indices] = np.random.randint(0, 4, 50)
    
    # Evaluate
    evaluator = ModelEvaluator()
    evaluator.evaluate_comprehensive(y_true, y_pred)
    
    # Generate visualizations
    evaluator.plot_confusion_matrix()
    evaluator.plot_normalized_confusion_matrix()
    
    # Save report
    evaluator.save_evaluation_report()
    
    # Generate thesis tables
    evaluator.generate_thesis_tables()
    
    return evaluator


if __name__ == "__main__":
    evaluator = main()
