# Transport Delay Prediction System - Setup Guide

## 🚀 Quick Start Guide

This guide will help you set up and run the complete Transport Delay Prediction system.

## Prerequisites

- **Python 3.9+** (for backend)
- **Modern web browser** (Chrome, Firefox, Safari, Edge)
- **pip** (Python package manager)

## Step 1: Backend Setup

### 1.1 Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 1.2 (Optional) Configure Environment

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` if you need to change default settings (port, CORS, etc.)

### 1.3 (Optional) Add ML Model

If you have a trained model:
- Place `trained_model.pkl` in `backend/ml_models/`
- Optionally add `feature_config.json` for feature metadata

**Note:** The system works in mock mode without a model!

### 1.4 Start Backend Server

```bash
# From backend directory
uvicorn app.main:app --reload --host 0.0.0.0 --port 5000
```

Or using Python:
```bash
python -m app.main
```

**Verify:** Open http://localhost:5000/docs to see API documentation

## Step 2: Frontend Setup

### 2.1 Start Frontend Server

Open a new terminal:

```bash
# From project root
cd /home/jmr0xd/Workspace/frontAI
python3 -m http.server 8000
```

Or use any static file server:
- Node.js: `npx http-server -p 8000`
- VS Code: Use Live Server extension

### 2.2 Access Frontend

Open your browser and navigate to:
- **Frontend:** http://localhost:8000
- **Backend API Docs:** http://localhost:5000/docs

## Step 3: Test the System

### 3.1 Test Frontend

1. Fill in the form:
   - Route ID: 1-10
   - Weather: Select from dropdown
   - Passengers: 0-500
   - Time of Day: Select radio button
   - Weekend: Toggle switch

2. Click "Predict Delay"

3. View results in the right panel

### 3.2 Test Backend API

**Using curl:**
```bash
curl -X POST "http://localhost:5000/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "route_id": 3,
    "weather": "cloudy",
    "passenger_count": 120,
    "time_of_day": 1,
    "is_weekend": 0
  }'
```

**Using API Documentation:**
- Visit http://localhost:5000/docs
- Use the interactive Swagger UI to test endpoints

## Troubleshooting

### Backend Issues

**Port already in use:**
```bash
# Change port in .env or command
uvicorn app.main:app --port 5001
```

**Import errors:**
```bash
# Make sure you're in the backend directory
cd backend
pip install -r requirements.txt
```

**CORS errors:**
- Check that frontend URL is in `ALLOWED_ORIGINS` in `backend/app/config.py`
- Or set `DEBUG=True` in `.env` for development

### Frontend Issues

**API connection errors:**
- Verify backend is running on port 5000
- Check browser console for errors
- Verify API URL in `js/api.js` (default: `http://localhost:5000/api/v1`)

**Styling issues:**
- Clear browser cache
- Verify `css/styles.css` is loading (check Network tab)

## Development Mode

### Backend Development

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 5000
```

The `--reload` flag enables auto-reload on code changes.

### Frontend Development

The frontend uses vanilla JavaScript, so just refresh the browser after changes.

## Production Deployment

### Backend

```bash
# Production server (multiple workers)
uvicorn app.main:app --host 0.0.0.0 --port 5000 --workers 4

# Or use a production ASGI server like Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend

Deploy static files to any hosting service:
- **GitHub Pages**
- **Netlify**
- **Vercel**
- **AWS S3 + CloudFront**

Update API URL in `js/api.js` or via `window.API_BASE_URL`.

## File Structure

```
frontAI/
├── backend/              # FastAPI backend
│   ├── app/
│   ├── ml_models/       # Place trained models here
│   ├── requirements.txt
│   └── .env.example
│
├── index.html           # Frontend entry point
├── css/
│   └── styles.css
├── js/
│   ├── app.js          # Main application logic
│   └── api.js          # API integration
│
└── Documentation/
    ├── Frontend Design Specification.md
    └── Backend Design Document.md
```

## API Endpoints

- `POST /api/v1/predict` - Make delay prediction
- `GET /api/v1/feature-importance` - Get feature importance
- `GET /api/v1/health` - Health check
- `GET /health` - Simple health check
- `GET /docs` - API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation

## Configuration

### Backend Configuration

Edit `backend/.env`:
```env
PORT=5000
DEBUG=True
ALLOWED_ORIGINS=http://localhost:8000
```

### Frontend API URL

Edit `index.html` or set before scripts load:
```html
<script>window.API_BASE_URL = 'http://your-api-url:5000/api/v1';</script>
```

## Testing

### Backend Tests

```bash
cd backend
pytest tests/
```

### Manual Testing

1. **Frontend Validation:**
   - Try invalid inputs (route > 10, passengers > 500)
   - Submit empty form
   - Test all form fields

2. **API Integration:**
   - Test with backend running
   - Test without backend (should show connection error)

3. **Responsive Design:**
   - Resize browser window
   - Test on mobile device

## Support

For issues or questions:
1. Check the documentation files
2. Review error messages in browser console (F12)
3. Check backend logs in terminal
4. Verify all prerequisites are installed

## Next Steps

1. **Add Trained Model:** Place your trained ML model in `backend/ml_models/`
2. **Customize Design:** Edit `css/styles.css` for branding
3. **Add Features:** Extend API endpoints or frontend components
4. **Deploy:** Follow production deployment steps

---

**Status:** ✅ Ready for Development and Production  
**Last Updated:** December 2024

