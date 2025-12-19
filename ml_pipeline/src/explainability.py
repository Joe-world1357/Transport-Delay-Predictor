"""
Model Explainability Module (FR-22 to FR-24)
Computes feature importance and SHAP values
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Try to import SHAP, but make it optional
try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    logger.warning("SHAP not available. Will use feature importance only.")


class ModelExplainability:
    """Provides model explainability per SRS requirements"""
    
    def __init__(self, model, model_name: str, feature_names: list, 
                 X_train: pd.DataFrame = None, output_dir: str = "outputs/visualizations"):
        """
        Initialize explainability analyzer
        
        Args:
            model: Trained model
            model_name: Name of the model
            feature_names: List of feature names
            X_train: Training data (for SHAP)
            output_dir: Directory to save visualizations
        """
        self.model = model
        self.model_name = model_name
        self.feature_names = feature_names
        self.X_train = X_train
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def compute_feature_importance(self) -> pd.DataFrame:
        """
        Compute feature importance (FR-22)
        
        Returns:
            DataFrame with feature names and importance scores
        """
        logger.info(f"Computing feature importance for {self.model_name}...")
        
        importance_dict = {}
        
        # Tree-based models have feature_importances_
        if hasattr(self.model, 'feature_importances_'):
            importances = self.model.feature_importances_
            importance_dict = dict(zip(self.feature_names, importances))
        
        # Linear models have coefficients
        elif hasattr(self.model, 'coef_'):
            coefs = np.abs(self.model.coef_)
            # Normalize to 0-1 range
            if coefs.max() > 0:
                coefs = coefs / coefs.max()
            importance_dict = dict(zip(self.feature_names, coefs))
        
        # KNN doesn't have direct importance, use permutation importance approximation
        else:
            logger.warning(f"{self.model_name} doesn't have direct feature importance")
            # Assign equal importance as fallback
            importance_dict = {name: 1.0 / len(self.feature_names) 
                             for name in self.feature_names}
        
        # Create DataFrame
        importance_df = pd.DataFrame([
            {'feature': name, 'importance': score}
            for name, score in importance_dict.items()
        ])
        
        # Sort by importance
        importance_df = importance_df.sort_values('importance', ascending=False)
        
        logger.info(f"Feature importance computed. Top feature: {importance_df.iloc[0]['feature']}")
        
        return importance_df
    
    def compute_shap_values(self) -> np.ndarray:
        """
        Compute SHAP values if available (FR-22)
        
        Returns:
            SHAP values array or None
        """
        if not SHAP_AVAILABLE:
            logger.warning("SHAP not available, skipping SHAP values")
            return None
        
        if self.X_train is None:
            logger.warning("Training data not provided, cannot compute SHAP values")
            return None
        
        try:
            logger.info(f"Computing SHAP values for {self.model_name}...")
            
            # Create SHAP explainer
            if hasattr(self.model, 'predict_proba'):
                explainer = shap.TreeExplainer(self.model)
            else:
                explainer = shap.Explainer(self.model, self.X_train)
            
            # Compute SHAP values
            shap_values = explainer(self.X_train)
            
            logger.info("SHAP values computed successfully")
            return shap_values
        
        except Exception as e:
            logger.error(f"Error computing SHAP values: {str(e)}")
            return None
    
    def visualize_feature_importance(self, importance_df: pd.DataFrame = None) -> str:
        """
        Visualize feature contributions (FR-23)
        
        Args:
            importance_df: DataFrame with feature importance (if None, computes it)
            
        Returns:
            Path to saved visualization
        """
        logger.info(f"Visualizing feature importance for {self.model_name}...")
        
        if importance_df is None:
            importance_df = self.compute_feature_importance()
        
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        fig.suptitle(f'Feature Importance - {self.model_name}', fontsize=16, fontweight='bold')
        
        # Horizontal bar chart
        top_features = importance_df.head(10)
        axes[0].barh(range(len(top_features)), top_features['importance'], 
                    color='steelblue', edgecolor='black')
        axes[0].set_yticks(range(len(top_features)))
        axes[0].set_yticklabels(top_features['feature'])
        axes[0].set_xlabel('Importance Score')
        axes[0].set_title('Top 10 Features')
        axes[0].invert_yaxis()
        axes[0].grid(True, alpha=0.3, axis='x')
        
        # Pie chart for top 5
        top_5 = importance_df.head(5)
        other_sum = importance_df.iloc[5:]['importance'].sum() if len(importance_df) > 5 else 0
        
        if other_sum > 0:
            plot_data = pd.concat([top_5, pd.DataFrame([{'feature': 'Others', 'importance': other_sum}])])
        else:
            plot_data = top_5
        
        axes[1].pie(plot_data['importance'], labels=plot_data['feature'], 
                   autopct='%1.1f%%', startangle=90)
        axes[1].set_title('Feature Importance Distribution (Top 5)')
        
        plt.tight_layout()
        
        output_path = self.output_dir / f"feature_importance_{self.model_name}.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Feature importance visualization saved to {output_path}")
        return str(output_path)
    
    def visualize_shap(self, shap_values=None) -> str:
        """
        Visualize SHAP values if available
        
        Args:
            shap_values: Pre-computed SHAP values
            
        Returns:
            Path to saved visualization or None
        """
        if shap_values is None:
            shap_values = self.compute_shap_values()
        
        if shap_values is None:
            return None
        
        try:
            logger.info(f"Visualizing SHAP values for {self.model_name}...")
            
            fig = plt.figure(figsize=(12, 8))
            shap.summary_plot(shap_values, self.X_train, feature_names=self.feature_names, 
                           show=False, plot_type="bar")
            plt.title(f'SHAP Feature Importance - {self.model_name}', fontsize=14, fontweight='bold')
            
            output_path = self.output_dir / f"shap_values_{self.model_name}.png"
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"SHAP visualization saved to {output_path}")
            return str(output_path)
        
        except Exception as e:
            logger.error(f"Error visualizing SHAP values: {str(e)}")
            return None
    
    def interpret_features(self, importance_df: pd.DataFrame = None) -> dict:
        """
        Provide interpretation of influential features (FR-24)
        
        Args:
            importance_df: DataFrame with feature importance
            
        Returns:
            Dictionary with interpretations
        """
        if importance_df is None:
            importance_df = self.compute_feature_importance()
        
        top_3 = importance_df.head(3)
        
        interpretation = {
            'top_features': top_3.to_dict('records'),
            'summary': f"The top 3 most influential features are: {', '.join(top_3['feature'].tolist())}",
            'insights': []
        }
        
        # Generate insights
        for idx, row in top_3.iterrows():
            feature = row['feature']
            importance = row['importance']
            
            if 'weather' in feature.lower():
                interpretation['insights'].append(
                    f"Weather conditions ({importance:.1%} importance) significantly impact delays"
                )
            elif 'time' in feature.lower():
                interpretation['insights'].append(
                    f"Time of day ({importance:.1%} importance) is a key factor in delays"
                )
            elif 'passenger' in feature.lower():
                interpretation['insights'].append(
                    f"Passenger count ({importance:.1%} importance) affects delay predictions"
                )
        
        logger.info("Feature interpretation generated")
        return interpretation
    
    def generate_all_explanations(self) -> dict:
        """
        Generate all explainability outputs
        
        Returns:
            Dictionary with all results
        """
        logger.info(f"Generating all explainability outputs for {self.model_name}...")
        
        importance_df = self.compute_feature_importance()
        
        results = {
            'feature_importance': importance_df,
            'visualization': self.visualize_feature_importance(importance_df),
            'interpretation': self.interpret_features(importance_df)
        }
        
        # Try SHAP if available
        shap_values = self.compute_shap_values()
        if shap_values is not None:
            results['shap_values'] = shap_values
            results['shap_visualization'] = self.visualize_shap(shap_values)
        
        return results

