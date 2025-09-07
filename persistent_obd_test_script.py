#!/usr/bin/env python3
"""
Persistent OBD Connection Test Script

This script demonstrates how to establish and maintain a persistent OBD connection,
then retrieve data while keeping the connection alive.
"""

import asyncio
import sys
import os
import time

# Add the car_diagnostic_agent directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'car_diagnostic_agent'))

from car_diagnostic_agent.app.enhanced_obd_interface import PersistentOBDInterfaceManager
import obd

async def test_persistent_connection():
    """Test persistent OBD connection with data retrieval."""
    print("Persistent OBD Connection Test")
    print("=" * 40)
    
    # Create OBD interface manager
    obd_manager = PersistentOBDInterfaceManager()
    
    try:
        # Step 1: Establish connection (this is the explicit connection request you wanted)
        print("Step 1: Establishing OBD connection...")
        connect_result = await obd_manager.connect()
        
        if not connect_result.success:
            print(f"❌ Connection failed: {connect_result.error_message}")
            return
        
        print("✅ Connection established successfully!")
        
        # Get connection info
        conn_info = await obd_manager.get_connection_info()
        print(f"   Port: {conn_info.get('port', 'Unknown')}")
        print(f"   Protocol: {conn_info.get('protocol', 'Unknown')}")
        print(f"   Supported Commands: {conn_info.get('supported_commands', 0)}")
        
        # Step 2: Retrieve data multiple times to test connection persistence
        print("\nStep 2: Testing connection persistence with data retrieval...")
        
        # Test multiple data retrievals with delays to verify connection stays active
        for i in range(3):
            print(f"\n--- Data Retrieval #{i+1} ---")
            
            # Check connection status before each query
            print(f"Connection status: {'Connected' if obd_manager.is_connected else 'Disconnected'}")
            
            if obd_manager.is_connected:
                try:
                    # Query ELM version (lightweight command)
                    print("Querying ELM version...")
                    response = await obd_manager.query(obd.commands.ELM_VERSION)
                    if response.success:
                        print(f"ELM Version: {response.data.get('value', 'Unknown')}")
                    else:
                        print(f"Query failed: {response.error_message}")
                except Exception as e:
                    print(f"Error during query: {e}")
            else:
                print("Not connected, attempting to reconnect...")
                reconnect_result = await obd_manager.connect()
                if reconnect_result.success:
                    print("Reconnected successfully!")
                else:
                    print(f"Reconnection failed: {reconnect_result.error_message}")
                    break
            
            # Wait before next query to test connection persistence
            print("Waiting 5 seconds before next query...")
            await asyncio.sleep(5)
        
        # Step 3: Test with more complex queries if connection is still active
        print("\nStep 3: Testing with engine data queries...")
        
        if obd_manager.is_connected:
            # Try to get RPM
            print("Querying engine RPM...")
            rpm_response = await obd_manager.query(obd.commands.RPM)
            if rpm_response.success:
                print(f"Engine RPM: {rpm_response.data.get('value', 'Unknown')} {rpm_response.data.get('unit', '')}")
            else:
                print(f"RPM query failed: {rpm_response.error_message}")
            
            # Try to get vehicle speed
            print("Querying vehicle speed...")
            speed_response = await obd_manager.query(obd.commands.SPEED)
            if speed_response.success:
                print(f"Vehicle Speed: {speed_response.data.get('value', 'Unknown')} {speed_response.data.get('unit', '')}")
            else:
                print(f"Speed query failed: {speed_response.error_message}")
        
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Step 4: Clean up connection
        print("\nStep 4: Cleaning up connection...")
        try:
            disconnect_result = await obd_manager.disconnect()
            if disconnect_result.success:
                print("✅ Disconnected successfully")
            else:
                print(f"⚠️  Disconnection reported issue: {disconnect_result.error_message}")
        except Exception as e:
            print(f"❌ Error during disconnection: {e}")

def run_test():
    """Run the async test."""
    print("Starting OBD Connection Test...")
    asyncio.run(test_persistent_connection())

if __name__ == "__main__":
    run_test()