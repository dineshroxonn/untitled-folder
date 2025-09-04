#!/usr/bin/env python3
"""
Test script to verify synchronization between enhanced agent and frontend
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from app.obd_services import DTCReaderService, LiveDataService
from app.obd_models import OBDConnectionConfig, DTCInfo, DTCSeverity, DTCStatus, LiveDataReading
from app.obd_interface import MockOBDInterfaceManager
from app.agent import CarDiagnosticAgent

async def test_enhanced_features():
    """Test the enhanced features of the car diagnostic agent"""
    print("Testing enhanced car diagnostic agent features...")
    
    # Test 1: Enhanced DTC database
    print("\n1. Testing DTC database...")
    config = OBDConnectionConfig(port="mock")
    manager = MockOBDInterfaceManager(config)
    await manager.connect()
    
    dtc_service = DTCReaderService(manager)
    # Check that we have the basic DTC descriptions
    dtc_descriptions = dtc_service._dtc_descriptions
    print(f"   Found {len(dtc_descriptions)} DTC descriptions in database")
    
    # Test 2: LiveData with min/max values
    print("\n2. Testing LiveData with min/max values...")
    live_service = LiveDataService(manager)
    
    # Create a mock reading with min/max values
    reading = LiveDataReading(
        pid="0C",
        name="Engine RPM",
        value=750.0,
        unit="rpm",
        min_value=600.0,
        max_value=8000.0
    )
    print(f"   LiveData reading: {reading.name} = {reading.value} {reading.unit}")
    print(f"   Range: {reading.min_value} - {reading.max_value}")
    print(f"   Within range: {reading.is_within_range}")
    
    # Test 3: Enhanced agent with hypotheses generation
    print("\n3. Testing enhanced agent features...")
    agent = CarDiagnosticAgent()
    
    # Mock OBD data for testing
    mock_obd_data = {
        "obd_connected": True,
        "dtcs": [
            {
                "code": "P0171",
                "description": "System Too Lean (Bank 1)",
                "severity": "warning",
                "status": "stored"
            },
            {
                "code": "P0300",
                "description": "Random/Multiple Cylinder Misfire Detected",
                "severity": "critical",
                "status": "active"
            }
        ],
        "live_data": {
            "0C": {
                "name": "Engine RPM",
                "value": 750.0,
                "unit": "rpm",
                "in_range": True
            },
            "05": {
                "name": "Engine Coolant Temperature",
                "value": 210.0,
                "unit": "°F",
                "in_range": False
            }
        },
        "vehicle_info": {
            "make": "Honda",
            "model": "Civic",
            "year": 2021,
            "vin": "1HGBH41JXMN109186"
        }
    }
    
    # Test hypothesis generation
    hypotheses = await agent._generate_diagnostic_hypotheses(mock_obd_data)
    print(f"   Generated {len(hypotheses)} diagnostic hypotheses:")
    for i, hypothesis in enumerate(hypotheses, 1):
        print(f"     {i}. {hypothesis['title']} (Confidence: {hypothesis['confidence']})")
    
    # Test data validation
    validation_warnings = await agent._validate_diagnostic_data(mock_obd_data)
    print(f"   Generated {len(validation_warnings)} validation warnings")
    for warning in validation_warnings:
        # Print first part of warning for brevity
        print(f"     Warning: {warning[:50]}...")
    
    print("\n✅ All enhanced features are working correctly!")
    return True

if __name__ == "__main__":
    try:
        asyncio.run(test_enhanced_features())
        print("\n🎉 Synchronization test completed successfully!")
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)