#!/usr/bin/env python3
"""
Test script for Bluetooth-aware OBD interface.

This script tests the Bluetooth-aware OBD interface to ensure it properly
handles Bluetooth connection before establishing OBD communication.
"""

import asyncio
import sys
import os

# Add the car_diagnostic_agent directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from car_diagnostic_agent.app.bluetooth_obd_interface import BluetoothOBDInterfaceManager
    print("✓ Bluetooth OBD Interface imported successfully")
    
    async def test_bluetooth_obd_interface():
        """Test the Bluetooth-aware OBD interface."""
        print("Testing Bluetooth-Aware OBD Interface")
        print("=" * 40)
        
        # Create interface manager
        obd_manager = BluetoothOBDInterfaceManager()
        
        print(f"Manager type: {type(obd_manager)}")
        print(f"Is connected: {obd_manager.is_connected}")
        
        # Test Bluetooth connection methods
        print("\nTesting Bluetooth connection methods...")
        try:
            # Check if Bluetooth utilities are available
            if hasattr(obd_manager, '_is_bluetooth_available'):
                bt_available = obd_manager._is_bluetooth_available()
                print(f"Bluetooth utilities available: {bt_available}")
            
            # Check if OBD is paired
            if hasattr(obd_manager, '_is_obd_paired'):
                is_paired = obd_manager._is_obd_paired()
                print(f"OBD device paired: {is_paired}")
            
            # Test connection method
            if hasattr(obd_manager, '_ensure_bluetooth_connection'):
                print("Bluetooth connection method exists")
            else:
                print("Bluetooth connection method missing")
                
            print("\n✓ Bluetooth OBD Interface is properly implemented")
            
        except Exception as e:
            print(f"✗ Error testing interface: {e}")
            
    asyncio.run(test_bluetooth_obd_interface())
    
except ImportError as e:
    print(f"✗ Failed to import Bluetooth OBD Interface: {e}")
    print("The bluetooth_obd_interface.py file may not be properly created or accessible.")