#!/usr/bin/env python3
"""
Car Diagnostic Agent OBD Connection Test
Based on the actual car diagnostic agent implementation
"""
import obd
import time
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_connection_with_obd_library(port, baudrate=38400):
    """Test connection using the same method as the car diagnostic agent"""
    print(f"\n=== Testing OBD Connection (Agent Method) ===")
    print(f"Port: {port}")
    print(f"Baudrate: {baudrate}")
    
    try:
        # This is how the car diagnostic agent connects
        connection = obd.OBD(
            portstr=port,
            baudrate=baudrate,
            protocol=None,  # AUTO
            fast=False,     # Important: Use slow initialization
            timeout=30.0    # Longer timeout
        )
        
        print(f"Connection object created: {connection}")
        print(f"Is connected: {connection.is_connected()}")
        
        if connection.is_connected():
            print("✅ SUCCESS: OBD connection established!")
            print(f"Protocol: {connection.protocol_name()}")
            print(f"Port: {connection.port_name()}")
            print(f"Supported commands: {len(connection.supported_commands)}")
            
            # Try to get basic info
            try:
                print("\n--- Testing basic commands ---")
                # Try VIN command
                vin_response = connection.query(obd.commands.VIN)
                print(f"VIN response: {vin_response}")
                
                # Try RPM command
                rpm_response = connection.query(obd.commands.RPM)
                print(f"RPM response: {rpm_response}")
                
                # Try DTC command
                dtc_response = connection.query(obd.commands.GET_DTC)
                print(f"DTC response: {dtc_response}")
                
            except Exception as e:
                print(f"Command test error: {e}")
            
            connection.close()
            return True
        else:
            print("❌ FAILED: OBD connection not established")
            print("Error details:")
            print(f"  Connection object: {connection}")
            if hasattr(connection, '_status'):
                print(f"  Status: {connection._status}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiple_protocols(port, baudrate=38400):
    """Test with different protocols"""
    print(f"\n=== Testing Multiple Protocols ===")
    
    # Protocol mapping as used in the car diagnostic agent
    protocols = [
        (None, "AUTO"),
        ("6", "ISO 15765-4 CAN (11 bit ID, 500 kbaud)"),
        ("7", "ISO 15765-4 CAN (29 bit ID, 500 kbaud)"),
        ("8", "ISO 9141-2"),
        ("9", "SAE J1850 PWM")
    ]
    
    for protocol_code, protocol_name in protocols:
        print(f"\n--- Testing Protocol: {protocol_name} ---")
        try:
            connection = obd.OBD(
                portstr=port,
                baudrate=baudrate,
                protocol=protocol_code,
                fast=False,
                timeout=15.0
            )
            
            if connection.is_connected():
                print(f"✅ SUCCESS with {protocol_name}")
                print(f"  Actual protocol: {connection.protocol_name()}")
                connection.close()
                return protocol_code, protocol_name
            else:
                print(f"❌ FAILED with {protocol_name}")
                
            connection.close()
        except Exception as e:
            print(f"❌ ERROR with {protocol_name}: {e}")
    
    return None, None

if __name__ == "__main__":
    print("Car Diagnostic Agent OBD Connection Test")
    print("=" * 50)
    
    # Test with your port
    port = "/dev/cu.OBDIIADAPTER"
    
    # First try with standard settings
    success = test_connection_with_obd_library(port)
    
    if not success:
        print("\n" + "="*50)
        print("STANDARD CONNECTION FAILED")
        print("Trying different protocols...")
        print("="*50)
        
        # Test different protocols
        protocol_code, protocol_name = test_multiple_protocols(port)
        
        if protocol_code:
            print(f"\n✅ Recommended configuration:")
            print(f"  Port: {port}")
            print(f"  Baudrate: 38400")
            print(f"  Protocol: {protocol_code} ({protocol_name})")
        else:
            print(f"\n❌ Could not establish connection with any protocol")
            print("\nTroubleshooting steps:")
            print("1. Ensure car ignition is ON")
            print("2. Try disconnecting/reconnecting Bluetooth")
            print("3. Try different baud rates (9600, 19200, 57600, 115200)")
            print("4. Check if another application is using the port")
            print("5. Try a different OBD-II adapter")