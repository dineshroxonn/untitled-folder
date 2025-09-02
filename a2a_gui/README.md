# A2A GUI - Car Diagnostic Agent Web Interface

Web GUI for the Car Diagnostic Agent with OBD-II Integration. This interface provides a user-friendly way to connect to your vehicle, run diagnostics, and interact with the AI-powered car mechanic.

## 🚗 Features

### Vehicle Connection Management
- Connect to OBD-II adapters (Bluetooth, USB, WiFi)
- Real-time connection status monitoring
- Connection configuration and troubleshooting

### Diagnostic Tools
- One-click vehicle scanning
- Real-time engine parameter monitoring
- DTC code reading and clearing
- Live data visualization

### AI-Powered Chat Interface
- Natural language interaction with your vehicle
- AI analysis of diagnostic data
- Step-by-step repair guidance
- Persona-based responses (AI responds as your specific vehicle)

## 🛠️ Technology Stack

### Frontend
- **React** with TypeScript
- **Next.js** 15+ for SSR and routing
- **Tailwind CSS** for styling
- **Radix UI** components
- **Lucide React** icons

### Backend
- **FastAPI** for API endpoints
- **Server-Sent Events (SSE)** for real-time streaming
- **HTTPX** for async HTTP requests

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- UV package manager
- Car Diagnostic Agent running (separate service)

### Installation

1. **Install backend dependencies:**
   ```bash
   cd a2a_gui
   uv install
   ```

2. **Install frontend dependencies:**
   ```bash
   cd frontend
   npm install
   ```

3. **Build the frontend:**
   ```bash
   npm run build
   ```

### Running the Application

1. **Start the backend server:**
   ```bash
   cd a2a_gui
   uvicorn main:app --reload
   ```
   The backend will start on `http://localhost:8000`

2. **Access the GUI:**
   Open your browser and navigate to `http://localhost:8000`

### Development

1. **Frontend Development:**
   ```bash
   cd frontend
   npm run dev
   ```
   The frontend development server will start on `http://localhost:5173`

2. **Backend Development:**
   ```bash
   cd a2a_gui
   uvicorn main:app --reload
   ```

## 📁 Project Structure

```
a2a_gui/
├── main.py              # FastAPI application entry point
├── api/                 # API endpoints
│   └── endpoints.py     # REST API routes
├── services/            # Business logic and services
│   └── car_agent_client.py  # Client for car diagnostic agent
├── frontend/            # React frontend application
│   ├── app/             # Next.js pages
│   ├── src/             # React components and logic
│   │   ├── components/  # UI components
│   │   ├── hooks/       # React hooks
│   │   ├── services/    # Frontend services
│   │   └── types.ts     # TypeScript types
│   ├── public/          # Static assets
│   └── package.json     # Frontend dependencies
├── pyproject.toml       # Backend dependencies
└── README.md            # This file
```

## 🔧 Configuration

The GUI connects to the Car Diagnostic Agent service. By default, it expects the agent to be running on `http://localhost:10011`.

To change the agent URL:
```bash
# Set environment variable
export CAR_AGENT_URL=http://your-agent-host:port
```

Or create a `.env` file in the `a2a_gui` directory:
```bash
CAR_AGENT_URL=http://your-agent-host:port
```

## 🎯 Usage

### Connecting to Your Vehicle
1. Connect your OBD-II adapter to your vehicle
2. Turn on the vehicle ignition
3. In the GUI, click "Connect to Vehicle"
4. The system will auto-detect and connect to your adapter

### Running Diagnostics
1. After connecting, click "Run Full Diagnostic"
2. The system will scan for DTC codes and read live data
3. Results will appear in the chat interface

### Chatting with the AI Mechanic
1. Type natural language questions in the chat input
2. Examples:
   - "What do these codes mean?"
   - "How can I fix the P0171 code?"
   - "Is my engine running normally?"
3. The AI will respond as your specific vehicle

## 🧪 Testing

### Mock Mode
To test without physical hardware, enable mock mode in the Car Diagnostic Agent:

1. In the agent directory:
   ```bash
   echo "enable_mock_mode=true" >> .env
   ```

2. Start the agent and GUI as normal
3. The GUI will work with simulated data

## 🤝 Development Guidelines

### Frontend
- Use React hooks and functional components
- Follow TypeScript best practices
- Use Tailwind CSS for styling
- Implement proper error handling

### Backend
- Use FastAPI for API endpoints
- Implement async/await for non-blocking operations
- Use Pydantic for data validation
- Follow REST API conventions

## 🆘 Troubleshooting

### Common Issues
1. **Agent Not Found**: Ensure the Car Diagnostic Agent is running on port 10011
2. **Connection Failed**: Check OBD adapter connection and vehicle ignition
3. **No Data**: Verify vehicle OBD-II compatibility (1996+)

### Debugging
Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📄 License

This project is licensed under the MIT License.