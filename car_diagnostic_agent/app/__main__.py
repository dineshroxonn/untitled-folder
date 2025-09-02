
import os

import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard, AgentSkill
from dotenv import load_dotenv

from .agent_executor import get_agent_executor


def create_agent_card():
    return AgentCard(
        name="Car Diagnostic Agent",
        description="An AI agent that acts as a virtual car mechanic. Provide the car model, year, and Diagnostic Trouble Codes (DTCs) to get a diagnosis and repair suggestions.",
        version="0.1.0",
        url="http://localhost:10011/",
        skills=[
            AgentSkill(
                id="diagnose_car_problems",
                name="Diagnose Car Problems",
                description="Analyzes Diagnostic Trouble Codes (DTCs) for a specific car model and provides a diagnosis and repair plan.",
                examples=[
                    "My 2015 Ford Focus is showing codes P0171 and P0174. What's going on?",
                    "I have a 2019 Toyota Camry with a check engine light and code C1201.",
                ],
                tags=["diagnostics", "automotive", "mechanic", "DTC"],
            )
        ],
        capabilities={"streaming": True},
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
    )


load_dotenv()
if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError("GOOGLE_API_KEY environment variable not set.")

agent_card = create_agent_card()

# Manually construct the request handler like in the langgraph example
request_handler = DefaultRequestHandler(
    agent_executor=get_agent_executor(),
    task_store=InMemoryTaskStore(),
)

app = A2AStarletteApplication(
    agent_card=agent_card,
    http_handler=request_handler,
)

if __name__ == "__main__":
    uvicorn.run(app.build(), host="0.0.0.0", port=10011)
