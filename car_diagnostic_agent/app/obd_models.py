"""
OBD-II Data Models for Car Diagnostic Agent.

This module defines the data models used for OBD-II integration including
DTC information, live data readings, vehicle information, and connection configuration.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any


class DTCStatus(Enum):
    """Status of a Diagnostic Trouble Code."""
    ACTIVE = "active"
    PENDING = "pending"
    STORED = "stored"
    CLEARED = "cleared"


class DTCSeverity(Enum):
    """Severity level of a Diagnostic Trouble Code."""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class OBDProtocol(Enum):
    """Supported OBD-II communication protocols."""
    AUTO = "auto"
    SAE_J1850_PWM = "sae_j1850_pwm"
    SAE_J1850_VPW = "sae_j1850_vpw"
    ISO_14230_4 = "iso_14230_4"
    ISO_15765_4 = "iso_15765_4"
    ISO_9141_2 = "iso_9141_2"


@dataclass
class OBDConnectionConfig:
    """Configuration for OBD-II connection."""
    port: str  # Serial port identifier (e.g., "/dev/ttyUSB0", "COM3")
    baudrate: int = 38400  # Communication speed
    timeout: float = 30.0  # Connection timeout in seconds
    protocol: OBDProtocol = OBDProtocol.AUTO  # OBD protocol
    auto_detect: bool = True  # Enable automatic protocol detection
    max_retries: int = 3  # Maximum connection retry attempts


@dataclass
class FreezeFrameData:
    """Freeze frame data associated with a DTC."""
    frame_number: int
    data: Dict[str, Any]
    timestamp: datetime


@dataclass
class DTCInfo:
    """Diagnostic Trouble Code information."""
    code: str  # DTC code (e.g., "P0171")
    description: str  # Human-readable description
    severity: DTCSeverity  # Error severity
    status: DTCStatus  # Current status
    freeze_frame: Optional[FreezeFrameData] = None  # Associated freeze frame data
    timestamp: datetime = None  # When the code was detected
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class LiveDataReading:
    """Real-time OBD parameter reading."""
    pid: str  # Parameter ID
    name: str  # Parameter name
    value: float  # Current value
    unit: str  # Unit of measurement
    min_value: Optional[float] = None  # Minimum expected value
    max_value: Optional[float] = None  # Maximum expected value
    timestamp: datetime = None  # Reading timestamp
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    @property
    def is_within_range(self) -> bool:
        """Check if the current value is within expected range."""
        if self.min_value is not None and self.value < self.min_value:
            return False
        if self.max_value is not None and self.value > self.max_value:
            return False
        return True


@dataclass
class ECUInfo:
    """Electronic Control Unit information."""
    ecu_id: str
    protocol: str
    supported_pids: List[str]
    calibration_id: Optional[str] = None
    cvn: Optional[str] = None  # Calibration Verification Number


@dataclass
class VehicleInfo:
    """Vehicle identification and specification information."""
    vin: str  # Vehicle Identification Number
    make: Optional[str] = None  # Vehicle manufacturer
    model: Optional[str] = None  # Vehicle model
    year: Optional[int] = None  # Model year
    engine_type: Optional[str] = None  # Engine specification
    supported_pids: List[str] = None  # List of supported Parameter IDs
    ecu_info: List[ECUInfo] = None  # ECU identification data
    
    def __post_init__(self):
        if self.supported_pids is None:
            self.supported_pids = []
        if self.ecu_info is None:
            self.ecu_info = []


@dataclass
class OBDResponse:
    """Generic OBD response wrapper."""
    success: bool
    data: Any
    error_message: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class DiagnosticSession:
    """Information about a diagnostic session."""
    session_id: str
    vehicle_info: Optional[VehicleInfo] = None
    connection_config: Optional[OBDConnectionConfig] = None
    start_time: datetime = None
    end_time: Optional[datetime] = None
    dtcs_found: List[DTCInfo] = None
    live_data_readings: List[LiveDataReading] = None
    
    def __post_init__(self):
        if self.start_time is None:
            self.start_time = datetime.now()
        if self.dtcs_found is None:
            self.dtcs_found = []
        if self.live_data_readings is None:
            self.live_data_readings = []
    
    @property
    def duration(self) -> Optional[float]:
        """Get session duration in seconds."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    def add_dtc(self, dtc: DTCInfo):
        """Add a DTC to the session."""
        self.dtcs_found.append(dtc)
    
    def add_live_data(self, reading: LiveDataReading):
        """Add a live data reading to the session."""
        self.live_data_readings.append(reading)
    
    def end_session(self):
        """Mark the session as ended."""
        self.end_time = datetime.now()


# Common OBD Parameter IDs and their descriptions
COMMON_PIDS = {
    "01": {"name": "Monitor status since DTCs cleared", "unit": "bit"},
    "02": {"name": "Freeze DTC", "unit": ""},
    "03": {"name": "Fuel system status", "unit": "bit"},
    "04": {"name": "Calculated engine load", "unit": "%"},
    "05": {"name": "Engine coolant temperature", "unit": "°C"},
    "06": {"name": "Short term fuel trim—Bank 1", "unit": "%"},
    "07": {"name": "Long term fuel trim—Bank 1", "unit": "%"},
    "08": {"name": "Short term fuel trim—Bank 2", "unit": "%"},
    "09": {"name": "Long term fuel trim—Bank 2", "unit": "%"},
    "0A": {"name": "Fuel pressure", "unit": "kPa"},
    "0B": {"name": "Intake manifold absolute pressure", "unit": "kPa"},
    "0C": {"name": "Engine RPM", "unit": "rpm"},
    "0D": {"name": "Vehicle speed", "unit": "km/h"},
    "0E": {"name": "Timing advance", "unit": "°"},
    "0F": {"name": "Intake air temperature", "unit": "°C"},
    "10": {"name": "Mass air flow rate", "unit": "g/s"},
    "11": {"name": "Throttle position", "unit": "%"},
    "12": {"name": "Commanded secondary air status", "unit": "bit"},
    "13": {"name": "Oxygen sensors present", "unit": "bit"},
    "14": {"name": "Oxygen sensor 1 voltage", "unit": "V"},
    "15": {"name": "Oxygen sensor 2 voltage", "unit": "V"},
    "1C": {"name": "OBD standards", "unit": "bit"},
    "1F": {"name": "Run time since engine start", "unit": "sec"},
    "21": {"name": "Distance traveled with malfunction indicator lamp", "unit": "km"},
    "2F": {"name": "Fuel Tank Level Input", "unit": "%"},
    "33": {"name": "Absolute Barometric Pressure", "unit": "kPa"},
    "42": {"name": "Control module voltage", "unit": "V"},
    "43": {"name": "Absolute load value", "unit": "%"},
    "44": {"name": "Fuel–Air commanded equivalence ratio", "unit": "ratio"},
    "45": {"name": "Relative throttle position", "unit": "%"},
    "46": {"name": "Ambient air temperature", "unit": "°C"},
    "47": {"name": "Absolute throttle position B", "unit": "%"},
    "49": {"name": "Accelerator pedal position D", "unit": "%"},
    "4A": {"name": "Accelerator pedal position E", "unit": "%"},
    "4C": {"name": "Commanded throttle actuator", "unit": "%"},
    "51": {"name": "Fuel Type", "unit": ""},
    "52": {"name": "Ethanol fuel %", "unit": "%"},
}