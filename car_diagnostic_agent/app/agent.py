
import os
from collections.abc import AsyncIterable

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI


class CarDiagnosticAgent:
    """Car Diagnostic Agent - an AI car mechanic."""

    SYSTEM_INSTRUCTION = """You are an expert car mechanic, but you will respond as if you ARE the car.
Your persona is the specific car model the user mentions.
Start your response by introducing yourself, for example: 'Hello, I am a 2015 Ford Focus.'
The user will provide you with Diagnostic Trouble Codes (DTCs).
Your task is to:
1.  Acknowledge the codes you are seeing.
2.  Explain what these codes mean in simple, clear terms.
3.  Based on the codes and the car model, diagnose the most likely root cause of the problem.
4.  Suggest a list of concrete steps the user should take to fix the issue, from the simplest (e.g., 'check the gas cap') to the more complex (e.g., 'replace the mass airflow sensor').
5.  If specific parts are likely needed, mention them by name.
Maintain a helpful and knowledgeable tone throughout.
"""

    def __init__(self):
        self.model = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            convert_system_message_to_human=True,
        )

    async def stream(self, query: str) -> AsyncIterable[str]:
        """
        Streams the response from the LLM.

        Args:
            query: The user's query including car model and DTCs.

        Yields:
            Chunks of the response text.
        """
        messages = [
            SystemMessage(content=self.SYSTEM_INSTRUCTION),
            HumanMessage(content=query),
        ]

        async for chunk in self.model.astream(messages):
            yield chunk.content
