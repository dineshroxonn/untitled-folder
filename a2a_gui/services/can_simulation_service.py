"""
CAN Simulation Service for Car Diagnostic Agent

This service uses python-can to generate realistic CAN data for simulation mode.
"""

import can
import random
import asyncio
import json
from typing import Dict, List, Any
from datetime import datetime


class CANSimulationService:
    """Service for generating CAN simulation data using python-can."""
    
    # Common vehicle scenarios
    SCENARIOS = {
        "healthy": {
            "name": "Healthy Vehicle",
            "dtc_codes": [],
            "description": "No diagnostic trouble codes, normal operation"
        },
        "rich_condition": {
            "name": "Rich Condition",
            "dtc_codes": ["P0171", "P0174"],
            "description": "System too lean (Bank 1 and 2)"
        },
        "misfire": {
            "name": "Engine Misfire",
            "dtc_codes": ["P0300", "P0301"],
            "description": "Random/multiple cylinder misfire detected"
        },
        "catalyst": {
            "name": "Catalyst Issue",
            "dtc_codes": ["P0420"],
            "description": "Catalyst system efficiency below threshold"
        }
    }
    
    # Common CAN IDs for OBD-II data
    CAN_IDS = {
        'ENGINE_RPM': 0x190,
        'VEHICLE_SPEED': 0x18F,
        'THROTTLE_POSITION': 0x191,
        'COOLANT_TEMP': 0x192,
        'INTAKE_TEMP': 0x193,
        'MAF': 0x194,
        'FUEL_LEVEL': 0x195,
        'BATTERY_VOLTAGE': 0x196,
        'KEEP_ALIVE': 0x140
    }
    
    def __init__(self):
        """Initialize the CAN simulation service."""
        self.bus = None
        self.is_simulating = False
        
    async def simulate_scenario(self, scenario: str = "healthy") -> Dict[str, Any]:
        """
        Generate CAN data for a specific vehicle scenario.
        
        Args:
            scenario: The scenario to simulate
            
        Returns:
            Dictionary with simulation results and generated data
        """
        if scenario not in self.SCENARIOS:
            scenario = "healthy"
            
        scenario_config = self.SCENARIOS[scenario]
        
        try:
            # Create virtual CAN bus for simulation
            self.bus = can.Bus(interface='virtual', channel='simulated_car')
            
            # Generate simulation data
            can_data = await self._generate_can_data(scenario)
            
            # Convert to OBD format for mock interface
            obd_data = self._convert_can_to_obd(can_data, scenario_config)
            
            return {
                "success": True,
                "scenario": scenario,
                "scenario_name": scenario_config["name"],
                "dtc_codes": scenario_config["dtc_codes"],
                "obd_data": obd_data,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "scenario": scenario
            }
        finally:
            if self.bus:
                self.bus.shutdown()
    
    async def _generate_can_data(self, scenario: str) -> List[Dict[str, Any]]:
        """
        Generate realistic CAN messages for a scenario.
        
        Args:
            scenario: The scenario to generate data for
            
        Returns:
            List of CAN message dictionaries
        """
        messages = []
        message_count = 100  # Number of messages to generate
        
        # Determine vehicle state based on scenario
        if scenario == "healthy":
            state = "normal"
        elif scenario in ["rich_condition", "catalyst"]:
            state = "driving"
        elif scenario == "misfire":
            state = "misfiring"
        else:
            state = "normal"
            
        # Generate messages
        for i in range(message_count):
            # Always send keep-alive
            messages.append({
                "arbitration_id": self.CAN_IDS['KEEP_ALIVE'],
                "data": self._generate_keep_alive_data(),
                "timestamp": i * 0.01
            })
            
            # Generate scenario-specific data
            if scenario == "healthy":
                messages.extend(self._generate_healthy_data(i))
            elif scenario == "rich_condition":
                messages.extend(self._generate_rich_condition_data(i))
            elif scenario == "misfire":
                messages.extend(self._generate_misfire_data(i))
            elif scenario == "catalyst":
                messages.extend(self._generate_catalyst_data(i))
                
        return messages
    
    def _generate_keep_alive_data(self) -> bytearray:
        """Generate keep-alive message data."""
        return bytearray([
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255)
        ])
    
    def _generate_healthy_data(self, index: int) -> List[Dict[str, Any]]:
        """Generate data for a healthy vehicle."""
        messages = []
        
        # Engine RPM (700-800 RPM at idle)
        rpm = random.randint(700, 800)
        rpm_high = (rpm * 4) // 256
        rpm_low = (rpm * 4) % 256
        messages.append({
            "arbitration_id": self.CAN_IDS['ENGINE_RPM'],
            "data": bytearray([rpm_high, rpm_low, 0, 0, 0, 0, 0, 0]),
            "timestamp": index * 0.01
        })
        
        # Coolant temperature (85-95°C)
        coolant_temp = random.randint(85, 95)
        messages.append({
            "arbitration_id": self.CAN_IDS['COOLANT_TEMP'],
            "data": bytearray([coolant_temp + 40, 0, 0, 0, 0, 0, 0, 0]),
            "timestamp": index * 0.01
        })
        
        # Throttle position (5-10%)
        throttle = random.randint(5, 10)
        throttle_byte = int(throttle * 2.55)
        messages.append({
            "arbitration_id": self.CAN_IDS['THROTTLE_POSITION'],
            "data": bytearray([throttle_byte, 0, 0, 0, 0, 0, 0, 0]),
            "timestamp": index * 0.01
        })
        
        return messages
    
    def _generate_rich_condition_data(self, index: int) -> List[Dict[str, Any]]:
        """Generate data for rich condition scenario."""
        messages = []
        
        # Engine RPM (normal driving)
        rpm = random.randint(1500, 2500)
        rpm_high = (rpm * 4) // 256
        rpm_low = (rpm * 4) % 255
        messages.append({
            "arbitration_id": self.CAN_IDS['ENGINE_RPM'],
            "data": bytearray([rpm_high, rpm_low, 0, 0, 0, 0, 0, 0]),
            "timestamp": index * 0.01
        })
        
        # Coolant temperature (normal)
        coolant_temp = random.randint(85, 95)
        messages.append({
            "arbitration_id": self.CAN_IDS['COOLANT_TEMP'],
            "data": bytearray([coolant_temp + 40, 0, 0, 0, 0, 0, 0, 0]),
            "timestamp": index * 0.01
        })
        
        # MAF sensor reading (higher than normal for rich condition)
        maf = random.randint(25, 35)  # grams/sec
        maf_high = (maf * 100) // 256
        maf_low = (maf * 100) % 256
        messages.append({
            "arbitration_id": self.CAN_IDS['MAF'],
            "data": bytearray([maf_high, maf_low, 0, 0, 0, 0, 0, 0]),
            "timestamp": index * 0.01
        })
        
        return messages
    
    def _generate_misfire_data(self, index: int) -> List[Dict[str, Any]]:
        """Generate data for misfire scenario."""
        messages = []
        
        # Irregular RPM (simulating misfire)
        if index % 10 == 0:
            rpm = random.randint(500, 600)  # Misfiring
        else:
            rpm = random.randint(750, 850)  # Normal
        rpm_high = (rpm * 4) // 256
        rpm_low = (rpm * 4) % 256
        messages.append({
            "arbitration_id": self.CAN_IDS['ENGINE_RPM'],
            "data": bytearray([rpm_high, rpm_low, 0, 0, 0, 0, 0, 0]),
            "timestamp": index * 0.01
        })
        
        return messages
    
    def _generate_catalyst_data(self, index: int) -> List[Dict[str, Any]]:
        """Generate data for catalyst issue scenario."""
        messages = []
        
        # Higher exhaust temperatures (indicating catalyst inefficiency)
        coolant_temp = random.randint(95, 105)  # Higher than normal
        messages.append({
            "arbitration_id": self.CAN_IDS['COOLANT_TEMP'],
            "data": bytearray([coolant_temp + 40, 0, 0, 0, 0, 0, 0, 0]),
            "timestamp": index * 0.01
        })
        
        return messages
    
    def _convert_can_to_obd(self, can_data: List[Dict[str, Any]], scenario_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert CAN data to OBD format for mock interface.
        
        Args:
            can_data: List of CAN messages
            scenario_config: Scenario configuration
            
        Returns:
            OBD data dictionary
        """
        obd_data = {
            "dtcs": [],
            "live_data": {},
            "vehicle_info": {
                "vin": "SIMULATED_VIN_1234567890",
                "make": "Toyota",
                "model": "Camry",
                "year": 2018
            }
        }
        
        # Add DTCs from scenario
        for dtc_code in scenario_config["dtc_codes"]:
            obd_data["dtcs"].append({
                "code": dtc_code,
                "description": self._get_dtc_description(dtc_code),
                "severity": self._get_dtc_severity(dtc_code),
                "status": "stored"
            })
        
        # Process CAN data to extract OBD parameters
        for message in can_data[:20]:  # Just process first 20 messages for demo
            arbitration_id = message["arbitration_id"]
            data = message["data"]
            
            if arbitration_id == self.CAN_IDS['ENGINE_RPM'] and len(data) >= 2:
                rpm = (data[0] * 256 + data[1]) // 4
                obd_data["live_data"]["0C"] = {
                    "name": "Engine RPM",
                    "value": float(rpm),
                    "unit": "rpm",
                    "in_range": 500 <= rpm <= 8000
                }
            elif arbitration_id == self.CAN_IDS['COOLANT_TEMP'] and len(data) >= 1:
                temp = data[0] - 40
                obd_data["live_data"]["05"] = {
                    "name": "Engine Coolant Temperature",
                    "value": float(temp),
                    "unit": "°C",
                    "in_range": 80 <= temp <= 105
                }
            elif arbitration_id == self.CAN_IDS['THROTTLE_POSITION'] and len(data) >= 1:
                throttle = (data[0] * 100) / 255
                obd_data["live_data"]["11"] = {
                    "name": "Throttle Position",
                    "value": float(throttle),
                    "unit": "%",
                    "in_range": 0 <= throttle <= 100
                }
        
        return obd_data
    
    def _get_dtc_description(self, dtc_code: str) -> str:
        """Get description for a DTC code."""
        descriptions = {
            "P0171": "System Too Lean (Bank 1)",
            "P0174": "System Too Lean (Bank 2)",
            "P0300": "Random/Multiple Cylinder Misfire Detected",
            "P0301": "Cylinder 1 Misfire Detected",
            "P0420": "Catalyst System Efficiency Below Threshold (Bank 1)"
        }
        return descriptions.get(dtc_code, "Unknown DTC Description")
    
    def _get_dtc_severity(self, dtc_code: str) -> str:
        """Get severity for a DTC code."""
        critical_codes = ["P0300", "P0301"]
        warning_codes = ["P0171", "P0174", "P0420"]
        
        if dtc_code in critical_codes:
            return "critical"
        elif dtc_code in warning_codes:
            return "warning"
        else:
            return "info"


# Global instance
simulation_service = CANSimulationService()