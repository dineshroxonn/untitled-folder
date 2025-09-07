#!/usr/bin/env python3
"""
Advanced OBD-II Connection Test Script

This script provides more detailed testing of OBD-II connections with
additional debugging information and more connection attempts.
"""

import obd
import serial
import time
import serial.tools.list_ports

def detailed_serial_test(port, baudrate=38400, timeout=5):
    """Perform detailed serial testing with various commands"""
    print(f"\n=== Detailed Serial Test for {port} at {baudrate} baud ===")
    
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
        time.sleep(0.1)
        
        # Test various ELM327 commands
        commands = [
            ("ATZ", "Reset"),
            ("ATE0", "Echo Off"),
            ("ATSP0", "Automatic Protocol Search"),
            ("ATDP", "Describe Protocol"),
            ("ATRV", "Read Vehicle Voltage"),
            ("0100", "Supported PIDs [01-20]")
        ]
        
        for cmd, description in commands:
            print(f"\nSending {cmd} ({description})...")
            ser.write((cmd + "\r").encode())
            time.sleep(1)
            
            # Read response
            response = ser.read_all()
            if response:
                decoded = response.decode('utf-8', errors='ignore')
                print(f"  Response: {repr(decoded)}")
                print(f"  Clean: {decoded.strip()}")
            else:
                print("  No response received")
        
        ser.close()
        print("✓ Detailed serial test completed")
        return True
        
    except Exception as e:
        print(f"✗ Serial test failed: {e}")
        return False

def test_obd_with_debug(port, baudrate=38400, protocol=None, timeout=10):
    """Test OBD connection with detailed debugging"""
    print(f"\n=== OBD Test with Debug ===")
    print(f"Port: {port}")
    print(f"Baudrate: {baudrate}")
    print(f"Protocol: {protocol}")
    print(f"Timeout: {timeout}")
    
    try:
        # Enable debug logging
        import logging
        logging.basicConfig(level=logging.DEBUG)
        
        # Create OBD connection with debugging
        connection = obd.OBD(
            portstr=port,
            baudrate=baudrate,
            protocol=protocol,
            fast=False,
            timeout=timeout
        )
        
        print(f"Connection object: {connection}")
        print(f"Is connected: {connection.is_connected()}")
        
        if connection.is_connected():
            print("✓ OBD connection successful!")
            print(f"Protocol: {connection.protocol_name()}")
            print(f"Port: {connection.port_name()}")
            print(f"Supported commands: {len(connection.supported_commands)}")
            
            # Try a simple command
            try:
                response = connection.query(obd.commands.ELM_VERSION)
                print(f"ELM Version response: {response}")
            except Exception as e:
                print(f"ELM Version command failed: {e}")
            
            connection.close()
            return True
        else:
            print("✗ OBD connection failed")
            return False
            
    except Exception as e:
        print(f"✗ OBD connection error: {e}")
        import traceback
        traceback.print_exc()
        return False

def list_all_ports():
    """List all available serial ports with detailed information"""
    print("=== All Available Serial Ports ===")
    ports = list(serial.tools.list_ports.comports())
    
    for port in ports:
        print(f"Device: {port.device}")
        print(f"  Description: {port.description}")
        print(f"  Manufacturer: {port.manufacturer}")
        print(f"  Product: {port.product}")
        print(f"  VID:PID: {port.vid}:{port.pid}")
        print(f"  Serial Number: {port.serial_number}")
        print(f"  Location: {port.location}")
        print(f"  Interface: {port.interface}")
        print()

def main():
    """Main test function"""
    print("Advanced OBD-II Connection Test")
    print("=" * 50)
    
    # List all ports first
    list_all_ports()
    
    # Test the OBDIIADAPTER port specifically
    port = "/dev/cu.OBDIIADAPTER"
    
    # Test with different baud rates
    baudrates = [38400, 9600, 19200, 57600, 115200]
    
    print(f"\nTesting port: {port}")
    
    # First do detailed serial test
    detailed_serial_test(port)
    
    # Then test OBD with different configurations
    for baudrate in baudrates:
        print(f"\n{'='*60}")
        print(f"Testing OBD at {baudrate} baud")
        print('='*60)
        
        # Try AUTO protocol
        test_obd_with_debug(port, baudrate, None)
        
        # Try specific protocols if AUTO fails
        if baudrate == 38400:  # Only test specific protocols at default baud rate
            protocols = ["6", "7", "8", "9"]
            for protocol in protocols:
                print(f"\n--- Testing with protocol {protocol} ---")
                test_obd_with_debug(port, baudrate, protocol)

if __name__ == "__main__":
    main()