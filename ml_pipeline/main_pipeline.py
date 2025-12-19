"""
Main ML Pipeline Script
Executes complete pipeline per SRS requirements
"""
import sys
from pathlib import Path
import logging
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from data_loader import DataLoader
from data_cleaning import DataCleaner
from feature_engineering import FeatureEngineer
from eda import EDA
from model_training import ModelTrainer
from model_evaluation import ModelEvaluator
from explainability import ModelExplainability

# Configure logging
# Setup logging
log_dir = Path(__file__).parent
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_dir / 'pipeline.log')
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Execute complete ML pipeline"""
    logger.info("=" * 60)
    logger.info("Starting ML Pipeline - Transport Delay Prediction")
    logger.info("=" * 60)
    
    # Setup paths
    base_dir = Path(__file__).parent
    data_dir = base_dir / "data"
    output_dir = base_dir / "outputs"
    models_dir = base_dir / "models"
    
    for dir_path in [data_dir, output_dir, models_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # Step 1: Data Loading (FR-1, FR-2)
        logger.info("\n" + "=" * 60)
        logger.info("STEP 1: Data Loading")
        logger.info("=" * 60)
        
        loader = DataLoader()
        df_raw = loader.load_and_validate()
        logger.info(f"Loaded {len(df_raw)} records with {len(df_raw.columns)} columns")
        
        # Step 2: Data Cleaning (FR-3 to FR-8)
        logger.info("\n" + "=" * 60)
        logger.info("STEP 2: Data Cleaning & Preprocessing")
        logger.info("=" * 60)
        
        cleaner = DataCleaner(df_raw)
        df_cleaned = cleaner.clean_all()
        
        # Save cleaned data
        cleaned_path = output_dir / "cleaned_dataset.csv"
        cleaner.save_cleaned_data(str(cleaned_path))
        logger.info(f"Cleaned dataset saved to {cleaned_path}")
        
        # Step 3: Feature Engineering (FR-9 to FR-13)
        logger.info("\n" + "=" * 60)
        logger.info("STEP 3: Feature Engineering")
        logger.info("=" * 60)
        
        engineer = FeatureEngineer(df_cleaned)
        df_features = engineer.engineer_all_features()
        logger.info(f"Engineered features. Dataset shape: {df_features.shape}")
        
        # Step 4: Exploratory Data Analysis (FR-14 to FR-16)
        logger.info("\n" + "=" * 60)
        logger.info("STEP 4: Exploratory Data Analysis")
        logger.info("=" * 60)
        
        eda = EDA(df_features, str(output_dir / "visualizations"))
        eda_visualizations = eda.generate_all_visualizations()
        logger.info(f"Generated {len(eda_visualizations)} EDA visualizations")
        
        # Step 5: Model Training (FR-17, FR-18)
        logger.info("\n" + "=" * 60)
        logger.info("STEP 5: Model Training")
        logger.info("=" * 60)
        
        trainer = ModelTrainer(df_features, target_col='delay_minutes', random_state=42)
        models = trainer.train_all_models()
        logger.info(f"Trained {len(models)} models")
        
        # Save models
        trainer.save_models(str(models_dir))
        
        # Step 6: Model Evaluation (FR-19 to FR-21)
        logger.info("\n" + "=" * 60)
        logger.info("STEP 6: Model Evaluation")
        logger.info("=" * 60)
        
        # Get training data for evaluation
        X, y = trainer.prepare_features()
        X_train, X_test, y_train, y_test = trainer.split_data(X, y)
        
        evaluator = ModelEvaluator(
            models, X_test, y_test, 
            scalers=trainer.scalers, 
            random_state=42
        )
        evaluation_results = evaluator.evaluate_all_models(X_train, y_train)
        
        # Save evaluation results
        eval_path = output_dir / "evaluation_results.csv"
        evaluator.save_results(str(eval_path))
        logger.info(f"Evaluation results saved to {eval_path}")
        
        # Get best model
        best_model_name, best_metrics = evaluator.get_best_model()
        logger.info(f"\nBest Model: {best_model_name}")
        logger.info(f"Best Model MAE: {best_metrics.get('MAE', 'N/A'):.2f}")
        
        # Step 7: Model Explainability (FR-22 to FR-24)
        logger.info("\n" + "=" * 60)
        logger.info("STEP 7: Model Explainability")
        logger.info("=" * 60)
        
        best_model = models[best_model_name]
        explainer = ModelExplainability(
            best_model, best_model_name, trainer.feature_names,
            X_train=X_train, output_dir=str(output_dir / "visualizations")
        )
        explainability_results = explainer.generate_all_explanations()
        logger.info("Explainability analysis completed")
        
        # Save best model to backend
        logger.info("\n" + "=" * 60)
        logger.info("STEP 8: Integration with Backend")
        logger.info("=" * 60)
        
        backend_models_dir = Path(__file__).parent.parent / "backend" / "ml_models"
        backend_models_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy best model
        import shutil
        best_model_path = models_dir / f"{best_model_name}.pkl"
        backend_model_path = backend_models_dir / "trained_model.pkl"
        
        if best_model_path.exists():
            shutil.copy(best_model_path, backend_model_path)
            logger.info(f"Best model copied to {backend_model_path}")
        
        # Save feature config
        import json
        feature_config = {
            'feature_names': trainer.feature_names,
            'model_name': best_model_name,
            'mae': best_metrics.get('MAE', 0),
            'target': 'delay_minutes'
        }
        config_path = backend_models_dir / "feature_config.json"
        with open(config_path, 'w') as f:
            json.dump(feature_config, f, indent=2)
        logger.info(f"Feature config saved to {config_path}")
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)
        logger.info(f"✓ Cleaned dataset: {cleaned_path}")
        logger.info(f"✓ Evaluation results: {eval_path}")
        logger.info(f"✓ Best model: {best_model_name} (MAE: {best_metrics.get('MAE', 0):.2f})")
        logger.info(f"✓ Model saved to backend: {backend_model_path}")
        logger.info(f"✓ Visualizations: {output_dir / 'visualizations'}")
        logger.info("=" * 60)
        
        return {
            'success': True,
            'best_model': best_model_name,
            'metrics': best_metrics,
            'cleaned_data_path': str(cleaned_path),
            'evaluation_path': str(eval_path)
        }
    
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
        return {'success': False, 'error': str(e)}


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result.get('success') else 1)

