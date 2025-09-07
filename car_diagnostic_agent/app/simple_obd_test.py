#!/usr/bin/env python3
"""
Simple OBD connection test
"""
import obd
import time

def test_obd_connection():
    print("Testing OBD connection...")
    
    # Try to connect with auto-detection
    connection = obd.OBD(fast=False)
    
    print(f"Connected: {connection.is_connected()}")
    
    if connection.is_connected():
        print(f"Protocol: {connection.protocol_name()}")
        print(f"Port: {connection.port_name()}")
        print(f"Supported commands: {len(connection.supported_commands)}")
        
        # Try a simple command
        try:
            response = connection.query(obd.commands.ELM_VERSION)
            print(f"ELM Version: {response}")
        except Exception as e:
            print(f"Error querying ELM version: {e}")
            
        connection.close()
    else:
        print("Failed to connect to OBD adapter")
        print("Available ports:")
        ports = obd.scan_serial()
        for port in ports:
            print(f"  - {port}")

if __name__ == "__main__":
    test_obd_connection()