from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any

from services.car_agent_client import agent_client, AgentStatus
from services.can_simulation_service import simulation_service

router = APIRouter()

class OBDConnectionRequest(BaseModel):
    config: Optional[Dict[str, Any]] = None

class SimulationRequest(BaseModel):
    scenario: str = "healthy"

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

@router.post("/simulate-car")
async def simulate_car_endpoint(request: SimulationRequest):
    """Endpoint to simulate a car connection with specific scenarios."""
    try:
        # Generate simulation data
        simulation_result = await simulation_service.simulate_scenario(request.scenario)
        
        if simulation_result["success"]:
            # Send simulation data to agent
            await agent_client.load_simulation_data(simulation_result)
            return simulation_result
        else:
            raise HTTPException(status_code=500, detail=simulation_result.get("error", "Simulation failed"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))