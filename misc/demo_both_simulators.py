#!/usr/bin/env python3
"""
Demo script showing both CAN simulation approaches
"""

import sys
import os
from pathlib import Path

# Add paths for both simulators
misc_path = Path(__file__).parent
can_sim_path = misc_path / "can_simulator"

# Add to Python path
sys.path.append(str(can_sim_path))


def demo_python_can_approach():
    """Demonstrate the python-can based approach."""
    print("=== python-can Based Approach ===")
    print("This approach generates realistic candump files.")
    print("Running the Honda Accord simulator...")
    
    # Run the simulator
    try:
        # Import and run the simulator
        sys.path.append(str(can_sim_path))
        import subprocess
        
        # Run the simulator using the virtual environment
        venv_python = misc_path.parent / "a2a_gui" / ".venv" / "bin" / "python"
        result = subprocess.run([
            str(venv_python), 
            str(can_sim_path / "honda_accord_simulator.py")
        ], cwd=str(can_sim_path), capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Honda Accord simulator ran successfully")
            print("  Generated: honda_accord_candump.log")
            
            # Show first few lines of the generated file
            candump_file = can_sim_path / "honda_accord_candump.log"
            if candump_file.exists():
                print("\nFirst few lines of generated candump file:")
                with open(candump_file, 'r') as f:
                    for i, line in enumerate(f):
                        if i >= 5:
                            break
                        print(f"  {line.strip()}")
        else:
            print("✗ Error running simulator:")
            print(result.stderr)
            
    except Exception as e:
        print(f"✗ Error: {e}")


def demo_custom_approach():
    """Demonstrate the custom JSON-based approach."""
    print("\n=== Custom JSON-Based Approach ===")
    print("This approach generates JSON format files.")
    print("Running the custom simulator...")
    
    try:
        # Import the custom simulator
        from can_simulator.can_simulator import CANFrameGenerator, save_can_dump
        
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
        save_can_dump(messages, "demo_custom_can_dump.json")
        print("✓ Custom simulator ran successfully")
        print("  Generated: demo_custom_can_dump.json")
        
        # Show first message as example
        if messages:
            msg = messages[0]
            print(f"\nExample message:")
            print(f"  ID: 0x{msg.arbitration_id:X}")
            print(f"  Data: {msg.data}")
            print(f"  DLC: {msg.dlc}")
            
    except Exception as e:
        print(f"✗ Error: {e}")


def main():
    print("CAN Simulator Demo")
    print("=" * 20)
    
    demo_python_can_approach()
    demo_custom_approach()
    
    print("\n=== Summary ===")
    print("1. python-can approach generates standard candump files")
    print("2. Custom approach generates JSON files")
    print("Both can be used for testing the car diagnostic agent")


if __name__ == "__main__":
    main()