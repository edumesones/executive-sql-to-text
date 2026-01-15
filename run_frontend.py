"""
Start the Streamlit frontend
"""
import os
import subprocess
import sys

if __name__ == "__main__":
    print("Starting Executive Analytics Frontend...")
    print("Opening browser at http://localhost:8501")
    print()
    print("WARNING: Make sure the API backend is running:")
    print("   python run_api.py")
    print()
    
    # Run streamlit
    subprocess.run([
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "frontend/streamlit_app.py",
        "--server.port=8501",
        "--server.address=localhost"
    ])
