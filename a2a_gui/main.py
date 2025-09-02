#!/usr/bin/env python3
"""
A2A GUI FastAPI Server

This server provides a web interface for the car diagnostic agent,
implementing the FastAPI backend with streaming SSE responses and
static file serving for the React frontend.
"""

import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from api.endpoints import router as api_router
from services.car_agent_client import agent_client

# Load environment variables
load_dotenv()

# Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# FastAPI application
app = FastAPI(
    title="A2A GUI API",
    description="Web interface API for Car Diagnostic Agent",
    version="0.2.0",
)

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.on_event("shutdown")
async def shutdown_event():
    await agent_client.close()

# Serve static files (React build)
static_dir = Path(__file__).parent / "frontend" / "dist"
if static_dir.exists():
    app.mount("/assets", StaticFiles(directory=static_dir / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str, request: Request):
        # Exclude API routes from being served by the frontend
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not Found")
        
        index_file = static_dir / "index.html"
        return FileResponse(index_file)
else:
    @app.get("/")
    async def root():
        return {"message": "A2A GUI API is running", "frontend_status": "not_built"}

if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, reload=DEBUG)
