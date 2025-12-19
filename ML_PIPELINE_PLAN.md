# ML Pipeline Implementation Plan
## Based on SRS Requirements

## Overview

This document outlines the implementation plan for the ML pipeline component as specified in the SRS document. The frontend and backend are already complete - this focuses on the data science/ML training pipeline.

## Current System Status

✅ **Completed:**
- Frontend web application
- Backend API (FastAPI)
- API endpoints for predictions
- Model wrapper with mock predictions

⏳ **To Implement:**
- Data cleaning and preprocessing pipeline
- Feature engineering
- Model training (4 models as per SRS)
- Model evaluation and comparison
- Explainability analysis
- Integration with existing backend

## SRS Requirements Mapping

### 3.1 Data Loading (FR-1, FR-2)
**Status:** ⏳ To Implement

**Tasks:**
- [ ] Create data loading module
- [ ] Load `dirty_transport_dataset.csv`
- [ ] Validate column existence
- [ ] Validate data types

**Location:** `ml_pipeline/data_loader.py`

### 3.2 Data Cleaning & Preprocessing (FR-3 to FR-8)
**Status:** ⏳ To Implement

**Tasks:**
- [ ] Handle missing values (document strategy)
- [ ] Standardize timestamps to ISO format
- [ ] Normalize weather categories
- [ ] Unify route identifier formats
- [ ] Treat outliers in passenger counts (IQR)
- [ ] Handle invalid GPS coordinates

**Location:** `ml_pipeline/data_cleaning.py`

### 3.3 Feature Engineering (FR-9 to FR-13)
**Status:** ⏳ To Implement

**Tasks:**
- [ ] Compute delay duration (target variable)
- [ ] Generate time-based features (time of day)
- [ ] Identify weekend trips
- [ ] Compute weather severity index
- [ ] Calculate route frequency

**Location:** `ml_pipeline/feature_engineering.py`

### 3.4 Exploratory Data Analysis (FR-14 to FR-16)
**Status:** ⏳ To Implement

**Tasks:**
- [ ] Visualize delay distributions
- [ ] Analyze weather impact on delays
- [ ] Analyze time of day vs delays
- [ ] Save visualizations for report

**Location:** `ml_pipeline/eda.py`

### 3.5 Machine Learning Modeling (FR-17, FR-18)
**Status:** ⏳ To Implement

**Required Models:**
- [ ] Linear Regression
- [ ] Random Forest Regressor
- [ ] Gradient Boosting Regressor
- [ ] k-Nearest Neighbors Regressor

**Location:** `ml_pipeline/model_training.py`

### 3.6 Model Evaluation (FR-19 to FR-21)
**Status:** ⏳ To Implement

**Tasks:**
- [ ] Calculate MAE, MSE, RMSE, R² for all models
- [ ] Perform cross-validation
- [ ] Create unified evaluation table
- [ ] Select best model

**Location:** `ml_pipeline/model_evaluation.py`

### 3.7 Model Explainability (FR-22 to FR-24)
**Status:** ⏳ To Implement

**Tasks:**
- [ ] Compute feature importance/SHAP values
- [ ] Visualize feature contributions
- [ ] Document interpretation

**Location:** `ml_pipeline/explainability.py`

## Proposed Directory Structure

```
ml_pipeline/
├── data/
│   └── dirty_transport_dataset.csv
│
├── notebooks/
│   └── main_pipeline.ipynb          # Jupyter notebook for analysis
│
├── src/
│   ├── data_loader.py
│   ├── data_cleaning.py
│   ├── feature_engineering.py
│   ├── eda.py
│   ├── model_training.py
│   ├── model_evaluation.py
│   └── explainability.py
│
├── models/
│   ├── linear_regression.pkl
│   ├── random_forest.pkl
│   ├── gradient_boosting.pkl
│   └── knn.pkl
│
├── outputs/
│   ├── cleaned_dataset.csv
│   ├── evaluation_results.csv
│   ├── feature_importance.png
│   └── visualizations/
│
├── requirements.txt
└── README.md
```

## Integration with Existing Backend

### Current Backend Structure
```
backend/
├── app/
│   ├── models/
│   │   └── ml_model.py  # Currently uses mock predictions
│   └── ...
└── ml_models/
    └── trained_model.pkl  # Place trained model here
```

### Integration Steps

1. **Train Models** using the pipeline
2. **Select Best Model** based on evaluation
3. **Save Model** to `backend/ml_models/trained_model.pkl`
4. **Update Backend** to use real model (already supports this)
5. **Add Feature Config** to `backend/ml_models/feature_config.json`

## Implementation Priority

### Phase 1: Data Pipeline (Week 1)
1. Data loading and validation
2. Data cleaning and preprocessing
3. Feature engineering
4. EDA and visualizations

### Phase 2: Model Training (Week 2)
1. Train all 4 models
2. Model evaluation and comparison
3. Select best model
4. Save model artifacts

### Phase 3: Integration (Week 3)
1. Integrate trained model with backend
2. Test API endpoints with real model
3. Verify predictions match training data format
4. Update documentation

### Phase 4: Explainability & Reporting (Week 4)
1. Feature importance analysis
2. SHAP values computation
3. Create visualizations
4. Write final report

## Deliverables Checklist

- [ ] Cleaned dataset (CSV)
- [ ] Python Jupyter Notebook
- [ ] Model comparison results
- [ ] Explainability visualizations
- [ ] Final written report (8–12 pages)
- [ ] Slide presentation
- [ ] Trained model integrated with backend

## Next Steps

1. **Obtain Dataset:** Get `dirty_transport_dataset.csv`
2. **Set Up Environment:** Create `ml_pipeline/` directory
3. **Start Implementation:** Begin with data loading
4. **Iterate:** Follow SRS requirements systematically

## Notes

- The existing backend already supports loading a trained model
- Mock mode will work until real model is trained
- All SRS requirements must be documented
- Code should be modular and well-commented
- Use fixed random seeds for reproducibility

---

**Status:** Planning Complete - Ready for Implementation

