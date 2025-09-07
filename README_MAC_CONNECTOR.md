# Mac OBD Connector

A complete solution for connecting ELM327 OBD2 scanners to MacBook Air, following best practices for macOS compatibility.

## Features

- Automatic detection of Bluetooth OBD devices
- Proper serial port path identification for macOS
- Connection with optimized parameters for Bluetooth devices
- Comprehensive testing and diagnostics
- Troubleshooting guidance

## Prerequisites

1. **Hardware**: ELM327 Bluetooth OBD2 scanner
2. **Vehicle**: A car with OBD2 port (usually under the dashboard)
3. **macOS**: Tested on MacBook Air and other Mac computers

## Installation

1. Clone or download this repository
2. Install the required Python packages:

```bash
pip install -r requirements.txt
```

## Usage

Run the connector script:

```bash
python3 mac_obd_connector.py
```

The script will automatically:
1. Scan for paired Bluetooth OBD devices
2. Identify the correct serial port path
3. Test serial connection with the device
4. Establish OBD connection using the python-obd library
5. Verify functionality with basic OBD commands

## How It Works

### Bluetooth Device Detection
The script uses `system_profiler SPBluetoothDataType` to scan for paired Bluetooth devices and identifies potential OBD adapters based on device names.

### Serial Port Identification
It scans all available serial ports using `serial.tools.list_ports` and looks for macOS-specific Bluetooth serial port patterns like `/dev/tty.OBDII-SPP`.

### Connection Optimization
The script uses connection parameters optimized for Bluetooth devices:
- `fast=False` for stability
- Extended timeouts (30 seconds) for Bluetooth reliability
- Standard baud rate of 38400 (with fallback to other rates)

### Testing and Verification
The script performs comprehensive testing:
1. Direct serial communication tests with AT commands
2. ELM327 protocol initialization
3. Basic OBD command execution

## Troubleshooting

If you encounter connection issues:

1. **Ensure Bluetooth Pairing**: 
   - Go to System Preferences > Bluetooth
   - Make sure your OBD device is paired (look for devices with "OBD", "ELM327" in the name)
   - The device should appear as connected

2. **Check Serial Ports**:
   - Run `ls /dev/tty.*` in Terminal
   - Look for ports with "OBD" or "ELM" in the name

3. **Vehicle Preparation**:
   - Ensure the OBD adapter is properly plugged into the vehicle's OBD port
   - Turn the vehicle's ignition to the ON position (engine off is fine for most tests)

4. **Try Different Baud Rates**:
   - The script automatically tries common baud rates (38400, 9600, 19200, 57600, 115200)

5. **Driver Issues**:
   - Some OBD adapters may require specific drivers
   - Check the manufacturer's website for macOS drivers

## Supported OBD Commands

Once connected, you can use any commands from the python-obd library:
- `obd.commands.RPM` - Engine RPM
- `obd.commands.SPEED` - Vehicle speed
- `obd.commands.COOLANT_TEMP` - Coolant temperature
- `obd.commands.DTC` - Diagnostic trouble codes
- And many more...

## Example Usage

After establishing connection with the script, you can extend it to read vehicle data:

```python
import obd

# The connection is already established by our script
# You can access it through the connector object

# Read engine RPM
rpm = connector.connection.query(obd.commands.RPM)
print(f"Engine RPM: {rpm.value}")

# Read vehicle speed
speed = connector.connection.query(obd.commands.SPEED)
print(f"Speed: {speed.value}")
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.