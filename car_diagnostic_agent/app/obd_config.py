"""
OBD Configuration Management for Car Diagnostic Agent.

This module provides configuration management for OBD-II connections,
including settings persistence, auto-detection, and connection profiles.
"""

import json
import os
import serial.tools.list_ports
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import asdict

from .obd_models import OBDConnectionConfig, OBDProtocol


class OBDConfigManager:
    """
    Manager for OBD configuration settings and connection profiles.
    
    Handles loading, saving, and managing OBD connection configurations
    with support for multiple connection profiles.
    """
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize OBD Config Manager.
        
        Args:
            config_dir: Optional directory for config files
        """
        self.config_dir = Path(config_dir) if config_dir else Path.home() / ".car_diagnostic_agent"
        self.config_file = self.config_dir / "obd_config.json"
        self.config_dir.mkdir(exist_ok=True)
        
        self._config_data = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
        
        # Default configuration
        return {
            "default_profile": "auto",
            "profiles": {
                "auto": {
                    "port": "auto",
                    "baudrate": 38400,
                    "timeout": 30.0,
                    "protocol": "auto",
                    "auto_detect": True,
                    "max_retries": 3
                }
            },
            "last_successful_connection": None,
            "enable_mock_mode": False,
            "auto_connect_on_start": False,
            "feedback_data": []
        }
    
    def _save_config(self):
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self._config_data, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get_default_config(self) -> OBDConnectionConfig:
        """
        Get the default OBD connection configuration.
        
        Returns:
            OBDConnectionConfig object
        """
        profile_name = self._config_data.get("default_profile", "auto")
        return self.get_profile_config(profile_name)
    
    def get_profile_config(self, profile_name: str) -> OBDConnectionConfig:
        """
        Get configuration for a specific profile.
        
        Args:
            profile_name: Name of the profile
            
        Returns:
            OBDConnectionConfig object
        """
        profile_data = self._config_data["profiles"].get(profile_name, self._config_data["profiles"]["auto"])
        
        return OBDConnectionConfig(
            port=profile_data["port"],
            baudrate=profile_data["baudrate"],
            timeout=profile_data["timeout"],
            protocol=OBDProtocol(profile_data["protocol"]),
            auto_detect=profile_data["auto_detect"],
            max_retries=profile_data["max_retries"]
        )
    
    def save_profile(self, profile_name: str, config: OBDConnectionConfig):
        """
        Save a connection profile.
        
        Args:
            profile_name: Name of the profile
            config: OBD connection configuration
        """
        config_dict = asdict(config)
        config_dict["protocol"] = config.protocol.value
        
        self._config_data["profiles"][profile_name] = config_dict
        self._save_config()
    
    def delete_profile(self, profile_name: str) -> bool:
        """
        Delete a connection profile.
        
        Args:
            profile_name: Name of the profile to delete
            
        Returns:
            True if deleted, False if profile doesn't exist or is default
        """
        if profile_name == "auto":
            return False  # Cannot delete default profile
        
        if profile_name in self._config_data["profiles"]:
            del self._config_data["profiles"][profile_name]
            
            # Update default if we deleted the current default
            if self._config_data["default_profile"] == profile_name:
                self._config_data["default_profile"] = "auto"
            
            self._save_config()
            return True
        
        return False
    
    def list_profiles(self) -> List[str]:
        """
        Get list of available connection profiles.
        
        Returns:
            List of profile names
        """
        return list(self._config_data["profiles"].keys())
    
    def set_default_profile(self, profile_name: str) -> bool:
        """
        Set the default connection profile.
        
        Args:
            profile_name: Name of the profile to set as default
            
        Returns:
            True if set successfully, False if profile doesn't exist
        """
        if profile_name in self._config_data["profiles"]:
            self._config_data["default_profile"] = profile_name
            self._save_config()
            return True
        return False
    
    def get_available_ports(self) -> List[Dict[str, str]]:
        """
        Get list of available serial ports.
        
        Returns:
            List of dictionaries with port information
        """
        ports = []
        for port in serial.tools.list_ports.comports():
            ports.append({
                "device": port.device,
                "description": port.description,
                "manufacturer": port.manufacturer or "Unknown"
            })
        return ports
    
    def auto_detect_port(self) -> Optional[str]:
        """
        Auto-detect OBD adapter port.
        
        Returns:
            Port name if detected, None otherwise
        """
        # Look for common OBD adapter patterns
        obd_patterns = [
            "ELM327",
            "OBD",
            "USB Serial",
            "FTDI",
            "CH340",
            "CP2102",
            "PL2303"
        ]
        
        ports = self.get_available_ports()
        
        for port in ports:
            description = port["description"].upper()
            manufacturer = port["manufacturer"].upper()
            
            for pattern in obd_patterns:
                if pattern in description or pattern in manufacturer:
                    return port["device"]
        
        # If no specific OBD adapter found, return first available port
        if ports:
            return ports[0]["device"]
        
        return None
    
    def save_successful_connection(self, config: OBDConnectionConfig):
        """
        Save the last successful connection configuration.
        
        Args:
            config: Successfully connected configuration
        """
        config_dict = asdict(config)
        config_dict["protocol"] = config.protocol.value
        
        self._config_data["last_successful_connection"] = config_dict
        self._save_config()
    
    def get_last_successful_connection(self) -> Optional[OBDConnectionConfig]:
        """
        Get the last successful connection configuration.
        
        Returns:
            OBDConnectionConfig object or None
        """
        last_config = self._config_data.get("last_successful_connection")
        if last_config:
            return OBDConnectionConfig(
                port=last_config["port"],
                baudrate=last_config["baudrate"],
                timeout=last_config["timeout"],
                protocol=OBDProtocol(last_config["protocol"]),
                auto_detect=last_config["auto_detect"],
                max_retries=last_config["max_retries"]
            )
        return None
    
    def is_mock_mode_enabled(self) -> bool:
        """Check if mock mode is enabled."""
        return self._config_data.get("enable_mock_mode", False)
    
    def set_mock_mode(self, enabled: bool):
        """
        Enable or disable mock mode.
        
        Args:
            enabled: Whether to enable mock mode
        """
        self._config_data["enable_mock_mode"] = enabled
        self._save_config()
    
    def is_auto_connect_enabled(self) -> bool:
        """Check if auto-connect on start is enabled."""
        return self._config_data.get("auto_connect_on_start", False)
    
    def set_auto_connect(self, enabled: bool):
        """
        Enable or disable auto-connect on start.
        
        Args:
            enabled: Whether to enable auto-connect
        """
        self._config_data["auto_connect_on_start"] = enabled
        self._save_config()
    
    def create_optimized_config(self, vehicle_info: Optional[Dict[str, Any]] = None) -> OBDConnectionConfig:
        """
        Create an optimized configuration based on vehicle information.
        
        Args:
            vehicle_info: Optional vehicle information for optimization
            
        Returns:
            Optimized OBDConnectionConfig
        """
        config = self.get_default_config()
        
        # Optimize based on vehicle info if available
        if vehicle_info:
            make = vehicle_info.get("make", "").upper()
            year = vehicle_info.get("year")
            
            # Optimize for specific manufacturers
            if make in ["FORD", "LINCOLN", "MERCURY"]:
                if year and year >= 2008:
                    config.protocol = OBDProtocol.ISO_15765_4  # CAN
                else:
                    config.protocol = OBDProtocol.SAE_J1850_PWM
            elif make in ["GM", "CHEVROLET", "CADILLAC", "BUICK", "GMC"]:
                if year and year >= 2008:
                    config.protocol = OBDProtocol.ISO_15765_4  # CAN
                else:
                    config.protocol = OBDProtocol.SAE_J1850_VPW
            elif make in ["CHRYSLER", "DODGE", "JEEP", "RAM"]:
                if year and year >= 2008:
                    config.protocol = OBDProtocol.ISO_15765_4  # CAN
                else:
                    config.protocol = OBDProtocol.ISO_9141_2
            elif make in ["TOYOTA", "LEXUS", "HONDA", "ACURA", "NISSAN", "INFINITI"]:
                if year and year >= 2008:
                    config.protocol = OBDProtocol.ISO_15765_4  # CAN
                else:
                    config.protocol = OBDProtocol.ISO_14230_4  # KWP2000
        
        return config
    
    def validate_config(self, config: OBDConnectionConfig) -> List[str]:
        """
        Validate an OBD configuration.
        
        Args:
            config: Configuration to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Validate port
        if config.port != "auto":
            available_ports = [p["device"] for p in self.get_available_ports()]
            if config.port not in available_ports:
                errors.append(f"Port {config.port} is not available")
        
        # Validate baudrate
        valid_baudrates = [9600, 19200, 38400, 57600, 115200]
        if config.baudrate not in valid_baudrates:
            errors.append(f"Invalid baudrate {config.baudrate}")
        
        # Validate timeout
        if config.timeout <= 0 or config.timeout > 300:
            errors.append("Timeout must be between 0 and 300 seconds")
        
        # Validate max_retries
        if config.max_retries < 0 or config.max_retries > 10:
            errors.append("Max retries must be between 0 and 10")
        
        return errors
    
    def export_config(self, file_path: str) -> bool:
        """
        Export configuration to a file.
        
        Args:
            file_path: Path to export file
            
        Returns:
            True if exported successfully
        """
        try:
            with open(file_path, 'w') as f:
                json.dump(self._config_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting config: {e}")
            return False
    
    def import_config(self, file_path: str) -> bool:
        """
        Import configuration from a file.
        
        Args:
            file_path: Path to import file
            
        Returns:
            True if imported successfully
        """
        try:
            with open(file_path, 'r') as f:
                imported_config = json.load(f)
            
            # Merge with existing config
            self._config_data.update(imported_config)
            self._save_config()
            return True
        except Exception as e:
            print(f"Error importing config: {e}")
            return False
    
    def add_feedback(self, feedback_entry: Dict[str, Any]) -> bool:
        """
        Add user feedback to the feedback database.
        
        Args:
            feedback_entry: Dictionary containing feedback data
            
        Returns:
            True if feedback was added successfully
        """
        try:
            if "feedback_data" not in self._config_data:
                self._config_data["feedback_data"] = []
            
            self._config_data["feedback_data"].append(feedback_entry)
            self._save_config()
            return True
        except Exception as e:
            print(f"Error adding feedback: {e}")
            return False
    
    def get_feedback_data(self) -> List[Dict[str, Any]]:
        """
        Get all feedback data.
        
        Returns:
            List of feedback entries
        """
        return self._config_data.get("feedback_data", [])
    
    def get_feedback_for_dtc(self, dtc_code: str) -> List[Dict[str, Any]]:
        """
        Get feedback entries related to a specific DTC code.
        
        Args:
            dtc_code: DTC code to search for
            
        Returns:
            List of feedback entries for the specified DTC
        """
        feedback_data = self._config_data.get("feedback_data", [])
        return [entry for entry in feedback_data if entry.get("dtc_code") == dtc_code]
    
    def reset_to_defaults(self):
        """Reset configuration to defaults."""
        self._config_data = self._load_config().__class__().__dict__
        # Force reload defaults
        default_config = {
            "default_profile": "auto",
            "profiles": {
                "auto": {
                    "port": "auto",
                    "baudrate": 38400,
                    "timeout": 30.0,
                    "protocol": "auto",
                    "auto_detect": True,
                    "max_retries": 3
                }
            },
            "last_successful_connection": None,
            "enable_mock_mode": False,
            "auto_connect_on_start": False
        }
        self._config_data = default_config
        self._save_config()


# Global config manager instance
config_manager = OBDConfigManager()