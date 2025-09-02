"""
OBD Services for Car Diagnostic Agent.

This module provides specialized services for reading DTCs, live data,
and vehicle information through the OBD-II interface.
"""

import asyncio
import logging
import obd
from datetime import datetime
from typing import List, Dict, Optional, Any

from .obd_interface import OBDInterfaceManager
from .obd_models import (
    DTCInfo, 
    DTCStatus, 
    DTCSeverity,
    LiveDataReading,
    VehicleInfo,
    ECUInfo,
    OBDResponse,
    COMMON_PIDS
)

logger = logging.getLogger(__name__)


class DTCReaderService:
    """
    Service for reading and managing Diagnostic Trouble Codes.
    
    Provides methods to read stored DTCs, pending DTCs, clear codes,
    and retrieve associated freeze frame data.
    """
    
    def __init__(self, obd_manager: OBDInterfaceManager):
        """
        Initialize DTC Reader Service.
        
        Args:
            obd_manager: OBD Interface Manager instance
        """
        self.obd_manager = obd_manager
        self._dtc_descriptions = self._load_dtc_descriptions()
    
    def _load_dtc_descriptions(self) -> Dict[str, str]:
        """Load DTC code descriptions."""
        # Basic DTC descriptions - in a real implementation, this would be loaded from a database
        return {
            "P0100": "Mass or Volume Air Flow Circuit Malfunction",
            "P0101": "Mass or Volume Air Flow Circuit Range/Performance Problem",
            "P0102": "Mass or Volume Air Flow Circuit Low Input",
            "P0103": "Mass or Volume Air Flow Circuit High Input",
            "P0171": "System Too Lean (Bank 1)",
            "P0172": "System Too Rich (Bank 1)",
            "P0174": "System Too Lean (Bank 2)",
            "P0175": "System Too Rich (Bank 2)",
            "P0300": "Random/Multiple Cylinder Misfire Detected",
            "P0301": "Cylinder 1 Misfire Detected",
            "P0302": "Cylinder 2 Misfire Detected",
            "P0303": "Cylinder 3 Misfire Detected",
            "P0304": "Cylinder 4 Misfire Detected",
            "P0420": "Catalyst System Efficiency Below Threshold (Bank 1)",
            "P0430": "Catalyst System Efficiency Below Threshold (Bank 2)",
            "P0442": "Evaporative Emission Control System Leak Detected (small leak)",
            "P0443": "Evaporative Emission Control System Purge Control Valve Circuit Malfunction",
            "P0500": "Vehicle Speed Sensor Malfunction",
            "P0505": "Idle Control System Malfunction",
            "P0506": "Idle Control System RPM Lower Than Expected",
            "P0507": "Idle Control System RPM Higher Than Expected",
        }
    
    async def read_stored_dtcs(self) -> List[DTCInfo]:
        """
        Read stored Diagnostic Trouble Codes.
        
        Returns:
            List of stored DTCInfo objects
        """
        if not self.obd_manager.is_connected:
            logger.warning("OBD not connected, cannot read DTCs")
            return []
        
        try:
            # Query for stored DTCs
            response = await self.obd_manager.query(obd.commands.GET_DTC)
            
            if not response.success:
                logger.error(f"Failed to read DTCs: {response.error_message}")
                return []
            
            dtcs = []
            dtc_data = response.data.get("value", [])
            
            if isinstance(dtc_data, list):
                for dtc_tuple in dtc_data:
                    if isinstance(dtc_tuple, tuple) and len(dtc_tuple) >= 2:
                        code = dtc_tuple[0]
                        description = self._dtc_descriptions.get(code, "Unknown DTC")
                        
                        dtc_info = DTCInfo(
                            code=code,
                            description=description,
                            severity=self._determine_severity(code),
                            status=DTCStatus.STORED,
                            timestamp=datetime.now()
                        )
                        dtcs.append(dtc_info)
            
            logger.info(f"Read {len(dtcs)} stored DTCs")
            return dtcs
            
        except Exception as e:
            logger.error(f"Error reading stored DTCs: {e}")
            return []
    
    async def read_pending_dtcs(self) -> List[DTCInfo]:
        """
        Read pending Diagnostic Trouble Codes.
        
        Returns:
            List of pending DTCInfo objects
        """
        if not self.obd_manager.is_connected:
            logger.warning("OBD not connected, cannot read pending DTCs")
            return []
        
        try:
            # Note: Pending DTCs might not be available in all OBD implementations
            # This is a simplified implementation
            pending_dtcs = []
            logger.info(f"Read {len(pending_dtcs)} pending DTCs")
            return pending_dtcs
            
        except Exception as e:
            logger.error(f"Error reading pending DTCs: {e}")
            return []
    
    async def clear_dtcs(self) -> OBDResponse:
        """
        Clear stored Diagnostic Trouble Codes.
        
        Returns:
            OBDResponse indicating success/failure
        """
        if not self.obd_manager.is_connected:
            return OBDResponse(
                success=False,
                data=None,
                error_message="OBD not connected"
            )
        
        try:
            # Clear DTCs command
            response = await self.obd_manager.query(obd.commands.CLEAR_DTC)
            
            if response.success:
                logger.info("DTCs cleared successfully")
                return OBDResponse(
                    success=True,
                    data={"status": "DTCs cleared"},
                    timestamp=datetime.now()
                )
            else:
                return OBDResponse(
                    success=False,
                    data=None,
                    error_message=response.error_message
                )
                
        except Exception as e:
            logger.error(f"Error clearing DTCs: {e}")
            return OBDResponse(
                success=False,
                data=None,
                error_message=str(e)
            )
    
    def _determine_severity(self, dtc_code: str) -> DTCSeverity:
        """
        Determine severity of a DTC based on the code.
        
        Args:
            dtc_code: DTC code string
            
        Returns:
            DTCSeverity level
        """
        # Critical DTCs (examples)
        critical_patterns = ["P0300", "P030", "P0420", "P0430"]  # Misfires, catalyst issues
        warning_patterns = ["P0171", "P0172", "P0174", "P0175"]  # Fuel system issues
        
        for pattern in critical_patterns:
            if dtc_code.startswith(pattern):
                return DTCSeverity.CRITICAL
        
        for pattern in warning_patterns:
            if dtc_code.startswith(pattern):
                return DTCSeverity.WARNING
        
        return DTCSeverity.INFO


