# Model Comparison & Dataset Upload Guide

## 📊 Model Comparison

### Current Model Performance

The system has trained 4 machine learning algorithms. Here's the comparison:

| Algorithm | MAE | RMSE | R² | Status |
|-----------|-----|------|----|----|
| **Gradient Boosting** | 28,690.51 | 77,072.38 | -0.405 | ⭐ Best |
| Random Forest | 31,278.94 | 71,119.15 | -0.197 | Available |
| k-Nearest Neighbors | 30,604.56 | 73,006.56 | -0.261 | Available |
| Linear Regression | 340,908.34 | 397,988.62 | -36.477 | Available |

**Best Model:** Gradient Boosting (lowest MAE)

### Viewing Comparison in UI

1. Make a prediction using the form
2. Scroll down in the results panel
3. Find the "Model Comparison" section
4. View all algorithms side-by-side
5. Click "View Full Comparison" to refresh data

## 📁 Dataset Upload

### How to Upload Your Dataset

1. **Prepare Your Dataset:**
   - Must be CSV format
   - Required columns:
     - `route_id` - Route identifier
     - `scheduled_time` - Scheduled arrival time
     - `actual_time` - Actual arrival time
     - `weather` - Weather condition
     - `passenger_count` - Number of passengers
     - `latitude` - GPS latitude
     - `longitude` - GPS longitude

2. **Upload Process:**
   - Click "Choose CSV file" button
   - Select your dataset file
   - Click "Upload & Train Models"
   - Wait for training to complete (1-5 minutes)

3. **After Upload:**
   - All 4 models will be retrained
   - Comparison table will update
   - Best model will be automatically selected
   - You can now choose different algorithms

### Dataset Format Example

```csv
route_id,scheduled_time,actual_time,weather,passenger_count,latitude,longitude
3,2024-01-01 10:00:00,2024-01-01 10:15:00,cloudy,120,40.7128,-74.0060
5,2024-01-01 11:00:00,2024-01-01 11:20:00,rainy,150,40.7580,-73.9855
```

## 🔄 Algorithm Selection

### How to Choose Algorithm

1. **In the Form:**
   - Find "Select ML Algorithm" dropdown
   - Choose from:
     - Gradient Boosting (Best) - Default
     - Random Forest
     - Linear Regression
     - k-Nearest Neighbors

2. **Make Prediction:**
   - Fill in trip details
   - Click "Predict Delay"
   - Results will use selected algorithm

3. **Compare Results:**
   - Try different algorithms
   - Compare predictions
   - See which works best for your data

## 📍 File Locations

### Comparison Data
- **CSV:** `ml_pipeline/outputs/evaluation_results.csv`
- **API:** `GET /api/v1/model-comparison`

### Trained Models
- **Gradient Boosting:** `ml_pipeline/models/gradient_boosting.pkl`
- **Random Forest:** `ml_pipeline/models/random_forest.pkl`
- **Linear Regression:** `ml_pipeline/models/linear_regression.pkl`
- **k-NN:** `ml_pipeline/models/knn.pkl`

### Uploaded Datasets
- **Location:** `ml_pipeline/data/dirty_transport_dataset.csv`
- **Backed up:** Original saved before upload

## 🎯 Usage Tips

1. **First Time:**
   - Use default Gradient Boosting model
   - Make a few predictions to test

2. **With Your Data:**
   - Upload your dataset
   - Wait for training
   - Check comparison table
   - Select best performing model

3. **Comparing Algorithms:**
   - Make same prediction with different algorithms
   - Compare results
   - Choose most consistent one

## 🔍 Understanding Metrics

- **MAE (Mean Absolute Error):** Lower is better - average prediction error
- **RMSE (Root Mean Squared Error):** Lower is better - penalizes large errors
- **R² (R-squared):** Higher is better - how well model fits data (can be negative)

## ⚠️ Notes

- Training takes 1-5 minutes depending on dataset size
- Large datasets (>1000 records) may take longer
- Model comparison updates automatically after upload
- Best model is highlighted in comparison table

---

**Status:** ✅ All Features Implemented  
**Ready to Use:** Yes

