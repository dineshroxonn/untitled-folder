"""
Advanced Example: Simulating a Driving Scenario

This example demonstrates advanced usage of the CAN simulator to generate
a sequence of CAN messages that simulate a driving scenario.
"""

import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from can_simulator import CANFrameGenerator, save_can_dump


def simulate_driving_scenario():
    """Simulate a driving scenario with changing vehicle parameters."""
    print("Advanced CAN Simulator Example - Driving Scenario")
    print("=" * 50)
    
    # Create generator
    generator = CANFrameGenerator()
    
    # Start with engine off
    generator.engine_running = False
    messages = []
    
    print("Phase 1: Engine Off")
    # Generate some messages with engine off
    for _ in range(10):
        pid = list(generator.OBD_PIDS.keys())[0]  # Just use first PID
        msg = generator.generate_obd_pid_response(pid)
        messages.append(msg)
        print(f"  Message: {msg.data}")
        time.sleep(0.1)
    
    # Start engine
    print("\nPhase 2: Starting Engine")
    generator.engine_running = True
    
    # Simulate engine starting (increasing RPM)
    for i in range(5):
        generator.engine_rpm = 500 + i * 200  # Gradually increase RPM
        msg = generator.generate_obd_pid_response(0x0C)  # RPM
        messages.append(msg)
        print(f"  RPM: {msg.data}")
        time.sleep(0.1)
    
    # Simulate driving (varying speed and RPM)
    print("\nPhase 3: Driving")
    for i in range(20):
        # Vary speed and RPM
        generator.vehicle_speed = 20 + (i % 10) * 5  # 20-70 km/h cycle
        generator.engine_rpm = 1500 + (i % 5) * 500  # 1500-3500 RPM cycle
        generator.throttle_position = 20 + (i % 8) * 10  # 20-90% throttle
        
        # Generate messages for different PIDs
        speed_msg = generator.generate_obd_pid_response(0x0D)  # Speed
        rpm_msg = generator.generate_obd_pid_response(0x0C)   # RPM
        throttle_msg = generator.generate_obd_pid_response(0x11)  # Throttle
        
        messages.extend([speed_msg, rpm_msg, throttle_msg])
        print(f"  Speed: {speed_msg.data[3]} km/h, RPM: {rpm_msg.data[3]*256 + rpm_msg.data[4]}")
        time.sleep(0.05)
    
    # Add some DTCs
    print("\nPhase 4: Adding DTCs")
    dtc_msgs = generator.generate_dtcs(3)
    messages.extend(dtc_msgs)
    for msg in dtc_msgs:
        print(f"  DTC: {msg.data}")
    
    # Save to file
    save_can_dump(messages, "driving_scenario_dump.json")
    print(f"\nSaved {len(messages)} messages to driving_scenario_dump.json")


def main():
    simulate_driving_scenario()


if __name__ == "__main__":
    main()