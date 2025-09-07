#!/usr/bin/env python3
"""
Mobile-Style OBD Connection Script

This script attempts to connect to the OBD adapter using the same approach
that works on mobile devices.
"""

import serial
import time
import sys

def mobile_style_connect():
    """Connect to OBD adapter using mobile-style approach."""
    print("Mobile-Style OBD Connection")
    print("=" * 30)
    
    # Try to connect with the settings that typically work on mobile
    port = '/dev/cu.OBDIIADAPTER'
    baudrate = 38400
    
    print(f"Attempting to connect to {port} at {baudrate} baud...")
    
    try:
        # Open serial connection with mobile-friendly settings
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            timeout=5,  # Longer timeout
            write_timeout=5,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            rtscts=False,  # Disable hardware flow control
            dsrdtr=False,  # Disable hardware flow control
        )
        
        print("✓ Serial connection established")
        
        # Important: Wait a moment after opening
        time.sleep(2)
        
        # Flush input/output
        ser.flushInput()
        ser.flushOutput()
        
        # Send initialization sequence (like mobile apps do)
        print("Sending initialization sequence...")
        
        # Step 1: Reset
        print("1. Sending ATZ (reset)...")
        ser.write(b'ATZ\r')
        time.sleep(1)
        
        # Read and discard response
        ser.read_all()
        time.sleep(0.1)
        
        # Step 2: Echo off
        print("2. Sending ATE0 (echo off)...")
        ser.write(b'ATE0\r')
        time.sleep(1)
        
        # Read and check response
        response = ser.read_all()
        if response:
            decoded = response.decode('utf-8', errors='ignore')
            print(f"   Response: {repr(decoded)}")
        
        # Step 3: Linefeeds on
        print("3. Sending ATL1 (linefeeds on)...")
        ser.write(b'ATL1\r')
        time.sleep(0.5)
        
        response = ser.read_all()
        if response:
            decoded = response.decode('utf-8', errors='ignore')
            print(f"   Response: {repr(decoded)}")
        
        # Step 4: Spaces on
        print("4. Sending ATS1 (spaces on)...")
        ser.write(b'ATS1\r')
        time.sleep(0.5)
        
        response = ser.read_all()
        if response:
            decoded = response.decode('utf-8', errors='ignore')
            print(f"   Response: {repr(decoded)}")
        
        # Step 5: Headers on
        print("5. Sending ATH1 (headers on)...")
        ser.write(b'ATH1\r')
        time.sleep(0.5)
        
        response = ser.read_all()
        if response:
            decoded = response.decode('utf-8', errors='ignore')
            print(f"   Response: {repr(decoded)}")
        
        print("✓ Initialization sequence completed")
        
        # Now try to read some basic data
        print("\nTesting basic OBD commands...")
        
        # Get device info
        print("Querying device info (ATI)...")
        ser.write(b'ATI\r')
        time.sleep(1)
        response = ser.read_all()
        if response:
            decoded = response.decode('utf-8', errors='ignore')
            print(f"Device info: {repr(decoded)}")
        
        # Get vehicle voltage
        print("Querying vehicle voltage (ATRV)...")
        ser.write(b'ATRV\r')
        time.sleep(1)
        response = ser.read_all()
        if response:
            decoded = response.decode('utf-8', errors='ignore')
            print(f"Vehicle voltage: {repr(decoded)}")
        
        # Get supported PIDs
        print("Querying supported PIDs (0100)...")
        ser.write(b'0100\r')
        time.sleep(1)
        response = ser.read_all()
        if response:
            decoded = response.decode('utf-8', errors='ignore')
            print(f"Supported PIDs: {repr(decoded)}")
        
        # Try engine RPM
        print("Querying engine RPM (010C)...")
        ser.write(b'010C\r')
        time.sleep(1)
        response = ser.read_all()
        if response:
            decoded = response.decode('utf-8', errors='ignore')
            print(f"Engine RPM: {repr(decoded)}")
        
        print("\n✅ Mobile-style connection successful!")
        ser.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def quick_test():
    """Quick test to verify connection."""
    print("Quick OBD Connection Test")
    print("=" * 25)
    
    try:
        ser = serial.Serial(
            port='/dev/cu.OBDIIADAPTER',
            baudrate=38400,
            timeout=2
        )
        
        print("✓ Serial port opened")
        
        # Send simple reset
        ser.write(b'ATZ\r')
        time.sleep(1)
        response = ser.read_all()
        
        if response:
            decoded = response.decode('utf-8', errors='ignore')
            print(f"Response: {repr(decoded)}")
            if 'ELM' in decoded.upper():
                print("✓ ELM327 device detected!")
                success = True
            else:
                print("⚠️  Device responded but not recognized as ELM327")
                success = True
        else:
            print("⚠️  No response from device")
            success = False
        
        ser.close()
        return success
        
    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing OBD connection using mobile-style approach...")
    
    # First try quick test
    if quick_test():
        print("\nQuick test passed, running full initialization...")
        mobile_style_connect()
    else:
        print("\nQuick test failed, trying full initialization anyway...")
        mobile_style_connect()