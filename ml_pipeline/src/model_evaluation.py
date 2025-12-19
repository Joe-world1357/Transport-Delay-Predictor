"""
Model Evaluation Module (FR-19 to FR-21)
Evaluates models using MAE, MSE, RMSE, R² and cross-validation
"""
import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import cross_val_score, KFold
import logging

logger = logging.getLogger(__name__)


class ModelEvaluator:
    """Evaluates ML models per SRS requirements"""
    
    def __init__(self, models: dict, X_test: pd.DataFrame, y_test: pd.Series, 
                 scalers: dict = None, random_state: int = 42):
        """
        Initialize evaluator
        
        Args:
            models: Dictionary of trained models
            X_test: Test features
            y_test: Test target
            scalers: Dictionary of scalers (for models that need scaling)
            random_state: Random seed
        """
        self.models = models
        self.X_test = X_test
        self.y_test = y_test
        self.scalers = scalers or {}
        self.random_state = random_state
        self.results = {}
    
    def evaluate_model(self, model_name: str, model, X_train: pd.DataFrame = None, 
                       y_train: pd.Series = None) -> dict:
        """
        Evaluate a single model (FR-19)
        
        Metrics: MAE, MSE, RMSE, R²
        
        Returns:
            Dictionary of metrics
        """
        # Prepare test data
        if model_name in ['linear_regression', 'knn'] and model_name in self.scalers:
            X_test_scaled = self.scalers[model_name].transform(self.X_test)
            y_pred = model.predict(X_test_scaled)
        else:
            y_pred = model.predict(self.X_test)
        
        # Calculate metrics
        mae = mean_absolute_error(self.y_test, y_pred)
        mse = mean_squared_error(self.y_test, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(self.y_test, y_pred)
        
        metrics = {
            'MAE': mae,
            'MSE': mse,
            'RMSE': rmse,
            'R²': r2
        }
        
        logger.info(f"{model_name} - MAE: {mae:.2f}, RMSE: {rmse:.2f}, R²: {r2:.3f}")
        
        return metrics
    
    def cross_validate(self, model_name: str, model, X_train: pd.DataFrame, 
                      y_train: pd.Series, cv: int = 5) -> dict:
        """
        Perform cross-validation (FR-20)
        
        Args:
            model_name: Name of model
            model: Model object
            X_train: Training features
            y_train: Training target
            cv: Number of folds
            
        Returns:
            Dictionary with CV scores
        """
        logger.info(f"Performing {cv}-fold cross-validation for {model_name}...")
        
        # Prepare data for CV
        if model_name in ['linear_regression', 'knn'] and model_name in self.scalers:
            scaler = self.scalers[model_name]
            X_train_scaled = scaler.transform(X_train)
        else:
            X_train_scaled = X_train
        
        # Cross-validation with MAE
        kfold = KFold(n_splits=cv, shuffle=True, random_state=self.random_state)
        cv_scores = cross_val_score(model, X_train_scaled, y_train, 
                                    cv=kfold, scoring='neg_mean_absolute_error')
        
        cv_mae = -cv_scores.mean()
        cv_std = cv_scores.std()
        
        cv_results = {
            'CV_MAE_mean': cv_mae,
            'CV_MAE_std': cv_std,
            'CV_scores': cv_scores.tolist()
        }
        
        logger.info(f"{model_name} CV MAE: {cv_mae:.2f} (+/- {cv_std:.2f})")
        
        return cv_results
    
    def evaluate_all_models(self, X_train: pd.DataFrame = None, 
                            y_train: pd.Series = None) -> pd.DataFrame:
        """
        Evaluate all models and create comparison table (FR-21)
        
        Returns:
            DataFrame with evaluation results
        """
        logger.info("Evaluating all models...")
        
        results_list = []
        
        for model_name, model in self.models.items():
            # Test set evaluation
            metrics = self.evaluate_model(model_name, model, X_train, y_train)
            
            # Cross-validation if training data provided
            cv_results = {}
            if X_train is not None and y_train is not None:
                cv_results = self.cross_validate(model_name, model, X_train, y_train)
            
            # Combine results
            result = {
                'Model': model_name,
                **metrics,
                **cv_results
            }
            
            results_list.append(result)
            self.results[model_name] = {**metrics, **cv_results}
        
        # Create comparison DataFrame
        comparison_df = pd.DataFrame(results_list)
        
        logger.info("Model evaluation completed")
        return comparison_df
    
    def get_best_model(self) -> tuple[str, dict]:
        """
        Get best model based on MAE (lower is better)
        
        Returns:
            Tuple of (model_name, metrics)
        """
        if not self.results:
            raise ValueError("No evaluation results available. Run evaluate_all_models first.")
        
        best_model = min(self.results.items(), key=lambda x: x[1].get('MAE', float('inf')))
        return best_model
    
    def save_results(self, output_path: str):
        """Save evaluation results to CSV"""
        if not self.results:
            raise ValueError("No results to save")
        
        results_list = []
        for model_name, metrics in self.results.items():
            result = {'Model': model_name, **metrics}
            results_list.append(result)
        
        df = pd.DataFrame(results_list)
        df.to_csv(output_path, index=False)
        logger.info(f"Evaluation results saved to {output_path}")

