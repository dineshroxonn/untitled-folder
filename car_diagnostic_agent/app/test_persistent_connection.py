#!/usr/bin/env python3
"""
Test script for persistent OBD connections.

This script tests the persistent OBD connection functionality
in the car diagnostic agent.
"""

import asyncio
import sys
import os

# Add the car_diagnostic_agent directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from car_diagnostic_agent.app.agent import CarDiagnosticAgent
from car_diagnostic_agent.app.obd_config import config_manager


async def test_persistent_connection():
    """Test persistent OBD connection functionality."""
    print("Testing Persistent OBD Connection")
    print("=" * 40)
    
    # Create agent instance
    agent = CarDiagnosticAgent()
    
    try:
        # Initialize OBD system
        print("Initializing OBD system...")
        await agent.initialize_obd_system()
        print("OBD system initialized")
        
        # Check if we have an OBD manager
        if agent.obd_manager is None:
            print("No OBD manager available")
            return
            
        print(f"OBD manager type: {type(agent.obd_manager)}")
        
        # Test connection
        print("\nConnecting to OBD adapter...")
        result = await agent.connect_obd()
        
        if result["success"]:
            print("✓ Connection successful")
            
            # Get connection info
            conn_info = await agent.obd_manager.get_connection_info()
            print(f"Port: {conn_info.get('port', 'Unknown')}")
            print(f"Protocol: {conn_info.get('protocol', 'Unknown')}")
            print(f"Connected: {conn_info.get('connected', False)}")
            
            # Test multiple queries to see if connection persists
            print("\nTesting connection persistence...")
            for i in range(3):
                print(f"Query {i+1}:")
                conn_info = await agent.obd_manager.get_connection_info()
                print(f"  Connected: {conn_info.get('connected', False)}")
                await asyncio.sleep(1)
            
            # Test disconnection
            print("\nDisconnecting...")
            disconnect_result = await agent.disconnect_obd()
            if disconnect_result["success"]:
                print("✓ Disconnected successfully")
            else:
                print(f"✗ Disconnection failed: {disconnect_result.get('error')}")
                
        else:
            print(f"✗ Connection failed: {result.get('error')}")
            print("Testing mock mode fallback...")
            
            # Try with mock mode
            print("Enabling mock mode...")
            config_manager.set_mock_mode(True)
            await agent.initialize_obd_system()
            
            print("Connecting with mock mode...")
            result = await agent.connect_obd()
            if result["success"]:
                print("✓ Mock connection successful")
            else:
                print(f"✗ Mock connection failed: {result.get('error')}")
            
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Ensure disconnection
        if agent.obd_manager:
            try:
                await agent.disconnect_obd()
                print("Cleaned up connection")
            except:
                pass


if __name__ == "__main__":
    asyncio.run(test_persistent_connection())
