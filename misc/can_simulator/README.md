# CAN Simulator with python-can

This directory contains tools for simulating CAN bus traffic using the `python-can` library, which generates realistic candump files that closely match the format used by actual CAN analyzers.

## Files

- `honda_accord_simulator.py`: Generates realistic candump files for a Honda Accord
- `can_simulator.py`: Original simulator using custom implementation
- `cli.py`: Command-line interface for the original simulator
- `test_can_simulator.py`: Test utility for the original simulator
- `examples/`: Example usage scripts for the original simulator

## Honda Accord Simulator (Recommended)

The `honda_accord_simulator.py` script uses the `python-can` library to generate realistic candump files that can be used for testing the car diagnostic agent.

### Features

- Generates realistic CAN messages for a Honda Accord
- Simulates different driving scenarios (idle, driving, braking, highway)
- Creates messages for common vehicle parameters:
  - Vehicle speed
  - Engine RPM
  - Throttle position
  - Brake pedal position
  - Steering wheel angle
  - Fuel level
  - Engine temperature
  - Battery voltage
  - Horn press
  - Keep-alive messages

### Usage

```bash
# Navigate to the CAN simulator directory
cd misc/can_simulator

# Run the Honda Accord simulator
../a2a_gui/.venv/bin/python honda_accord_simulator.py

# This will generate a 'honda_accord_candump.log' file
```

### Output Format

The simulator generates candump files with the following format:
```
(0.000000) vcan0 190#0C58C37200000000 R
(0.000000) vcan0 18F#0592690000000000 R
```

Where:
- `(0.000000)` is the timestamp
- `vcan0` is the CAN interface
- `190` is the CAN ID (hex)
- `0C58C37200000000` is the data bytes (hex)
- `R` indicates a received message

### Using the Generated Files

The generated candump files can be used in several ways:

1. **Replay with canplayer** (if you have can-utils installed):
   ```bash
   canplayer -I honda_accord_candump.log
   ```

2. **Parse with Python scripts** for testing applications:
   ```python
   # Example of parsing the candump file
   with open('honda_accord_candump.log', 'r') as f:
       for line in f:
           # Parse the line to extract timestamp, ID, and data
           # Process for testing
   ```

3. **Load into CAN analysis tools** like SavvyCAN for detailed inspection

## Original Simulator

The original simulator (`can_simulator.py`) is still available for cases where `python-can` is not available or when you need a simpler implementation.

[Original documentation continues...]