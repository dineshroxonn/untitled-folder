# Project Overview

This directory contains two related projects for an AI-powered car diagnostic system:

## 1. Car Diagnostic Agent (`car_diagnostic_agent/`)

A Python-based backend agent that connects to vehicle OBD-II systems and provides AI-powered diagnostics.

### Key Features
- Real-time OBD-II integration with live DTC reading and engine parameter monitoring
- AI-powered diagnostics using Google's Gemini API
- Support for all standard OBD-II protocols (CAN, ISO, SAE J1850)
- Smart fallback to manual input when OBD connection isn't available
- Persona-based responses where the AI responds as if it IS your specific vehicle

### Technology Stack
- Python 3.12+
- UV package manager
- Google Gemini API
- OBD-II library for vehicle communication
- FastAPI for HTTP endpoints
- A2A SDK for agent framework

### Directory Structure
```
car_diagnostic_agent/
├── app/                    # Core application code
│   ├── __main__.py        # Application entry point
│   ├── agent.py           # Main agent implementation
│   ├── obd_interface.py   # OBD connection management
│   ├── obd_config.py      # Configuration management
│   ├── obd_models.py      # Data models
│   ├── obd_services.py    # Diagnostic services
│   └── ...
├── pyproject.toml         # Project dependencies
├── README.md              # Documentation
└── ...
```

### Dependencies
Key dependencies include:
- `a2a-sdk[http-server]` - Agent framework
- `langchain-google-genai` - AI integration
- `obd` - OBD-II communication library
- `pyserial` - Serial communication
- `uvicorn` - ASGI server

### Building and Running
1. Set up environment:
   ```bash
   echo "GOOGLE_API_KEY=your_api_key_here" > .env
   ```
2. Install dependencies:
   ```bash
   uv install
   ```
3. Run the agent:
   ```bash
   ```

The agent will start on `http://localhost:10011`

## 2. A2A GUI (`a2a_gui/`)

A web-based GUI for the car diagnostic agent built with React and FastAPI. Provides a user-friendly interface for connecting to vehicles, running diagnostics, and interacting with the AI mechanic.

### Key Features
- Real-time vehicle connection status monitoring
- Diagnostic scanning with live data visualization
- Chat interface for interacting with the AI mechanic
- Responsive design with dark mode
- OBD-II connection management

### Technology Stack
- Frontend: React with TypeScript, Next.js, Tailwind CSS
- Backend: Python FastAPI
- Communication: Server-Sent Events (SSE) for streaming responses

### Directory Structure
```
a2a_gui/
├── main.py                # FastAPI backend server
├── api/                   # API endpoints
│   └── endpoints.py       # REST API routes
├── services/              # Backend services
│   └── car_agent_client.py # Client for car diagnostic agent
├── frontend/              # React frontend
│   ├── app/               # Next.js pages
│   ├── src/               # React components and logic
│   │   ├── components/    # UI components
│   │   ├── hooks/         # React hooks
│   │   ├── services/      # Frontend services
│   │   └── types.ts       # TypeScript types
│   └── ...
├── pyproject.toml         # Backend dependencies
├── README.md              # Documentation
└── ...
```

### Dependencies
Backend dependencies:
- FastAPI
- Uvicorn
- HTTPX
- Python-dotenv

Frontend dependencies:
- React 18+
- Next.js
- Tailwind CSS
- Lucide React icons
- Radix UI components

### Building and Running
1. Install backend dependencies:
   ```bash
   cd a2a_gui
   uv install
   ```

2. Install frontend dependencies:
   ```bash
   cd a2a_gui/frontend
   npm install
   ```

3. Build frontend:
   ```bash
   npm run build
   ```

4. Run the server:
   ```bash
   cd a2a_gui
   uvicorn main:app --reload
   ```

The GUI will be available at `http://localhost:8000`

## Integration

The two projects work together as follows:
1. The car_diagnostic_agent runs as a standalone service on port 10011
2. The a2a_gui connects to the agent via HTTP requests
3. User interactions in the GUI are sent to the agent for processing
4. The agent's responses are streamed back to the GUI for display

This architecture allows the diagnostic agent to run independently of the GUI, enabling multiple clients to connect to the same agent if needed.

## Testing Without Hardware

Both projects support mock mode for testing without physical OBD-II hardware:

### Enabling Mock Mode
```bash
cd car_diagnostic_agent
echo "enable_mock_mode=true" > .env
```

### Mock Data Provided
- DTC Codes: `["P0171", "P0174", "P0300", "P0301", "P0420"]`
- Live Data: RPM, speed, temperature, throttle position
- Vehicle Information: Simulated VIN and specs

## Development Workflows

### Frontend Development
```bash
cd a2a_gui/frontend
npm run dev  # Starts development server on http://localhost:5173
```

### Backend Development
```bash
cd a2a_gui
uvicorn main:app --reload  # Starts backend server on http://localhost:8000
```

### Agent Development
```bash
cd car_diagnostic_agent
uv run python -m app  # Starts agent on http://localhost:10011
```