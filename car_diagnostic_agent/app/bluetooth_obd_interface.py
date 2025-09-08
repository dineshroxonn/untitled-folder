"""
Bluetooth-Aware OBD Interface Manager for macOS

This module provides a robust OBD interface manager that uses macOS-specific
features to automatically find, verify, and connect to Bluetooth OBD adapters.
It also includes a persistent connection manager to ensure stable communication.
"""

import asyncio
import logging
import obd
import serial
import serial.tools.list_ports
import subprocess
import time
import sys
from typing import Optional, List, Dict, Any
from datetime import datetime

from .obd_models import (
    OBDConnectionConfig, 
    OBDProtocol, 
    OBDResponse,
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
        self.config = config or OBDConnectionConfig(port="auto")
        self._connection: Optional[obd.OBD] = None
        self._is_connected = False
        self._supported_commands: List[obd.OBDCommand] = []
        self._connection_lock = asyncio.Lock()
        self._query_lock = asyncio.Lock()  # Add a lock for queries
        
        self._keep_alive_task: Optional[asyncio.Task] = None
        self._keep_alive_interval = 15
        self._connection_monitor_task: Optional[asyncio.Task] = None
        self._monitor_interval = 5
        
        self._max_retries = 2
        self._retry_delay = 0.5
        self._auto_reconnect = True
        
    @property
    def is_connected(self) -> bool:
        # Check if we think we're connected
        if not self._is_connected or self._connection is None:
            logger.debug("Not connected: _is_connected is False or _connection is None")
            return False
            
        # Check if the connection object thinks it's connected
        try:
            connected = self._connection.is_connected()
            if not connected:
                logger.debug("Not connected: _connection.is_connected() returned False")
                return False
        except Exception as e:
            logger.debug(f"Error checking connection status: {e}")
            return False
            
        logger.debug(f"Connection appears to be alive")
        return True
    
    async def connect(self, config: Optional[OBDConnectionConfig] = None) -> OBDResponse:
        async with self._connection_lock:
            if self.is_connected:
                logger.info("Already connected to OBD adapter")
                return OBDResponse(
                    success=True,
                    data={"status": "already_connected", "protocol": str(self._connection.protocol_name())},
                    timestamp=datetime.now()
                )
            
            if config:
                self._update_config(config)
            
            try:
                await self._establish_connection()
                await self._start_persistent_tasks()
                logger.info("Successfully connected to OBD adapter with persistent connection")
                return OBDResponse(
                    success=True,
                    data={"status": "connected", "protocol": str(self._connection.protocol_name())},
                    timestamp=datetime.now()
                )
            except Exception as e:
                logger.error(f"Failed to connect to OBD adapter: {e}")
                return OBDResponse(success=False, data=None, error_message=str(e), timestamp=datetime.now())
    
    def _update_config(self, config):
        if isinstance(config, dict):
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
        for attempt in range(self._max_retries):
            try:
                port = self.config.port if self.config.port != "auto" else None
                protocol_map = {
                    OBDProtocol.AUTO: None,
                    OBDProtocol.SAE_J1850_PWM: obd.protocols.SAE_J1850_PWM,
                    OBDProtocol.SAE_J1850_VPW: obd.protocols.SAE_J1850_VPW,
                    OBDProtocol.ISO_14230_4: obd.protocols.ISO_14230_4_5baud,
                    OBDProtocol.ISO_15765_4: obd.protocols.ISO_15765_4_11bit_500k,
                    OBDProtocol.ISO_9141_2: obd.protocols.ISO_9141_2,
                }
                protocol = protocol_map.get(self.config.protocol)
                
                logger.info(f"Attempting to establish OBD connection - Attempt {attempt + 1}")
                logger.info(f"Port: {port}, Baudrate: {self.config.baudrate}, Protocol: {protocol}")
                
                loop = asyncio.get_event_loop()
                self._connection = await loop.run_in_executor(
                    None,
                    lambda: obd.OBD(
                        portstr=port,
                        baudrate=self.config.baudrate,
                        protocol=protocol,
                        fast=False,
                        timeout=10.0  # Increased from 5 seconds
                    )
                )
                
                logger.info(f"OBD connection object created: {self._connection}")
                logger.info(f"OBD connection status: {self._connection.is_connected()}")
                
                if not self._connection.is_connected():
                    raise OBDConnectionError("Failed to establish OBD connection")
                    
                self._is_connected = True
                self._supported_commands = list(self._connection.supported_commands)
                logger.info(f"Connected to OBD adapter on {self._connection.port_name()}")
                logger.info(f"Protocol: {self._connection.protocol_name()}")
                return
                
            except Exception as e:
                logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
                logger.exception("Exception details:")
                if attempt < self._max_retries - 1:
                    await asyncio.sleep(self._retry_delay * (attempt + 1))
                else:
                    raise
    
    async def _start_persistent_tasks(self):
        await self._stop_persistent_tasks()
        self._keep_alive_task = asyncio.create_task(self._keep_alive_worker())
        self._connection_monitor_task = asyncio.create_task(self._connection_monitor_worker())
    
    async def _stop_persistent_tasks(self):
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
        while True:
            try:
                if self.is_connected:
                    await self._send_keep_alive_command()
                await asyncio.sleep(self._keep_alive_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Keep-alive worker error: {e}")
                await asyncio.sleep(self._keep_alive_interval)
    
    async def _send_keep_alive_command(self):
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._connection.query, obd.commands.ELM_VERSION)
        except Exception as e:
            logger.warning(f"Keep-alive command failed: {e}")
            self._is_connected = False
    
    async def _connection_monitor_worker(self):
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
        async with self._connection_lock:
            try:
                await self._stop_persistent_tasks()
                if self._connection:
                    self._connection.close()
                self._connection = None
                self._is_connected = False
                self._supported_commands = []
                logger.info("Successfully disconnected from OBD adapter")
                return OBDResponse(success=True, data={"status": "disconnected"}, timestamp=datetime.now())
            except Exception as e:
                logger.error(f"Error during disconnection: {e}")
                return OBDResponse(success=False, data=None, error_message=str(e), timestamp=datetime.now())
    
    async def _test_connection_health(self) -> bool:
        """Test if the connection is still healthy by sending a simple command."""
        if not self._connection:
            return False
            
        try:
            # Send a simple command to test connection
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, self._connection.query, obd.commands.ELM_VERSION)
            return response is not None and not response.is_null()
        except Exception as e:
            logger.debug(f"Connection health test failed: {e}")
            return False

    async def query(self, command: obd.OBDCommand) -> OBDResponse:
        logger.info(f"Querying OBD command: {command.name}")
        if not self.is_connected:
            logger.warning("Not connected to OBD adapter")
            if self._auto_reconnect:
                reconnect_result = await self.reconnect()
                if not reconnect_result.success:
                    logger.error("Reconnection failed")
                    return OBDResponse(success=False, data=None, error_message="Not connected and reconnection failed")
            else:
                return OBDResponse(success=False, data=None, error_message="Not connected to OBD adapter")
        
        # Test connection health before executing the main query
        if not await self._test_connection_health():
            logger.warning("Connection health check failed, attempting to reconnect")
            if self._auto_reconnect:
                reconnect_result = await self.reconnect()
                if not reconnect_result.success:
                    logger.error("Reconnection failed")
                    return OBDResponse(success=False, data=None, error_message="Connection lost and reconnection failed")
        
        for attempt in range(2):  # Reduced from 3
            try:
                logger.info(f"Executing query attempt {attempt + 1}")
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(None, self._connection.query, command)
                logger.info(f"Query response: {response}")
                
                if response.is_null():
                    logger.warning(f"Null response for command {command.name}")
                    if attempt < 1:  # Reduced from 2
                        await asyncio.sleep(0.1 * (attempt + 1))
                        continue
                    return OBDResponse(success=False, data=None, error_message=f"No data for command {command.name}")
                
                return OBDResponse(
                    success=True,
                    data={"command": command.name, "value": response.value, "unit": str(response.unit) if response.unit else None},
                    timestamp=datetime.now()
                )
            except (OSError, serial.SerialException) as e:
                logger.error(f"Serial error executing query {command.name} (attempt {attempt + 1}): {e}")
                # Mark connection as disconnected due to serial error
                self._is_connected = False
                if self._connection:
                    try:
                        self._connection.close()
                    except:
                        pass
                    self._connection = None
                
                # Try to reconnect if this is the first attempt
                if attempt < 1 and self._auto_reconnect:
                    logger.info("Attempting to reconnect after serial error")
                    reconnect_result = await self.reconnect()
                    if reconnect_result.success:
                        logger.info("Reconnection successful, retrying query")
                        continue
                    else:
                        logger.error("Reconnection failed")
                        return OBDResponse(success=False, data=None, error_message=f"Connection lost and reconnection failed: {str(e)}")
                else:
                    return OBDResponse(success=False, data=None, error_message=f"Serial error: {str(e)}")
            except Exception as e:
                logger.error(f"Error executing query {command.name} (attempt {attempt + 1}): {e}")
                logger.exception("Exception details:")
                if attempt < 1:  # Reduced from 2
                    await asyncio.sleep(0.1 * (attempt + 1))
                    continue
                return OBDResponse(success=False, data=None, error_message=str(e))
    
    async def get_supported_commands(self) -> List[obd.OBDCommand]:
        return self._supported_commands.copy()
    
    async def get_connection_info(self) -> Dict[str, Any]:
        if not self.is_connected:
            return {"connected": False, "port": None, "protocol": None, "supported_commands": 0}
        
        return {
            "connected": True,
            "port": self._connection.port_name(),
            "protocol": self._connection.protocol_name(),
            "supported_commands": len(self._supported_commands),
            "config": {
                "port": self.config.port,
                "baudrate": self.config.baudrate,
                "timeout": self.config.timeout,
                "protocol": self.config.protocol.value if self.config.protocol else None,
                "auto_detect": self.config.auto_detect,
                "max_retries": self.config.max_retries
            }
        }
    
    async def reconnect(self) -> OBDResponse:
        logger.info("Attempting to reconnect to OBD adapter")
        await self.disconnect()
        return await self.connect()


