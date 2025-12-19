#!/bin/bash
# Start Both Frontend and Backend
# Transport Delay Prediction System

echo "🚀 Starting Transport Delay Prediction System"
echo "=============================================="
echo ""

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -f "index.html" ]; then
    echo "❌ Error: Project files not found!"
    echo "Please run this script from the project root directory."
    exit 1
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit
}

trap cleanup SIGINT SIGTERM

# Start backend in background
echo "🔧 Starting Backend Server..."
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate and install dependencies
source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Start backend
echo "✅ Backend starting on http://localhost:5000"
uvicorn app.main:app --reload --host 0.0.0.0 --port 5000 > /tmp/backend.log 2>&1 &
BACKEND_PID=$!

cd ..

# Wait a moment for backend to start
sleep 2

# Start frontend
echo "🌐 Starting Frontend Server..."
PORT=8000
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    PORT=8001
fi

python3 -m http.server $PORT > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!

echo ""
echo "=============================================="
echo "✅ System is running!"
echo ""
echo "📱 Frontend:  http://localhost:$PORT"
echo "🔧 Backend:   http://localhost:5000"
echo "📚 API Docs:   http://localhost:5000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"
echo "=============================================="
echo ""

# Wait for user interrupt
wait

