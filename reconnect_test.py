#!/usr/bin/env python3
"""
Test OBD connection with automatic reconnection
"""
import obd
import time

def test_with_reconnection():
    """Test OBD connection with automatic reconnection"""
    print("Testing OBD connection with automatic reconnection...")
    
    # Configure OBD with automatic reconnection
    connection = obd.OBD(
        portstr="/dev/cu.OBDIIADAPTER",
        baudrate=38400,
        protocol=None,
        fast=False,
        timeout=10.0
    )
    
    if not connection.is_connected():
        print("Initial connection failed")
        return
        
    print("Connected successfully!")
    print(f"Protocol: {connection.protocol_name()}")
    
    # Test multiple commands with delays to see if connection stays alive
    commands = [
        ("ELM Version", obd.commands.ELM_VERSION),
        ("VIN", obd.commands.VIN),
        ("RPM", obd.commands.RPM),
        ("Coolant Temp", obd.commands.COOLANT_TEMP)
    ]
    
    for name, command in commands:
        print(f"\nTesting {name}...")
        try:
            response = connection.query(command)
            print(f"  {name}: {response}")
        except Exception as e:
            print(f"  Error: {e}")
            
        # Wait a bit between commands
        time.sleep(3)
        
        # Check if still connected
        if not connection.is_connected():
            print("  Connection lost!")
            # Try to reconnect
            print("  Attempting to reconnect...")
            connection.close()
            connection = obd.OBD(
                portstr="/dev/cu.OBDIIADAPTER",
                baudrate=38400,
                protocol=None,
                fast=False,
                timeout=10.0
            )
            if connection.is_connected():
                print("  Reconnected successfully!")
            else:
                print("  Reconnection failed!")
                break
        else:
            print("  Connection still active")
    
    connection.close()
    print("\nTest completed!")

if __name__ == "__main__":
    test_with_reconnection()