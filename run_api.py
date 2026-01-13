"""
Start the FastAPI server
"""
import os
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    print(f"Starting Executive Analytics API on {host}:{port}")
    print(f"API Docs: http://{host if host != '0.0.0.0' else 'localhost'}:{port}/docs")
    print(f"Health Check: http://{host if host != '0.0.0.0' else 'localhost'}:{port}/api/health")
    
    uvicorn.run(
        "src.api.main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
