#!/usr/bin/env python3
"""
OBD Connection Status Checker

This script checks the connection status of potential OBD devices
and verifies if they are properly connected and responding.
"""

import serial
import serial.tools.list_ports
import time
import sys

def test_obd_connection(port, baudrate=38400, timeout=5):
    """Test OBD connection to a specific port"""
    print(f"Testing OBD connection to {port}...")
    
    try:
        # Try to open serial connection
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            timeout=timeout,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
        )
        
        print(f"✓ Successfully opened serial port {port}")
        
        # Flush input
        ser.flushInput()
        
        # Send ATZ command (ELM327 reset)
        print("Sending ATZ (reset) command...")
        ser.write(b"ATZ\r")
        time.sleep(1)
        
        # Read response
        response = ser.read_all()
        if response:
            decoded_response = response.decode('utf-8', errors='ignore')
            print(f"Response: {decoded_response}")
            ser.close()
            return True, decoded_response
        else:
            print("No response received")
            ser.close()
            return False, "No response"
            
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False, str(e)

def check_obd_device_status():
    """Check status of all potential OBD devices"""
    print("Checking OBD Device Status")
    print("=" * 40)
    
    # List all available ports
    all_ports = list(serial.tools.list_ports.comports())
    
    # Look for potential OBD ports
    obd_ports = []
    for port in all_ports:
        description = port.description.upper() if port.description else ""
        manufacturer = port.manufacturer.upper() if port.manufacturer else ""
        device = port.device.upper()
        
        obd_patterns = [
            "OBD", "ELM327", "BLUETOOTH", "USB SERIAL", 
            "FTDI", "CH340", "CP2102", "PL2303", "UART"
        ]
        
        for pattern in obd_patterns:
            if (pattern in description or 
                pattern in manufacturer or 
                pattern in device or
                "OBD" in device):
                obd_ports.append(port.device)
                break
    
    # Also add the specific OBDIIADAPTER if found
    for port in all_ports:
        if "OBDIIADAPTER" in port.device:
            if port.device not in obd_ports:
                obd_ports.append(port.device)
    
    if not obd_ports:
        # If no obvious OBD ports found, test all ports that might be relevant
        for port in all_ports:
            if "BLUETOOTH" in port.device.upper() or "USB" in port.device.upper() or "SERIAL" in port.device.upper():
                obd_ports.append(port.device)
    
    if not obd_ports:
        print("No potential OBD ports found!")
        return
    
    print(f"Found {len(obd_ports)} potential OBD port(s) to test:")
    for port in obd_ports:
        print(f"  - {port}")
    
    print("\nTesting each port...")
    results = {}
    
    # Common baud rates for OBD devices
    baud_rates = [38400, 9600, 19200, 57600, 115200]
    
    for port in obd_ports:
        print(f"\n{'='*50}")
        print(f"TESTING PORT: {port}")
        print('='*50)
        
        port_results = {}
        connection_success = False
        
        # Test different baud rates
        for baudrate in baud_rates:
            print(f"\n--- Testing at {baudrate} baud ---")
            success, response = test_obd_connection(port, baudrate)
            port_results[baudrate] = {"success": success, "response": response}
            
            if success:
                connection_success = True
                print(f"✓ Connection successful at {baudrate} baud")
                # If we have a successful connection, we don't need to test other baud rates
                break
            else:
                print(f"✗ Connection failed at {baudrate} baud")
        
        results[port] = {
            "connection_success": connection_success,
            "baud_rate_results": port_results
        }
        
        if connection_success:
            print(f"\n🎉 SUCCESS: {port} is connected and responding!")
        else:
            print(f"\n⚠️  FAILED: {port} is not responding or not connected properly.")
    
    # Summary
    print(f"\n{'='*50}")
    print("CONNECTION STATUS SUMMARY")
    print('='*50)
    
    connected_devices = []
    disconnected_devices = []
    
    for port, result in results.items():
        if result["connection_success"]:
            connected_devices.append(port)
        else:
            disconnected_devices.append(port)
    
    if connected_devices:
        print(f"\n✅ Connected OBD Devices ({len(connected_devices)}):")
        for device in connected_devices:
            print(f"  - {device}")
    else:
        print("\n❌ No connected OBD devices found")
    
    if disconnected_devices:
        print(f"\n🔌 Disconnected/Unavailable OBD Devices ({len(disconnected_devices)}):")
        for device in disconnected_devices:
            print(f"  - {device}")
        print("\nTroubleshooting tips for disconnected devices:")
        print("  1. Check if the OBD adapter is properly plugged into the vehicle")
        print("  2. Ensure the vehicle's ignition is turned on")
        print("  3. Verify Bluetooth pairing if using a wireless adapter")
        print("  4. Try different baud rates")
        print("  5. Check if the correct drivers are installed")

if __name__ == "__main__":
    check_obd_device_status()