# Simple System Architecture

```mermaid
graph LR
    %% Vehicle Side %%
    Car[("🚗 Renault Kwid<br/>OBD-II Port")]
    
    %% Hardware %%
    Adapter[("📡 ELM327 Bluetooth<br/>OBD Adapter")]
    
    %% Backend Services %%
    OBDService[("🔧 OBD Service<br/>Python-OBD Library")]
    AIService[("🤖 AI Diagnostic Agent<br/>Gemini Pro + LangChain")]
    
    %% Frontend %%
    Dashboard[("📱 Web Dashboard<br/>Next.js + FastAPI")]
    
    %% User %%
    User[("👨‍🔧 Car Owner")]
    
    %% Data Flows %%
    Car <--> Adapter
    Adapter <--> OBDService
    OBDService --> AIService
    AIService <--> Dashboard
    Dashboard <--> User
    
    %% Styling %%
    style Car fill:#e3f2fd,stroke:#1976d2
    style Adapter fill:#f3e5f5,stroke:#7b1fa2
    style OBDService fill:#e8f5e8,stroke:#388e3c
    style AIService fill:#fff3e0,stroke:#f57c00
    style Dashboard fill:#fce4ec,stroke:#c2185b
    style User fill:#fafafa,stroke:#616161
```

## Key Data Flow: User Question → Intelligent Response

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend (AI Agent)
    participant O as OBD Service
    participant V as Vehicle
    
    U->>F: "What is my coolant temp?"
    F->>B: HTTP POST /diagnose
    B->>O: Query COOLANT_TEMP command
    O->>V: Send OBD command via Bluetooth
    V->>O: Return 53°C reading
    O->>B: Parse and return 53.0 float
    B->>B: Analyze: "53°C is low for running engine"
    B->>F: Stream intelligent response
    F->>U: Display real-time diagnostic explanation
```

## Key Components:

1. **🚗 Vehicle**: Renault Kwid with OBD-II port
2. **📡 Adapter**: ELM327 Bluetooth OBD-II adapter
3. **🔧 OBD Service**: Manages Bluetooth connection and OBD commands
4. **🤖 AI Agent**: Interprets data and generates intelligent responses
5. **📱 Dashboard**: Web interface for users
6. **👨‍🔧 User**: Car owner asking diagnostic questions

This system transforms raw OBD data into intelligent, conversational diagnostics!