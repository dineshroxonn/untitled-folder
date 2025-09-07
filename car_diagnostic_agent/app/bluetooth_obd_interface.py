"""
Bluetooth-Aware OBD Interface Manager

This module provides an OBD interface manager that handles Bluetooth
pairing and connection for OBD adapters before establishing the OBD connection.
"""

import asyncio
import logging
import obd
import serial
import subprocess
import time
from typing import Optional, List, Dict, Any
from datetime import datetime

from .enhanced_obd_interface import PersistentOBDInterfaceManager, OBDConnectionConfig, OBDResponse
from .obd_models import OBDProtocol

logger = logging.getLogger(__name__)


class BluetoothOBDInterfaceManager(PersistentOBDInterfaceManager):
    """
    Bluetooth-Aware OBD Interface Manager.
    
    This manager handles Bluetooth pairing and connection for OBD adapters
    before establishing the OBD connection, using the same approach as mobile apps.
    """
    
    def __init__(self, config: Optional[OBDConnectionConfig] = None):
        """
        Initialize the Bluetooth-Aware OBD Interface Manager.
        
        Args:
            config: Optional OBD connection configuration
        """
        super().__init__(config)
        self.bluetooth_address = "00:10:CC:4F:36:03"  # Default OBD adapter address
        self.bluetooth_connected = False
        
    def _is_bluetooth_available(self) -> bool:
        """Check if Bluetooth utilities are available."""
        try:
            result = subprocess.run(['which', 'blueutil'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
    
    def _is_obd_paired(self) -> bool:
        """Check if OBD device is paired."""
        try:
            result = subprocess.run(['blueutil', '--paired'], 
                                  capture_output=True, text=True)
            return self.bluetooth_address.lower().replace(':', '-') in result.stdout.lower()
        except Exception as e:
            logger.warning(f"Error checking if OBD is paired: {e}")
            return False
    
    def _connect_bluetooth_device(self) -> bool:
        """Connect to the Bluetooth OBD device."""
        try:
            logger.info(f"Connecting to Bluetooth OBD device {self.bluetooth_address}")
            
            # Connect to the device
            result = subprocess.run(['blueutil', '--connect', self.bluetooth_address], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("Bluetooth connection established")
                time.sleep(2)  # Wait for connection to stabilize
                self.bluetooth_connected = True
                return True
            else:
                logger.error(f"Failed to connect to Bluetooth device: {result.stderr}")
                self.bluetooth_connected = False
                return False
                
        except Exception as e:
            logger.error(f"Error connecting to Bluetooth device: {e}")
            self.bluetooth_connected = False
            return False
    
    def _ensure_bluetooth_connection(self) -> bool:
        """Ensure Bluetooth connection to OBD device is established."""
        # Check if Bluetooth utilities are available
        if not self._is_bluetooth_available():
            logger.warning("Bluetooth utilities not available")
            return False
        
        # Check if device is paired
        if not self._is_obd_paired():
            logger.warning("OBD device not paired")
            return False
        
        # Connect to the device
        return self._connect_bluetooth_device()
    
    async def _establish_connection(self):
        """Internal method to establish OBD connection with Bluetooth handling."""
        # First ensure Bluetooth connection
        if not self._ensure_bluetooth_connection():
            logger.warning("Could not establish Bluetooth connection, proceeding with direct connection")
        
        # Then establish OBD connection using parent method
        await super()._establish_connection()
    
    async def connect(self, config: Optional[OBDConnectionConfig] = None) -> OBDResponse:
        """
        Establish persistent connection to OBD-II adapter with Bluetooth handling.
        
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
                # Attempt connection with Bluetooth handling
                await self._establish_connection()
                
                # Start keep-alive and monitoring tasks
                await self._start_persistent_tasks()
                
                logger.info("Successfully connected to OBD adapter with Bluetooth support")
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
    
    async def disconnect(self) -> OBDResponse:
        """
        Disconnect from OBD-II adapter and stop persistent tasks.
        
        Returns:
            OBDResponse indicating disconnection status
        """
        # First disconnect OBD connection using parent method
        result = await super().disconnect()
        
        # Then disconnect Bluetooth if needed
        if self.bluetooth_connected:
            try:
                subprocess.run(['blueutil', '--disconnect', self.bluetooth_address], 
                             capture_output=True)
                self.bluetooth_connected = False
                logger.info("Bluetooth device disconnected")
            except Exception as e:
                logger.warning(f"Error disconnecting Bluetooth device: {e}")
        
        return result


# Backward compatibility alias
class BluetoothAwareOBDInterfaceManager(BluetoothOBDInterfaceManager):
    """Backward compatibility alias."""
    pass