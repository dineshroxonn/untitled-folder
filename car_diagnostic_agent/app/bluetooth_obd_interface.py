"""
Bluetooth-Aware OBD Interface Manager for macOS

This module provides a robust OBD interface manager that uses macOS-specific
features to automatically find, verify, and connect to Bluetooth OBD adapters.
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

from .enhanced_obd_interface import PersistentOBDInterfaceManager, OBDConnectionConfig, OBDResponse, OBDConnectionError
from .obd_models import OBDProtocol

logger = logging.getLogger(__name__)


class BluetoothOBDInterfaceManager(PersistentOBDInterfaceManager):
    """
    macOS-optimized OBD Interface Manager for Bluetooth adapters.
    
    This manager uses the logic from `mac_obd_connector.py` to provide a
    reliable, diagnostic-driven connection process on macOS.
    """
    
    def __init__(self, config: Optional[OBDConnectionConfig] = None):
        """
        Initialize the macOS Bluetooth OBD Interface Manager.
        
        Args:
            config: Optional OBD connection configuration
        """
        super().__init__(config)

    def _scan_bluetooth_devices(self) -> List[Dict[str, str]]:
        """Scans for Bluetooth devices using macOS's system_profiler."""
        logger.info("🔍 Scanning for Bluetooth OBD devices...")
        try:
            result = subprocess.run(
                ['system_profiler', 'SPBluetoothDataType'],
                capture_output=True, text=True, timeout=15
            )
            if result.returncode != 0:
                logger.warning("⚠️  Failed to get Bluetooth information from system_profiler")
                return []
            lines = result.stdout.split('\n')
            obd_devices, current = [], {}
            in_section = False
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if 'Devices' in line and ('Paired' in line or 'Connected' in line):
                    in_section = True
                    continue
                if in_section:
                    if 'Device Name:' in line:
                        if current and self._is_obd_device(current.get('name', '')):
                            obd_devices.append(current)
                        current = {
                            'name': line.split(':',1)[1].strip(),
                            'address': '',
                            'connected': False
                        }
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
        """Checks if a device name suggests it's an OBD scanner."""
        return any(k in name.upper() for k in ['OBD', 'ELM327', 'OBDII', 'BLUE DRIVER', 'VGATE'])

    def _scan_serial_ports(self) -> List[Dict[str, str]]:
        """Scans for serial ports using pyserial."""
        logger.info("🔌 Scanning for serial ports...")
        try:
            ports = list(serial.tools.list_ports.comports())
            result = []
            for p in ports:
                info = {
                    'device': p.device,
                    'description': p.description or "n/a",
                    'manufacturer': p.manufacturer or "Unknown",
                    'is_obd': self._is_obd_serial_port(p)
                }
                result.append(info)
            return result
        except Exception as e:
            logger.error(f"❌ Error scanning serial ports: {e}")
            return []

    def _is_obd_serial_port(self, port) -> bool:
        """Checks if a serial port is likely an OBD device."""
        name = port.device.upper()
        desc = (port.description or "").upper()
        patterns = ['OBD', 'ELM327', 'BLUETOOTH', 'USB SERIAL', 'FTDI', 'CH340', 'CP2102', 'PL2303']
        return any(pat in name or pat in desc for pat in patterns)

    def _find_obd_serial_port(self) -> Optional[str]:
        """Finds the most likely OBD serial port."""
        logger.info("🔍 Looking for OBD serial port...")
        ports = self._scan_serial_ports()
        for p in ports:
            dn = p['device'].upper()
            if p['is_obd'] and 'INCOMING-PORT' not in dn:
                logger.info(f"✅ Found likely OBD port: {p['device']}")
                return p['device']
        logger.warning("⚠️  No specific OBD port found; listing all:")
        for p in ports:
            logger.warning(f"  - {p['device']} ({'OBD' if p['is_obd'] else 'non-OBD'})")
        return None

    def _test_serial_connection(self, port: str, baudrate: int = 38400) -> bool:
        """Performs a low-level test of the serial connection."""
        logger.info(f"🧪 Testing serial connection to {port} at {baudrate} baud...")
        try:
            with serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=3,
                write_timeout=3,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS
            ) as ser:
                time.sleep(1)
                ser.reset_input_buffer()
                ser.write(b"ATZ\r")
                ser.flush()
                time.sleep(2)
                resp = ser.read(ser.in_waiting or 128)
            if resp and any(x in resp.decode(errors='ignore').upper() for x in ['ELM', 'OK', '>']):
                logger.info("✅ ELM327 response detected. Serial test passed.")
                return True
            logger.warning("⚠️  No valid ELM327 response received from serial test.")
            return False
        except Exception as e:
            logger.error(f"❌ Serial connection test failed: {e}")
            return False

    async def _establish_connection(self):
        """
        Internal method to establish OBD connection using the macOS-specific
        diagnostic-driven approach.
        """
        # This method is only for macOS with Bluetooth
        if not sys.platform == "darwin":
            logger.info("Not on macOS, falling back to default connection method.")
            await super()._establish_connection()
            return

        logger.info("Starting macOS-specific OBD connection process...")
        loop = asyncio.get_event_loop()

        # Run synchronous scanning methods in a thread pool executor
        self._scan_bluetooth_devices() # Run this to inform the user
        port = await loop.run_in_executor(None, self._find_obd_serial_port)

        if not port:
            raise OBDConnectionError("Could not find a valid OBD serial port on macOS.")

        # Run the serial test in the executor
        is_valid = await loop.run_in_executor(None, self._test_serial_connection, port)

        if not is_valid:
            raise OBDConnectionError(f"Serial test failed for port {port}. The device may not be a responsive ELM327 adapter.")

        # Crucial step: convert /dev/cu.* to /dev/tty.* for python-obd
        tty_port = port.replace('/dev/cu.', '/dev/tty.')
        logger.info(f"macOS fix: Using port '{tty_port}' for python-obd.")

        # Set the discovered and verified port in the config
        self.config.port = tty_port
        self.config.baudrate = 38400  # Use baudrate proven by mac_obd_connector.py

        # Now, call the parent's _establish_connection to do the actual python-obd connection
        logger.info("Handing off to parent class to establish final connection...")
        await super()._establish_connection()


# Backward compatibility alias
class BluetoothAwareOBDInterfaceManager(BluetoothOBDInterfaceManager):
    """Backward compatibility alias."""
    pass
