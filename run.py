#!/usr/bin/env python3
"""
Quick start script for Transport Delay Prediction System
Runs both frontend and backend servers
"""
import subprocess
import sys
import time
import signal
import os
from pathlib import Path

def check_python():
    """Check if Python 3 is available"""
    if sys.version_info < (3, 9):
        print("❌ Error: Python 3.9+ is required!")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} detected")

def setup_backend():
    """Setup and start backend"""
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Error: backend directory not found!")
        sys.exit(1)
    
    os.chdir(backend_dir)
    
    # Create venv if needed
    venv_dir = Path("venv")
    if not venv_dir.exists():
        print("📦 Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
    
    # Determine activation script
    if sys.platform == "win32":
        activate = venv_dir / "Scripts" / "activate.bat"
        pip = venv_dir / "Scripts" / "pip"
    else:
        activate = venv_dir / "bin" / "activate"
        pip = venv_dir / "bin" / "pip"
    
    # Install dependencies
    print("📥 Installing dependencies...")
    subprocess.run([str(pip), "install", "-q", "--upgrade", "pip"], check=True)
    subprocess.run([str(pip), "install", "-q", "-r", "requirements.txt"], check=True)
    
    os.chdir("..")
    
    # Start backend
    print("🔧 Starting backend on http://localhost:5000...")
    if sys.platform == "win32":
        backend_process = subprocess.Popen(
            [str(venv_dir / "Scripts" / "uvicorn"), "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "5000"],
            cwd=backend_dir
        )
    else:
        backend_process = subprocess.Popen(
            [str(venv_dir / "bin" / "uvicorn"), "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "5000"],
            cwd=backend_dir
        )
    
    return backend_process

def start_frontend(port=8000):
    """Start frontend server"""
    print(f"🌐 Starting frontend on http://localhost:{port}...")
    frontend_process = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port)]
    )
    return frontend_process

def main():
    """Main function"""
    print("🚀 Transport Delay Prediction System")
    print("=" * 40)
    print()
    
    check_python()
    
    try:
        backend = setup_backend()
        time.sleep(2)  # Wait for backend to start
        frontend = start_frontend()
        
        print()
        print("=" * 40)
        print("✅ System is running!")
        print()
        print("📱 Frontend:  http://localhost:8000")
        print("🔧 Backend:   http://localhost:5000")
        print("📚 API Docs:   http://localhost:5000/docs")
        print()
        print("Press Ctrl+C to stop all servers")
        print("=" * 40)
        print()
        
        # Wait for interrupt
        backend.wait()
        frontend.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")
        backend.terminate()
        frontend.terminate()
        backend.wait()
        frontend.wait()
        print("✅ Servers stopped")

if __name__ == "__main__":
    main()
