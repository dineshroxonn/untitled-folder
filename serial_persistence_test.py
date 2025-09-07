#!/usr/bin/env python3
"""
Raw Serial Connection Persistence Test

This script tests raw serial connection behavior to understand why
connections might not be staying connected.
"""

import serial
import time

def test_serial_persistence():
    """Test raw serial connection persistence"""
    print("Testing Raw Serial Connection Persistence")
    print("=" * 45)
    
    try:
        # Open serial connection
        print("Opening serial connection...")
        ser = serial.Serial(
            port="/dev/cu.OBDIIADAPTER",
            baudrate=38400,
            timeout=2,
            write_timeout=2
        )
        print("Serial connection opened")
        
        # Initialize the device
        print("Initializing device...")
        ser.write(b"ATE0\r")  # Turn off echo
        time.sleep(1)
        response = ser.read_all()
        print(f"ATE0 response: {response}")
        
        ser.write(b"ATZ\r")  # Reset
        time.sleep(2)
        response = ser.read_all()
        print(f"ATZ response: {response}")
        
        # Test connection over time
        for i in range(5):
            print(f"\n--- Test Cycle {i+1} ---")
            
            # Send a simple command
            print("Sending ATI (version info)...")
            ser.write(b"ATI\r")
            time.sleep(1)
            response = ser.read_all()
            print(f"ATI response: {response}")
            
            # Check if port is still open
            print(f"Port is open: {ser.is_open}")
            
            # Wait before next test
            time.sleep(10)
        
        # Close connection
        ser.close()
        print("Serial connection closed")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

def test_connection_recovery():
    """Test automatic recovery from connection loss"""
    print("\nTesting Connection Recovery")
    print("=" * 30)
    
    ser = None
    try:
        # Open connection
        ser = serial.Serial(
            port="/dev/cu.OBDIIADAPTER",
            baudrate=38400,
            timeout=2
        )
        print("Connection established")
        
        # Test normal operation
        ser.write(b"ATI\r")
        time.sleep(1)
        response = ser.read_all()
        print(f"Initial response: {response}")
        
        # Simulate disconnection by closing
        print("Simulating disconnection...")
        ser.close()
        time.sleep(2)
        
        # Try to reopen
        print("Attempting to reconnect...")
        ser = serial.Serial(
            port="/dev/cu.OBDIIADAPTER",
            baudrate=38400,
            timeout=2
        )
        print("Reconnected successfully")
        
        # Test again
        ser.write(b"ATI\r")
        time.sleep(1)
        response = ser.read_all()
        print(f"Reconnect response: {response}")
        
    except Exception as e:
        print(f"Error during test: {e}")
    finally:
        if ser and ser.is_open:
            ser.close()
            print("Connection closed")

if __name__ == "__main__":
    test_serial_persistence()
    test_connection_recovery()