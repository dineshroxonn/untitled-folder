#!/usr/bin/env python3
"""
Simple OBD Connection Test
"""

import serial
import time

def test_obd_connection():
    """Test connecting to OBD device."""
    print("Testing OBD Connection")
    print("=" * 20)
    
    try:
        # Try to connect with a short timeout
        ser = serial.Serial(
            port='/dev/cu.OBDIIADAPTER',
            baudrate=38400,
            timeout=1,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
        )
        
        print("✓ Serial connection established")
        
        # Send a simple command
        print("Sending ATZ (reset)...")
        ser.write(b'ATZ\r')
        time.sleep(1)
        
        response = ser.read_all()
        if response:
            decoded = response.decode('utf-8', errors='ignore').strip()
            print(f"Response: {repr(decoded)}")
            
            if 'ELM' in decoded.upper():
                print("✅ ELM327 device detected!")
            else:
                print("⚠️  Device responded but not recognized")
        else:
            print("⚠️  No response from device")
        
        ser.close()
        
    except Exception as e:
        print(f"❌ Failed to connect: {e}")

if __name__ == "__main__":
    test_obd_connection()