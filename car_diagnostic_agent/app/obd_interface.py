"""
OBD Interface Manager for Car Diagnostic Agent.

This module provides the central OBD interface management functionality including
connection handling, protocol negotiation, and communication with OBD-II adapters.
"""

import asyncio
import logging
import obd
import serial
from typing import Optional, List, Dict, Any
from datetime import datetime
from unittest.mock import MagicMock

from .obd_models import (
    OBDConnectionConfig, 
    OBDProtocol, 
    OBDResponse, 
    DTCInfo, 
    LiveDataReading,
    VehicleInfo,
    DiagnosticSession
)

logger = logging.getLogger(__name__)


class OBDConnectionError(Exception):
    """Exception raised when OBD connection fails."""
    pass


class OBDProtocolError(Exception):
    """Exception raised when OBD protocol communication fails."""
    pass


class OBDInterfaceManager:
    """
    Central manager for OBD-II connections and communication.
    
    Handles connection lifecycle, protocol negotiation, and provides
    a unified interface for OBD operations across different adapters.
    """
    
    def __init__(self, config: Optional[OBDConnectionConfig] = None):
        """
        Initialize the OBD Interface Manager.
        
        Args:
            config: Optional OBD connection configuration
        """
        # If config is a dictionary, convert it to OBDConnectionConfig
        if isinstance(config, dict):
            from .obd_models import OBDConnectionConfig, OBDProtocol
            # Convert protocol string to enum if needed
            protocol = config.get("protocol", "auto")
            if isinstance(protocol, str):
                try:
                    protocol = OBDProtocol(protocol)
                except ValueError:
                    protocol = OBDProtocol.AUTO
            
            self.config = OBDConnectionConfig(
                port=config.get("port", "auto"),
                baudrate=config.get("baudrate", 38400),
                timeout=config.get("timeout", 30.0),
                protocol=protocol,
                auto_detect=config.get("auto_detect", True),
                max_retries=config.get("max_retries", 3)
            )
        else:
            self.config = config or OBDConnectionConfig(port="auto")
            
        self._connection: Optional[obd.OBD] = None
        self._is_connected = False
        self._supported_commands: List[obd.OBDCommand] = []
        self._connection_lock = asyncio.Lock()
        
    @property
    def is_connected(self) -> bool:
        """Check if OBD connection is active."""
        return self._is_connected and self._connection is not None
    
    async def connect(self, config: Optional[OBDConnectionConfig] = None) -> OBDResponse:
        """
        Establish connection to OBD-II adapter.
        
        Args:
            config: Optional configuration override (can be dict or OBDConnectionConfig)
            
        Returns:
            OBDResponse indicating connection success/failure
        """
        async with self._connection_lock:
            if config:
                # If config is a dictionary, convert it to OBDConnectionConfig
                if isinstance(config, dict):
                    # Convert protocol string to enum if needed
                    protocol = config.get("protocol", "auto")
                    if isinstance(protocol, str):
                        try:
                            protocol = OBDProtocol(protocol)
                        except ValueError:
                            protocol = OBDProtocol.AUTO
                    
                    self.config = OBDConnectionConfig(
                        port=config.get("port", "auto"),
                        baudrate=config.get("baudrate", 38400),
                        timeout=config.get("timeout", 30.0),
                        protocol=protocol,
                        auto_detect=config.get("auto_detect", True),
                        max_retries=config.get("max_retries", 3)
                    )
                else:
                    self.config = config
                
            try:
                await self._attempt_connection()
                return OBDResponse(
                    success=True,
                    data={"status": "connected", "protocol": str(self._connection.protocol_name())},
                    timestamp=datetime.now()
                )
            except Exception as e:
                logger.error(f"Failed to connect to OBD adapter: {e}")
                return OBDResponse(
                    success=False,
                    data=None,
                    error_message=str(e),
                    timestamp=datetime.now()
                )
    
    async def _attempt_connection(self):
        """Internal method to attempt OBD connection."""
        # Determine port
        port = self.config.port
        if port == "auto":
            port = None  # Let obd library auto-detect
            
        # Map protocol enum to obd library protocol
        protocol_map = {
            OBDProtocol.AUTO: None,
            OBDProtocol.SAE_J1850_PWM: obd.protocols.SAE_J1850_PWM,
            OBDProtocol.SAE_J1850_VPW: obd.protocols.SAE_J1850_VPW,
            OBDProtocol.ISO_14230_4: obd.protocols.ISO_14230_4_5baud,  # Use the correct protocol name
            OBDProtocol.ISO_15765_4: obd.protocols.ISO_15765_4_11bit_500k,  # Use a common CAN protocol
            OBDProtocol.ISO_9141_2: obd.protocols.ISO_9141_2,
        }
        
        protocol = protocol_map.get(self.config.protocol)
        
        # Attempt connection in a thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        self._connection = await loop.run_in_executor(
            None,
            lambda: obd.OBD(
                portstr=port,
                baudrate=self.config.baudrate,
                protocol=protocol,
                fast=False,
                timeout=self.config.timeout
            )
        )
        
        if not self._connection.is_connected():
            raise OBDConnectionError("Failed to establish OBD connection")
            
        self._is_connected = True
        
        # Cache supported commands
        self._supported_commands = list(self._connection.supported_commands)
        logger.info(f"Connected to OBD adapter on {self._connection.port_name()}")
        logger.info(f"Protocol: {self._connection.protocol_name()}")
        logger.info(f"Supported commands: {len(self._supported_commands)}")
    
    async def disconnect(self) -> OBDResponse:
        """
        Disconnect from OBD-II adapter.
        
        Returns:
            OBDResponse indicating disconnection status
        """
        async with self._connection_lock:
            try:
                if self._connection:
                    self._connection.close()
                self._connection = None
                self._is_connected = False
                self._supported_commands = []
                
                return OBDResponse(
                    success=True,
                    data={"status": "disconnected"},
                    timestamp=datetime.now()
                )
            except Exception as e:
                logger.error(f"Error during disconnection: {e}")
                return OBDResponse(
                    success=False,
                    data=None,
                    error_message=str(e),
                    timestamp=datetime.now()
                )
    
    async def query(self, command: obd.OBDCommand) -> OBDResponse:
        """
        Execute an OBD command query.
        
        Args:
            command: OBD command to execute
            
        Returns:
            OBDResponse with query result
        """
        if not self.is_connected:
            return OBDResponse(
                success=False,
                data=None,
                error_message="Not connected to OBD adapter"
            )
        
        # Try up to 3 times with a small delay between attempts
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Execute query in thread pool to avoid blocking
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    self._connection.query,
                    command
                )
                
                if response.is_null():
                    # If this is not the last attempt, wait before retrying
                    if attempt < max_retries - 1:
                        await asyncio.sleep(0.1 * (attempt + 1))  # Exponential backoff
                        continue
                    return OBDResponse(
                        success=False,
                        data=None,
                        error_message=f"No data received for command {command.name}"
                    )
                
                return OBDResponse(
                    success=True,
                    data={
                        "command": command.name,
                        "value": response.value,
                        "unit": str(response.unit) if response.unit else None
                    },
                    timestamp=datetime.now()
                )
                
            except Exception as e:
                logger.error(f"Error executing OBD query {command.name} (attempt {attempt + 1}): {e}")
                # If this is not the last attempt, wait before retrying
                if attempt < max_retries - 1:
                    await asyncio.sleep(0.1 * (attempt + 1))  # Exponential backoff
                    continue
                return OBDResponse(
                    success=False,
                    data=None,
                    error_message=str(e)
                )
    
    async def get_supported_commands(self) -> List[obd.OBDCommand]:
        """
        Get list of supported OBD commands.
        
        Returns:
            List of supported OBD commands
        """
        return self._supported_commands.copy()
    
    async def get_supported_protocols(self) -> List[str]:
        """
        Get list of supported OBD protocols.
        
        Returns:
            List of protocol names
        """
        return [protocol.value for protocol in OBDProtocol]
    
    async def set_protocol(self, protocol: OBDProtocol) -> OBDResponse:
        """
        Set the OBD communication protocol.
        
        Args:
            protocol: Protocol to set
            
        Returns:
            OBDResponse indicating success/failure
        """
        if self.is_connected:
            # Need to reconnect with new protocol
            await self.disconnect()
            
        self.config.protocol = protocol
        return await self.connect()
    
    async def test_connection(self) -> OBDResponse:
        """
        Test the OBD connection by sending a basic query.
        
        Returns:
            OBDResponse with connection test result
        """
        if not self.is_connected:
            return OBDResponse(
                success=False,
                data=None,
                error_message="Not connected to OBD adapter"
            )
        
        # Try to get VIN as a connection test
        try:
            vin_command = obd.commands.VIN
            if vin_command in self._supported_commands:
                response = await self.query(vin_command)
                if response.success:
                    return OBDResponse(
                        success=True,
                        data={"test": "passed", "vin": response.data.get("value")},
                        timestamp=datetime.now()
                    )
            
            # Fallback: try engine RPM
            rpm_command = obd.commands.RPM
            if rpm_command in self._supported_commands:
                response = await self.query(rpm_command)
                return OBDResponse(
                    success=response.success,
                    data={"test": "passed" if response.success else "failed"},
                    error_message=response.error_message,
                    timestamp=datetime.now()
                )
            
            return OBDResponse(
                success=False,
                data=None,
                error_message="No testable commands available"
            )
            
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return OBDResponse(
                success=False,
                data=None,
                error_message=str(e)
            )
    
    async def get_connection_info(self) -> Dict[str, Any]:
        """
        Get information about the current OBD connection.
        
        Returns:
            Dictionary with connection information
        """
        if not self.is_connected:
            return {
                "connected": False,
                "port": None,
                "protocol": None,
                "supported_commands": 0
            }
        
        return {
            "connected": True,
            "port": self._connection.port_name(),
            "protocol": self._connection.protocol_name(),
            "supported_commands": len(self._supported_commands),
            "config": {
                "baudrate": self.config.baudrate,
                "timeout": self.config.timeout,
                "auto_detect": self.config.auto_detect
            }
        }
    
    async def query(self, command: obd.OBDCommand) -> OBDResponse:
        """Mock query that returns simulated data."""
        if not self.is_connected:
            return OBDResponse(
                success=False,
                data=None,
                error_message="Not connected to mock OBD adapter"
            )
        
        # Use simulation data if available
        if self._simulation_data and "obd_data" in self._simulation_data:
            obd_data = self._simulation_data["obd_data"]
            
            # Handle DTC commands
            if hasattr(command, 'name') and "DTC" in command.name.upper():
                dtcs = obd_data.get("dtcs", [])
                # Convert to format expected by OBD library
                dtc_values = [(dtc["code"], "") for dtc in dtcs]  # (code, description) tuples
                return OBDResponse(
                    success=True,
                    data={"command": command.name, "value": dtc_values, "unit": None},
                    timestamp=datetime.now()
                )
            
            # Handle live data commands
            elif hasattr(command, 'name') and command.name == "RPM":
                # Try to get from simulation, fallback to mock
                rpm_value = self._mock_live_data["RPM"]
                if "live_data" in obd_data and "0C" in obd_data["live_data"]:
                    rpm_value = obd_data["live_data"]["0C"]["value"]
                return OBDResponse(
                    success=True,
                    data={"command": command.name, "value": rpm_value, "unit": "rpm"},
                    timestamp=datetime.now()
                )
            
            elif hasattr(command, 'name') and command.name == "COOLANT_TEMP":
                # Try to get from simulation, fallback to mock
                temp_value = self._mock_live_data["COOLANT_TEMP"]
                if "live_data" in obd_data and "05" in obd_data["live_data"]:
                    temp_value = obd_data["live_data"]["05"]["value"]
                return OBDResponse(
                    success=True,
                    data={"command": command.name, "value": temp_value, "unit": "°C"},
                    timestamp=datetime.now()
                )
            
            elif hasattr(command, 'name') and command.name == "THROTTLE_POS":
                # Try to get from simulation, fallback to mock
                throttle_value = self._mock_live_data["THROTTLE_POS"]
                if "live_data" in obd_data and "11" in obd_data["live_data"]:
                    throttle_value = obd_data["live_data"]["11"]["value"]
                return OBDResponse(
                    success=True,
                    data={"command": command.name, "value": throttle_value, "unit": "%"},
                    timestamp=datetime.now()
                )
        
        # Fallback to original mock behavior
        command_name = command.name if hasattr(command, 'name') else str(command)
        
        if "DTC" in command_name.upper():
            return OBDResponse(
                success=True,
                data={"command": command_name, "value": self._mock_dtcs, "unit": None},
                timestamp=datetime.now()
            )
        elif "RPM" in command_name.upper():
            return OBDResponse(
                success=True,
                data={"command": command_name, "value": self._mock_live_data["RPM"], "unit": "rpm"},
                timestamp=datetime.now()
            )
        elif "SPEED" in command_name.upper():
            return OBDResponse(
                success=True,
                data={"command": command_name, "value": self._mock_live_data["SPEED"], "unit": "km/h"},
                timestamp=datetime.now()
            )
        else:
            # Generic mock response
            return OBDResponse(
                success=True,
                data={"command": command_name, "value": 42.0, "unit": "unit"},
                timestamp=datetime.now()
            )

    async def reconnect(self) -> OBDResponse:
        """
        Reconnect to the OBD adapter using current configuration.
        
        Returns:
            OBDResponse indicating reconnection status
        """
        await self.disconnect()
        return await self.connect()


