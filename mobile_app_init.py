#!/usr/bin/env python3
"""
Mobile App Initialization Sequence

This script replicates the exact initialization sequence used by mobile OBD apps.
"""

import serial
import time

def mobile_app_init_sequence():
    """Replicate mobile app initialization sequence."""
    print("Mobile App Initialization Sequence")
    print("=" * 34)
    
    try:
        # Connect with mobile app typical settings
        ser = serial.Serial(
            port='/dev/cu.OBDIIADAPTER',
            baudrate=38400,
            timeout=1,
            write_timeout=1,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            xonxoff=False,
            rtscts=False,
            dsrdtr=False
        )
        
        print("✅ Serial connection established")
        
        # Mobile apps typically do this exact sequence:
        print("\nExecuting mobile app initialization sequence...")
        
        # Step 1: Wait after connection (critical!)
        print("Step 1: Waiting for adapter to settle...")
        time.sleep(2)
        
        # Step 2: Send multiple resets (mobile apps do this)
        print("Step 2: Sending multiple reset commands...")
        for i in range(3):
            ser.flushInput()
            ser.write(b'ATZ\r')
            time.sleep(0.5)
        
        # Step 3: Wait for responses
        print("Step 3: Reading reset responses...")
        time.sleep(2)
        response = ser.read_all()
        if response:
            decoded = response.decode('utf-8', errors='ignore').strip()
            print(f"Reset responses: {repr(decoded)}")
        
        # Step 4: Send configuration commands (exact sequence from mobile apps)
        config_commands = [
            'ATE0',   # Echo off
            'ATL0',   # Linefeeds off
            'ATS0',   # Spaces off
            'ATH0',   # Headers off
            'ATAT0',  # Adaptive timing off
            'ATSP0',  # Auto protocol
        ]
        
        print("Step 4: Sending configuration commands...")
        for cmd in config_commands:
            print(f"Sending {cmd}...")
            ser.flushInput()
            ser.write(f'{cmd}\r'.encode())
            time.sleep(0.5)
            
            # Read response
            response = ser.read_all()
            if response:
                decoded = response.decode('utf-8', errors='ignore').strip()
                print(f"  Response: {repr(decoded)}")
            time.sleep(0.1)
        
        # Step 5: Test with vehicle-specific commands
        print("\nStep 5: Testing with vehicle commands...")
        
        # Send a simple command that should always work if vehicle is connected
        test_commands = [
            ('ATRV', 'Vehicle voltage'),
            ('0100', 'Supported PIDs'),
            ('010C', 'Engine RPM'),
        ]
        
        for cmd, desc in test_commands:
            print(f"Testing {desc} ({cmd})...")
            ser.flushInput()
            ser.write(f'{cmd}\r'.encode())
            time.sleep(2)  # Give time for response
            
            response = ser.read_all()
            if response:
                decoded = response.decode('utf-8', errors='ignore').strip()
                print(f"  Response: {repr(decoded)}")
                
                # Check if it's a valid response
                if 'NO DATA' in decoded.upper():
                    print(f"  ⚠️  No data (vehicle may be off)")
                elif '>' in decoded:  # Prompt character
                    print(f"  ✅ Valid response received")
                else:
                    print(f"  ⚠️  Response received but format unclear")
            else:
                print(f"  ⚠️  No response")
            time.sleep(0.5)
        
        # Clean up
        ser.close()
        print("\n✅ Mobile app initialization sequence completed")
        return True
        
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return False

def brute_force_test():
    """Try various approaches to get a response."""
    print("Brute Force Response Test")
    print("=" * 24)
    
    try:
        ser = serial.Serial(
            port='/dev/cu.OBDIIADAPTER',
            baudrate=38400,
            timeout=0.5
        )
        
        print("✅ Serial connection established")
        
        # Try different approaches to get any response
        approaches = [
            (b'\r', 'Carriage return'),
            (b'ATZ\r', 'Reset command'),
            (b'ATI\r', 'Info command'),
            (b'?', 'Question mark'),
            (b' ', 'Space'),
        ]
        
        for cmd, desc in approaches:
            print(f"Trying {desc}...")
            ser.flushInput()
            ser.write(cmd)
            time.sleep(1)
            
            response = ser.read_all()
            if response:
                decoded = response.decode('utf-8', errors='ignore').strip()
                print(f"  Response: {repr(decoded)}")
                if decoded:
                    print("  ✅ Got a response!")
                    ser.close()
                    return True
            else:
                print("  No response")
        
        ser.close()
        print("❌ No approach yielded a response")
        return False
        
    except Exception as e:
        print(f"❌ Brute force test failed: {e}")
        return False

if __name__ == "__main__":
    print("Mobile OBD App Initialization Test")
    print("=" * 34)
    
    # First try brute force to see if we can get any response
    print("Step 1: Brute force response test...")
    if brute_force_test():
        print("\nStep 2: Full mobile app initialization...")
        mobile_app_init_sequence()
    else:
        print("\nNo response from adapter at all.")
        print("Possible issues:")
        print("1. Wrong port selected")
        print("2. Adapter not powered")
        print("3. Driver issues")
        print("4. Adapter is in sleep mode")
        print("5. Bluetooth pairing issues")