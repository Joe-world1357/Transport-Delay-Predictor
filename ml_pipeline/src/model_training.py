"""
Model Training Module (FR-17, FR-18)
Trains multiple ML models for delay prediction
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ModelTrainer:
    """Trains multiple ML models per SRS requirements"""
    
    def __init__(self, df: pd.DataFrame, target_col: str = 'delay_minutes', random_state: int = 42):
        """
        Initialize model trainer
        
        Args:
            df: DataFrame with features and target
            target_col: Name of target column
            random_state: Random seed for reproducibility
        """
        self.df = df.copy()
        self.target_col = target_col
        self.random_state = random_state
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.feature_names = None
        
        np.random.seed(random_state)
    
    def prepare_features(self) -> tuple[pd.DataFrame, pd.Series]:
        """
        Prepare features and target for training
        
        Returns:
            Tuple of (X_features, y_target)
        """
        logger.info("Preparing features for training...")
        
        # Select feature columns
        feature_cols = [
            'route_id', 'weather', 'passenger_count', 
            'time_of_day', 'is_weekend'
        ]
        
        # Get available features
        available_features = [col for col in feature_cols if col in self.df.columns]
        
        X = self.df[available_features].copy()
        y = self.df[self.target_col].copy()
        
        # Handle missing values - numeric columns with median, categorical with mode
        for col in X.columns:
            if X[col].dtype in [np.int64, np.float64]:
                X[col] = X[col].fillna(X[col].median())
            else:
                X[col] = X[col].fillna(X[col].mode()[0] if not X[col].mode().empty else 0)
        
        # One-hot encode weather for better performance
        if 'weather' in X.columns:
            weather_dummies = pd.get_dummies(X['weather'], prefix='weather')
            X = pd.concat([X.drop('weather', axis=1), weather_dummies], axis=1)
        
        # Store feature names
        self.feature_names = list(X.columns)
        
        logger.info(f"Prepared {len(X.columns)} features for {len(X)} samples")
        
        return X, y
    
    def split_data(self, X: pd.DataFrame, y: pd.Series, test_size: float = 0.2):
        """
        Split dataset into training and testing subsets (FR-17)
        
        Args:
            X: Features
            y: Target
            test_size: Proportion for test set
            
        Returns:
            X_train, X_test, y_train, y_test
        """
        logger.info(f"Splitting data: {1-test_size:.0%} train, {test_size:.0%} test")
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=self.random_state
        )
        
        logger.info(f"Training set: {len(X_train)} samples")
        logger.info(f"Test set: {len(X_test)} samples")
        
        return X_train, X_test, y_train, y_test
    
    def train_linear_regression(self, X_train: pd.DataFrame, y_train: pd.Series):
        """Train Linear Regression model"""
        logger.info("Training Linear Regression...")
        
        # Scale features for linear regression
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        self.scalers['linear'] = scaler
        
        model = LinearRegression()
        model.fit(X_train_scaled, y_train)
        self.models['linear_regression'] = model
        
        logger.info("Linear Regression trained")
        return model
    
    def train_random_forest(self, X_train: pd.DataFrame, y_train: pd.Series):
        """Train Random Forest Regressor"""
        logger.info("Training Random Forest Regressor...")
        
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=self.random_state,
            n_jobs=-1
        )
        model.fit(X_train, y_train)
        self.models['random_forest'] = model
        
        logger.info("Random Forest trained")
        return model
    
    def train_gradient_boosting(self, X_train: pd.DataFrame, y_train: pd.Series):
        """Train Gradient Boosting Regressor"""
        logger.info("Training Gradient Boosting Regressor...")
        
        model = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=self.random_state
        )
        model.fit(X_train, y_train)
        self.models['gradient_boosting'] = model
        
        logger.info("Gradient Boosting trained")
        return model
    
    def train_knn(self, X_train: pd.DataFrame, y_train: pd.Series):
        """Train k-Nearest Neighbors Regressor"""
        logger.info("Training k-Nearest Neighbors Regressor...")
        
        # Scale features for KNN
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        self.scalers['knn'] = scaler
        
        model = KNeighborsRegressor(n_neighbors=5)
        model.fit(X_train_scaled, y_train)
        self.models['knn'] = model
        
        logger.info("k-NN trained")
        return model
    
    def train_all_models(self) -> dict:
        """
        Train all four models as per SRS FR-18
        
        Returns:
            Dictionary of trained models
        """
        logger.info("Training all models...")
        
        # Prepare data
        X, y = self.prepare_features()
        X_train, X_test, y_train, y_test = self.split_data(X, y)
        
        # Store test data for evaluation
        self.X_test = X_test
        self.y_test = y_test
        
        # Train all models
        self.train_linear_regression(X_train, y_train)
        self.train_random_forest(X_train, y_train)
        self.train_gradient_boosting(X_train, y_train)
        self.train_knn(X_train, y_train)
        
        logger.info(f"All {len(self.models)} models trained successfully")
        
        return self.models
    
    def save_models(self, output_dir: str = "models"):
        """Save all trained models"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for name, model in self.models.items():
            model_path = output_path / f"{name}.pkl"
            joblib.dump(model, model_path)
            logger.info(f"Saved {name} to {model_path}")
        
        # Save scalers
        for name, scaler in self.scalers.items():
            scaler_path = output_path / f"{name}_scaler.pkl"
            joblib.dump(scaler, scaler_path)
        
        # Save feature names
        if self.feature_names:
            import json
            config = {
                'feature_names': self.feature_names,
                'target': self.target_col
            }
            config_path = output_path / "feature_config.json"
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            logger.info(f"Saved feature config to {config_path}")
    
    def get_best_model(self) -> tuple[str, object]:
        """
        Get the best model (to be determined by evaluation)
        For now, returns Random Forest as default
        """
        return 'random_forest', self.models.get('random_forest')

