"""
Dataset upload and model training routes
"""
from fastapi import APIRouter, HTTPException, status, UploadFile, File
from typing import Dict
import logging
import pandas as pd
from pathlib import Path
import subprocess
import sys

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload-dataset")
async def upload_dataset(file: UploadFile = File(..., description="CSV dataset file")) -> Dict:
    """
    Upload dataset and train models
    
    Args:
        file: CSV file with transport data
        
    Returns:
        Training results and model comparison
    """
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be a CSV file"
            )
        
        # Save uploaded file
        # Get the project root (go up from backend/app/api/routes to project root)
        # Path: backend/app/api/routes/dataset.py -> go up 4 levels
        project_root = Path(__file__).parent.parent.parent.parent.parent
        upload_dir = project_root / "ml_pipeline" / "data"
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / "dirty_transport_dataset.csv"
        
        # Save file
        content = await file.read()
        with open(file_path, 'wb') as f:
            f.write(content)
        
        logger.info(f"Dataset uploaded: {file_path}")
        
        # Run ML pipeline - use absolute path from project root
        pipeline_script = project_root / "ml_pipeline" / "main_pipeline.py"
        
        if not pipeline_script.exists():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Pipeline script not found at {pipeline_script}"
            )
        
        try:
            # Run pipeline from project root directory
            result = subprocess.run(
                [sys.executable, str(pipeline_script)],
                cwd=str(project_root),  # Run from project root
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            # CRITICAL: Only fail if pipeline actually failed (non-zero exit code)
            # Log output is NORMAL - INFO messages are NOT errors!
            if result.returncode != 0:
                # Combine stderr and stdout to find actual errors
                all_output = result.stderr + '\n' + result.stdout
                
                # Filter out info messages, warnings, and normal log output
                error_lines = []
                for line in all_output.split('\n'):
                    line = line.strip()
                    # Skip normal log messages and warnings
                    if line and not any(skip in line.lower() for skip in [
                        'shap not available',
                        'will use feature importance only',
                        'warning',
                        'userwarning',
                        'info -',
                        'starting ml pipeline',
                        'step 1:',
                        'step 2:',
                        'step 3:',
                        'step 4:',
                        'step 5:',
                        'step 6:',
                        'step 7:',
                        'step 8:',
                        '============================================================',
                        'data loading',
                        'data cleaning',
                        'feature engineering',
                        'exploratory data analysis',
                        'model training',
                        'model evaluation',
                        'model explainability',
                        'integration with backend',
                        'pipeline completed'
                    ]):
                        # Only include lines that look like ACTUAL errors (not log messages)
                        if any(error_indicator in line.lower() for error_indicator in [
                            'traceback',
                            'exception:',
                            'fatal error',
                            'cannot open file',
                            'no such file or directory',
                            'file not found',
                            'import error',
                            'module not found'
                        ]) and 'info -' not in line.lower():
                            error_lines.append(line)
                
                error_msg = '\n'.join(error_lines) if error_lines else all_output[:500]
                logger.error(f"Pipeline error (exit {result.returncode}): {error_msg}")
                
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Model training failed: {error_msg[:500]}"
                )
            
            # Pipeline succeeded - log info but don't treat as error
            logger.info("Pipeline completed successfully")
            
            # Log any warnings but don't fail
            if result.stderr:
                warnings = [line for line in result.stderr.split('\n') 
                           if line.strip() and any(w in line.lower() for w in ['shap', 'warning', 'userwarning'])]
                if warnings:
                    logger.info(f"Pipeline completed with warnings: {'; '.join(warnings[:3])}")
            
            # Load comparison results
            comparison_path = project_root / "ml_pipeline" / "outputs" / "evaluation_results.csv"
            
            if comparison_path.exists():
                comparison_df = pd.read_csv(comparison_path)
                comparison = comparison_df.to_dict('records')
            else:
                comparison = []
            
            # Get available models
            models_dir = project_root / "ml_pipeline" / "models"
            available_models = []
            
            model_names = {
                'gradient_boosting': 'Gradient Boosting',
                'random_forest': 'Random Forest',
                'linear_regression': 'Linear Regression',
                'knn': 'k-Nearest Neighbors'
            }
            
            # Find best model
            best_model_name = None
            if comparison:
                best_model = min(comparison, key=lambda x: float(x.get('MAE', float('inf'))))
                best_model_name = best_model.get('Model', '').replace('_', ' ')
            
            for model_file in models_dir.glob('*.pkl'):
                if model_file.stem in ['linear_scaler', 'knn_scaler']:
                    continue
                
                model_key = model_file.stem
                is_best = best_model_name and model_key.replace('_', ' ') in best_model_name
                
                available_models.append({
                    'name': model_key,
                    'display_name': model_names.get(model_key, model_key.replace('_', ' ').title()),
                    'is_best': is_best
                })
            
            return {
                "message": "Dataset uploaded and models trained successfully",
                "comparison": comparison,
                "models": available_models,
                "file_size": len(content)
            }
        
        except subprocess.TimeoutExpired:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Model training timed out. Please try with a smaller dataset."
            )
        except Exception as e:
            logger.error(f"Training error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Training failed: {str(e)}"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


@router.get("/dataset-preview")
async def get_dataset_preview() -> Dict:
    """
    Get dataset preview and statistics
    
    Returns:
        Dataset preview (first 10 rows) and statistics
    """
    try:
        # Get project root
        project_root = Path(__file__).parent.parent.parent.parent.parent
        cleaned_path = project_root / "ml_pipeline" / "outputs" / "cleaned_dataset.csv"
        
        if not cleaned_path.exists():
            return {
                "preview": [],
                "stats": {},
                "message": "No dataset available. Upload and train models first."
            }
        
        df = pd.read_csv(cleaned_path)
        
        # Get statistics
        stats = {
            "total_records": len(df),
            "total_features": len(df.columns),
        }
        
        # Add delay statistics if available
        if 'delay_minutes' in df.columns:
            stats.update({
                "mean_delay": float(df['delay_minutes'].mean()),
                "max_delay": float(df['delay_minutes'].max()),
                "min_delay": float(df['delay_minutes'].min()),
                "std_delay": float(df['delay_minutes'].std())
            })
        
        # Get preview (first 10 rows)
        preview = df.head(10).to_dict('records')
        
        return {
            "preview": preview,
            "stats": stats,
            "message": "Dataset preview loaded"
        }
    
    except Exception as e:
        logger.error(f"Error loading dataset preview: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load dataset preview: {str(e)}"
        )


@router.get("/eda-visualizations")
async def get_eda_visualizations() -> Dict:
    """
    Get EDA visualization URLs
    
    Returns:
        Dictionary with visualization image URLs/paths
    """
    try:
        # Get project root
        project_root = Path(__file__).parent.parent.parent.parent.parent
        viz_dir = project_root / "ml_pipeline" / "outputs" / "visualizations"
        
        visualizations = {}
        
        # Map visualization files
        viz_files = {
            "delay_distribution": "delay_distribution.png",
            "weather_impact": "weather_impact.png",
            "time_of_day_impact": "time_of_day_impact.png",
            "feature_importance": "feature_importance_gradient_boosting.png"
        }
        
        for key, filename in viz_files.items():
            file_path = viz_dir / filename
            if file_path.exists():
                # Return relative path that frontend can access
                visualizations[key] = f"/api/v1/visualizations/{filename}"
        
        return {
            "visualizations": visualizations,
            "message": "Visualizations loaded"
        }
    
    except Exception as e:
        logger.error(f"Error loading visualizations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load visualizations: {str(e)}"
        )


@router.get("/visualizations/{filename}")
async def get_visualization(filename: str):
    """
    Serve visualization images
    
    Args:
        filename: Name of the visualization file
        
    Returns:
        Image file
    """
    from fastapi.responses import FileResponse
    
    try:
        # Get project root
        project_root = Path(__file__).parent.parent.parent.parent.parent
        viz_dir = project_root / "ml_pipeline" / "outputs" / "visualizations"
        file_path = viz_dir / filename
        
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Visualization {filename} not found"
            )
        
        return FileResponse(
            str(file_path),
            media_type="image/png",
            filename=filename
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving visualization: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to serve visualization: {str(e)}"
        )


@router.get("/model-comparison")
async def get_model_comparison() -> Dict:
    """
    Get model comparison results
    
    Returns:
        Comparison data for all models
    """
    try:
        # Get project root (go up 4 levels from routes/)
        project_root = Path(__file__).parent.parent.parent.parent.parent
        comparison_path = project_root / "ml_pipeline" / "outputs" / "evaluation_results.csv"
        
        if not comparison_path.exists():
            return {
                "comparison": [],
                "message": "No comparison data available. Train models first."
            }
        
        comparison_df = pd.read_csv(comparison_path)
        comparison = comparison_df.to_dict('records')
        
        return {
            "comparison": comparison,
            "message": "Comparison data loaded"
        }
    
    except Exception as e:
        logger.error(f"Error loading comparison: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load comparison: {str(e)}"
        )

