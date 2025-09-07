#!/usr/bin/env python3
"""
Test connection using the car diagnostic agent's method
"""
import obd
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

def test_agent_connection():
    """Test connection using the agent's method"""
    print("Testing connection using car diagnostic agent method")
    
    try:
        # Try with different settings
        connection = obd.OBD(
            portstr="/dev/cu.OBDIIADAPTER",
            baudrate=38400,
            protocol=None,  # AUTO
            fast=False,     # Important: Use slow initialization
            timeout=30.0    # Longer timeout
        )
        
        print(f"Connection object: {connection}")
        print(f"Is connected: {connection.is_connected()}")
        
        if connection.is_connected():
            print("SUCCESS: Connected to OBD adapter!")
            print(f"Protocol: {connection.protocol_name()}")
            print(f"Supported commands: {len(connection.supported_commands)}")
            
            # Try a simple command
            try:
                response = connection.query(obd.commands.ELM_VERSION)
                print(f"ELM Version: {response}")
            except Exception as e:
                print(f"Command error: {e}")
                
            connection.close()
            return True
        else:
            print("FAILED: Could not connect to OBD adapter")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_agent_connection()