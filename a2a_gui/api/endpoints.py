from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import StreamingResponse, JSONResponse, Response
from pydantic import BaseModel
from typing import Optional, Dict, Any
import httpx

from services.car_agent_client import agent_client, AgentStatus

router = APIRouter()

class OBDConnectionRequest(BaseModel):
    config: Optional[Dict[str, Any]] = None

class TextToSpeechRequest(BaseModel):
    text: str

@router.get("/agent-status", response_model=AgentStatus)
async def get_agent_status():
    return await agent_client.check_status()

@router.get("/diagnose")
async def diagnose_stream(message: str = Query(..., description="The diagnostic message from the user.")):
    status = await agent_client.check_status()
    if not status.available:
        raise HTTPException(status_code=503, detail=f"Car diagnostic agent is not available: {status.error}")
    
    async def generate_stream():
        async for chunk in agent_client.stream_diagnosis(message):
            yield chunk
    
    return StreamingResponse(generate_stream(), media_type="text/event-stream")

@router.post("/connect-obd")
async def connect_obd_endpoint(request: OBDConnectionRequest):
    return await agent_client.connect_obd(request.config)

@router.post("/disconnect-obd")
async def disconnect_obd_endpoint():
    return await agent_client.disconnect_obd()

@router.get("/connection-info")
async def get_connection_info_endpoint():
    return await agent_client.get_connection_info()

@router.get("/voice-status")
async def get_voice_status():
    """Proxy endpoint to check voice service status from the car diagnostic agent"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:10011/voice-status", timeout=5)
            return JSONResponse(response.json())
    except Exception as e:
        return JSONResponse({"available": False, "error": str(e)}, status_code=503)

@router.post("/text-to-speech")
async def text_to_speech(request: Request):
    """Proxy endpoint to convert text to speech via the car diagnostic agent"""
    try:
        # Get the request body
        body = await request.json()
        text = body.get("text", "")
        
        if not text:
            return JSONResponse({"success": False, "error": "No text provided"}, status_code=400)
        
        # Forward the request to the car diagnostic agent
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:10011/text-to-speech",
                json={"text": text},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                # Return the audio data
                return Response(
                    content=response.content,
                    media_type="audio/wav",
                    headers={"Content-Disposition": "inline; filename=speech.wav"}
                )
            else:
                return JSONResponse(
                    {"success": False, "error": f"Voice service error: {response.status_code}"}, 
                    status_code=response.status_code
                )
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)