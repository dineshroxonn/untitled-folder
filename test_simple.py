
#!/usr/bin/env python3
import asyncio
import sys
import os

# Add the project directory to sys.path
sys.path.insert(0, '/Users/dineshrampalli/Desktop/untitled-folder/car_diagnostic_agent')

try:
    from app.enhanced_obd_interface import PersistentOBDInterfaceManager
    import obd
    print("Import successful")
except ImportError as e:
    print(f"Import failed: {e}")
    sys.exit(1)

async def test_connection():
    print("Creating OBD manager...")
    manager = PersistentOBDInterfaceManager()
    
    print("Connecting...")
    result = await manager.connect()
    
    if result.success:
        print("Connected!")
        # Get some data
        response = await manager.query(obd.commands.ELM_VERSION)
        if response.success:
            print(f"ELM Version: {response.data}")
        else:
            print(f"Query failed: {response.error_message}")
    else:
        print(f"Connection failed: {result.error_message}")
    
    # Clean up
    await manager.disconnect()
    print("Disconnected")

if __name__ == "__main__":
    asyncio.run(test_connection())