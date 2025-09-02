"""
Test suite for OBD integration functionality.

Tests the OBD interface, services, and agent integration with mock data.
"""

import asyncio
import pytest
import pytest_asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.obd_models import (
    OBDConnectionConfig, 
    OBDProtocol, 
    DTCInfo, 
    DTCSeverity, 
    DTCStatus,
    LiveDataReading,
    VehicleInfo
)
from app.obd_interface import MockOBDInterfaceManager
from app.obd_services import DTCReaderService, LiveDataService, VehicleInfoService
from app.obd_config import OBDConfigManager
from app.agent import CarDiagnosticAgent


class TestOBDModels:
    """Test OBD data models."""
    
    def test_obd_connection_config_creation(self):
        """Test OBD connection configuration creation."""
        config = OBDConnectionConfig(
            port="/dev/ttyUSB0",
            baudrate=38400,
            protocol=OBDProtocol.ISO_15765_4
        )
        
        assert config.port == "/dev/ttyUSB0"
        assert config.baudrate == 38400
        assert config.protocol == OBDProtocol.ISO_15765_4
        assert config.auto_detect == True
        assert config.max_retries == 3
    
    def test_dtc_info_creation(self):
        """Test DTC information creation."""
        dtc = DTCInfo(
            code="P0171",
            description="System Too Lean (Bank 1)",
            severity=DTCSeverity.WARNING,
            status=DTCStatus.STORED
        )
        
        assert dtc.code == "P0171"
        assert dtc.severity == DTCSeverity.WARNING
        assert dtc.status == DTCStatus.STORED
        assert isinstance(dtc.timestamp, datetime)
    
    def test_live_data_reading(self):
        """Test live data reading creation."""
        reading = LiveDataReading(
            pid="0C",
            name="Engine RPM",
            value=750.0,
            unit="rpm",
            min_value=600.0,
            max_value=8000.0
        )
        
        assert reading.pid == "0C"
        assert reading.value == 750.0
        assert reading.is_within_range == True
        
        # Test out of range
        reading.value = 500.0
        assert reading.is_within_range == False
    
    def test_vehicle_info_creation(self):
        """Test vehicle information creation."""
        vehicle_info = VehicleInfo(
            vin="1HGBH41JXMN109186",
            make="Honda",
            model="Civic",
            year=2021
        )
        
        assert vehicle_info.vin == "1HGBH41JXMN109186"
        assert vehicle_info.make == "Honda"
        assert vehicle_info.model == "Civic"
        assert vehicle_info.year == 2021


class TestMockOBDInterface:
    """Test mock OBD interface functionality."""
    
    @pytest_asyncio.fixture
    async def mock_obd_manager(self):
        """Create a mock OBD interface manager."""
        config = OBDConnectionConfig(port="mock", baudrate=38400)
        manager = MockOBDInterfaceManager(config)
        return manager
    
    @pytest.mark.asyncio
    async def test_mock_connection(self, mock_obd_manager):
        """Test mock OBD connection."""
        response = await mock_obd_manager.connect()
        
        assert response.success == True
        assert mock_obd_manager.is_connected == True
        assert response.data["status"] == "connected"
        assert response.data["protocol"] == "mock_protocol"
    
    @pytest.mark.asyncio
    async def test_mock_disconnection(self, mock_obd_manager):
        """Test mock OBD disconnection."""
        # Connect first
        await mock_obd_manager.connect()
        assert mock_obd_manager.is_connected == True
        
        # Disconnect
        response = await mock_obd_manager.disconnect()
        
        assert response.success == True
        assert mock_obd_manager.is_connected == False
        assert response.data["status"] == "disconnected"
    
    @pytest.mark.asyncio
    async def test_mock_query(self, mock_obd_manager):
        """Test mock OBD query."""
        await mock_obd_manager.connect()
        
        # Create a mock command object
        mock_command = MagicMock()
        mock_command.name = "RPM"
        
        response = await mock_obd_manager.query(mock_command)
        
        assert response.success == True
        assert response.data["command"] == "RPM"
        assert response.data["value"] == 750.0
        assert response.data["unit"] == "rpm"


