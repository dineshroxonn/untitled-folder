#!/usr/bin/env python3
"""
OBD-II Bluetooth Connection Test Script

This script tests connectivity to an OBD-II adapter via Bluetooth
on macOS. It tries various common configurations and ports.
"""

import obd
import time
import serial
import serial.tools.list_ports
import sys

def list_bluetooth_ports():
    """List all available Bluetooth serial ports"""
    print("=== Searching for Bluetooth/OBD ports ===")
    ports = []
    
    # List all available ports
    all_ports = list(serial.tools.list_ports.comports())
    
    for port in all_ports:
        print(f"Found port: {port.device}")
        print(f"  Description: {port.description}")
        print(f"  Manufacturer: {port.manufacturer}")
        print(f"  HWID: {port.hwid}")
        print()
        
        # Look for common OBD adapter patterns
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
                pattern in device):
                ports.append(port.device)
                print(f"  *** MATCHED OBD PATTERN: {pattern} ***")
                break
    
    if not ports:
        print("No obvious OBD ports found. Listing all serial ports:")
        for port in all_ports:
            ports.append(port.device)
    
    return ports

def test_serial_connection(port, baudrate=38400, timeout=5):
    """Test raw serial connection to port"""
    print(f"\n=== Testing raw serial connection to {port} at {baudrate} baud ===")
    
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
            print(f"Response: {response.decode('utf-8', errors='ignore')}")
        else:
            print("No response received")
        
        # Send ATE0 command (echo off)
        print("Sending ATE0 (echo off) command...")
        ser.write(b"ATE0\r")
        time.sleep(1)
        
        # Read response
        response = ser.read_all()
        if response:
            print(f"Response: {response.decode('utf-8', errors='ignore')}")
        
        ser.close()
        print("✓ Serial test completed")
        return True
        
    except Exception as e:
        print(f"✗ Serial connection failed: {e}")
        return False

def test_obd_connection(port, baudrate=38400, protocol="AUTO", timeout=10):
    """Test OBD connection using obd library"""
    print(f"\n=== Testing OBD connection to {port} ===")
    print(f"Baudrate: {baudrate}, Protocol: {protocol}, Timeout: {timeout}")
    
    try:
        # Create OBD connection
        connection = obd.OBD(
            portstr=port,
            baudrate=baudrate,
            protocol=None if protocol == "AUTO" else protocol,
            fast=False,
            timeout=timeout
        )
        
        if connection.is_connected():
            print("✓ OBD connection successful!")
            print(f"Protocol: {connection.protocol_name()}")
            print(f"Port: {connection.port_name()}")
            print(f"Supports {len(connection.supported_commands)} commands")
            
            # Try a simple command
            print("\nTesting basic commands...")
            
            # Test ID command
            try:
                response = connection.query(obd.commands.ELM_VERSION)
                if not response.is_null():
                    print(f"ELM Version: {response.value}")
            except Exception as e:
                print(f"ELM Version command failed: {e}")
            
            # Test vehicle identification
            try:
                response = connection.query(obd.commands.VIN)
                if not response.is_null():
                    print(f"VIN: {response.value}")
            except Exception as e:
                print(f"VIN command failed: {e}")
            
            connection.close()
            return True
        else:
            print("✗ OBD connection failed")
            return False
            
    except Exception as e:
        print(f"✗ OBD connection error: {e}")
        return False

def main():
    """Main test function"""
    print("OBD-II Bluetooth Connection Test")
    print("=" * 50)
    
    # List available ports
    ports = list_bluetooth_ports()
    
    if not ports:
        print("No serial ports found!")
        return
    
    print(f"\nFound {len(ports)} potential ports to test")
    
    # Common configurations to test
    baudrates = [38400, 9600, 19200, 57600, 115200]
    protocols = ["AUTO", "6", "7", "8", "9"]  # Common ELM327 protocols
    
    # Test each port
    for port in ports:
        print(f"\n{'='*60}")
        print(f"TESTING PORT: {port}")
        print('='*60)
        
        # Test 1: Raw serial connection
        if test_serial_connection(port):
            print(f"\n✓ Serial connection to {port} works!")
            
            # Test 2: OBD connection with different configurations
            success = False
            for baudrate in baudrates:
                for protocol in protocols[:2]:  # Test only first few protocols to save time
                    if test_obd_connection(port, baudrate, protocol):
                        print(f"\n🎉 SUCCESS! Working configuration:")
                        print(f"   Port: {port}")
                        print(f"   Baudrate: {baudrate}")
                        print(f"   Protocol: {protocol}")
                        success = True
                        break
                if success:
                    break
            
            if not success:
                print(f"\n⚠️  Serial works but OBD connection failed for {port}")
        else:
            print(f"\n✗ Serial connection to {port} failed")
    
    print(f"\n{'='*60}")
    print("TEST COMPLETE")
    print('='*60)

if __name__ == "__main__":
    main()