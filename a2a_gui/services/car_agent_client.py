import os
import json
import time
import random
import string
from typing import AsyncGenerator, Optional, Dict, Any

import httpx
from fastapi import HTTPException
from pydantic import BaseModel

CAR_AGENT_URL = os.getenv("CAR_AGENT_URL", "http://localhost:10011")
CAR_AGENT_TIMEOUT = int(os.getenv("CAR_AGENT_TIMEOUT", "10"))

class AgentStatus(BaseModel):
    available: bool
    agent_url: str
    status_code: Optional[int] = None
    error: Optional[str] = None

class CarAgentClient:
    """Client for communicating with the car diagnostic agent."""
    
    def __init__(self, base_url: str, timeout: int = 10):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        # Increase timeout for streaming connections
        self.client = httpx.AsyncClient(timeout=httpx.Timeout(timeout, read=None))
    
    async def _agent_request(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
        """Helper to make requests to the agent."""
        url = f"{self.base_url}{endpoint}"
        try:
            response = await self.client.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Agent error: {e.response.text}")
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Agent connection error: {e}")

    async def check_status(self) -> AgentStatus:
        """Check if the car diagnostic agent is available."""
        try:
            response = await self.client.get(f"{self.base_url}/health", timeout=2)
            if response.status_code == 200:
                return AgentStatus(available=True, agent_url=self.base_url, status_code=response.status_code)
            else:
                return AgentStatus(available=False, agent_url=self.base_url, status_code=response.status_code, error=f"Agent returned status {response.status_code}")
        except httpx.RequestError as e:
            return AgentStatus(available=False, agent_url=self.base_url, error=f"Connection error: {e}")

    async def connect_obd(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send connect command to the agent."""
        response = await self._agent_request("POST", "/connect_obd", json={"config": config})
        return response.json()

    async def disconnect_obd(self) -> Dict[str, Any]:
        """Send disconnect command to the agent."""
        response = await self._agent_request("POST", "/disconnect_obd")
        return response.json()

    async def get_connection_info(self) -> Dict[str, Any]:
        """Get OBD connection info from the agent."""
        response = await self._agent_request("GET", "/connection_info")
        return response.json()

    async def stream_diagnosis(self, message: str) -> AsyncGenerator[str, None]:
        """Stream diagnostic response from the car agent."""
        message_id = f"{int(time.time())}-{ ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))}"
        payload = {
            "jsonrpc": "2.0",
            "method": "message/stream",
            "params": {
                "message": {
                    "messageId": message_id,
                    "role": "user",
                    "parts": [{"text": message}],
                }
            },
            "id": "1"
        }
        try:
            # Use a longer timeout for streaming
            timeout = httpx.Timeout(self.timeout, read=None)
            async with self.client.stream("POST", f"{self.base_url}/", json=payload, headers={"Content-Type": "application/json"}, timeout=timeout) as response:
                print(f"Stream response status: {response.status_code}")
                if response.status_code != 200:
                    error_text = await response.aread()
                    print(f"Stream error response: {error_text.decode()}")
                    yield f"data: {json.dumps({'error': f'Agent error {response.status_code}: {error_text.decode()}'})}\n\n"
                    return

                async for line in response.aiter_lines():
                    print(f"Received line: {line}")
                    if line.startswith("data:"):
                        try:
                            data_json = json.loads(line[5:])
                            if "result" in data_json and "kind" in data_json["result"]:
                                result = data_json["result"]
                                if result["kind"] == "status-update" and "status" in result and "message" in result["status"]:
                                    if result["status"]["message"] and result["status"]["message"]["parts"]:
                                        for part in result["status"]["message"]["parts"]:
                                            if part.get("kind") == "text" and part.get("text"):
                                                yield f"data: {json.dumps({'content': part['text']})}\n\n"
                        except json.JSONDecodeError as e:
                            print(f"JSON decode error: {e}")
                            continue
                    elif line.strip():  # Handle other types of lines
                        print(f"Non-data line: {line}")
                
                yield f"data: {json.dumps({'status': 'complete'})}\n\n"
        except httpx.ReadTimeout as e:
            print(f"Read timeout during streaming: {e}")
            yield f"data: {json.dumps({'error': f'Read timeout: {str(e)}'})}\n\n"
        except httpx.RequestError as e:
            print(f"Request error during streaming: {e}")
            yield f"data: {json.dumps({'error': f'Connection error: {str(e)}'})}\n\n"
        except Exception as e:
            print(f"Unexpected error during streaming: {e}")
            yield f"data: {json.dumps({'error': f'Unexpected error: {str(e)}'})}\n\n"

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

agent_client = CarAgentClient(CAR_AGENT_URL, CAR_AGENT_TIMEOUT)
