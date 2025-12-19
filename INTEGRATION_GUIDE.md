# Integration Guide: SRS Requirements with Existing System

## Overview

This guide explains how the SRS requirements (file.md) integrate with the existing Transport Delay Prediction system we've built.

## System Architecture

```
┌─────────────────────────────────────────┐
│         Frontend (Complete)             │
│  - HTML/CSS/JS Web Interface          │
│  - Form validation                     │
│  - Results display                      │
└──────────────┬──────────────────────────┘
               │ HTTP/JSON
               ▼
┌─────────────────────────────────────────┐
│      Backend API (Complete)             │
│  - FastAPI server                       │
│  - Prediction endpoints                 │
│  - Model wrapper                        │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│   ML Pipeline (To Implement)           │
│  - Data cleaning (SRS FR-3 to FR-8)    │
│  - Feature engineering (SRS FR-9-13)   │
│  - Model training (SRS FR-17-18)       │
│  - Evaluation (SRS FR-19-21)           │
│  - Explainability (SRS FR-22-24)        │
└─────────────────────────────────────────┘
```

## What We Have vs. What's Needed

### ✅ Already Complete

1. **Frontend Application**
   - All UI components
   - Form inputs matching SRS data fields
   - Results display
   - Feature importance visualization

2. **Backend API**
   - FastAPI server
   - `/api/v1/predict` endpoint
   - Model wrapper (ready for real model)
   - Error handling

3. **Integration**
   - Frontend-backend connection
   - API request/response format
   - Mock predictions working

### ⏳ Needs Implementation (Per SRS)

1. **Data Pipeline**
   - Load `dirty_transport_dataset.csv`
   - Clean and preprocess data
   - Feature engineering
   - EDA visualizations

2. **Model Training**
   - Train 4 models (Linear, RF, GB, k-NN)
   - Evaluate and compare
   - Select best model

3. **Model Integration**
   - Save trained model
   - Update backend to use it
   - Verify predictions

4. **Explainability**
   - Feature importance
   - SHAP values
   - Visualizations

## Data Flow

### Current (Mock Mode)
```
User Input → Frontend → Backend API → Mock Predictions → Results
```

### Target (With Real Model)
```
User Input → Frontend → Backend API → Trained Model → Real Predictions → Results
                ↑
                │
        ML Pipeline (Training)
        ↓
    Trained Model.pkl
```

## SRS Requirements Mapping

| SRS Requirement | Current Status | Action Needed |
|----------------|----------------|--------------|
| FR-1, FR-2: Data Loading | ❌ Not Implemented | Create data loader |
| FR-3 to FR-8: Data Cleaning | ❌ Not Implemented | Implement cleaning pipeline |
| FR-9 to FR-13: Feature Engineering | ❌ Not Implemented | Create feature engineering |
| FR-14 to FR-16: EDA | ❌ Not Implemented | Create EDA notebook |
| FR-17, FR-18: Model Training | ❌ Not Implemented | Train 4 models |
| FR-19 to FR-21: Evaluation | ❌ Not Implemented | Evaluate and compare |
| FR-22 to FR-24: Explainability | ⚠️ Partial | Add SHAP/importance |

## Integration Points

### 1. Model File Location
**Current:** `backend/ml_models/trained_model.pkl` (empty, uses mock)
**After Training:** Place trained model here

### 2. Feature Configuration
**Current:** Mock feature names
**After Training:** Create `backend/ml_models/feature_config.json` with:
```json
{
  "feature_names": ["route_id", "weather_clear", ...],
  "model_type": "Random Forest",
  "mae": 3.2
}
```

### 3. API Response Format
**Current:** Already matches SRS requirements
**After Training:** Real predictions replace mock

### 4. Feature Importance
**Current:** Mock importance values
**After Training:** Real feature importance from model

## Implementation Roadmap

### Step 1: Set Up ML Pipeline
```bash
mkdir -p ml_pipeline/{data,notebooks,src,models,outputs}
```

### Step 2: Implement Data Pipeline
- Create data loading module
- Implement cleaning functions
- Feature engineering
- EDA notebook

### Step 3: Train Models
- Train all 4 models
- Evaluate and compare
- Select best model

### Step 4: Integrate with Backend
- Save model to `backend/ml_models/`
- Update feature config
- Test API endpoints

### Step 5: Verify Integration
- Test predictions match training format
- Verify feature importance
- Check all endpoints

## File Structure After Integration

```
frontAI/
├── frontend/              # ✅ Complete
├── backend/               # ✅ Complete (needs model)
│   └── ml_models/
│       ├── trained_model.pkl  # ⏳ Add after training
│       └── feature_config.json # ⏳ Add after training
│
└── ml_pipeline/           # ⏳ To Create
    ├── data/
    ├── notebooks/
    ├── src/
    └── models/
```

## Testing Integration

### Before Training
- ✅ Frontend works with mock predictions
- ✅ Backend API responds correctly
- ✅ All endpoints functional

### After Training
- [ ] Model loads successfully
- [ ] Predictions are reasonable
- [ ] Feature importance matches training
- [ ] API response format unchanged
- [ ] Frontend displays real predictions

## Deliverables Status

| Deliverable | Status | Location |
|------------|-------|----------|
| Cleaned dataset | ⏳ Pending | `ml_pipeline/outputs/` |
| Jupyter Notebook | ⏳ Pending | `ml_pipeline/notebooks/` |
| Model comparison | ⏳ Pending | `ml_pipeline/outputs/` |
| Explainability viz | ⏳ Pending | `ml_pipeline/outputs/` |
| Final report | ⏳ Pending | Root directory |
| Presentation | ⏳ Pending | Root directory |
| Trained model | ⏳ Pending | `backend/ml_models/` |

## Next Actions

1. **Obtain Dataset:** Get `dirty_transport_dataset.csv`
2. **Create ML Pipeline:** Set up directory structure
3. **Implement Requirements:** Follow SRS systematically
4. **Integrate:** Connect trained model to backend
5. **Test:** Verify end-to-end functionality

---

**Current Status:** Frontend and Backend complete, ML Pipeline to be implemented per SRS

