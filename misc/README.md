# Miscellaneous Tools

This directory contains miscellaneous tools and utilities for the car diagnostic agent project.

## Directories

- `can_simulator/` - CAN bus simulator for generating test data

## CAN Simulator

The CAN simulator provides two approaches for generating test data for the car diagnostic agent:

### 1. python-can Based Simulator (Recommended)

The `can_simulator/honda_accord_simulator.py` uses the `python-can` library to generate realistic candump files that closely match the format used by actual CAN analyzers.

#### Features

- Generates realistic CAN messages for a Honda Accord
- Simulates different driving scenarios (idle, driving, braking, highway)
- Creates messages for common vehicle parameters
- Outputs to standard candump format for compatibility with CAN analysis tools

#### Usage

```bash
# Navigate to the CAN simulator directory
cd misc/can_simulator

# Run the Honda Accord simulator (requires python-can)
../a2a_gui/.venv/bin/python honda_accord_simulator.py
```

### 2. Custom Implementation

The original simulator (`can_simulator/can_simulator.py`) is a custom implementation that generates JSON format files.

#### Features

- Generates realistic OBD-II PID responses
- Simulates Diagnostic Trouble Codes (DTCs)
- Creates random CAN traffic
- Outputs to JSON format for easy parsing
- Command-line interface for easy use
- Python API for programmatic usage

#### Usage

```bash
# Navigate to the CAN simulator directory
cd misc/can_simulator

# Run the test suite
python3 test_can_simulator.py

# Use the command-line interface
python3 cli.py --help

# Generate a CAN dump with default settings
python3 cli.py

# Generate a larger dump with engine running
python3 cli.py -c 500 --engine-running --output my_test_dump.json

# Run example scripts
python3 examples/basic_example.py
python3 examples/advanced_example.py
```

Both approaches provide valuable testing capabilities for the car diagnostic agent without requiring physical hardware.