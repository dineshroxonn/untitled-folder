#!/usr/bin/env python3
"""
A2A GUI FastAPI Server

This server provides a web interface for the car diagnostic agent,
implementing the FastAPI backend with streaming SSE responses and
static file serving for the React frontend.
"""

import os
import json
import asyncio
from typing import AsyncGenerator, Optional
from pathlib import Path

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
CAR_AGENT_URL = os.getenv("CAR_AGENT_URL", "http://localhost:10011")
CAR_AGENT_TIMEOUT = int(os.getenv("CAR_AGENT_TIMEOUT", "30"))
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Request/Response models
class DiagnosticRequest(BaseModel):
    message: str

class AgentStatus(BaseModel):
    available: bool
    agent_url: str
    status_code: Optional[int] = None
    error: Optional[str] = None

# FastAPI application
app = FastAPI(
    title="A2A GUI API",
    description="Web interface API for Car Diagnostic Agent",
    version="0.1.0",
)

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite and CRA dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CarAgentClient:
    """Client for communicating with the car diagnostic agent."""
    
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
    
    async def check_status(self) -> AgentStatus:
        """Check if the car diagnostic agent is available."""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            if response.status_code == 200:
                return AgentStatus(
                    available=True,
                    agent_url=self.base_url,
                    status_code=response.status_code
                )
            else:
                return AgentStatus(
                    available=False,
                    agent_url=self.base_url,
                    status_code=response.status_code,
                    error=f"Agent returned status {response.status_code}"
                )
        except httpx.RequestError as e:
            return AgentStatus(
                available=False,
                agent_url=self.base_url,
                error=f"Connection error: {str(e)}"
            )
        except Exception as e:
            return AgentStatus(
                available=False,
                agent_url=self.base_url,
                error=f"Unexpected error: {str(e)}"
            )
    
    async def stream_diagnosis(self, message: str) -> AsyncGenerator[str, None]:
        """Stream diagnostic response from the car agent."""
        try:
            # Prepare the request payload for A2A agent
            payload = {
                "messages": [{"role": "user", "content": message}],
                "stream": True
            }
            
            async with self.client.stream(
                "POST",
                f"{self.base_url}/invoke",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status_code != 200:
                    error_text = await response.aread()
                    yield f"data: {json.dumps({'error': f'Agent error {response.status_code}: {error_text.decode()}'})}\n\n"
                    return
                
                async for chunk in response.aiter_text():
                    if chunk.strip():
                        # Parse and forward the chunk
                        lines = chunk.strip().split('\n')
                        for line in lines:
                            if line.startswith('data: '):
                                try:
                                    # Parse the A2A response
                                    data = json.loads(line[6:])
                                    if 'content' in data:
                                        # Forward the content as our SSE format
                                        yield f"data: {json.dumps({'text': data['content']})}\n\n"
                                    elif 'error' in data:
                                        yield f"data: {json.dumps({'error': data['error']})}\n\n"
                                        return
                                except json.JSONDecodeError:
                                    # If it's not JSON, treat it as text content
                                    if line.strip() and not line.startswith('data: [DONE]'):
                                        yield f"data: {json.dumps({'text': line.strip()})}\n\n"
                
                # Signal completion
                yield f"data: {json.dumps({'status': 'complete'})}\n\n"
                
        except httpx.RequestError as e:
            yield f"data: {json.dumps({'error': f'Connection error: {str(e)}'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': f'Unexpected error: {str(e)}'})}\n\n"
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

# Global agent client
agent_client = CarAgentClient(CAR_AGENT_URL, CAR_AGENT_TIMEOUT)

@app.get("/agent-status", response_model=AgentStatus)
async def get_agent_status():
    """Check the status of the car diagnostic agent."""
    return await agent_client.check_status()

@app.post("/diagnose")
async def diagnose_stream(request: DiagnosticRequest):
    """Stream diagnostic response from the car agent."""
    
    # Check agent availability first
    status = await agent_client.check_status()
    if not status.available:
        raise HTTPException(
            status_code=503,
            detail=f"Car diagnostic agent is not available: {status.error}"
        )
    
    async def generate_stream():
        async for chunk in agent_client.stream_diagnosis(request.message):
            yield chunk
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    await agent_client.close()

# Serve static files (React build)
static_dir = Path(__file__).parent / "frontend" / "dist"
if static_dir.exists():
    # Mount assets directory for CSS and JS files
    assets_dir = static_dir / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve the React frontend for all unmatched routes."""
        # API routes should not be served by the frontend
        if full_path.startswith(("agent-status", "diagnose", "api/", "assets/")):
            raise HTTPException(status_code=404, detail="Not found")
        
        # Serve index.html for all other routes (SPA routing)
        index_file = static_dir / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        else:
            raise HTTPException(status_code=404, detail="Frontend not built")
else:
    @app.get("/")
    async def root():
        """Development endpoint when frontend is not built."""
        return {
            "message": "A2A GUI API is running",
            "frontend_status": "not_built",
            "instructions": "Run 'npm run build' in the frontend directory to serve the React app"
        }

if __name__ == "__main__":
    print(f"Starting A2A GUI server on {HOST}:{PORT}")
    print(f"Car diagnostic agent URL: {CAR_AGENT_URL}")
    print(f"Frontend directory: {static_dir}")
    
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=DEBUG,
        log_level="info" if not DEBUG else "debug"
    )