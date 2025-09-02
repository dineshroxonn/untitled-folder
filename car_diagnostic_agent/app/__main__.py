
import os
import logging
import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse, Response
from starlette.routing import Route, Mount
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard, AgentSkill
from dotenv import load_dotenv
from pathlib import Path

from .agent import CarDiagnosticAgent
from .agent_executor import CarDiagnosticAgentExecutor
# Import azure_voice_service after loading environment variables

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Agent Card Definition ---
def create_agent_card():
    return AgentCard(
        name="Car Diagnostic Agent with OBD-II Integration",
        description="An AI agent that acts as a virtual car mechanic with real-time OBD-II diagnostic capabilities.",
        version="0.2.1",
        url="http://localhost:10011/",
        skills=[
            AgentSkill(
                id="diagnose_car_problems",
                name="Diagnose Car Problems",
                description="Analyzes Diagnostic Trouble Codes (DTCs) and provides a diagnosis and repair plan.",
                examples=[
                    "My 2015 Ford Focus is showing codes P0171 and P0174.",
                    "Scan my vehicle for trouble codes.",
                ],
                tags=["diagnostics", "automotive", "mechanic", "DTC", "OBD-II"],
            ),
        ],
        capabilities={"streaming": True, "obd_integration": True, "voice_output": True},
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
    )

# --- Environment and Agent Initialization ---
# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError("GOOGLE_API_KEY environment variable not set.")

# Import azure_voice_service after loading environment variables
from .azure_voice_service import azure_voice_service

# Create a single agent instance to be shared
agent = CarDiagnosticAgent()
agent_card = create_agent_card()
agent_executor = CarDiagnosticAgentExecutor(agent)

# --- A2A Application Setup ---
request_handler = DefaultRequestHandler(
    agent_executor=agent_executor,
    task_store=InMemoryTaskStore(),
)
a2a_app = A2AStarletteApplication(
    agent_card=agent_card,
    http_handler=request_handler,
).build()

# --- Additional API Endpoints ---
async def connect_obd(request):
    """Endpoint to connect to the OBD adapter."""
    body = await request.json()
    config = body.get("config")
    result = await agent.connect_obd(config)
    return JSONResponse(result)

async def disconnect_obd(request):
    """Endpoint to disconnect from the OBD adapter."""
    result = await agent.disconnect_obd()
    return JSONResponse(result)

async def get_connection_info(request):
    """Endpoint to get current OBD connection info."""
    if not agent.obd_manager:
        return JSONResponse({"connected": False, "error": "OBD manager not initialized"}, status_code=500)
    info = await agent.obd_manager.get_connection_info()
    return JSONResponse(info)

async def text_to_speech(request):
    """Endpoint to convert text to speech"""
    if not azure_voice_service.is_available():
        return JSONResponse({
            "success": False, 
            "error": "Azure voice service not configured. Set AZURE_SPEECH_KEY environment variable."
        }, status_code=503)
    
    try:
        body = await request.json()
        text = body.get("text", "")
        if not text:
            return JSONResponse({"success": False, "error": "No text provided"}, status_code=400)
        
        audio_data = await azure_voice_service.text_to_speech(text)
        if audio_data:
            return Response(
                content=audio_data,
                media_type="audio/wav",
                headers={"Content-Disposition": "inline; filename=speech.wav"}
            )
        else:
            return JSONResponse({"success": False, "error": "Failed to synthesize speech"}, status_code=500)
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

async def voice_status(request):
    """Endpoint to check voice service status"""
    print(f"Voice service available: {azure_voice_service.is_available()}")
    print(f"Voice service configured: {azure_voice_service.subscription_key is not None}")
    print(f"Subscription key: {azure_voice_service.subscription_key}")
    print(f"Speech config: {azure_voice_service.speech_config}")
    return JSONResponse({
        "available": azure_voice_service.is_available(),
        "configured": azure_voice_service.subscription_key is not None
    })

async def health_check(request):
    """Health check endpoint."""
    return JSONResponse({"status": "ok"})

# --- Main Application Assembly ---

async def on_startup():
    """Asynchronous startup event handler."""
    logger.info("Application startup: Initializing OBD system...")
    await agent.initialize_obd_system()
    logger.info("OBD system initialization complete.")

# Combine the A2A app with the new control endpoints
app = Starlette(
    middleware=[
        Middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:8000"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    ],
    on_startup=[on_startup],
    routes=[
        Route("/health", health_check, methods=["GET"]),
        Route("/connect_obd", connect_obd, methods=["POST"]),
        Route("/disconnect_obd", disconnect_obd, methods=["POST"]),
        Route("/connection_info", get_connection_info, methods=["GET"]),
        Route("/text-to-speech", text_to_speech, methods=["POST"]),
        Route("/voice-status", voice_status, methods=["GET"]),
        Mount("/", app=a2a_app)
    ]
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10011)
