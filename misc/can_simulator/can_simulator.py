"""
CAN Simulator for Car Diagnostic Testing

This module provides tools to simulate CAN bus traffic and generate
test data files for the car diagnostic agent.
"""

import random
import time
import json
from datetime import datetime
from typing import List, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class CANMessage:
    """Represents a CAN bus message."""
    arbitration_id: int
    data: List[int]
    timestamp: float
    is_extended_id: bool = False
    is_error_frame: bool = False
    is_remote_frame: bool = False
    dlc: int = None

    def __post_init__(self):
        if self.dlc is None:
            self.dlc = len(self.data)


class CANFrameGenerator:
    """Generates realistic CAN frames for testing."""
    
    # Common OBD-II PIDs (Parameter IDs)
    OBD_PIDS = {
        0x0C: "Engine RPM",
        0x0D: "Vehicle Speed",
        0x05: "Engine Coolant Temperature",
        0x0F: "Intake Air Temperature",
        0x11: "Throttle Position",
        0x04: "Engine Load",
        0x2F: "Fuel Level",
        0x42: "Control Module Voltage",
        0x46: "Ambient Air Temperature"
    }
    
    # Common DTC (Diagnostic Trouble Codes)
    DTC_CODES = [
        "P0171", "P0174", "P0300", "P0301", "P0302", "P0303", "P0304", "P0305", "P0306",
        "P0420", "P0440", "P0500", "P0507", "P0700", "P0730", "P0750", "P0755", "P0800",
        "C0121", "C0128", "C0245", "U0100", "U0103", "U0422"
    ]
    
    def __init__(self):
        self.engine_running = True
        self.vehicle_speed = 0
        self.engine_rpm = 0
        self.coolant_temp = 80
        self.throttle_position = 0
        
    def generate_obd_pid_response(self, pid: int) -> CANMessage:
        """Generate a response for a specific OBD PID."""
        # OBD-II response format:
        # Arbitration ID: 0x7E8 (Physical response) or 0x7DF (Functional request)
        # Data: [length, mode, pid, data_bytes...]
        
        if pid == 0x0C:  # Engine RPM
            self.engine_rpm = random.randint(700, 3500) if self.engine_running else 0
            # RPM = ((A*256)+B)/4
            rpm_high = (self.engine_rpm * 4) // 256
            rpm_low = (self.engine_rpm * 4) % 256
            data = [0x04, 0x41, pid, rpm_high, rpm_low, 0x00, 0x00, 0x00]
            
        elif pid == 0x0D:  # Vehicle Speed
            self.vehicle_speed = random.randint(0, 120) if self.engine_running else 0
            data = [0x03, 0x41, pid, self.vehicle_speed, 0x00, 0x00, 0x00, 0x00]
            
        elif pid == 0x05:  # Engine Coolant Temperature
            self.coolant_temp = random.randint(80, 105) if self.engine_running else 80
            # Temperature = A - 40
            temp_byte = self.coolant_temp + 40
            data = [0x03, 0x41, pid, temp_byte, 0x00, 0x00, 0x00, 0x00]
            
        elif pid == 0x11:  # Throttle Position
            self.throttle_position = random.randint(0, 100)
            # Percentage = A * 100 / 255
            throttle_byte = int(self.throttle_position * 255 / 100)
            data = [0x03, 0x41, pid, throttle_byte, 0x00, 0x00, 0x00, 0x00]
            
        elif pid == 0x04:  # Engine Load
            engine_load = random.randint(0, 100)
            # Percentage = A * 100 / 255
            load_byte = int(engine_load * 255 / 100)
            data = [0x03, 0x41, pid, load_byte, 0x00, 0x00, 0x00, 0x00]
            
        elif pid == 0x2F:  # Fuel Level
            fuel_level = random.randint(0, 100)
            # Percentage = A * 100 / 255
            fuel_byte = int(fuel_level * 255 / 100)
            data = [0x03, 0x41, pid, fuel_byte, 0x00, 0x00, 0x00, 0x00]
            
        elif pid == 0x42:  # Control Module Voltage
            voltage = random.uniform(12.0, 14.5)
            # Voltage = ((A*256)+B)/1000
            voltage_int = int(voltage * 1000)
            voltage_high = voltage_int // 256
            voltage_low = voltage_int % 256
            data = [0x04, 0x41, pid, voltage_high, voltage_low, 0x00, 0x00, 0x00]
            
        elif pid == 0x46:  # Ambient Air Temperature
            ambient_temp = random.randint(10, 35)
            # Temperature = A - 40
            temp_byte = ambient_temp + 40
            data = [0x03, 0x41, pid, temp_byte, 0x00, 0x00, 0x00, 0x00]
            
        else:
            # Unknown PID, return "service not supported"
            data = [0x02, 0x7F, 0x01, 0x12, 0x00, 0x00, 0x00, 0x00]
        
        return CANMessage(
            arbitration_id=0x7E8,  # Standard OBD-II response ID
            data=data,
            timestamp=time.time()
        )
    
    def generate_dtcs(self, count: int = 5) -> List[CANMessage]:
        """Generate DTC responses."""
        messages = []
        
        # Mode 03 - Request DTCs
        # Response format: [length, mode, DTC_count, DTC1_high, DTC1_low, DTC2_high, DTC2_low, ...]
        dtc_count = min(count, 3)  # Max 3 DTCs per message
        
        data = [2 + dtc_count * 2, 0x43, dtc_count]  # Length, mode, count
        
        for _ in range(dtc_count):
            dtc = random.choice(self.DTC_CODES)
            # Convert DTC to bytes
            dtc_bytes = self._dtc_to_bytes(dtc)
            data.extend(dtc_bytes)
        
        # Pad with zeros
        while len(data) < 8:
            data.append(0x00)
            
        messages.append(CANMessage(
            arbitration_id=0x7E8,
            data=data[:8],
            timestamp=time.time()
        ))
        
        return messages
    
    def _dtc_to_bytes(self, dtc: str) -> List[int]:
        """Convert a DTC string to bytes."""
        # DTC format: [P|C|U|B][0-3][0-9A-F][0-9A-F]
        # First character determines the type
        type_map = {'P': 0, 'C': 1, 'B': 2, 'U': 3}
        dtc_type = type_map.get(dtc[0], 0)
        
        # Second character determines the number (0-3)
        dtc_number = int(dtc[1])
        
        # Third character (0-9, A-F) -> 0-15
        third_char = dtc[2]
        if third_char.isdigit():
            third_val = int(third_char)
        else:
            third_val = ord(third_char) - ord('A') + 10
            
        # Fourth character (0-9, A-F) -> 0-15
        fourth_char = dtc[3]
        if fourth_char.isdigit():
            fourth_val = int(fourth_char)
        else:
            fourth_val = ord(fourth_char) - ord('A') + 10
            
        # First byte: (type << 6) | (number << 4) | (third_val >> 4)
        first_byte = (dtc_type << 6) | (dtc_number << 4) | (third_val >> 4)
        
        # Second byte: (third_val << 4) | fourth_val
        second_byte = ((third_val & 0x0F) << 4) | fourth_val
        
        return [first_byte, second_byte]
    
    def generate_random_can_traffic(self, count: int = 100) -> List[CANMessage]:
        """Generate random CAN traffic including OBD requests and responses."""
        messages = []
        
        for _ in range(count):
            # Randomly decide between request and response
            if random.random() < 0.7:  # 70% chance of response
                # Generate response message
                pid = random.choice(list(self.OBD_PIDS.keys()))
                msg = self.generate_obd_pid_response(pid)
                messages.append(msg)
            else:
                # Generate request message
                arbitration_id = 0x7DF  # Functional request ID
                pid = random.choice(list(self.OBD_PIDS.keys()))
                data = [0x02, 0x01, pid, 0x00, 0x00, 0x00, 0x00, 0x00]
                
                messages.append(CANMessage(
                    arbitration_id=arbitration_id,
                    data=data,
                    timestamp=time.time()
                ))
            
            # Add some random delay between messages
            time.sleep(random.uniform(0.001, 0.01))
        
        return messages


