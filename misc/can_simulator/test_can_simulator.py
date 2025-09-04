"""
Test utility for the CAN simulator
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from can_simulator import CANFrameGenerator, save_can_dump


def test_can_simulator():
    """Test the CAN simulator functionality."""
    print("Testing CAN Simulator...")
    
    # Create generator
    generator = CANFrameGenerator()
    
    # Test OBD PID responses
    print("Testing OBD PID responses...")
    pid_responses = []
    for pid in [0x0C, 0x0D, 0x05, 0x11, 0x04]:
        response = generator.generate_obd_pid_response(pid)
        pid_responses.append(response)
        print(f"  PID 0x{pid:02X}: {response.data}")
    
    # Test DTC generation
    print("Testing DTC generation...")
    dtc_responses = generator.generate_dtcs(3)
    for response in dtc_responses:
        print(f"  DTC Response: {response.data}")
    
    # Test random traffic
    print("Testing random traffic generation...")
    random_traffic = generator.generate_random_can_traffic(10)
    print(f"  Generated {len(random_traffic)} random messages")
    
    # Combine and save
    all_messages = pid_responses + dtc_responses + random_traffic
    save_can_dump(all_messages, "test_can_dump.json")
    print("  Saved test dump to test_can_dump.json")
    
    print("Test completed successfully!")


if __name__ == "__main__":
    test_can_simulator()