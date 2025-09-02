#!/usr/bin/env python3
"""
Demo script for Car Diagnostic Agent OBD-II Integration

This script demonstrates the OBD integration capabilities including:
- Connection management
- DTC reading
- Live data monitoring
- Vehicle information retrieval
"""

import asyncio
import os
from datetime import datetime

# Add the app directory to the Python path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.obd_interface import MockOBDInterfaceManager
from app.obd_services import DTCReaderService, LiveDataService, VehicleInfoService
from app.obd_models import OBDConnectionConfig, OBDProtocol
from app.obd_config import config_manager


async def demo_obd_integration():
    """Demonstrate OBD-II integration capabilities."""
    print("✨ Car Diagnostic Agent - OBD-II Integration Demo")
    print("=" * 50)
    
    # 1. Setup mock OBD interface for demonstration
    print("n🔧 Setting up OBD interface...")
    config = OBDConnectionConfig(
        port="mock",
        baudrate=38400,
        protocol=OBDProtocol.ISO_15765_4
    )
    
    obd_manager = MockOBDInterfaceManager(config)
    
    # 2. Connect to "vehicle"
    print("n📡 Connecting to vehicle...")
    response = await obd_manager.connect()
    
    if response.success:
        print("✅ Successfully connected to vehicle!")
        print(f"   Protocol: {response.data.get('protocol')}")
        print(f"   Status: {response.data.get('status')}")
    else:
        print(f"❌ Connection failed: {response.error_message}")
        return
    
    # 3. Initialize services
    print("n🛠️  Initializing diagnostic services...")
    dtc_reader = DTCReaderService(obd_manager)
    live_data_service = LiveDataService(obd_manager)
    vehicle_info_service = VehicleInfoService(obd_manager)
    
    # 4. Get vehicle information
    print("n🚗 Reading vehicle information...")
    vehicle_info = await vehicle_info_service.get_vehicle_info()
    
    if vehicle_info:
        print(f"   VIN: {vehicle_info.vin}")
        print(f"   Make: {vehicle_info.make or 'Unknown'}")
        print(f"   Model: {vehicle_info.model or 'Unknown'}")
        print(f"   Year: {vehicle_info.year or 'Unknown'}")
        print(f"   Supported PIDs: {len(vehicle_info.supported_pids)}")
    
    # 5. Read diagnostic trouble codes
    print("n🔍 Scanning for diagnostic trouble codes...")
    dtcs = await dtc_reader.read_stored_dtcs()
    
    if dtcs:
        print(f"   Found {len(dtcs)} trouble codes:")
        for dtc in dtcs:
            severity_emoji = {
                "critical": "🔴",
                "warning": "🟡", 
                "info": "🔵"
            }
            emoji = severity_emoji.get(dtc.severity.value, "ℹ️")
            print(f"   {emoji} {dtc.code}: {dtc.description}")
            print(f"      Severity: {dtc.severity.value.title()}")
            print(f"      Status: {dtc.status.value.title()}")
    else:
        print("   ✅ No trouble codes found - vehicle running clean!")
    
    # 6. Read live engine parameters
    print("n📊 Reading live engine parameters...")
    live_data = await live_data_service.get_basic_engine_data()
    
    if live_data:
        print("   Current readings:")
        for pid, reading in live_data.items():
            status_emoji = "✅" if reading.is_within_range else "⚠️"
            range_status = "NORMAL" if reading.is_within_range else "OUT OF RANGE"
            print(f"   {status_emoji} {reading.name}: {reading.value} {reading.unit} ({range_status})")
    
    # 7. Demonstrate real-time monitoring (short demo)
    print("n🔄 Starting real-time monitoring (5 seconds)...")
    
    readings_count = 0
    
    async def data_callback(readings):
        nonlocal readings_count
        readings_count += 1
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"   [{timestamp}] Live readings #{readings_count}:")
        
        for pid, reading in readings.items():
            status = "✅" if reading.is_within_range else "⚠️"
            print(f"     {status} {reading.name}: {reading.value} {reading.unit}")
    
    # Monitor key parameters
    monitor_pids = ["0C", "05", "11"]  # RPM, Coolant Temp, Throttle Position
    await live_data_service.start_monitoring(
        pids=monitor_pids,
        interval=1.0,
        callback=data_callback
    )
    
    # Let it run for 5 seconds
    await asyncio.sleep(5)
    
    # Stop monitoring
    await live_data_service.stop_monitoring()
    print("n   ⏹️  Monitoring stopped.")
    
    # 8. Configuration management demo
    print("n⚙️  Configuration management demo...")
    
    # Save current config as a profile
    config_manager.save_profile("demo_profile", config)
    profiles = config_manager.list_profiles()
    print(f"   Available profiles: {profiles}")
    
    # Show available ports (would show real ports on actual system)
    ports = config_manager.get_available_ports()
    print(f"   Available ports: {len(ports)} detected")
    
    # 9. Connection info
    print("n📦 Connection information:")
    conn_info = await obd_manager.get_connection_info()
    for key, value in conn_info.items():
        print(f"   {key}: {value}")
    
    # 10. Disconnect
    print("n🔌 Disconnecting from vehicle...")
    response = await obd_manager.disconnect()
    
    if response.success:
        print("✅ Successfully disconnected.")
    
    print("n✨ Demo completed successfully!")
    print("n📄 Summary:")
    print(f"   - Connected to mock OBD adapter")
    print(f"   - Read {len(dtcs) if dtcs else 0} diagnostic trouble codes")
    print(f"   - Monitored {len(live_data) if live_data else 0} live parameters")
    print(f"   - Collected {readings_count} real-time readings")
    print(f"   - Demonstrated configuration management")
    
    print("n🚀 Ready for real vehicle diagnostics!")
    print("   To use with a real vehicle:")
    print("   1. Connect an OBD-II adapter to your vehicle")
    print("   2. Set enable_mock_mode=false in configuration")
    print("   3. Run the Car Diagnostic Agent")
    print("   4. Use commands like 'Connect to OBD' and 'Scan for trouble codes'")