def save_can_dump(messages: List[CANMessage], filename: str):
    """Save CAN messages to a dump file in JSON format."""
    # Convert messages to dict for JSON serialization
    dump_data = {
        "timestamp": datetime.now().isoformat(),
        "message_count": len(messages),
        "messages": [asdict(msg) for msg in messages]
    }
    
    with open(filename, 'w') as f:
        json.dump(dump_data, f, indent=2)


def load_can_dump(filename: str) -> List[CANMessage]:
    """Load CAN messages from a dump file."""
    with open(filename, 'r') as f:
        dump_data = json.load(f)
    
    messages = []
    for msg_dict in dump_data["messages"]:
        # Convert dict back to CANMessage
        msg = CANMessage(**msg_dict)
        messages.append(msg)
    
    return messages


def main():
    """Main function to demonstrate the CAN simulator."""
    print("CAN Simulator for Car Diagnostic Testing")
    print("=" * 40)
    
    # Create generator
    generator = CANFrameGenerator()
    
    # Generate some OBD PID responses
    print("\nGenerating OBD PID responses...")
    pid_messages = []
    for pid in list(generator.OBD_PIDS.keys())[:5]:  # First 5 PIDs
        msg = generator.generate_obd_pid_response(pid)
        pid_messages.append(msg)
        print(f"PID 0x{pid:02X} ({generator.OBD_PIDS[pid]}): {msg.data}")
    
    # Generate DTCs
    print("\nGenerating DTC responses...")
    dtc_messages = generator.generate_dtcs(3)
    for msg in dtc_messages:
        print(f"DTC Response: {msg.data}")
    
    # Generate random traffic
    print("\nGenerating random CAN traffic...")
    random_messages = generator.generate_random_can_traffic(20)
    print(f"Generated {len(random_messages)} messages")
    
    # Combine all messages
    all_messages = pid_messages + dtc_messages + random_messages
    
    # Save to file
    filename = f"can_dump_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    save_can_dump(all_messages, filename)
    print(f"\nSaved {len(all_messages)} messages to {filename}")
    
    # Demonstrate loading
    print("\nLoading and verifying...")
    loaded_messages = load_can_dump(filename)
    print(f"Loaded {len(loaded_messages)} messages from file")


if __name__ == "__main__":
    main()