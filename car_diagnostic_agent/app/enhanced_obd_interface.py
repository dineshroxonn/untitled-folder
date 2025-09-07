"""
Enhanced OBD Interface Manager with Persistent Connection Support

This module provides an enhanced OBD interface manager that maintains
persistent connections and implements connection recovery mechanisms.
It also handles Bluetooth pairing and connection for OBD adapters.
"""

import asyncio
import logging
import obd
import serial
import threading
import time
import subprocess
import os
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


class PersistentOBDInterfaceManager:
    """
    Enhanced OBD Interface Manager with persistent connection support.
    
    This manager maintains a persistent connection to the OBD-II adapter
    and implements automatic reconnection and keep-alive mechanisms.
    """
    
    def __init__(self, config: Optional[OBDConnectionConfig] = None):
        """
        Initialize the Persistent OBD Interface Manager.
        
        Args:
            config: Optional OBD connection configuration
        """
        self.config = config or OBDConnectionConfig(port="auto")
        self._connection: Optional[obd.OBD] = None
        self._is_connected = False
        self._supported_commands: List[obd.OBDCommand] = []
        self._connection_lock = asyncio.Lock()
        
        # Persistent connection management
        self._keep_alive_task: Optional[asyncio.Task] = None
        self._keep_alive_interval = 30  # seconds
        self._connection_monitor_task: Optional[asyncio.Task] = None
        self._monitor_interval = 10  # seconds
        
        # Connection recovery
        self._max_retries = 3
        self._retry_delay = 2  # seconds
        self._auto_reconnect = True
        
    @property
    def is_connected(self) -> bool:
        """Check if OBD connection is active."""
        return self._is_connected and self._connection is not None and self._connection.is_connected()
    
    async def connect(self, config: Optional[OBDConnectionConfig] = None) -> OBDResponse:
        """
        Establish persistent connection to OBD-II adapter.
        
        Args:
            config: Optional configuration override
            
        Returns:
            OBDResponse indicating connection success/failure
        """
        async with self._connection_lock:
            # If already connected with a valid connection, return success
            if self.is_connected:
                logger.info("Already connected to OBD adapter")
                return OBDResponse(
                    success=True,
                    data={"status": "already_connected", "protocol": str(self._connection.protocol_name())},
                    timestamp=datetime.now()
                )
            
            # Update config if provided
            if config:
                self._update_config(config)
            
            try:
                # Attempt connection
                await self._establish_connection()
                
                # Start keep-alive and monitoring tasks
                await self._start_persistent_tasks()
                
                logger.info("Successfully connected to OBD adapter with persistent connection")
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
    
    def _update_config(self, config):
        """Update configuration from various input types."""
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
    
    async def _establish_connection(self):
        """Internal method to establish OBD connection with retry logic."""
        for attempt in range(self._max_retries):
            try:
                # Determine port
                port = self.config.port
                if port == "auto":
                    port = None  # Let obd library auto-detect
                    
                # Map protocol enum to obd library protocol
                protocol_map = {
                    OBDProtocol.AUTO: None,
                    OBDProtocol.SAE_J1850_PWM: obd.protocols.SAE_J1850_PWM,
                    OBDProtocol.SAE_J1850_VPW: obd.protocols.SAE_J1850_VPW,
                    OBDProtocol.ISO_14230_4: obd.protocols.ISO_14230_4_5baud,
                    OBDProtocol.ISO_15765_4: obd.protocols.ISO_15765_4_11bit_500k,
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
                
                return  # Success, exit retry loop
                
            except Exception as e:
                logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < self._max_retries - 1:
                    await asyncio.sleep(self._retry_delay * (attempt + 1))  # Exponential backoff
                else:
                    raise  # Re-raise the last exception
    
    async def _start_persistent_tasks(self):
        """Start keep-alive and monitoring tasks."""
        # Cancel existing tasks if any
        await self._stop_persistent_tasks()
        
        # Start keep-alive task
        self._keep_alive_task = asyncio.create_task(self._keep_alive_worker())
        
        # Start connection monitor task
        self._connection_monitor_task = asyncio.create_task(self._connection_monitor_worker())
    
    async def _stop_persistent_tasks(self):
        """Stop all persistent tasks."""
        if self._keep_alive_task and not self._keep_alive_task.done():
            self._keep_alive_task.cancel()
            try:
                await self._keep_alive_task
            except asyncio.CancelledError:
                pass
        
        if self._connection_monitor_task and not self._connection_monitor_task.done():
            self._connection_monitor_task.cancel()
            try:
                await self._connection_monitor_task
            except asyncio.CancelledError:
                pass
    
    async def _keep_alive_worker(self):
        """Worker function to send periodic keep-alive commands."""
        while True:
            try:
                if self.is_connected:
                    # Send a simple command to keep connection alive
                    await self._send_keep_alive_command()
                await asyncio.sleep(self._keep_alive_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Keep-alive worker error: {e}")
                await asyncio.sleep(self._keep_alive_interval)
    
    async def _send_keep_alive_command(self):
        """Send a keep-alive command to maintain connection."""
        try:
            # Execute a lightweight command
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                self._connection.query,
                obd.commands.ELM_VERSION
            )
            logger.debug(f"Keep-alive command response: {response}")
        except Exception as e:
            logger.warning(f"Keep-alive command failed: {e}")
            # Mark connection as potentially broken
            self._is_connected = False
    
    async def _connection_monitor_worker(self):
        """Worker function to monitor connection status."""
        while True:
            try:
                if not self.is_connected and self._auto_reconnect:
                    logger.warning("Connection lost, attempting to reconnect...")
                    await self.reconnect()
                await asyncio.sleep(self._monitor_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Connection monitor error: {e}")
                await asyncio.sleep(self._monitor_interval)
    
    async def disconnect(self) -> OBDResponse:
        """
        Disconnect from OBD-II adapter and stop persistent tasks.
        
        Returns:
            OBDResponse indicating disconnection status
        """
        async with self._connection_lock:
            try:
                # Stop persistent tasks first
                await self._stop_persistent_tasks()
                
                # Close connection
                if self._connection:
                    self._connection.close()
                
                self._connection = None
                self._is_connected = False
                self._supported_commands = []
                
                logger.info("Successfully disconnected from OBD adapter")
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
        Execute an OBD command query with automatic reconnection.
        
        Args:
            command: OBD command to execute
            
        Returns:
            OBDResponse with query result
        """
        # Check connection and attempt to reconnect if needed
        if not self.is_connected:
            if self._auto_reconnect:
                logger.info("Not connected, attempting to reconnect...")
                reconnect_result = await self.reconnect()
                if not reconnect_result.success:
                    return OBDResponse(
                        success=False,
                        data=None,
                        error_message="Not connected to OBD adapter and reconnection failed"
                    )
            else:
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
    
    async def reconnect(self) -> OBDResponse:
        """
        Reconnect to the OBD adapter using current configuration.
        
        Returns:
            OBDResponse indicating reconnection status
        """
        logger.info("Attempting to reconnect to OBD adapter")
        await self.disconnect()
        return await self.connect()


# Keep the original classes for backward compatibility
class OBDInterfaceManager(PersistentOBDInterfaceManager):
    """Backward compatibility alias."""
    pass


class MockOBDInterfaceManager:
    """
    Mock OBD Interface Manager for testing and development.
    
    Simulates OBD-II responses without requiring actual hardware.
    """
    
    def __init__(self, config: Optional[OBDConnectionConfig] = None):
        self.config = config or OBDConnectionConfig(port="mock")
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
        self._is_connected = False
        self._supported_commands = []  # Mock supported commands
    
    async def connect(self, config: Optional[OBDConnectionConfig] = None) -> OBDResponse:
        """Mock connection that always succeeds."""
        if config:
            self.config = config
        
        self._is_connected = True
        
        logger.info("Mock OBD connection established")
        
        return OBDResponse(
            success=True,
            data={"status": "connected", "protocol": "mock_protocol"},
            timestamp=datetime.now()
        )
    
    @property
    def is_connected(self) -> bool:
        """Check if mock connection is active."""
        return self._is_connected
    
    async def disconnect(self) -> OBDResponse:
        """Mock disconnection."""
        self._is_connected = False
        logger.info("Mock OBD connection closed")
        return OBDResponse(
            success=True,
            data={"status": "disconnected"},
            timestamp=datetime.now()
        )
    
    async def get_connection_info(self) -> Dict[str, Any]:
        """Override to provide mock connection info."""
        if not self.is_connected:
            return {
                "connected": False,
                "port": None,
                "protocol": None,
                "supported_commands": 0
            }
        
        return {
            "connected": True,
            "port": "mock_port",
            "protocol": "mock_protocol", 
            "supported_commands": 25,
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
        
        # Simulate different responses based on command
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
    
    async def get_supported_commands(self) -> List[obd.OBDCommand]:
        """Get mock supported commands."""
        return self._supported_commands.copy()
    
    async def reconnect(self) -> OBDResponse:
        """Mock reconnection."""
        await self.disconnect()
        return await self.connect()