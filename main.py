"""
Main launcher script for the Camp Dashboard.
Starts both the FastAPI backend and the Streamlit frontend.
Admins only need to run: python main.py
"""

import subprocess
import sys
import time

def run_backend():
    # Launch FastAPI backend
    return subprocess.Popen([sys.executable, "-m", "uvicorn", "backend.auth_backend:app", "--port", "8000"])

def run_frontend():
    # Launch Streamlit frontend
    return subprocess.Popen([sys.executable, "-m", "streamlit", "run", "app.py"])

if __name__ == "__main__":
    print("🚀 Starting Camp Dashboard...")
    backend = run_backend()
    time.sleep(2)  # give backend time to start
    frontend = run_frontend()

    try:
        backend.wait()
        frontend.wait()
    except KeyboardInterrupt:
        print("Stopping services...")
        backend.terminate()
        frontend.terminate()
