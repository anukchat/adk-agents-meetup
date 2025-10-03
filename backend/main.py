#!/usr/bin/env python3
"""
Main entry point for running the Job Application Agent with DatabaseSessionService via FastAPI.
"""

import sys
import os
from dotenv import load_dotenv
from fastapi import APIRouter
from google.adk.cli.fast_api import get_fast_api_app

# Load environment variables
load_dotenv()

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Configure database URL
db_url = os.getenv("DATABASE_URL", "sqlite:///./adk_session.db")

# Create FastAPI app with ADK integration
app = get_fast_api_app(
    agents_dir="src/agents",
    session_service_uri=db_url,
    web=True,
    allow_origins=["*"],  # Configure as needed for your environment
)

# Health check router
health_router = APIRouter()

@health_router.get("/health")
async def health_check():
    return {"status": "ok", "service": "job-application-agent"}

app.include_router(health_router)

def main():
    import uvicorn
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True
    )

if __name__ == "__main__":
    main()

