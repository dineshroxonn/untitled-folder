#!/usr/bin/env python3
"""
Detailed OBD connection test
"""
import obd
import serial
import time

def test_serial_connection():
    """Test raw serial connection to OBD adapter"""
    print("Testing raw serial connection...")
    
    try:
        # Try to open serial connection
        ser = serial.Serial(
            port='/dev/tty.OBDIIADAPTER',
            baudrate=38400,
            timeout=2,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
        )
        
        print("✓ Serial connection opened")
        
        # Flush input
        ser.flushInput()
        time.sleep(1)
        
        # Send ATZ command (ELM327 reset)
        print("Sending ATZ (reset) command...")
        ser.write(b"ATZ\r")
        time.sleep(1)
        
        # Read response
        response = ser.read_all()
        if response:
            print(f"Response: {response}")
        else:
            print("No response received")
            
        ser.close()
        return True
        
    except Exception as e:
        print(f"✗ Serial connection failed: {e}")
        return False

def test_obd_with_params():
    """Test OBD connection with specific parameters"""
    print("\nTesting OBD connection with specific parameters...")
    
    # Common baud rates for OBD adapters
    baud_rates = [38400, 9600, 19200, 57600, 115200]
    
    for baudrate in baud_rates:
        print(f"\nTrying baud rate: {baudrate}")
        try:
            connection = obd.OBD(
                portstr='/dev/tty.OBDIIADAPTER',
                baudrate=baudrate,
                fast=False,
                timeout=5
            )
            
            if connection.is_connected():
                print(f"✓ Connected at {baudrate} baud")
                print(f"Protocol: {connection.protocol_name()}")
                connection.close()
                return True
            else:
                print(f"✗ Failed to connect at {baudrate} baud")
                
            connection.close()
            
        except Exception as e:
            print(f"✗ Error at {baudrate} baud: {e}")
    
    return False

if __name__ == "__main__":
    print("Detailed OBD Connection Test")
    print("=" * 30)
    
    # Test 1: Raw serial connection
    serial_success = test_serial_connection()
    
    # Test 2: OBD connection with parameters
    obd_success = test_obd_with_params()
    
    print("\n" + "=" * 30)
    print("SUMMARY")
    print("=" * 30)
    print(f"Serial connection: {'✓ Success' if serial_success else '✗ Failed'}")
    print(f"OBD connection: {'✓ Success' if obd_success else '✗ Failed'}")
    
    if not serial_success:
        print("\nRecommendations:")
        print("1. Check if OBD adapter is properly connected to vehicle")
        print("2. Ensure vehicle ignition is ON")
        print("3. Try a different USB cable")
        print("4. Check if the correct drivers are installed")