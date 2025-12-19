#!/bin/bash
# Start Frontend Server
# Transport Delay Prediction Frontend

echo "🌐 Starting Frontend Server..."
echo ""

# Check if we're in the right directory
if [ ! -f "index.html" ]; then
    echo "❌ Error: index.html not found!"
    echo "Please run this script from the project root directory."
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed!"
    exit 1
fi

# Get available port (default 8000)
PORT=${1:-8000}

# Check if port is in use
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  Port $PORT is already in use. Trying port 8001..."
    PORT=8001
fi

echo "✅ Starting frontend server on http://localhost:$PORT"
echo "🔗 Make sure backend is running on http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 -m http.server $PORT