class MockOBDInterfaceManager(OBDInterfaceManager):
    """
    Mock OBD Interface Manager for testing and development.
    
    Simulates OBD-II responses without requiring actual hardware.
    """
    
    def __init__(self, config: Optional[OBDConnectionConfig] = None):
        super().__init__(config)
        self._mock_dtcs = [
            "P0171", "P0174", "P0300", "P0301", "P0420"
        ]
        self._mock_live_data = {
            "RPM": 750.0,
            "SPEED": 0.0,
            "COOLANT_TEMP": 85.0,
            "INTAKE_TEMP": 25.0,
            "THROTTLE_POS": 0.0,
            "FUEL_LEVEL": 75.0
        }
        self._simulation_data = None
    
    async def connect(self, config: Optional[OBDConnectionConfig] = None) -> OBDResponse:
        """Mock connection that always succeeds."""
        if config:
            self.config = config
        
        # Create a mock connection object
        self._connection = MagicMock()
        self._connection.protocol_name.return_value = "mock_protocol"
        self._connection.port_name.return_value = "mock_port"
        self._connection.is_connected.return_value = True
        
        self._is_connected = True
        self._supported_commands = []  # Mock supported commands
        
        logger.info("Mock OBD connection established")
        
        return OBDResponse(
            success=True,
            data={"status": "connected", "protocol": "mock_protocol"},
            timestamp=datetime.now()
        )
    
    async def load_simulation_data(self, simulation_data: Dict[str, Any]):
        """
        Load simulation data into the mock OBD interface.
        
        Args:
            simulation_data: Dictionary containing simulated OBD data
        """
        self._simulation_data = simulation_data
        
        # Update mock DTCs from simulation
        if "obd_data" in simulation_data and "dtcs" in simulation_data["obd_data"]:
            self._mock_dtcs = [dtc["code"] for dtc in simulation_data["obd_data"]["dtcs"]]
        
        # Update mock live data from simulation
        if "obd_data" in simulation_data and "live_data" in simulation_data["obd_data"]:
            live_data = simulation_data["obd_data"]["live_data"]
            # Map OBD PIDs to mock data
            if "0C" in live_data:  # RPM
                self._mock_live_data["RPM"] = live_data["0C"]["value"]
            if "05" in live_data:  # Coolant Temp
                self._mock_live_data["COOLANT_TEMP"] = live_data["05"]["value"]
            if "11" in live_data:  # Throttle Position
                self._mock_live_data["THROTTLE_POS"] = live_data["11"]["value"]
    
    async def get_connection_info(self) -> Dict[str, Any]:
        """Override to provide mock connection info."""
        if not self.is_connected:
            return {
                "connected": False,
                "port": None,
                "protocol": None,
                "supported_commands": 0
            }
        
        # If we have simulation data, indicate it's simulated
        port_info = "simulated_car" if self._simulation_data else "mock_port"
        
        return {
            "connected": True,
            "port": port_info,
            "protocol": "mock_protocol", 
            "supported_commands": 25,
            "config": {
                "baudrate": self.config.baudrate,
                "timeout": self.config.timeout,
                "auto_detect": self.config.auto_detect
            }
        }
    
    async def load_simulation_data(self, simulation_data: Dict[str, Any]):
        """
        Load simulation data into the mock OBD interface.
        
        Args:
            simulation_data: Dictionary containing simulated OBD data
        """
        self._simulation_data = simulation_data
        
        # Update mock DTCs from simulation
        if "obd_data" in simulation_data and "dtcs" in simulation_data["obd_data"]:
            self._mock_dtcs = [dtc["code"] for dtc in simulation_data["obd_data"]["dtcs"]]
        
        # Update mock live data from simulation
        if "obd_data" in simulation_data and "live_data" in simulation_data["obd_data"]:
            live_data = simulation_data["obd_data"]["live_data"]
            # Map OBD PIDs to mock data
            if "0C" in live_data:  # RPM
                self._mock_live_data["RPM"] = live_data["0C"]["value"]
            if "05" in live_data:  # Coolant Temp
                self._mock_live_data["COOLANT_TEMP"] = live_data["05"]["value"]
            if "11" in live_data:  # Throttle Position
                self._mock_live_data["THROTTLE_POS"] = live_data["11"]["value"]