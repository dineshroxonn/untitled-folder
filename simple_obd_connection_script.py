#!/usr/bin/env python3
"""
Simple OBD Connection Script

This script establishes a persistent OBD connection and keeps it alive
for subsequent data requests.
"""

import asyncio
import sys
import os

# Add the car_diagnostic_agent directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'car_diagnostic_agent'))

from car_diagnostic_agent.app.enhanced_obd_interface import PersistentOBDInterfaceManager
import obd

class OBDConnectionManager:
    """Manages persistent OBD connection."""
    
    def __init__(self):
        self.obd_manager = PersistentOBDInterfaceManager()
        self.is_initialized = False
    
    async def connect(self):
        """Establish OBD connection."""
        print("Establishing OBD connection...")
        result = await self.obd_manager.connect()
        
        if result.success:
            self.is_initialized = True
            print("✅ OBD connection established")
            # Show connection details
            info = await self.obd_manager.get_connection_info()
            print(f"   Port: {info.get('port')}")
            print(f"   Protocol: {info.get('protocol')}")
        else:
            print(f"❌ Connection failed: {result.error_message}")
            
        return result.success
    
    async def disconnect(self):
        """Close OBD connection."""
        if self.is_initialized:
            print("Closing OBD connection...")
            result = await self.obd_manager.disconnect()
            self.is_initialized = False
            if result.success:
                print("✅ OBD connection closed")
            else:
                print(f"⚠️  Disconnection issue: {result.error_message}")
    
    async def query(self, command):
        """Query OBD command with connection check."""
        if not self.is_initialized:
            print("❌ Not connected to OBD")
            return None
            
        if not self.obd_manager.is_connected:
            print("⚠️  Connection lost, attempting to reconnect...")
            if not await self.connect():
                print("❌ Reconnection failed")
                return None
        
        print(f"Querying {command.name}...")
        response = await self.obd_manager.query(command)
        
        if response.success:
            print(f"✅ Response: {response.data.get('value')} {response.data.get('unit', '')}")
        else:
            print(f"❌ Query failed: {response.error_message}")
            
        return response

async def main():
    """Main test function."""
    print("OBD Connection Manager Test")
    print("=" * 30)
    
    # Create connection manager
    conn_manager = OBDConnectionManager()
    
    try:
        # Establish connection first (as requested)
        if not await conn_manager.connect():
            print("Failed to establish initial connection")
            return
        
        # Now we can query data multiple times using the persistent connection
        print("\nTesting persistent connection with multiple queries...")
        
        # Query 1: ELM version
        await conn_manager.query(obd.commands.ELM_VERSION)
        
        # Wait a bit
        await asyncio.sleep(2)
        
        # Query 2: RPM (if supported)
        await conn_manager.query(obd.commands.RPM)
        
        # Wait a bit
        await asyncio.sleep(2)
        
        # Query 3: Vehicle speed (if supported)
        await conn_manager.query(obd.commands.SPEED)
        
        print("\n✅ All queries completed successfully with persistent connection!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        await conn_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(main())