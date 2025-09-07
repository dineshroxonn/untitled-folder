#!/usr/bin/env python3
"""
Mobile App Style OBD Connection

This script mimics how mobile OBD apps establish connections.
"""

import serial
import time

def mobile_app_connection():
    """Establish connection like a mobile app would."""
    print("Mobile App Style OBD Connection")
    print("=" * 32)
    
    try:
        # Connect with mobile-app style settings
        ser = serial.Serial(
            port='/dev/cu.OBDIIADAPTER',
            baudrate=38400,
            timeout=1,  # Short timeout for quick responses
            write_timeout=1,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            xonxoff=False,  # Software flow control off
            rtscts=False,   # Hardware flow control off
            dsrdtr=False    # Hardware flow control off
        )
        
        print("✓ Serial connection opened")
        
        # Mobile apps typically send this sequence:
        commands = [
            ('ATZ', 'Reset device'),
            ('ATE0', 'Turn off echo'),
            ('ATL0', 'Turn off linefeeds'),
            ('ATS0', 'Turn off spaces'),
            ('ATH0', 'Turn off headers'),
            ('ATSP0', 'Set auto protocol'),
        ]
        
        # Send each command and wait for response
        for cmd, desc in commands:
            print(f"Sending {cmd} ({desc})...")
            
            # Clear input buffer
            ser.flushInput()
            
            # Send command
            ser.write(f'{cmd}\r'.encode())
            
            # Wait for response (mobile apps are patient)
            time.sleep(1.5)
            
            # Read response
            response = ser.read_all()
            if response:
                decoded = response.decode('utf-8', errors='ignore').strip()
                print(f"  Response: {repr(decoded)}")
                
                # Check if it looks like a valid response
                if 'OK' in decoded.upper() or cmd in decoded.upper() or 'ELM' in decoded.upper():
                    print("  ✓ Valid response received")
                else:
                    print("  ⚠️  Response received but not recognized as valid")
            else:
                print("  ⚠️  No response (this might be normal for some commands)")
        
        print("\nInitialization sequence completed")
        
        # Now try to detect if a vehicle is connected
        print("\nChecking for vehicle connection...")
        
        # Mobile apps often use ATRV to check for vehicle
        print("Sending ATRV (read vehicle voltage)...")
        ser.flushInput()
        ser.write(b'ATRV\r')
        time.sleep(2)
        
        response = ser.read_all()
        if response:
            decoded = response.decode('utf-8', errors='ignore').strip()
            print(f"Voltage response: {repr(decoded)}")
            
            # Look for voltage reading
            if any(c.isdigit() for c in decoded):
                print("✓ Vehicle detected (voltage reading received)")
                vehicle_detected = True
            else:
                print("⚠️  Response received but doesn't look like voltage")
                vehicle_detected = False
        else:
            print("⚠️  No voltage response")
            vehicle_detected = False
        
        # Try to read engine RPM if vehicle detected
        if vehicle_detected:
            print("\nReading engine data...")
            ser.flushInput()
            ser.write(b'010C\r')  # Engine RPM
            time.sleep(2)
            
            response = ser.read_all()
            if response:
                decoded = response.decode('utf-8', errors='ignore').strip()
                print(f"RPM response: {repr(decoded)}")
        
        # Clean up
        ser.close()
        print("\n✓ Connection test completed")
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def progressive_baudrate_test():
    """Test different baud rates like mobile apps do."""
    print("Progressive Baud Rate Test")
    print("=" * 26)
    
    baud_rates = [38400, 9600, 19200, 57600, 115200]
    
    for baudrate in baud_rates:
        print(f"\nTesting baud rate: {baudrate}")
        
        try:
            ser = serial.Serial(
                port='/dev/cu.OBDIIADAPTER',
                baudrate=baudrate,
                timeout=1
            )
            
            print(f"✓ Connected at {baudrate} baud")
            
            # Send reset command
            print("Sending ATZ...")
            ser.flushInput()
            ser.write(b'ATZ\r')
            time.sleep(1.5)
            
            response = ser.read_all()
            if response:
                decoded = response.decode('utf-8', errors='ignore').strip()
                print(f"Response: {repr(decoded)}")
                
                if 'ELM' in decoded.upper() or 'OK' in decoded.upper():
                    print(f"✅ Success at {baudrate} baud!")
                    ser.close()
                    return baudrate
            
            ser.close()
            
        except Exception as e:
            print(f"Failed at {baudrate} baud: {e}")
    
    print("❌ No baud rate worked")
    return None

if __name__ == "__main__":
    print("OBD Connection Test - Mobile App Approach")
    print("=" * 42)
    
    # First try progressive baud rate test
    print("Step 1: Finding correct baud rate...")
    correct_baud = progressive_baudrate_test()
    
    if correct_baud:
        print(f"\nStep 2: Testing full mobile app connection at {correct_baud} baud...")
        mobile_app_connection()
    else:
        print("\nStep 2: Trying default connection anyway...")
        mobile_app_connection()