async def demo_agent_integration():
    """Demonstrate integration with the main agent."""
    print("n" + "=" * 50)
    print("🤖 Agent Integration Demo")
    print("=" * 50)
    
    # This would normally require a Google API key
    print("n📄 Note: Agent integration demo requires GOOGLE_API_KEY")
    print("The agent can:")
    print("   - Accept OBD commands like 'Connect to OBD'")
    print("   - Automatically read live diagnostic data")
    print("   - Enhance responses with real-time vehicle information")
    print("   - Provide persona-based diagnosis as the vehicle itself")
    
    print("n💬 Example interactions:")
    print('   User: "Connect to OBD and scan my vehicle"')
    print('   Agent: "🔍 Scanning your vehicle for diagnostic trouble codes..."')
    print('          "📋 Found 2 trouble codes:"')
    print('          "🔴 P0171: System Too Lean (Bank 1)"')
    print('          "🟡 P0420: Catalyst System Efficiency Below Threshold"')
    print('')
    print('          "📊 Current Engine Parameters:"')
    print('          "✅ Engine RPM: 750 rpm"')
    print('          "⚠️  Coolant Temperature: 210°F (OUT OF RANGE)"')
    print('')
    print('          "Hello, I am your 2021 Honda Civic. I can see that I'm"')
    print('          "running a bit lean and my catalytic converter..."')


if __name__ == "__main__":
    print("🎆 Starting Car Diagnostic Agent OBD-II Demo...")
    
    # Run the demonstration
    asyncio.run(demo_obd_integration())
    asyncio.run(demo_agent_integration())
    
    print("n🎉 Demo completed! Check the documentation for more details.")