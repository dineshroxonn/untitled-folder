"""
OBD-II CAN Simulator CLI Tool

This script provides a command-line interface for generating CAN dump files
for testing the car diagnostic agent.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from can_simulator import CANFrameGenerator, save_can_dump


def main():
    parser = argparse.ArgumentParser(description="OBD-II CAN Simulator")
    parser.add_argument(
        "--output", "-o",
        default=f"can_dump_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        help="Output filename for the CAN dump (default: can_dump_TIMESTAMP.json)"
    )
    parser.add_argument(
        "--count", "-c",
        type=int,
        default=100,
        help="Number of CAN messages to generate (default: 100)"
    )
    parser.add_argument(
        "--dtc-count",
        type=int,
        default=5,
        help="Number of DTCs to include (default: 5)"
    )
    parser.add_argument(
        "--engine-running",
        action="store_true",
        help="Simulate engine running (affects RPM, speed, temperature values)"
    )
    
    args = parser.parse_args()
    
    print("OBD-II CAN Simulator")
    print("=" * 30)
    print(f"Generating {args.count} CAN messages")
    print(f"Including {args.dtc_count} DTCs")
    print(f"Engine running: {args.engine_running}")
    print(f"Output file: {args.output}")
    
    # Create generator
    generator = CANFrameGenerator()
    generator.engine_running = args.engine_running
    
    # Generate messages
    messages = []
    
    # Add some OBD PID responses
    print("\nGenerating OBD PID responses...")
    pid_count = min(20, args.count // 3)  # At least 20, or 1/3 of total count
    for i in range(pid_count):
        pid = list(generator.OBD_PIDS.keys())[i % len(generator.OBD_PIDS)]
        msg = generator.generate_obd_pid_response(pid)
        messages.append(msg)
    
    # Add DTC responses
    print(f"Generating {args.dtc_count} DTCs...")
    dtc_messages = generator.generate_dtcs(args.dtc_count)
    messages.extend(dtc_messages)
    
    # Fill remaining with random traffic
    remaining_count = args.count - len(messages)
    if remaining_count > 0:
        print(f"Generating {remaining_count} random CAN messages...")
        random_messages = generator.generate_random_can_traffic(remaining_count)
        messages.extend(random_messages)
    
    # Save to file
    save_can_dump(messages, args.output)
    print(f"\nSaved {len(messages)} messages to {args.output}")
    
    # Print summary
    print("\nSummary:")
    print(f"  Total messages: {len(messages)}")
    print(f"  OBD PID responses: {pid_count}")
    print(f"  DTC responses: {len(dtc_messages)}")
    print(f"  Random traffic: {remaining_count}")


if __name__ == "__main__":
    main()