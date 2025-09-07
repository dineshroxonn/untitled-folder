#!/usr/bin/env python3
"""
Extended OBD Connection Test
"""

import serial
import time

def send_command(ser, command):
    """Send a command and get response."""
    ser.write(f"{command}\r".encode())
    time.sleep(1)
    response = ser.read_all()
    return response.decode('utf-8', errors='ignore').strip()

def test_obd_connection():
    """Test connecting to OBD device with multiple commands."""
    print("Extended OBD Connection Test")
    print("=" * 25)
    
    try:
        # Try to connect
        ser = serial.Serial(
            port='/dev/cu.OBDIIADAPTER',
            baudrate=38400,
            timeout=2,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
        )
        
        print("✓ Serial connection established")
        
        # Try ATZ (reset)
        print("\n1. Sending ATZ (reset)...")
        response = send_command(ser, "ATZ")
        print(f"Response: {repr(response)}")
        
        # Try ATE0 (echo off)
        print("\n2. Sending ATE0 (echo off)...")
        response = send_command(ser, "ATE0")
        print(f"Response: {repr(response)}")
        
        # Try ATSP0 (auto protocol)
        print("\n3. Sending ATSP0 (auto protocol)...")
        response = send_command(ser, "ATSP0")
        print(f"Response: {repr(response)}")
        
        # Try ATI (version info)
        print("\n4. Sending ATI (version info)...")
        response = send_command(ser, "ATI")
        print(f"Response: {repr(response)}")
        
        # Try a simple OBD command (engine RPM)
        print("\n5. Sending 010C (engine RPM)...")
        response = send_command(ser, "010C")
        print(f"Response: {repr(response)}")
        
        ser.close()
        print("\n✅ Test completed")
        
    except Exception as e:
        print(f"❌ Failed to connect: {e}")

if __name__ == "__main__":
    test_obd_connection()