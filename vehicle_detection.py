#!/usr/bin/env python3
"""
Vehicle Detection and OBD Connection Script

This script detects if a vehicle is connected and attempts to read data.
"""

import serial
import time

def detect_vehicle():
    """Detect if a vehicle is connected by checking for responses."""
    print("Vehicle Detection Test")
    print("=" * 22)
    
    try:
        # Connect to OBD adapter
        ser = serial.Serial(
            port='/dev/cu.OBDIIADAPTER',
            baudrate=38400,
            timeout=3  # 3 second timeout for responses
        )
        
        print("✓ Connected to OBD adapter")
        
        # Initialize
        time.sleep(1)
        ser.flushInput()
        ser.flushOutput()
        
        # Send reset
        print("Sending ATZ...")
        ser.write(b'ATZ\r')
        time.sleep(1)
        
        response = ser.read_all()
        if response:
            decoded = response.decode('utf-8', errors='ignore')
            print(f"Reset response: {repr(decoded)}")
        
        # Send echo off
        print("Sending ATE0...")
        ser.write(b'ATE0\r')
        time.sleep(1)
        
        response = ser.read_all()
        if response:
            decoded = response.decode('utf-8', errors='ignore')
            print(f"Echo off response: {repr(decoded)}")
        
        # Now check if vehicle is connected by sending a vehicle-specific command
        print("\nChecking for vehicle connection...")
        
        # Try vehicle voltage - this should work even with engine off
        print("Sending ATRV (vehicle voltage)...")
        ser.write(b'ATRV\r')
        time.sleep(2)  # Give more time for this response
        
        response = ser.read_all()
        if response:
            decoded = response.decode('utf-8', errors='ignore').strip()
            print(f"Voltage response: {repr(decoded)}")
            
            # Check if it looks like a valid voltage reading
            if any(char.isdigit() for char in decoded) and 'V' in decoded.upper():
                voltage = ''.join(filter(lambda x: x.isdigit() or x in '.-', decoded))
                if voltage:
                    try:
                        volts = float(voltage)
                        if 10 <= volts <= 15:
                            print(f"✅ Vehicle detected! Battery voltage: {volts}V")
                            vehicle_connected = True
                        else:
                            print(f"⚠️  Voltage reading ({volts}V) outside normal range (10-15V)")
                            vehicle_connected = False
                    except ValueError:
                        print("⚠️  Could not parse voltage reading")
                        vehicle_connected = False
                else:
                    print("⚠️  No valid voltage data in response")
                    vehicle_connected = False
            else:
                print("⚠️  Response doesn't look like voltage reading")
                vehicle_connected = False
        else:
            print("⚠️  No response to voltage query")
            vehicle_connected = False
        
        # If we detected a vehicle, try to read some engine data
        if vehicle_connected:
            print("\nVehicle connected, reading engine data...")
            
            # Try supported PIDs
            print("Sending 0100 (supported PIDs)...")
            ser.write(b'0100\r')
            time.sleep(2)
            
            response = ser.read_all()
            if response:
                decoded = response.decode('utf-8', errors='ignore').strip()
                print(f"PIDs response: {repr(decoded)}")
            
            # Try engine RPM (should be 0 if engine off)
            print("Sending 010C (engine RPM)...")
            ser.write(b'010C\r')
            time.sleep(2)
            
            response = ser.read_all()
            if response:
                decoded = response.decode('utf-8', errors='ignore').strip()
                print(f"RPM response: {repr(decoded)}")
        
        ser.close()
        return vehicle_connected
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_obd_adapter():
    """Check if OBD adapter is responding."""
    print("OBD Adapter Check")
    print("=" * 16)
    
    try:
        ser = serial.Serial(
            port='/dev/cu.OBDIIADAPTER',
            baudrate=38400,
            timeout=2
        )
        
        print("✓ Serial connection established")
        
        # Flush and wait
        ser.flushInput()
        time.sleep(1)
        
        # Send device info request
        print("Querying device info...")
        ser.write(b'ATI\r')
        time.sleep(1)
        
        response = ser.read_all()
        if response:
            decoded = response.decode('utf-8', errors='ignore').strip()
            print(f"Device info: {repr(decoded)}")
            
            if 'ELM' in decoded.upper():
                print("✅ ELM327 adapter detected")
                adapter_ok = True
            else:
                print("⚠️  Device responded but not recognized as ELM327")
                adapter_ok = True
        else:
            print("⚠️  No response from adapter")
            adapter_ok = False
        
        ser.close()
        return adapter_ok
        
    except Exception as e:
        print(f"❌ Adapter check failed: {e}")
        return False

if __name__ == "__main__":
    print("OBD Vehicle Detection and Connection Test")
    print("=" * 40)
    
    # First check if adapter is working
    if check_obd_adapter():
        print("\nAdapter is responding, checking for vehicle...")
        
        # Then check if vehicle is connected
        if detect_vehicle():
            print("\n🎉 Success! Vehicle is connected and responding!")
        else:
            print("\n⚠️  Adapter is working but no vehicle detected.")
            print("   Please check:")
            print("   1. OBD adapter is properly plugged into vehicle")
            print("   2. Vehicle ignition is turned on")
            print("   3. Vehicle is not in sleep mode")
    else:
        print("\n❌ OBD adapter is not responding.")
        print("   Please check:")
        print("   1. USB cable connection")
        print("   2. Adapter power/LED status")
        print("   3. Driver installation")