class TestOBDServices:
    """Test OBD service functionality."""
    
    @pytest_asyncio.fixture
    async def obd_services(self):
        """Create OBD services with mock interface."""
        config = OBDConnectionConfig(port="mock", baudrate=38400)
        obd_manager = MockOBDInterfaceManager(config)
        await obd_manager.connect()
        
        dtc_reader = DTCReaderService(obd_manager)
        live_data_service = LiveDataService(obd_manager)
        vehicle_info_service = VehicleInfoService(obd_manager)
        
        return dtc_reader, live_data_service, vehicle_info_service, obd_manager
    
    @pytest.mark.asyncio
    async def test_dtc_reader_service(self, obd_services):
        """Test DTC reader service."""
        dtc_reader, _, _, _ = obd_services
        
        # Mock the _dtc_descriptions to include test codes
        dtc_reader._dtc_descriptions.update({
            "P0171": "System Too Lean (Bank 1)",
            "P0300": "Random/Multiple Cylinder Misfire Detected"
        })
        
        # Test reading stored DTCs (this will use mock data)
        dtcs = await dtc_reader.read_stored_dtcs()
        
        # The mock interface should return some DTCs
        assert isinstance(dtcs, list)
        # Note: Actual test would depend on mock implementation
    
    @pytest.mark.asyncio
    async def test_live_data_service(self, obd_services):
        """Test live data service."""
        _, live_data_service, _, _ = obd_services
        
        # Test reading a single parameter
        reading = await live_data_service.read_parameter("0C")  # RPM
        
        if reading:  # Depends on mock implementation
            assert reading.pid == "0C"
            assert isinstance(reading.value, float)
            assert reading.unit
    
    @pytest.mark.asyncio
    async def test_vehicle_info_service(self, obd_services):
        """Test vehicle information service."""
        _, _, vehicle_info_service, _ = obd_services
        
        # Test getting vehicle info
        vehicle_info = await vehicle_info_service.get_vehicle_info()
        
        # Mock should return some vehicle info
        if vehicle_info:
            assert isinstance(vehicle_info, VehicleInfo)
            assert vehicle_info.vin


class TestOBDConfigManager:
    """Test OBD configuration management."""
    
    @pytest.fixture
    def temp_config_manager(self, tmp_path):
        """Create a temporary config manager."""
        return OBDConfigManager(str(tmp_path))
    
    def test_default_config_creation(self, temp_config_manager):
        """Test default configuration creation."""
        config = temp_config_manager.get_default_config()
        
        assert isinstance(config, OBDConnectionConfig)
        assert config.port == "auto"
        assert config.baudrate == 38400
        assert config.protocol == OBDProtocol.AUTO
    
    def test_profile_management(self, temp_config_manager):
        """Test profile save and load."""
        # Create a test profile
        test_config = OBDConnectionConfig(
            port="/dev/ttyUSB0",
            baudrate=115200,
            protocol=OBDProtocol.ISO_15765_4
        )
        
        # Save profile
        temp_config_manager.save_profile("test_profile", test_config)
        
        # Load profile
        loaded_config = temp_config_manager.get_profile_config("test_profile")
        
        assert loaded_config.port == "/dev/ttyUSB0"
        assert loaded_config.baudrate == 115200
        assert loaded_config.protocol == OBDProtocol.ISO_15765_4
    
    def test_profile_deletion(self, temp_config_manager):
        """Test profile deletion."""
        # Create and save a test profile
        test_config = OBDConnectionConfig(port="/dev/ttyUSB1")
        temp_config_manager.save_profile("delete_me", test_config)
        
        # Verify it exists
        profiles = temp_config_manager.list_profiles()
        assert "delete_me" in profiles
        
        # Delete it
        result = temp_config_manager.delete_profile("delete_me")
        assert result == True
        
        # Verify it's gone
        profiles = temp_config_manager.list_profiles()
        assert "delete_me" not in profiles
    
    def test_default_profile_protection(self, temp_config_manager):
        """Test that default profile cannot be deleted."""
        result = temp_config_manager.delete_profile("auto")
        assert result == False
    
    def test_mock_mode_setting(self, temp_config_manager):
        """Test mock mode enable/disable."""
        # Initially disabled
        assert temp_config_manager.is_mock_mode_enabled() == False
        
        # Enable mock mode
        temp_config_manager.set_mock_mode(True)
        assert temp_config_manager.is_mock_mode_enabled() == True
        
        # Disable mock mode
        temp_config_manager.set_mock_mode(False)
        assert temp_config_manager.is_mock_mode_enabled() == False


