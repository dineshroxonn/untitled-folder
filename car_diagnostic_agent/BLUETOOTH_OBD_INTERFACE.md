# Bluetooth-Aware OBD Interface Implementation

## Overview

This document describes the implementation of a Bluetooth-aware OBD interface that handles Bluetooth pairing and connection before establishing OBD communication, using the same approach as mobile apps.

## Key Features

1. **Bluetooth Connection Handling**: Automatically connects to paired OBD devices via Bluetooth before OBD communication
2. **Persistent Connections**: Maintains persistent OBD connections with keep-alive mechanisms
3. **Automatic Reconnection**: Automatically reconnects if connections are lost
4. **Mobile App Compatibility**: Uses the same approach as successful mobile OBD apps

## Implementation Details

### BluetoothOBDInterfaceManager Class

The `BluetoothOBDInterfaceManager` extends `PersistentOBDInterfaceManager` and adds Bluetooth-specific functionality:

```python
from car_diagnostic_agent.app.bluetooth_obd_interface import BluetoothOBDInterfaceManager

# Create manager instance
obd_manager = BluetoothOBDInterfaceManager()

# Connect (automatically handles Bluetooth connection)
result = await obd_manager.connect()
```

### Key Methods

1. **`_is_bluetooth_available()`**: Checks if Bluetooth utilities (blueutil) are available
2. **`_is_obd_paired()`**: Verifies if the OBD device is paired with the system
3. **`_connect_bluetooth_device()`**: Establishes Bluetooth connection to the OBD device
4. **`_ensure_bluetooth_connection()`**: Ensures Bluetooth connection before OBD communication

### Connection Flow

1. Check if Bluetooth utilities are available
2. Verify OBD device is paired
3. Connect to Bluetooth device using `blueutil --connect`
4. Wait for connection to stabilize (2 seconds)
5. Establish OBD connection through the serial port
6. Start keep-alive and monitoring tasks

## Usage in Car Diagnostic Agent

The agent now uses the Bluetooth-aware OBD interface by default:

```python
# In agent.py
try:
    from .bluetooth_obd_interface import BluetoothOBDInterfaceManager as OBDInterfaceManager
except ImportError:
    # Fallback chain to enhanced and original versions
```

## Benefits

1. **Automatic Bluetooth Handling**: No manual Bluetooth connection required
2. **Mobile App Parity**: Uses the same approach that works in mobile apps
3. **Persistent Connections**: Connections stay alive between operations
4. **Error Recovery**: Automatic reconnection if connections are lost
5. **Backward Compatibility**: Falls back to enhanced/original versions if needed

## Requirements

1. **blueutil**: Command-line Bluetooth utility (install via Homebrew: `brew install blueutil`)
2. **Paired OBD Device**: OBD adapter must be paired with the system
3. **Correct Bluetooth Address**: Default address is `00:10:CC:4F:36:03` (can be configured)

## Troubleshooting

### Common Issues

1. **Bluetooth Utilities Not Found**: Install blueutil with `brew install blueutil`
2. **Device Not Paired**: Pair the OBD adapter via System Preferences > Bluetooth
3. **Connection Failures**: Ensure vehicle ignition is ON and adapter is properly connected

### Testing Bluetooth Connection

```bash
# Check if device is paired
blueutil --paired

# Manually connect to device
blueutil --connect 00:10:CC:4F:36:03

# Check connection status
blueutil --is-connected 00:10:CC:4F:36:03
```

## Integration with Existing Code

The implementation is fully backward compatible. Existing code that uses `OBDInterfaceManager` will automatically benefit from Bluetooth-aware connection handling without any changes required.

## Future Enhancements

1. **Dynamic Bluetooth Address Detection**: Automatically detect OBD adapter address
2. **Multiple Device Support**: Handle multiple paired OBD devices
3. **Connection Quality Monitoring**: Monitor Bluetooth signal strength
4. **Advanced Error Handling**: More sophisticated error recovery mechanisms