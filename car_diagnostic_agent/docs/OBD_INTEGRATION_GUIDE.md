# OBD-II Integration Guide

This guide provides detailed information about the OBD-II integration capabilities of the Car Diagnostic Agent.

## \ud83d\udccb Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Supported Hardware](#supported-hardware)
3. [Installation & Setup](#installation--setup)
4. [Configuration](#configuration)
5. [Usage Examples](#usage-examples)
6. [API Reference](#api-reference)
7. [Troubleshooting](#troubleshooting)
8. [Testing](#testing)

## Architecture Overview

The OBD-II integration follows a layered architecture:

```
\u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510
\u2502   Car Diagnostic Agent       \u2502
\u251c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2524
\u2502 \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510 \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510 \u2502
\u2502 \u2502 DTC Reader \u2502 \u2502Live Data  \u2502 \u2502
\u2502 \u2502  Service   \u2502 \u2502 Service   \u2502 \u2502
\u2502 \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518 \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518 \u2502
\u251c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2524
\u2502    OBD Interface Manager      \u2502
\u251c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2524
\u2502     Protocol Handlers         \u2502
\u2502  \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2510\u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2510\u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2510  \u2502
\u2502  \u2502 CAN  \u2502\u2502 ISO  \u2502\u2502J1850\u2502  \u2502
\u2502  \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2518\u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2518\u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2518  \u2502
\u251c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2524
\u2502      ELM327 Adapter          \u2502
\u251c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2524
\u2502       Vehicle ECU            \u2502
\u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518
```

### Core Components

1. **OBD Interface Manager**: Central connection and communication management
2. **OBD Services**: Specialized services for DTCs, live data, and vehicle info
3. **Protocol Handlers**: Support for different OBD-II protocols
4. **Configuration Manager**: Settings and profile management
5. **Data Models**: Structured data representations

## Supported Hardware

### OBD-II Adapters

| Adapter Type | Interface | Protocols | Recommended Use |
|--------------|-----------|-----------|----------------|
| ELM327 USB | USB Serial | All OBD-II | Desktop applications |
| ELM327 Bluetooth | Bluetooth SPP | All OBD-II | Mobile/wireless |
| ELM327 WiFi | TCP/IP | All OBD-II | Network diagnostics |
| Professional Tools | USB/Ethernet | Enhanced | Advanced diagnostics |

### Tested Adapters

\u2705 **Verified Compatible**
- BAFX Products ELM327 USB
- OBDLink SX USB
- Veepeak ELM327 Bluetooth
- FIXD OBD-II Scanner

\u26a0\ufe0f **Known Issues**
- Some cheap clone adapters may have timing issues
- Bluetooth adapters can have connectivity problems on some systems

### Vehicle Compatibility

- **Year**: 1996 and newer (OBD-II mandated)
- **Region**: NAFTA, EU, and most global markets
- **Engine Types**: Gasoline, diesel, hybrid
- **Vehicle Classes**: Light-duty vehicles (under 14,000 lbs GVWR)

## Installation & Setup

### System Requirements

- Python 3.12+
- Operating System: Windows 10+, macOS 10.15+, Linux (any recent distribution)
- RAM: Minimum 1GB, Recommended 2GB+
- Storage: 100MB for installation, additional space for logs
- USB port (for USB adapters) or Bluetooth/WiFi capability

### Dependencies Installation

```bash
# Install the car diagnostic agent
cd car_diagnostic_agent
uv install

# Verify OBD dependencies
uv run python -c \"import obd; import serial; print('OBD dependencies OK')\"
```

### Driver Installation

#### Windows
1. Install drivers for your specific OBD adapter
2. Check Device Manager for proper COM port assignment
3. Note the COM port number (e.g., COM3)

#### macOS
1. Install FTDI or CH340 drivers if needed
2. Check for device in `/dev/tty.usbserial-*`
3. Grant permission in System Preferences > Security

#### Linux
1. Install appropriate kernel modules
2. Add user to `dialout` group: `sudo usermod -a -G dialout $USER`
3. Check device in `/dev/ttyUSB*` or `/dev/ttyACM*`

## Configuration

### Configuration File Location

Configuration is stored in:
- **Windows**: `%USERPROFILE%\\.car_diagnostic_agent\\obd_config.json`
- **macOS/Linux**: `~/.car_diagnostic_agent/obd_config.json`

### Basic Configuration

```json
{
  \"default_profile\": \"auto\",
  \"profiles\": {
    \"auto\": {
      \"port\": \"auto\",
      \"baudrate\": 38400,
      \"timeout\": 30.0,
      \"protocol\": \"auto\",
      \"auto_detect\": true,
      \"max_retries\": 3
    }
  },
  \"enable_mock_mode\": false,
  \"auto_connect_on_start\": false
}
```

### Advanced Configuration

#### Custom Profiles

```python
from app.obd_config import config_manager
from app.obd_models import OBDConnectionConfig, OBDProtocol

# Ford vehicles (2008+)
ford_config = OBDConnectionConfig(
    port=\"/dev/ttyUSB0\",
    baudrate=500000,  # High-speed CAN
    protocol=OBDProtocol.ISO_15765_4,
    timeout=10.0
)
config_manager.save_profile(\"ford_modern\", ford_config)

# GM vehicles (pre-2008)
gm_config = OBDConnectionConfig(
    port=\"/dev/ttyUSB0\",
    baudrate=38400,
    protocol=OBDProtocol.SAE_J1850_VPW,
    timeout=45.0
)
config_manager.save_profile(\"gm_legacy\", gm_config)
```

#### Environment Variables

```bash
# .env file
GOOGLE_API_KEY=your_api_key_here
OBD_MOCK_MODE=false
OBD_AUTO_CONNECT=true
OBD_LOG_LEVEL=INFO
```

## Usage Examples

### Basic OBD Operations

```python
from app.agent import CarDiagnosticAgent

# Create agent instance
agent = CarDiagnosticAgent()

# Connect to vehicle
result = await agent.connect_obd()
if result[\"success\"]:
    print(\"Connected to vehicle!\")

# Get diagnostic data
data = await agent.get_obd_diagnostic_data()
print(f\"Found {len(data['dtcs'])} trouble codes\")

# Start diagnostic session
session = await agent.start_diagnostic_session()
print(f\"Session ID: {session.session_id}\")
```

### Interactive Commands

#### Connection Management
```
User: \"Connect to OBD\"
Agent: \"Attempting to connect to your vehicle's OBD-II port...
        \u2705 Successfully connected to your vehicle!
        \ud83d\udce1 Connection Details:
        - Port: /dev/ttyUSB0
        - Protocol: ISO 15765-4 (CAN)
        - Supported Commands: 47\"
```

#### Diagnostic Scanning
```
User: \"Scan for trouble codes\"
Agent: \"\ud83d\udd0d Scanning your vehicle for diagnostic trouble codes...
        \ud83d\udccb Found 2 trouble codes:
        \ud83d\udd34 P0171: System Too Lean (Bank 1)
        \ud83d\udfe1 P0420: Catalyst System Efficiency Below Threshold\"
```

#### Live Data Monitoring
```
User: \"Show me live engine parameters\"
Agent: \"\ud83d\udcca Current Engine Parameters:
        \u2705 Engine RPM: 750 rpm
        \u2705 Coolant Temperature: 195\u00b0F
        \u26a0\ufe0f  Mass Air Flow: 45.2 g/s (HIGH)
        \u2705 Throttle Position: 0%\"
```

### Programmatic API

#### DTC Reading
```python
from app.obd_services import DTCReaderService
from app.obd_interface import OBDInterfaceManager

# Setup
manager = OBDInterfaceManager()
await manager.connect()
dtc_reader = DTCReaderService(manager)

# Read DTCs
dtcs = await dtc_reader.read_stored_dtcs()
for dtc in dtcs:
    print(f\"{dtc.code}: {dtc.description} ({dtc.severity.value})\")

# Clear DTCs (with confirmation)
response = await dtc_reader.clear_dtcs()
if response.success:
    print(\"DTCs cleared successfully\")
```

#### Live Data Streaming
```python
from app.obd_services import LiveDataService

# Setup monitoring
live_service = LiveDataService(manager)

async def data_callback(readings):
    for pid, reading in readings.items():
        print(f\"{reading.name}: {reading.value} {reading.unit}\")
        if not reading.is_within_range:
            print(f\"WARNING: {reading.name} out of range!\")

# Start monitoring
pids = [\"0C\", \"05\", \"11\", \"0D\"]  # RPM, coolant, throttle, speed
await live_service.start_monitoring(pids, interval=1.0, callback=data_callback)

# Stop monitoring
await live_service.stop_monitoring()
```

## API Reference

### OBDInterfaceManager

```python
class OBDInterfaceManager:
    async def connect(config: OBDConnectionConfig = None) -> OBDResponse
    async def disconnect() -> OBDResponse
    async def query(command: OBDCommand) -> OBDResponse
    async def test_connection() -> OBDResponse
    async def get_connection_info() -> Dict[str, Any]
    
    @property
    def is_connected(self) -> bool
```

### DTCReaderService

```python
class DTCReaderService:
    async def read_stored_dtcs() -> List[DTCInfo]
    async def read_pending_dtcs() -> List[DTCInfo]
    async def clear_dtcs() -> OBDResponse
```

### LiveDataService

```python
class LiveDataService:
    async def read_parameter(pid: str) -> LiveDataReading
    async def read_multiple_parameters(pids: List[str]) -> Dict[str, LiveDataReading]
    async def get_basic_engine_data() -> Dict[str, LiveDataReading]
    async def start_monitoring(pids: List[str], interval: float, callback)
    async def stop_monitoring()
```

### VehicleInfoService

```python
class VehicleInfoService:
    async def get_vehicle_info() -> VehicleInfo
```

## Troubleshooting

### Connection Issues

#### \"Failed to connect to OBD adapter\"

**Possible Causes:**
- Adapter not plugged in
- Vehicle ignition off
- Driver issues
- Port permissions

**Solutions:**
```bash
# Check device detection
# Linux/macOS
ls /dev/tty* | grep -E \"(USB|ACM)\"

# Windows
# Check Device Manager > Ports (COM & LPT)

# Test with different configurations
from app.obd_config import config_manager
ports = config_manager.get_available_ports()
print(\"Available ports:\", ports)
```

#### \"No data received for command\"

**Possible Causes:**
- Vehicle doesn't support the parameter
- Wrong protocol
- Timing issues

**Solutions:**
```python
# Check supported commands
commands = await manager.get_supported_commands()
print(f\"Supported commands: {len(commands)}\")

# Try manual protocol selection
config.protocol = OBDProtocol.ISO_15765_4
await manager.connect(config)
```

### Performance Issues

#### Slow Response Times

```python
# Optimize configuration
config = OBDConnectionConfig(
    port=\"/dev/ttyUSB0\",
    baudrate=115200,  # Higher speed
    timeout=10.0,     # Shorter timeout
    protocol=OBDProtocol.ISO_15765_4  # Specific protocol
)
```

#### Memory Usage

```python
# Limit monitoring parameters
pids = [\"0C\", \"05\"]  # Only essential parameters

# Increase monitoring interval
await live_service.start_monitoring(pids, interval=5.0)  # 5 second intervals
```

### Protocol-Specific Issues

#### CAN Bus (ISO 15765-4)
- Most reliable for 2008+ vehicles
- High-speed communication
- Best parameter support

#### J1850 PWM/VPW
- Older Ford/GM vehicles
- Slower communication
- May require longer timeouts

#### ISO 14230-4 (KWP2000)
- Many Asian manufacturers
- Moderate speed
- Good reliability

## Testing

### Unit Tests

```bash
# Run all OBD tests
uv run pytest tests/test_obd_integration.py -v

# Run specific test categories
uv run pytest tests/test_obd_integration.py::TestOBDModels -v
uv run pytest tests/test_obd_integration.py::TestMockOBDInterface -v
```

### Integration Tests

```bash
# Test with mock adapter
OBD_MOCK_MODE=true uv run pytest tests/test_obd_integration.py

# Test with real hardware (if available)
OBD_MOCK_MODE=false uv run pytest tests/test_obd_integration.py
```

### Manual Testing

```python
# Test script for manual verification
from app.obd_interface import MockOBDInterfaceManager
from app.obd_models import OBDConnectionConfig

async def test_mock_connection():
    manager = MockOBDInterfaceManager(OBDConnectionConfig(port=\"mock\"))
    response = await manager.connect()
    assert response.success
    print(\"Mock connection test passed!\")

# Run with: python -c \"import asyncio; asyncio.run(test_mock_connection())\"
```

### Performance Benchmarks

```python
import time
from app.obd_services import LiveDataService

async def benchmark_live_data():
    # Measure parameter read time
    start = time.time()
    reading = await live_service.read_parameter(\"0C\")
    duration = time.time() - start
    print(f\"Parameter read time: {duration:.3f}s\")

    # Measure multiple parameter read time
    start = time.time()
    readings = await live_service.read_multiple_parameters([\"0C\", \"05\", \"11\"])
    duration = time.time() - start
    print(f\"Multiple parameter read time: {duration:.3f}s\")
```

---

## Advanced Features

### Custom Protocol Implementation

For specialized vehicle diagnostics:

```python
from app.obd_interface import OBDInterfaceManager
import obd

class CustomProtocolManager(OBDInterfaceManager):
    async def custom_query(self, pid: str, data: bytes) -> OBDResponse:
        # Implement custom protocol logic
        pass
```

### Data Logging

```python
from app.obd_models import DiagnosticSession
import json

class DataLogger:
    def __init__(self, session: DiagnosticSession):
        self.session = session
        
    def export_session(self, filename: str):
        data = {
            \"session_id\": self.session.session_id,
            \"vehicle_info\": asdict(self.session.vehicle_info),
            \"dtcs\": [asdict(dtc) for dtc in self.session.dtcs_found],
            \"live_data\": [asdict(reading) for reading in self.session.live_data_readings]
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
```

This integration guide provides comprehensive coverage of the OBD-II capabilities. For additional support, refer to the main README.md and the test suite examples.", "original_text": "# Test package for car diagnostic agent"