class BluetoothOBDInterfaceManager(PersistentOBDInterfaceManager):
    """
    macOS-optimized OBD Interface Manager for Bluetooth adapters.
    """
    
    def __init__(self, config: Optional[OBDConnectionConfig] = None):
        super().__init__(config)

    def _scan_bluetooth_devices(self) -> List[Dict[str, str]]:
        logger.info("🔍 Scanning for Bluetooth OBD devices...")
        try:
            result = subprocess.run(['system_profiler', 'SPBluetoothDataType'], capture_output=True, text=True, timeout=15)
            if result.returncode != 0:
                return []
            lines = result.stdout.split('\n')
            obd_devices, current = [], {}
            in_section = False
            for line in lines:
                line = line.strip()
                if not line: continue
                if 'Devices' in line and ('Paired' in line or 'Connected' in line):
                    in_section = True
                    continue
                if in_section:
                    if 'Device Name:' in line:
                        if current and self._is_obd_device(current.get('name', '')):
                            obd_devices.append(current)
                        current = {'name': line.split(':',1)[1].strip(), 'address': '', 'connected': False}
                    elif 'Device Address:' in line and current:
                        current['address'] = line.split(':',1)[1].strip()
                    elif 'Connected:' in line and current:
                        current['connected'] = 'yes' in line.split(':',1)[1].strip().lower()
            if current and self._is_obd_device(current.get('name', '')):
                obd_devices.append(current)
            return obd_devices
        except Exception as e:
            logger.error(f"❌ Error scanning Bluetooth devices: {e}")
            return []

    def _is_obd_device(self, name: str) -> bool:
        return any(k in name.upper() for k in ['OBD', 'ELM327', 'OBDII', 'BLUE DRIVER', 'VGATE'])

    def _find_obd_serial_port(self) -> Optional[str]:
        logger.info("🔍 Looking for OBD serial port...")
        try:
            ports = list(serial.tools.list_ports.comports())
            for p in ports:
                is_obd = any(k in (p.description or "").upper() or k in p.device.upper() for k in ['OBD', 'ELM327', 'BLUETOOTH'])
                if is_obd and 'INCOMING-PORT' not in p.device.upper():
                    logger.info(f"✅ Found likely OBD port: {p.device}")
                    return p.device
        except Exception as e:
            logger.error(f"❌ Error scanning serial ports: {e}")
        return None

    async def _establish_connection(self):
        if not sys.platform == "darwin":
            await super()._establish_connection()
            return

        logger.info("Starting macOS-specific OBD connection process...")
        loop = asyncio.get_event_loop()
        port = await loop.run_in_executor(None, self._find_obd_serial_port)

        if not port:
            raise OBDConnectionError("Could not find a valid OBD serial port on macOS.")

        logger.info(f"Found OBD port: {port}")

        # Add delay to ensure Bluetooth connection is fully established
        await asyncio.sleep(2)

        # Convert /dev/cu.* to /dev/tty.* for python-obd compatibility
        tty_port = port.replace('/dev/cu.', '/dev/tty.')
        self.config.port = tty_port
        self.config.baudrate = 38400
        
        logger.info(f"Calling super()._establish_connection() with port: {self.config.port}")
        await super()._establish_connection()
        logger.info("Finished super()._establish_connection()")