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
        
        self._keep_alive_task: Optional[asyncio.Task] = None
        self._keep_alive_interval = 30
        self._connection_monitor_task: Optional[asyncio.Task] = None
        self._monitor_interval = 10
        
        self._max_retries = 3
        self._retry_delay = 2
        self._auto_reconnect = True
        
    @property
    def is_connected(self) -> bool:
        return self._is_connected and self._connection is not None and self._connection.is_connected()
    
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
                self._supported_commands = list(self._connection.supported_commands)
                logger.info(f"Connected to OBD adapter on {self._connection.port_name()}")
                logger.info(f"Protocol: {self._connection.protocol_name()}")
                return
                
            except Exception as e:
                logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
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
    
    async def query(self, command: obd.OBDCommand) -> OBDResponse:
        if not self.is_connected:
            if self._auto_reconnect:
                reconnect_result = await self.reconnect()
                if not reconnect_result.success:
                    return OBDResponse(success=False, data=None, error_message="Not connected and reconnection failed")
            else:
                return OBDResponse(success=False, data=None, error_message="Not connected to OBD adapter")
        
        for attempt in range(3):
            try:
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(None, self._connection.query, command)
                
                if response.is_null():
                    if attempt < 2:
                        await asyncio.sleep(0.1 * (attempt + 1))
                        continue
                    return OBDResponse(success=False, data=None, error_message=f"No data for command {command.name}")
                
                return OBDResponse(
                    success=True,
                    data={"command": command.name, "value": response.value, "unit": str(response.unit) if response.unit else None},
                    timestamp=datetime.now()
                )
            except Exception as e:
                logger.error(f"Error executing query {command.name} (attempt {attempt + 1}): {e}")
                if attempt < 2:
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
            "config": self.config.dict()
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

    def _test_serial_connection(self, port: str, baudrate: int = 38400) -> bool:
        logger.info(f"🧪 Testing serial connection to {port} at {baudrate} baud...")
        try:
            with serial.Serial(port=port, baudrate=baudrate, timeout=3) as ser:
                time.sleep(1)
                ser.write(b"ATZ\r")
                time.sleep(2)
                resp = ser.read(ser.in_waiting or 128)
            if resp and any(x in resp.decode(errors='ignore').upper() for x in ['ELM', 'OK', '>']):
                logger.info("✅ ELM327 response detected. Serial test passed.")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Serial connection test failed: {e}")
            return False

    async def _establish_connection(self):
        if not sys.platform == "darwin":
            await super()._establish_connection()
            return

        logger.info("Starting macOS-specific OBD connection process...")
        loop = asyncio.get_event_loop()
        port = await loop.run_in_executor(None, self._find_obd_serial_port)

        if not port:
            raise OBDConnectionError("Could not find a valid OBD serial port on macOS.")

        is_valid = await loop.run_in_executor(None, self._test_serial_connection, port)
        if not is_valid:
            raise OBDConnectionError(f"Serial test failed for port {port}.")

        tty_port = port.replace('/dev/cu.', '/dev/tty.')
        self.config.port = tty_port
        self.config.baudrate = 38400
        
        await super()._establish_connection()