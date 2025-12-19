# 🚀 Quick Start Guide

Get the Transport Delay Prediction System running in under 2 minutes!

## Option 1: Automated Start (Recommended)

### Linux/Mac:
```bash
# Start both frontend and backend
./start.sh
```

### Windows:
```cmd
# Start backend
start_backend.bat

# In another terminal, start frontend
start_frontend.bat
```

## Option 2: Manual Start

### Step 1: Start Backend

**Linux/Mac:**
```bash
./start_backend.sh
```

**Windows:**
```cmd
start_backend.bat
```

**Or manually:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 5000
```

### Step 2: Start Frontend

**Linux/Mac:**
```bash
./start_frontend.sh
```

**Windows:**
```cmd
start_frontend.bat
```

**Or manually:**
```bash
python3 -m http.server 8000
```

## Access the Application

- **Frontend:** http://localhost:8000
- **Backend API Docs:** http://localhost:5000/docs
- **Health Check:** http://localhost:5000/health

## First Time Setup

The scripts will automatically:
- ✅ Create Python virtual environment
- ✅ Install all dependencies
- ✅ Create configuration files
- ✅ Start the servers

## Troubleshooting

### Port Already in Use
If port 5000 or 8000 is in use:
- Backend: Edit `backend/.env` and change `PORT=5000` to another port
- Frontend: Run `./start_frontend.sh 8001` to use port 8001

### Python Not Found
- Install Python 3.9+ from https://www.python.org/
- Make sure Python is in your PATH

### Permission Denied (Linux/Mac)
```bash
chmod +x start.sh start_backend.sh start_frontend.sh
```

## What's Next?

1. Open http://localhost:8000 in your browser
2. Fill in the form and click "Predict Delay"
3. View the prediction results!

## Need Help?

See `SETUP_GUIDE.md` for detailed instructions.

---

**That's it! You're ready to go! 🎉**

