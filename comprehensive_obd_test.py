#!/usr/bin/env python3
"""
Comprehensive OBD test
"""
import obd

def comprehensive_obd_test():
    """Comprehensive OBD test"""
    print("Running comprehensive OBD test...")
    
    try:
        # Connect to OBD adapter
        connection = obd.OBD(
            portstr="/dev/cu.OBDIIADAPTER",
            baudrate=38400,
            protocol=None,
            fast=False,
            timeout=10.0
        )
        
        if not connection.is_connected():
            print("FAILED: Could not connect to OBD adapter")
            return
            
        print("SUCCESS: Connected to OBD adapter!")
        print(f"Protocol: {connection.protocol_name()}")
        print(f"Supported commands: {len(connection.supported_commands)}")
        
        # Test various commands
        print("\n--- Testing ELM Commands ---")
        elm_version = connection.query(obd.commands.ELM_VERSION)
        print(f"ELM Version: {elm_version}")
        
        print("\n--- Testing Vehicle Information ---")
        vin = connection.query(obd.commands.VIN)
        print(f"VIN: {vin}")
        
        print("\n--- Testing Diagnostic Trouble Codes ---")
        dtc = connection.query(obd.commands.GET_DTC)
        print(f"DTCs: {dtc}")
        
        print("\n--- Testing Basic Engine Data ---")
        rpm = connection.query(obd.commands.RPM)
        print(f"RPM: {rpm}")
        
        coolant_temp = connection.query(obd.commands.COOLANT_TEMP)
        print(f"Coolant Temperature: {coolant_temp}")
        
        throttle_pos = connection.query(obd.commands.THROTTLE_POS)
        print(f"Throttle Position: {throttle_pos}")
        
        print("\n--- Testing Supported PIDs ---")
        pids = connection.query(obd.commands.PIDS_A)
        print(f"Supported PIDs [01-20]: {pids}")
        
        connection.close()
        print("\nTest completed successfully!")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    comprehensive_obd_test()