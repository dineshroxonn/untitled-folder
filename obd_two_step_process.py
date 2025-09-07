#!/usr/bin/env python3
"""
OBD Data Retrieval with Explicit Connection

This script demonstrates the pattern you requested:
1. Send explicit connection request first
2. Then retrieve all data using the established connection
"""

import asyncio
import sys
import os

# Add the car_diagnostic_agent directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'car_diagnostic_agent'))

from car_diagnostic_agent.app.enhanced_obd_interface import PersistentOBDInterfaceManager
import obd

async def establish_connection():
    """Step 1: Establish persistent OBD connection."""
    print("Step 1: Sending connection request...")
    
    # Create OBD manager
    obd_manager = PersistentOBDInterfaceManager()
    
    # Send connection request
    connect_result = await obd_manager.connect()
    
    if connect_result.success:
        print("✅ Connection established successfully!")
        # Get connection details
        conn_info = await obd_manager.get_connection_info()
        print(f"   Connected to: {conn_info.get('port', 'Unknown')}")
        print(f"   Using protocol: {conn_info.get('protocol', 'Unknown')}")
        print(f"   Supported commands: {conn_info.get('supported_commands', 0)}")
        return obd_manager
    else:
        print(f"❌ Connection failed: {connect_result.error_message}")
        return None

async def retrieve_all_data(obd_manager):
    """Step 2: Retrieve all data using established connection."""
    print("\nStep 2: Retrieving all data...")
    
    if not obd_manager or not obd_manager.is_connected:
        print("❌ No active connection available")
        return False
    
    # List of commands to query
    commands = [
        ("ELM Version", obd.commands.ELM_VERSION),
        ("Vehicle Identification", obd.commands.VIN),
        ("Calibration ID", obd.commands.CALIBRATION_ID),
        ("CVN", obd.commands.CV_N),
        ("DTC Count", obd.commands.DTC_COUNT),
        ("Freeze DTC", obd.commands.FREEZE_DTC),
        ("Fuel Status", obd.commands.FUEL_STATUS),
        ("Engine Load", obd.commands.ENGINE_LOAD),
        ("Coolant Temperature", obd.commands.COOLANT_TEMP),
        ("Short Fuel Trim Bank 1", obd.commands.SHORT_FUEL_TRIM_1),
        ("Long Fuel Trim Bank 1", obd.commands.LONG_FUEL_TRIM_1),
        ("Short Fuel Trim Bank 2", obd.commands.SHORT_FUEL_TRIM_2),
        ("Long Fuel Trim Bank 2", obd.commands.LONG_FUEL_TRIM_2),
        ("Fuel Pressure", obd.commands.FUEL_PRESSURE),
        ("Intake Manifold Pressure", obd.commands.INTAKE_PRESSURE),
        ("Engine RPM", obd.commands.RPM),
        ("Vehicle Speed", obd.commands.SPEED),
        ("Timing Advance", obd.commands.TIMING_ADVANCE),
        ("Intake Air Temp", obd.commands.INTAKE_TEMP),
        ("MAF Air Flow Rate", obd.commands.MAF),
        ("Throttle Position", obd.commands.THROTTLE_POS),
        ("Run Time", obd.commands.RUN_TIME),
        ("Distance Traveled MIL On", obd.commands.DISTANCE_W_MIL),
        ("Fuel Level Input", obd.commands.FUEL_LEVEL),
        ("Barometric Pressure", obd.commands.BAROMETRIC_PRESSURE),
    ]
    
    # Query each command
    successful_queries = 0
    failed_queries = 0
    
    for name, command in commands:
        try:
            print(f"Querying {name}...")
            response = await obd_manager.query(command)
            
            if response.success:
                value = response.data.get('value', 'N/A')
                unit = response.data.get('unit', '')
                print(f"   ✅ {name}: {value} {unit}")
                successful_queries += 1
            else:
                print(f"   ⚠️  {name}: No data (not supported or unavailable)")
                failed_queries += 1
                
        except Exception as e:
            print(f"   ❌ {name}: Error - {e}")
            failed_queries += 1
    
    print(f"\n📊 Summary:")
    print(f"   Successful queries: {successful_queries}")
    print(f"   Unavailable queries: {failed_queries}")
    print(f"   Total commands tested: {len(commands)}")
    
    return successful_queries > 0

async def main():
    """Main function implementing the two-step process."""
    print("OBD Data Retrieval - Two-Step Process")
    print("=" * 45)
    
    # Step 1: Establish connection
    obd_manager = await establish_connection()
    
    if not obd_manager:
        print("Cannot proceed without connection")
        return
    
    try:
        # Step 2: Retrieve all data
        success = await retrieve_all_data(obd_manager)
        
        if success:
            print("\n✅ Data retrieval completed successfully!")
        else:
            print("\n⚠️  Data retrieval completed with limited results")
            
    except Exception as e:
        print(f"❌ Error during data retrieval: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up connection
        print("\nCleaning up connection...")
        try:
            disconnect_result = await obd_manager.disconnect()
            if disconnect_result.success:
                print("✅ Connection closed successfully")
            else:
                print(f"⚠️  Disconnection issue: {disconnect_result.error_message}")
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")

if __name__ == "__main__":
    asyncio.run(main())or_message}")\n        except Exception as e:\n            print(f"❌ Error during cleanup: {e}")\n\nif __name__ == "__main__":\n    asyncio.run(main())