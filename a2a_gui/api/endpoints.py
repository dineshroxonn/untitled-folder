from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
import json

from services.car_agent_client import agent_client, AgentStatus

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class OBDConnectionRequest(BaseModel):
    config: Optional[Dict[str, Any]] = None

@router.get("/agent-status", response_model=AgentStatus)
async def get_agent_status():
    logger.info("Checking agent status")
    status = await agent_client.check_status()
    logger.info(f"Agent status: {status}")
    return status

@router.get("/diagnose")
async def diagnose_stream(message: str = Query(..., description="The diagnostic message from the user.")):
    logger.info(f"Starting diagnosis stream for message: {message}")
    status = await agent_client.check_status()
    if not status.available:
        logger.error(f"Car diagnostic agent is not available: {status.error}")
        raise HTTPException(status_code=503, detail=f"Car diagnostic agent is not available: {status.error}")
    
    async def generate_stream():
        logger.info("Starting stream generation")
        try:
            async for chunk in agent_client.stream_diagnosis(message):
                logger.info(f"Sending chunk: {chunk[:100]}...")  # Log first 100 chars
                yield chunk
            logger.info("Stream generation completed")
        except Exception as e:
            logger.error(f"Error during stream generation: {e}")
            yield f"data: {json.dumps({'error': f'Stream error: {str(e)}'})}\n\n"
    
    logger.info("Returning StreamingResponse")
    return StreamingResponse(generate_stream(), media_type="text/event-stream")

@router.post("/connect-obd")
async def connect_obd_endpoint(request: OBDConnectionRequest):
    logger.info(f"Connecting to OBD with config: {request.config}")
    result = await agent_client.connect_obd(request.config)
    logger.info(f"OBD connection result: {result}")
    return result

@router.post("/disconnect-obd")
async def disconnect_obd_endpoint():
    logger.info("Disconnecting from OBD")
    result = await agent_client.disconnect_obd()
    logger.info(f"OBD disconnection result: {result}")
    return result

@router.get("/connection-info")
async def get_connection_info_endpoint():
    logger.info("Getting connection info")
    info = await agent_client.get_connection_info()
    logger.info(f"Connection info: {info}")
    return info