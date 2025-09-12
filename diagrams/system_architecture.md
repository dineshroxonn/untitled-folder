# System Architecture Diagram

```mermaid
graph TD
    %% Style Definitions %%
    classDef vehicleStyle fill:#e1f5fe,stroke:#01579b,color:#000
    classDef adapterStyle fill:#f3e5f5,stroke:#4a148c,color:#000
    classDef agentStyle fill:#e8f5e8,stroke:#1b5e20,color:#000
    classDef guiStyle fill:#fff3e0,stroke:#e65100,color:#000
    classDef userStyle fill:#fafafa,stroke:#616161,color:#000
    classDef dataFlow fill:#bbdefb,stroke:#1976d2,color:#000
    classDef controlFlow fill:#ffcdd2,stroke:#c62828,color:#000
    
    %% Entities %%
    subgraph Vehicle["🚗 Vehicle (Renault Kwid)"]
        ECU[("ECU<br/>Engine Control Unit")]
        Sensors[("_engine Sensors_<br/>RPM, Temp, O2, etc.")]
        OBDPort[("OBD-II Port<br/>Diagnostic Interface")]
    end
    
    subgraph Hardware["📡 Hardware Layer"]
        OBDAdapter[("ELM327 OBD Adapter<br/>Bluetooth Classic")]
    end
    
    subgraph Backend["🖥️ Backend Services"]
        subgraph CarAgent["🔧 Car Diagnostic Agent"]
            OBDInterface[("Bluetooth OBD Interface<br/>Persistent Connection Manager")]
            DTCSvc[("DTC Reader Service")]
            LiveDataSvc[("Live Data Service")]
            VehicleInfoSvc[("Vehicle Info Service")]
            AIAgent[("Gemini AI Agent<br/>LangChain Integration")]
        end
        
        subgraph AGUI["🎨 A2A GUI Backend"]
            APIEndpoints[("FastAPI Endpoints")]
            CarClient[("Car Agent Client")]
        end
    end
    
    subgraph Frontend["📱 Frontend"]
        WebUI[("Next.js Web Interface<br/>Real-time Dashboard")]
        ChatInterface[("AI Diagnostic Chat")]
    end
    
    User[("👨‍🔧 User<br/>Car Owner/Mechanic")]
    
    %% Connections %%
    %% Vehicle to Hardware %%
    OBDPort <-- "Wired Connection" --> OBDAdapter
    
    %% Hardware to Backend %%
    OBDAdapter <-- "Bluetooth Serial" --> OBDInterface
    
    %% Backend Internal Connections %%
    OBDInterface --> DTCSvc
    OBDInterface --> LiveDataSvc
    OBDInterface --> VehicleInfoSvc
    DTCSvc --> AIAgent
    LiveDataSvc --> AIAgent
    VehicleInfoSvc --> AIAgent
    AIAgent --> APIEndpoints
    CarClient <-- "HTTP/REST" --> APIEndpoints
    
    %% Frontend to Backend %%
    WebUI <-- "HTTP/WebSocket" --> APIEndpoints
    ChatInterface <-- "Server-Sent Events" --> APIEndpoints
    
    %% User Interaction %%
    User <-- "Interacts" --> WebUI
    User <-- "Asks Questions" --> ChatInterface
    
    %% Data Flows %%
    LiveDataSvc -- "Real-time Data Stream" --> AIAgent
    AIAgent -- "Intelligent Analysis" --> ChatInterface
    OBDInterface -- "Raw OBD Commands" --> OBDAdapter
    OBDAdapter -- "Vehicle Data" --> OBDInterface
    
    %% Styling %%
    class Vehicle,ECU,Sensors,OBDPort vehicleStyle
    class OBDAdapter adapterStyle
    class OBDInterface,DTCSvc,LiveDataSvc,VehicleInfoSvc,AIAgent agentStyle
    class APIEndpoints,CarClient,WebUI,ChatInterface guiStyle
    class User userStyle
    
    %% Legend %%
    subgraph Legend["🔑 Legend"]
        DataFlowLegend[("Data Flow<br/>Real-time Information")]
        ControlFlowLegend[("Control Flow<br/>Commands/Requests")]
    end
    
    class DataFlowLegend dataFlow
    class ControlFlowLegend controlFlow
```

## System Components Explained

### 🚗 **Vehicle Layer**
- **ECU**: The car's main computer that controls engine operations
- **Sensors**: Various sensors monitoring engine parameters (RPM, temperature, oxygen levels, etc.)
- **OBD-II Port**: Standardized diagnostic interface for accessing vehicle data

### 📡 **Hardware Layer** 
- **ELM327 OBD Adapter**: Bluetooth-enabled device that translates between OBD-II protocol and serial communication

### 🖥️ **Backend Services**

#### 🔧 **Car Diagnostic Agent**
- **Bluetooth OBD Interface**: Manages persistent Bluetooth connection to OBD adapter
- **DTC Reader Service**: Reads and interprets Diagnostic Trouble Codes
- **Live Data Service**: Monitors real-time engine parameters
- **Vehicle Info Service**: Retrieves vehicle identification and specifications
- **Gemini AI Agent**: Processes data and generates intelligent diagnostic insights

#### 🎨 **A2A GUI Backend**
- **FastAPI Endpoints**: REST API for frontend communication
- **Car Agent Client**: Proxy client for communicating with Car Diagnostic Agent

### 📱 **Frontend**
- **Next.js Web Interface**: Modern web-based dashboard for vehicle diagnostics
- **AI Diagnostic Chat**: Interactive chat interface for asking diagnostic questions

### 👨‍🔧 **User**
- **Car Owner/Mechanic**: End user interacting with the system

## Data Flow Process

1. **Vehicle Data Collection**: Sensors → ECU → OBD-II Port
2. **Hardware Translation**: OBD-II Protocol → Bluetooth Serial → OBD Adapter
3. **Backend Processing**: OBD Interface → Service Layers → AI Analysis
4. **Frontend Presentation**: API → Web Interface → User Dashboard
5. **Intelligent Interaction**: User Questions → AI Agent → Diagnostic Insights

This architecture enables real-time, intelligent vehicle diagnostics with an autonomous AI agent that continuously monitors and analyzes vehicle health.