class LiveDataService:
    """
    Service for reading real-time vehicle parameter data.
    
    Provides methods to monitor engine parameters, sensor readings,
    and other live data from the vehicle's ECU.
    """
    
    def __init__(self, obd_manager: OBDInterfaceManager):
        """
        Initialize Live Data Service.
        
        Args:
            obd_manager: OBD Interface Manager instance
        """
        self.obd_manager = obd_manager
        self._monitoring_active = False
        self._monitoring_task: Optional[asyncio.Task] = None
        self._data_callback = None
    
    async def read_parameter(self, pid: str) -> Optional[LiveDataReading]:
        """
        Read a single parameter by PID.
        
        Args:
            pid: Parameter ID to read
            
        Returns:
            LiveDataReading object or None if failed
        """
        if not self.obd_manager.is_connected:
            logger.warning("OBD not connected, cannot read parameter")
            return None
        
        try:
            # Map PID to OBD command
            command = self._get_command_for_pid(pid)
            if not command:
                logger.warning(f"No command found for PID {pid}")
                return None
            
            response = await self.obd_manager.query(command)
            
            if response.success:
                pid_info = COMMON_PIDS.get(pid, {"name": f"PID_{pid}", "unit": ""})
                
                return LiveDataReading(
                    pid=pid,
                    name=pid_info["name"],
                    value=float(response.data["value"]) if response.data["value"] is not None else 0.0,
                    unit=response.data.get("unit", pid_info["unit"]),
                    timestamp=datetime.now()
                )
            else:
                logger.error(f"Failed to read parameter {pid}: {response.error_message}")
                return None
                
        except Exception as e:
            logger.error(f"Error reading parameter {pid}: {e}")
            return None
    
    async def read_multiple_parameters(self, pids: List[str]) -> Dict[str, LiveDataReading]:
        """
        Read multiple parameters simultaneously.
        
        Args:
            pids: List of Parameter IDs to read
            
        Returns:
            Dictionary mapping PID to LiveDataReading
        """
        results = {}
        
        # Create tasks for concurrent reading
        tasks = []
        for pid in pids:
            task = asyncio.create_task(self.read_parameter(pid))
            tasks.append((pid, task))
        
        # Wait for all tasks to complete
        for pid, task in tasks:
            try:
                result = await task
                if result:
                    results[pid] = result
            except Exception as e:
                logger.error(f"Error reading parameter {pid}: {e}")
        
        return results
    
    async def get_basic_engine_data(self) -> Dict[str, LiveDataReading]:
        """
        Get basic engine parameters (RPM, coolant temp, throttle, etc.).
        
        Returns:
            Dictionary of basic engine data
        """
        basic_pids = ["0C", "05", "11", "0D", "0F", "10"]  # RPM, coolant, throttle, speed, intake temp, MAF
        return await self.read_multiple_parameters(basic_pids)
    
    async def start_monitoring(self, pids: List[str], interval: float = 1.0, callback=None):
        """
        Start continuous monitoring of specified parameters.
        
        Args:
            pids: List of Parameter IDs to monitor
            interval: Monitoring interval in seconds
            callback: Optional callback function for data updates
        """
        if self._monitoring_active:
            logger.warning("Monitoring already active")
            return
        
        self._monitoring_active = True
        self._data_callback = callback
        
        self._monitoring_task = asyncio.create_task(
            self._monitoring_loop(pids, interval)
        )
        
        logger.info(f"Started monitoring {len(pids)} parameters")
    
    async def stop_monitoring(self):
        """Stop continuous parameter monitoring."""
        if not self._monitoring_active:
            return
        
        self._monitoring_active = False
        
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Stopped parameter monitoring")
    
    async def _monitoring_loop(self, pids: List[str], interval: float):
        """Internal monitoring loop."""
        while self._monitoring_active:
            try:
                data = await self.read_multiple_parameters(pids)
                
                if self._data_callback and data:
                    await self._data_callback(data)
                
                await asyncio.sleep(interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(interval)
    
    def _get_command_for_pid(self, pid: str) -> Optional[obd.OBDCommand]:
        """
        Map PID string to OBD command object.
        
        Args:
            pid: Parameter ID string
            
        Returns:
            OBD command object or None
        """
        # Common PID to command mappings
        pid_commands = {
            "0C": obd.commands.RPM,
            "05": obd.commands.COOLANT_TEMP,
            "11": obd.commands.THROTTLE_POS,
            "0D": obd.commands.SPEED,
            "0F": obd.commands.INTAKE_TEMP,
            "10": obd.commands.MAF,
            "04": obd.commands.ENGINE_LOAD,
            "0B": obd.commands.INTAKE_PRESSURE,
            "2F": obd.commands.FUEL_LEVEL,
            "42": obd.commands.CONTROL_MODULE_VOLTAGE,
        }
        
        return pid_commands.get(pid)


class VehicleInfoService:
    """
    Service for retrieving vehicle identification and specification information.
    
    Provides methods to get VIN, ECU information, supported PIDs,
    and other static vehicle data.
    """
    
    def __init__(self, obd_manager: OBDInterfaceManager):
        """
        Initialize Vehicle Info Service.
        
        Args:
            obd_manager: OBD Interface Manager instance
        """
        self.obd_manager = obd_manager
    
    async def get_vehicle_info(self) -> Optional[VehicleInfo]:
        """
        Get comprehensive vehicle information.
        
        Returns:
            VehicleInfo object or None if failed
        """
        if not self.obd_manager.is_connected:
            logger.warning("OBD not connected, cannot get vehicle info")
            return None
        
        try:
            # Get VIN
            vin = await self._get_vin()
            
            # Get supported PIDs
            supported_pids = await self._get_supported_pids()
            
            # Get ECU information
            ecu_info = await self._get_ecu_info()
            
            # Parse VIN for make/model/year if available
            make, model, year = self._parse_vin(vin) if vin else (None, None, None)
            
            return VehicleInfo(
                vin=vin or "Unknown",
                make=make,
                model=model,
                year=year,
                supported_pids=supported_pids,
                ecu_info=ecu_info
            )
            
        except Exception as e:
            logger.error(f"Error getting vehicle info: {e}")
            return None
    
    async def _get_vin(self) -> Optional[str]:
        """Get Vehicle Identification Number."""
        try:
            response = await self.obd_manager.query(obd.commands.VIN)
            if response.success:
                return response.data.get("value")
        except Exception as e:
            logger.error(f"Error getting VIN: {e}")
        return None
    
    async def _get_supported_pids(self) -> List[str]:
        """Get list of supported Parameter IDs."""
        supported_pids = []
        
        try:
            # Check PIDs 01-20
            response = await self.obd_manager.query(obd.commands.PIDS_A)
            if response.success and response.data.get("value"):
                # Parse supported PIDs from response
                # This is a simplified implementation
                supported_pids.extend(["01", "02", "03", "04", "05", "0C", "0D", "0F", "10", "11"])
            
            # Additional PID ranges could be checked here (21-40, 41-60, etc.)
            
        except Exception as e:
            logger.error(f"Error getting supported PIDs: {e}")
        
        return supported_pids
    
    async def _get_ecu_info(self) -> List[ECUInfo]:
        """Get ECU information."""
        ecu_info = []
        
        try:
            # Get calibration ID if available
            cal_id = None
            try:
                response = await self.obd_manager.query(obd.commands.CALIBRATION_ID)
                if response.success:
                    cal_id = response.data.get("value")
            except:
                pass
            
            # Get supported commands as PIDs
            commands = await self.obd_manager.get_supported_commands()
            supported_pids = [cmd.pid for cmd in commands if hasattr(cmd, 'pid')]
            
            ecu_info.append(ECUInfo(
                ecu_id="primary_ecu",
                protocol=self.obd_manager._connection.protocol_name() if self.obd_manager._connection else "unknown",
                supported_pids=supported_pids,
                calibration_id=cal_id
            ))
            
        except Exception as e:
            logger.error(f"Error getting ECU info: {e}")
        
        return ecu_info
    
    def _parse_vin(self, vin: str) -> tuple[Optional[str], Optional[str], Optional[int]]:
        """
        Parse VIN to extract make, model, and year.
        
        Args:
            vin: Vehicle Identification Number
            
        Returns:
            Tuple of (make, model, year)
        """
        if not vin or len(vin) != 17:
            return None, None, None
        
        try:
            # VIN position 10 is the model year code
            year_code = vin[9]
            year = self._decode_year_from_vin(year_code)
            
            # VIN positions 1-3 are World Manufacturer Identifier
            wmi = vin[:3]
            make = self._decode_make_from_wmi(wmi)
            
            # Model would require a comprehensive VIN database
            model = None
            
            return make, model, year
            
        except Exception as e:
            logger.error(f"Error parsing VIN {vin}: {e}")
            return None, None, None
    
    def _decode_year_from_vin(self, year_code: str) -> Optional[int]:
        """Decode model year from VIN year code."""
        # Simplified VIN year decoding
        year_map = {
            'A': 1980, 'B': 1981, 'C': 1982, 'D': 1983, 'E': 1984, 'F': 1985,
            'G': 1986, 'H': 1987, 'J': 1988, 'K': 1989, 'L': 1990, 'M': 1991,
            'N': 1992, 'P': 1993, 'R': 1994, 'S': 1995, 'T': 1996, 'V': 1997,
            'W': 1998, 'X': 1999, 'Y': 2000, '1': 2001, '2': 2002, '3': 2003,
            '4': 2004, '5': 2005, '6': 2006, '7': 2007, '8': 2008, '9': 2009,
            'A': 2010, 'B': 2011, 'C': 2012, 'D': 2013, 'E': 2014, 'F': 2015,
            'G': 2016, 'H': 2017, 'J': 2018, 'K': 2019, 'L': 2020, 'M': 2021,
            'N': 2022, 'P': 2023, 'R': 2024, 'S': 2025
        }
        return year_map.get(year_code.upper())
    
    def _decode_make_from_wmi(self, wmi: str) -> Optional[str]:
        """Decode manufacturer from World Manufacturer Identifier."""
        # Simplified WMI decoding - only major manufacturers
        wmi_map = {
            '1G1': 'Chevrolet', '1G6': 'Cadillac', '1GT': 'GMC',
            '1FT': 'Ford', '1FA': 'Ford', '1FB': 'Ford',
            '2HG': 'Honda', '2HK': 'Honda',
            '4T1': 'Toyota', '4T3': 'Lexus',
            'WBA': 'BMW', 'WBS': 'BMW',
            'WAU': 'Audi', 'WVW': 'Volkswagen',
            'JHM': 'Honda', 'JTD': 'Toyota',
            'KNA': 'Kia', 'KMH': 'Hyundai',
        }
        
        return wmi_map.get(wmi.upper())