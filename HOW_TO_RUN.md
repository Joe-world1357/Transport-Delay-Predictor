# 🚀 How to Run the Application

## Quick Start (Easiest Way)

### Option 1: All-in-One Script (Recommended)

**Linux/Mac:**
```bash
./start.sh
```

**Windows:**
```cmd
start.bat
```

**Python (Cross-platform):**
```bash
python3 run.py
```

This starts both frontend and backend automatically!

### Option 2: Separate Scripts

**Start Backend:**
```bash
# Linux/Mac
./start_backend.sh

# Windows
start_backend.bat
```

**Start Frontend (in another terminal):**
```bash
# Linux/Mac
./start_frontend.sh

# Windows
start_frontend.bat
```

## What the Scripts Do

### Backend Script (`start_backend.sh` / `start_backend.bat`)
1. ✅ Checks for Python 3
2. ✅ Creates virtual environment (if needed)
3. ✅ Installs all dependencies
4. ✅ Creates `.env` file (if needed)
5. ✅ Starts FastAPI server on port 5000

### Frontend Script (`start_frontend.sh` / `start_frontend.bat`)
1. ✅ Checks for Python 3
2. ✅ Finds available port (8000 or 8001)
3. ✅ Starts HTTP server

### Combined Script (`start.sh` / `start.bat` / `run.py`)
1. ✅ Does everything above
2. ✅ Starts both servers simultaneously
3. ✅ Handles cleanup on exit

## Manual Setup (If Scripts Don't Work)

### Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start server
uvicorn app.main:app --reload --port 5000
```

### Frontend Setup

```bash
# From project root
python3 -m http.server 8000
```

## Access the Application

Once running, open in your browser:

- **Frontend:** http://localhost:8000
- **Backend API:** http://localhost:5000
- **API Documentation:** http://localhost:5000/docs
- **Health Check:** http://localhost:5000/health

## First Run

On first run, the scripts will:
- Create Python virtual environment
- Install all required packages
- Create configuration files
- Start the servers

**This may take 1-2 minutes the first time.**

## Troubleshooting

### "Permission Denied" (Linux/Mac)
```bash
chmod +x start.sh start_backend.sh start_frontend.sh
```

### Port Already in Use
- **Backend:** Edit `backend/.env` and change `PORT=5000`
- **Frontend:** Run `./start_frontend.sh 8001` to use port 8001

### Python Not Found
- Install Python 3.9+ from https://www.python.org/
- Make sure Python is in your PATH

### Virtual Environment Issues
```bash
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Dependencies Installation Fails
```bash
cd backend
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Stopping the Servers

- **If using scripts:** Press `Ctrl+C` in the terminal
- **If running manually:** Press `Ctrl+C` in each terminal

## Verification

### Check Backend is Running
```bash
curl http://localhost:5000/health
```

Should return:
```json
{"status": "healthy", "timestamp": "..."}
```

### Check Frontend is Running
Open http://localhost:8000 in your browser - you should see the form.

## Next Steps

1. ✅ Servers are running
2. ✅ Open http://localhost:8000
3. ✅ Fill in the form
4. ✅ Click "Predict Delay"
5. ✅ View results!

## Need More Help?

- See `SETUP_GUIDE.md` for detailed setup instructions
- See `QUICK_START.md` for quick reference
- Check backend logs in terminal for errors

---

**That's it! You're ready to use the application! 🎉**

