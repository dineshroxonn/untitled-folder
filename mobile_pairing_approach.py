#!/usr/bin/env python3
"""
Bluetooth Pairing Approach for OBD

This script uses the same approach as mobile apps - just pairing, no complex connection.
"""

import subprocess
import time
import serial

def check_bluetooth_pairing():
    """Check if OBD device is properly paired via Bluetooth."""
    print("Bluetooth Pairing Check")
    print("=" * 22)
    
    try:
        # Check Bluetooth device status
        result = subprocess.run(['system_profiler', 'SPBluetoothDataType'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            output = result.stdout
            
            # Look for OBD device
            if 'OBD' in output or 'ELM' in output or 'OBDII' in output:
                print("✅ OBD device found in Bluetooth devices")
                
                # Check if it's connected
                lines = output.split('\n')
                for i, line in enumerate(lines):
                    if 'OBD' in line or 'ELM' in line or 'OBDII' in line:
                        # Look for connection status in nearby lines
                        for j in range(i, min(i+5, len(lines))):
                            if 'Connected:' in lines[j]:
                                if 'yes' in lines[j].lower():
                                    print("✅ OBD device is Bluetooth connected")
                                    return True
                                else:
                                    print("⚠️  OBD device is paired but not connected")
                                    return False
                print("ℹ️  OBD device is paired (connection status unknown)")
                return True
            else:
                print("⚠️  No OBD device found in Bluetooth devices")
                return False
        else:
            print("⚠️  Could not check Bluetooth status")
            return False
            
    except Exception as e:
        print(f"❌ Error checking Bluetooth: {e}")
        return False

def simple_pairing_approach():
    """Use simple pairing approach like mobile apps."""
    print("Simple Pairing Approach")
    print("=" * 21)
    
    # First check if device is paired
    if not check_bluetooth_pairing():
        print("⚠️  Device may not be properly paired")
    
    # Try to access the serial port that should be available after pairing
    print("Attempting to access OBD serial port...")
    
    try:
        # Open connection with minimal configuration (like mobile apps)
        ser = serial.Serial(
            port='/dev/cu.OBDIIADAPTER',
            baudrate=38400,
            timeout=1  # Very short timeout like mobile apps
        )
        
        print("✅ Serial port accessible")
        
        # Mobile apps don't send complex initialization, they just send:
        ser.write(b'\r')  # Simple carriage return like many mobile apps
        time.sleep(0.1)
        
        # Read any immediate response
        response = ser.read_all()
        if response:
            decoded = response.decode('utf-8', errors='ignore').strip()
            print(f"Immediate response: {repr(decoded)}")
        
        # Send a simple query that works when vehicle is on
        print("Sending simple vehicle query...")
        ser.flushInput()
        ser.write(b'ATRV\r')  # Vehicle voltage - simple and reliable
        time.sleep(1)
        
        response = ser.read_all()
        if response:
            decoded = response.decode('utf-8', errors='ignore').strip()
            print(f"Vehicle voltage: {repr(decoded)}")
            
            # Check if it looks like a voltage reading
            if any(c.isdigit() for c in decoded) and 'v' in decoded.lower():
                print("✅ Vehicle detected via voltage reading!")
                ser.close()
                return True
            elif 'no data' in decoded.lower():
                print("⚠️  Adapter responding but no vehicle data")
                ser.close()
                return True
            else:
                print("⚠️  Got response but not a clear voltage reading")
        else:
            print("⚠️  No response to vehicle query")
        
        ser.close()
        return False
        
    except Exception as e:
        print(f"❌ Error in simple pairing approach: {e}")
        return False

def mobile_like_connection():
    """Try to connect exactly like mobile apps do."""
    print("Mobile-Like Connection")
    print("=" * 20)
    
    try:
        # Mobile apps typically use these exact settings
        ser = serial.Serial(
            port='/dev/cu.OBDIIADAPTER',
            baudrate=38400,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1,
            xonxoff=False,
            rtscts=False,
            dsrdtr=False,
            write_timeout=1
        )
        
        print("✅ Serial connection established (mobile-style)")
        
        # Critical: Wait after connection like mobile apps do
        print("Waiting for adapter (like mobile apps)...")
        time.sleep(2)
        
        # Mobile apps send this exact sequence:
        commands = [
            b'ATZ\r',    # Reset
            b'\r',       # Simple prompt request
            b'ATI\r',    # Info
            b'ATRV\r',   # Vehicle voltage
        ]
        
        for cmd in commands:
            ser.flushInput()
            ser.write(cmd)
            time.sleep(0.5)  # Brief pause like mobile apps
            
            response = ser.read_all()
            if response:
                decoded = response.decode('utf-8', errors='ignore').strip()
                cmd_str = cmd.decode('utf-8', errors='ignore').strip()
                print(f"Command '{cmd_str}' response: {repr(decoded)}")
        
        ser.close()
        print("✅ Mobile-like connection sequence completed")
        return True
        
    except Exception as e:
        print(f"❌ Mobile-like connection failed: {e}")
        return False

if __name__ == "__main__":
    print("OBD Connection - Mobile Pairing Approach")
    print("=" * 40)
    
    print("The key insight: Mobile apps work with simple pairing, not complex connection.")
    print()
    
    # Try simple pairing approach
    print("Step 1: Simple pairing approach...")
    simple_pairing_approach()
    
    print()
    
    # Try mobile-like connection
    print("Step 2: Mobile-like connection...")
    mobile_like_connection()
    
    print("\n" + "=" * 50)
    print("MOBILE PAIRING APPROACH TEST COMPLETE")
    print("=" * 50)
    print("Key takeaway: Mobile apps succeed because they use simple, direct approaches")
    print("rather than complex initialization sequences.")