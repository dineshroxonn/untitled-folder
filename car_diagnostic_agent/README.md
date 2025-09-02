
# Car Diagnostic Agent with OBD-II Integration

This A2A agent acts as a virtual car mechanic with real-time OBD-II diagnostic capabilities. It can connect directly to your vehicle's OBD-II port to read live diagnostic data, or work with manually provided Diagnostic Trouble Codes (DTCs).

## 🚗 Features

### Real-time OBD-II Integration
- **Live DTC Reading**: Automatically reads trouble codes directly from your vehicle's ECU
- **Real-time Parameters**: Monitors engine RPM, coolant temperature, throttle position, and more
- **Vehicle Information**: Automatically detects VIN, make, model, and year
- **Multiple Protocols**: Supports all standard OBD-II protocols (CAN, ISO, SAE J1850)
- **Smart Fallback**: Falls back to manual input when OBD connection isn't available

### AI-Powered Diagnostics
- **Persona-based Response**: The AI responds as if it IS your specific vehicle
- **Comprehensive Analysis**: Combines live data with expert mechanical knowledge
- **Step-by-step Repair Guidance**: From simple checks to complex repairs
- **Safety Warnings**: Prioritizes critical issues detected from live data

## 🔧 Hardware Requirements

### Supported OBD-II Adapters
- **ELM327 USB**: Recommended for desktop use
- **ELM327 Bluetooth**: For wireless connection
- **ELM327 WiFi**: For network-based diagnostics
- **Professional Scan Tools**: Advanced diagnostics support

### Vehicle Compatibility
- All vehicles manufactured after 1996 (OBD-II compliant)
- Supports gasoline and diesel engines
- Light-duty vehicles (cars, SUVs, light trucks)

## 🚀 Quick Start

### Prerequisites

- Python 3.12 or higher
- [UV](https://docs.astral.sh/uv/) package manager
- Google Gemini API Key
- OBD-II adapter (optional - can work without)

### Installation

1. **Clone and navigate to the project:**
   ```bash
   cd car_diagnostic_agent
   ```

2. **Set up your environment:**
   ```bash
   echo "GOOGLE_API_KEY=your_api_key_here" > .env
   ```

3. **Install dependencies:**
   ```bash
   uv install
   ```

### Running the Agent

1. **Start the agent server:**
   ```bash
   uv run python -m app
   ```
   The agent will start on `http://localhost:10011`

2. **Connect to your vehicle (optional):**
   - Plug your OBD-II adapter into your vehicle's diagnostic port
   - Turn on your vehicle's ignition (engine doesn't need to be running)
   - The agent will attempt to auto-connect on first use

3. **Interact with the agent:**
   ```bash
   # From the a2a-samples root directory
   cd samples/python/hosts/cli
   uv run . --agent http://localhost:10011
   ```

## 💬 Usage Examples

### With OBD-II Connection
```
> Connect to OBD and scan my vehicle
🔍 Scanning your vehicle for diagnostic trouble codes...

📋 Found 2 trouble codes:
🔴 P0171: System Too Lean (Bank 1)
🟡 P0420: Catalyst System Efficiency Below Threshold (Bank 1)

📊 Current Engine Parameters:
✅ Engine RPM: 750 rpm
⚠️  Coolant Temperature: 210°F (OUT OF RANGE)
✅ Throttle Position: 0%

🚗 Vehicle Information:
- Make & Model: Honda Civic
- Year: 2021
- VIN: 1HGBH41JXMN109186

Hello, I am your 2021 Honda Civic. I can see that I'm running a bit lean and my catalytic converter efficiency is below threshold...
```

### Manual DTC Input (No OBD)
```
> My 2015 Ford Focus is showing codes P0171 and P0174. What's going on?

Hello, I am a 2015 Ford Focus. I can see you're experiencing codes P0171 and P0174. These codes indicate that both Bank 1 and Bank 2 are running too lean...
```

