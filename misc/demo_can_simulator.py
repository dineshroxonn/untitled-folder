#!/usr/bin/env python3
"""
Demo script for the CAN simulator
"""

import sys
from pathlib import Path

# Add can_simulator to path
sys.path.append(str(Path(__file__).parent / "can_simulator"))

from can_simulator.can_simulator import CANFrameGenerator, save_can_dump


def main():
    print("CAN Simulator Demo")
    print("=" * 20)
    
    # Create generator
    generator = CANFrameGenerator()
    
    # Generate some messages
    messages = []
    
    # Add a few OBD responses
    for pid in [0x0C, 0x0D, 0x05]:  # RPM, Speed, Temperature
        msg = generator.generate_obd_pid_response(pid)
        messages.append(msg)
    
    # Add some DTCs
    dtc_msgs = generator.generate_dtcs(2)
    messages.extend(dtc_msgs)
    
    # Save to file
    save_can_dump(messages, "demo_can_dump.json")
    print(f"Generated {len(messages)} CAN messages and saved to demo_can_dump.json")
    
    # Show first message as example
    if messages:
        msg = messages[0]
        print(f"\nExample message:")
        print(f"  ID: 0x{msg.arbitration_id:X}")
        print(f"  Data: {msg.data}")
        print(f"  DLC: {msg.dlc}")


if __name__ == "__main__":
    main()