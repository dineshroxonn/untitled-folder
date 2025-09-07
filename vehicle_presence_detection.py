#!/usr/bin/env python3
"""
Vehicle Presence Detection with Proper Timing

This script focuses on detecting vehicle presence with proper timing.
"""

import serial
import time

def detect_vehicle_presence():
    """Detect if vehicle is present with proper timing."""
    print("Vehicle Presence Detection")
    print("=" * 25)
    
    try:
        # Connect with specific timing parameters
        ser = serial.Serial(
            port='/dev/cu.OBDIIADAPTER',
            baudrate=38400,
            timeout=1,  # Short timeout for quick responses
            write_timeout=1,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            xonxoff=False,
            rtscts=False,
            dsrdtr=False
        )
        
        print("✅ Serial connection established")
        
        # Important: Wait after opening connection
        print("Waiting for adapter to initialize...")
        time.sleep(2)
        
        # Clear any buffered data
        ser.flushInput()
        ser.flushOutput()
        time.sleep(0.5)
        
        # Send reset command and immediately read
        print("Sending ATZ (reset)...")
        ser.write(b'ATZ\r')
        
        # Wait a moment for response
        time.sleep(1)
        
        # Read response
        response = ser.read_all()
        if response:
            decoded = response.decode('utf-8', errors='ignore').strip()
            print(f"Reset response: {repr(decoded)}")
            
            # Check if we got a response from ELM327
            if 'ELM' in decoded.upper() or '>' in decoded:
                print("✅ ELM327 adapter detected")
                adapter_responding = True
            else:
                print("⚠️  Adapter responded but not recognized")
                adapter_responding = True
        else:
            print("⚠️  No response to reset command")
            adapter_responding = False
        
        # If adapter is responding, check for vehicle
        if adapter_responding:
            print("\nChecking for vehicle presence...")
            
            # Try vehicle voltage with longer timeout
            print("Sending ATRV (vehicle voltage)...")
            ser.flushInput()
            ser.write(b'ATRV\r')
            
            # Give more time for this response
            time.sleep(3)
            
            response = ser.read_all()
            if response:
                decoded = response.decode('utf-8', errors='ignore').strip()
                print(f"Voltage response: {repr(decoded)}")
                
                # Look for voltage reading
                if any(c.isdigit() for c in decoded) and 'V' in decoded.upper():
                    print("✅ Vehicle detected (voltage reading received)")
                    vehicle_present = True
                else:
                    print("⚠️  Response received but doesn't look like voltage")
                    vehicle_present = False
            else:
                print("⚠️  No voltage response (vehicle may not be connected)")
                vehicle_present = False
        
        # Clean up
        ser.close()
        print("\n✅ Detection completed")
        return adapter_responding, vehicle_present
        
    except Exception as e:
        print(f"❌ Detection failed: {e}")
        return False, False

def quick_adapter_test():
    """Quick test to verify adapter is working."""
    print("Quick Adapter Test")
    print("=" * 18)
    
    try:
        # Quick connection
        ser = serial.Serial(
            port='/dev/cu.OBDIIADAPTER',
            baudrate=38400,
            timeout=0.5  # Very short timeout
        )
        
        print("✅ Serial port accessible")
        
        # Send a single character to see if anything comes back
        ser.write(b'\r')
        time.sleep(0.5)
        
        response = ser.read_all()
        if response:
            decoded = response.decode('utf-8', errors='ignore').strip()
            print(f"Prompt response: {repr(decoded)}")
            if '>' in decoded:
                print("✅ Adapter is ready and waiting for commands")
                result = True
            else:
                print("⚠️  Got response but not the expected prompt")
                result = True
        else:
            # Try reset command
            ser.write(b'ATZ\r')
            time.sleep(1)
            
            response = ser.read_all()
            if response:
                decoded = response.decode('utf-8', errors='ignore').strip()
                print(f"Reset response: {repr(decoded)}")
                result = True
            else:
                print("⚠️  No response to commands")
                result = False
        
        ser.close()
        return result
        
    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        return False

if __name__ == "__main__":
    print("OBD Vehicle Presence Detection")
    print("=" * 30)
    
    # First do a quick test
    print("Step 1: Quick adapter test...")
    if quick_adapter_test():
        print("\nStep 2: Detailed vehicle presence detection...")
        adapter_ok, vehicle_ok = detect_vehicle_presence()
        
        print(f"\nResults:")
        print(f"  Adapter responding: {'Yes' if adapter_ok else 'No'}")
        print(f"  Vehicle present: {'Yes' if vehicle_ok else 'No'}")
        
        if adapter_ok and vehicle_ok:
            print("\n🎉 Everything is working correctly!")
        elif adapter_ok and not vehicle_ok:
            print("\n⚠️  Adapter works but no vehicle detected.")
            print("   Check that vehicle ignition is ON.")
        else:
            print("\n❌ Adapter is not responding properly.")
    else:
        print("\n❌ Quick test failed. Check connections.")