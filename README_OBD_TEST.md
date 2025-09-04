# OBD-II Bluetooth Connection Test

This script helps diagnose connectivity issues with OBD-II Bluetooth adapters on macOS.

## Prerequisites

1. Python 3.6+
2. Bluetooth OBD-II adapter (ELM327 or compatible)
3. OBD-II adapter paired with your laptop

## Installation

```bash
pip install -r requirements.txt
```

## Usage

1. **Pair your OBD-II adapter with your laptop** via Bluetooth
2. **Run the test script**:
   ```bash
   python obd_test.py
   ```

## What the script does

1. **Lists all available serial ports** and identifies potential OBD ports
2. **Tests raw serial connectivity** to each port
3. **Tests OBD protocol connectivity** with various configurations
4. **Reports successful connections** with working parameters

## Common Issues and Solutions

### 1. "No serial ports found"
- Make sure your OBD adapter is paired with your laptop
- Check Bluetooth settings and ensure the adapter is connected

### 2. "Serial connection failed"
- Try different baud rates (38400, 9600, 19200, 57600, 115200)
- Check if another application is using the port
- Restart the Bluetooth service on your laptop

### 3. "OBD connection failed"
- Try different protocols (AUTO, 6, 7, 8, 9)
- Ensure your car's ignition is ON (engine doesn't need to be running)
- Check if the OBD adapter is properly plugged into the OBD port

## Expected Output

When successful, you should see something like:
```
🎉 SUCCESS! Working configuration:
   Port: /dev/tty.OBDII-Port
   Baudrate: 38400
   Protocol: AUTO
```

## Using the Results

Once you find a working configuration, you can use these parameters in your car diagnostic agent by modifying the OBD configuration file at `~/.car_diagnostic_agent/obd_config.json`.