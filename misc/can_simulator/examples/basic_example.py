"""
Basic Example: Using the CAN Simulator

This example demonstrates basic usage of the CAN simulator to generate
a simple CAN dump file for testing.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from can_simulator import CANFrameGenerator, save_can_dump


def main():
    print("Basic CAN Simulator Example")
    print("=" * 30)
    
    # Create generator
    generator = CANFrameGenerator()
    
    # Generate some OBD responses
    messages = []
    
    # Add engine RPM
    rpm_msg = generator.generate_obd_pid_response(0x0C)
    messages.append(rpm_msg)
    print(f"Engine RPM: {rpm_msg.data}")
    
    # Add vehicle speed
    speed_msg = generator.generate_obd_pid_response(0x0D)
    messages.append(speed_msg)
    print(f"Vehicle Speed: {speed_msg.data}")
    
    # Add coolant temperature
    temp_msg = generator.generate_obd_pid_response(0x05)
    messages.append(temp_msg)
    print(f"Coolant Temperature: {temp_msg.data}")
    
    # Add some DTCs
    dtc_msgs = generator.generate_dtcs(2)
    messages.extend(dtc_msgs)
    for msg in dtc_msgs:
        print(f"DTC Response: {msg.data}")
    
    # Save to file
    save_can_dump(messages, "basic_example_dump.json")
    print(f"\nSaved {len(messages)} messages to basic_example_dump.json")


if __name__ == "__main__":
    main()