### Live Monitoring
```
> Show me live engine parameters
📊 Current Engine Parameters:
✅ Engine RPM: 2,150 rpm
✅ Vehicle Speed: 35 mph
✅ Coolant Temperature: 195°F
✅ Intake Air Temperature: 75°F
⚠️  Mass Air Flow: 45.2 g/s (HIGH)
✅ Throttle Position: 25%
```

## ⚙️ Configuration

### OBD Configuration

The agent automatically manages OBD connections, but you can customize settings:

```python
# Configuration is stored in ~/.car_diagnostic_agent/obd_config.json
{
  "default_profile": "auto",
  "profiles": {
    "auto": {
      "port": "auto",          # Auto-detect port
      "baudrate": 38400,        # Communication speed
      "timeout": 30.0,          # Connection timeout
      "protocol": "auto",       # Auto-detect protocol
      "auto_detect": true,      # Enable auto-detection
      "max_retries": 3          # Connection retry attempts
    }
  },
  "enable_mock_mode": false,   # For testing without hardware
  "auto_connect_on_start": false
}
```

### Mock Mode for Testing

Test the OBD features without hardware:

```bash
# Enable mock mode
echo "enable_mock_mode=true" >> .env
```

### Available Commands

| Command | Description |
|---------|-------------|
| `Connect to OBD` | Connect to vehicle's OBD-II port |
| `Disconnect OBD` | Disconnect from OBD adapter |
| `Scan for trouble codes` | Read all stored DTCs |
| `Show live engine data` | Display real-time parameters |
| `Clear trouble codes` | Clear stored DTCs (with confirmation) |

## 🧪 Testing

Run the test suite to verify OBD integration:

```bash
# Run all tests
uv run pytest tests/

# Run specific test categories
uv run pytest tests/test_obd_integration.py -v
```

## 🔍 Troubleshooting

### Common OBD Connection Issues

1. **"Failed to connect to OBD adapter"**
   - Check adapter is plugged into vehicle's OBD port
   - Ensure vehicle ignition is ON
   - Verify adapter drivers are installed
   - Try different USB port

2. **"No data received"**
   - Vehicle may not support requested parameter
   - Check protocol compatibility
   - Try manual protocol selection

3. **"Port not found"**
   - Install adapter drivers
   - Check device manager (Windows) or lsusb (Linux)
   - Try manual port specification

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🛡️ Safety & Legal

### Safety Considerations
- **Read-only by default**: Agent only reads data, never writes
- **Critical alerts**: Prioritizes safety-related issues
- **Engine protection**: Monitors for dangerous conditions

### Legal Compliance
- Respects automotive data protection standards
- Optional VIN anonymization
- Audit logging of all OBD operations

## 🔧 Advanced Configuration

### Custom Protocol Settings

For specific vehicle requirements:

```python
from app.obd_config import config_manager
from app.obd_models import OBDConnectionConfig, OBDProtocol

# Create custom profile for older GM vehicle
config = OBDConnectionConfig(
    port="/dev/ttyUSB0",
    baudrate=38400,
    protocol=OBDProtocol.SAE_J1850_VPW,
    timeout=45.0
)

config_manager.save_profile("gm_older", config)
config_manager.set_default_profile("gm_older")
```

### Performance Tuning

- **Monitoring Interval**: Adjust real-time data refresh rate
- **Connection Pooling**: Optimize for multiple concurrent requests
- **Protocol Selection**: Use specific protocols for better performance

## 📚 API Reference

### OBD Interface Manager
```python
from app.obd_interface import OBDInterfaceManager

manager = OBDInterfaceManager(config)
await manager.connect()
response = await manager.query(obd.commands.RPM)
```

### Diagnostic Services
```python
from app.obd_services import DTCReaderService, LiveDataService

dtc_reader = DTCReaderService(manager)
dtcs = await dtc_reader.read_stored_dtcs()

live_service = LiveDataService(manager)
data = await live_service.get_basic_engine_data()
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Run the test suite
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the test suite for usage examples

---

**Note**: This tool is for diagnostic purposes only. Always consult a qualified mechanic for vehicle repairs and safety-critical issues.
