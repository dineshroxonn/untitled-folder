# Untitled Folder - Car Diagnostic System

This repository contains an AI-powered car diagnostic system with OBD-II integration.

## 📁 Project Structure

```
.
├── a2a_gui/                 # Web GUI for the car diagnostic agent
│   ├── README.md           # GUI documentation
│   ├── main.py             # FastAPI backend server
│   ├── api/                # API endpoints
│   ├── services/           # Backend services
│   └── frontend/           # React frontend application
│
├── car_diagnostic_agent/    # Backend agent that connects to vehicles
│   ├── README.md           # Agent documentation
│   ├── pyproject.toml      # Dependencies
│   └── app/                # Core application code
│
└── QWEN.md                 # Development context and project overview
```

## 🚗 Car Diagnostic Agent

An AI agent that acts as a virtual car mechanic with real-time OBD-II diagnostic capabilities.

### Features
- Connects directly to your vehicle's OBD-II port
- Reads live diagnostic trouble codes (DTCs) from the ECU
- Monitors real-time engine parameters
- Automatically detects VIN, make, model, and year
- AI-powered diagnostics using Google Gemini API
- Responds as if it IS your specific vehicle

### Quick Start
```bash
cd car_diagnostic_agent
echo "GOOGLE_API_KEY=your_api_key_here" > .env
uv install
uv run python -m app
```

The agent starts on `http://localhost:10011`

## 🖥️ A2A GUI

Web-based graphical interface for interacting with the car diagnostic agent.

### Features
- Vehicle connection management
- Diagnostic scanning and monitoring
- Chat interface with AI mechanic
- Real-time data visualization
- Responsive design with dark mode

### Quick Start
```bash
# Terminal 1: Start the agent
cd car_diagnostic_agent
uv run python -m app

# Terminal 2: Start the GUI
cd a2a_gui
uv install
cd frontend
npm install
npm run build
cd ..
uvicorn main:app --reload
```

The GUI is available at `http://localhost:8000`

## 🧪 Testing Without Hardware

Enable mock mode to test without physical OBD-II hardware:

```bash
cd car_diagnostic_agent
echo "enable_mock_mode=true" > .env
```

This provides simulated diagnostic data for testing purposes.

## 📄 Documentation

- [Car Diagnostic Agent README](car_diagnostic_agent/README.md)
- [A2A GUI README](a2a_gui/README.md)
- [Development Context](QWEN.md)