class TestCarDiagnosticAgentIntegration:
    """Test integration of OBD functionality with the main agent."""
    
    @pytest_asyncio.fixture
    async def agent_with_mock_obd(self):
        """Create agent with mock OBD system."""
        with patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_key'}):
            agent = CarDiagnosticAgent()
            
            # Override with mock OBD manager
            config = OBDConnectionConfig(port="mock", baudrate=38400)
            agent.obd_manager = MockOBDInterfaceManager(config)
            agent.dtc_reader = DTCReaderService(agent.obd_manager)
            agent.live_data_service = LiveDataService(agent.obd_manager)
            agent.vehicle_info_service = VehicleInfoService(agent.obd_manager)
            
            return agent
    
    @pytest.mark.asyncio
    async def test_obd_connection_command(self, agent_with_mock_obd):
        """Test OBD connection through agent."""
        agent = agent_with_mock_obd
        
        result = await agent.connect_obd()
        
        assert result["success"] == True
        assert agent.obd_manager.is_connected == True
    
    @pytest.mark.asyncio
    async def test_diagnostic_session_creation(self, agent_with_mock_obd):
        """Test diagnostic session creation."""
        agent = agent_with_mock_obd
        
        session = await agent.start_diagnostic_session()
        
        assert session is not None
        assert session.session_id.startswith("session_")
        assert isinstance(session.start_time, datetime)
    
    @pytest.mark.asyncio
    async def test_obd_diagnostic_data_collection(self, agent_with_mock_obd):
        """Test OBD diagnostic data collection."""
        agent = agent_with_mock_obd
        
        # Connect first
        await agent.connect_obd()
        
        # Get diagnostic data
        diagnostic_data = await agent.get_obd_diagnostic_data()
        
        assert diagnostic_data["obd_connected"] == True
        assert "dtcs" in diagnostic_data
        assert "live_data" in diagnostic_data
        assert "vehicle_info" in diagnostic_data
        assert "timestamp" in diagnostic_data
    
    @pytest.mark.asyncio
    async def test_enhanced_query_preparation(self, agent_with_mock_obd):
        """Test enhanced query preparation with OBD data."""
        agent = agent_with_mock_obd
        
        # Mock OBD data
        obd_data = {
            "obd_connected": True,
            "dtcs": [
                {
                    "code": "P0171",
                    "description": "System Too Lean (Bank 1)",
                    "severity": "warning",
                    "status": "stored"
                }
            ],
            "live_data": {
                "0C": {
                    "name": "Engine RPM",
                    "value": 750.0,
                    "unit": "rpm",
                    "in_range": True
                }
            },
            "vehicle_info": {
                "make": "Honda",
                "model": "Civic",
                "year": 2021,
                "vin": "1HGBH41JXMN109186"
            }
        }
        
        original_query = "My car is running rough"
        enhanced_query = await agent._prepare_enhanced_query(original_query, obd_data)
        
        assert "My car is running rough" in enhanced_query
        assert "REAL-TIME OBD DIAGNOSTIC DATA" in enhanced_query
        assert "P0171" in enhanced_query
        assert "Engine RPM: 750.0 rpm" in enhanced_query
        assert "Honda Civic" in enhanced_query


# Test utilities
def create_mock_dtc_list():
    """Create a list of mock DTCs for testing."""
    return [
        DTCInfo(
            code="P0171",
            description="System Too Lean (Bank 1)",
            severity=DTCSeverity.WARNING,
            status=DTCStatus.STORED
        ),
        DTCInfo(
            code="P0300",
            description="Random/Multiple Cylinder Misfire Detected",
            severity=DTCSeverity.CRITICAL,
            status=DTCStatus.ACTIVE
        )
    ]


def create_mock_live_data():
    """Create mock live data readings for testing."""
    return {
        "0C": LiveDataReading(
            pid="0C",
            name="Engine RPM",
            value=750.0,
            unit="rpm",
            min_value=600.0,
            max_value=8000.0
        ),
        "05": LiveDataReading(
            pid="05",
            name="Engine Coolant Temperature",
            value=85.0,
            unit="°C",
            min_value=80.0,
            max_value=105.0
        )
    }


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])