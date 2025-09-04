"""
Honda Accord CAN Simulator using python-can

This script generates a realistic candump file for a Honda Accord
using the python-can library.
"""

import can
import time
import random
from datetime import datetime


# Configuration
LOG_FILE_NAME = 'honda_accord_candump.log'
MESSAGE_COUNT = 500  # Number of messages to generate

# Known or common CAN IDs for Honda Accord (examples)
# Note: These are representative examples, not guaranteed to be
# the exact IDs for a specific Honda Accord model.
CAN_IDS = {
    'VEHICLE_SPEED': 0x18F,      # Example ID for vehicle speed
    'ENGINE_RPM': 0x190,         # Example ID for engine RPM
    'THROTTLE_POSITION': 0x191,  # Example ID for throttle position
    'HORN_PRESS': 0x280,         # Example ID for a button press (e.g., horn)
    'KEEP_ALIVE': 0x140,         # Example ID for a regular "keep-alive" message
    'BRAKE_PRESS': 0x192,        # Example ID for brake pedal position
    'STEERING_ANGLE': 0x193,     # Example ID for steering wheel angle
    'FUEL_LEVEL': 0x194,         # Example ID for fuel level
    'ENGINE_TEMP': 0x195,        # Example ID for engine coolant temperature
    'BATTERY_VOLTAGE': 0x196,    # Example ID for battery voltage
}


def generate_random_can_data(length):
    """Generates a random bytearray of a given length."""
    return bytearray([random.randint(0, 255) for _ in range(length)])


def generate_realistic_data(can_id, state):
    """Generate realistic data based on CAN ID and vehicle state."""
    data = bytearray(8)  # Standard CAN frame has 8 bytes
    
    if can_id == CAN_IDS['VEHICLE_SPEED']:
        # Speed in km/h, typically in byte 0
        if state == 'idle':
            speed = random.randint(0, 5)
        elif state == 'driving':
            speed = random.randint(30, 100)
        elif state == 'highway':
            speed = random.randint(80, 120)
        else:  # default
            speed = random.randint(0, 120)
        data[0] = speed
        # Add some variation in other bytes
        data[1] = random.randint(0, 255)
        data[2] = random.randint(0, 255)
        
    elif can_id == CAN_IDS['ENGINE_RPM']:
        # RPM, typically in bytes 0-1 (RPM = (byte0*256 + byte1) / 4)
        if state == 'idle':
            rpm = random.randint(700, 900)
        elif state == 'driving':
            rpm = random.randint(1500, 3500)
        elif state == 'highway':
            rpm = random.randint(2000, 4000)
        else:  # default
            rpm = random.randint(700, 4000)
        data[0] = (rpm * 4) // 256
        data[1] = (rpm * 4) % 256
        # Add some variation in other bytes
        data[2] = random.randint(0, 255)
        data[3] = random.randint(0, 255)
        
    elif can_id == CAN_IDS['THROTTLE_POSITION']:
        # Throttle position as percentage in byte 0
        if state == 'idle':
            throttle = random.randint(0, 5)
        elif state == 'driving':
            throttle = random.randint(20, 80)
        elif state == 'highway':
            throttle = random.randint(30, 90)
        else:  # default
            throttle = random.randint(0, 100)
        data[0] = int(throttle * 2.55)  # Convert 0-100% to 0-255
        # Add some variation in other bytes
        data[1] = random.randint(0, 255)
        data[2] = random.randint(0, 255)
        
    elif can_id == CAN_IDS['BRAKE_PRESS']:
        # Brake pedal position as percentage in byte 0
        if state == 'idle':
            brake = random.randint(0, 5)
        elif state == 'driving':
            brake = random.randint(0, 30)
        elif state == 'braking':
            brake = random.randint(40, 100)
        else:  # default
            brake = random.randint(0, 100)
        data[0] = int(brake * 2.55)  # Convert 0-100% to 0-255
        # Add some variation in other bytes
        data[1] = random.randint(0, 255)
        
    elif can_id == CAN_IDS['STEERING_ANGLE']:
        # Steering wheel angle, typically in bytes 0-1
        # Range: -720 to +720 degrees, scaled to 0-65535
        angle = random.randint(-360, 360)  # -360 to +360 degrees
        scaled_angle = int((angle + 720) * (65535 / 1440))  # Scale to 0-65535
        data[0] = (scaled_angle >> 8) & 0xFF  # High byte
        data[1] = scaled_angle & 0xFF         # Low byte
        # Add some variation in other bytes
        data[2] = random.randint(0, 255)
        
    elif can_id == CAN_IDS['FUEL_LEVEL']:
        # Fuel level as percentage in byte 0
        fuel_level = random.randint(20, 100)  # 20-100% fuel
        data[0] = int(fuel_level * 2.55)  # Convert 0-100% to 0-255
        # Add some variation in other bytes
        data[1] = random.randint(0, 255)
        
    elif can_id == CAN_IDS['ENGINE_TEMP']:
        # Engine coolant temperature in °C, typically in byte 0
        # Range: -40 to +215°C, offset by 40
        temp = random.randint(80, 110)  # Normal operating temp: 80-110°C
        data[0] = temp + 40  # Offset by 40 as per OBD-II standard
        # Add some variation in other bytes
        data[1] = random.randint(0, 255)
        
    elif can_id == CAN_IDS['BATTERY_VOLTAGE']:
        # Battery voltage, typically in bytes 0-1 (Voltage = (byte0*256 + byte1) / 1000)
        voltage = random.uniform(12.0, 14.5)  # Normal range: 12.0-14.5V
        voltage_int = int(voltage * 1000)
        data[0] = (voltage_int >> 8) & 0xFF  # High byte
        data[1] = voltage_int & 0xFF         # Low byte
        # Add some variation in other bytes
        data[2] = random.randint(0, 255)
        
    elif can_id == CAN_IDS['HORN_PRESS']:
        # Horn press: 0x01 when pressed, 0x00 when released
        data[0] = 0x01 if random.random() < 0.05 else 0x00  # 5% chance of being pressed
        # Add some variation in other bytes
        data[1] = random.randint(0, 255)
        
    else:
        # For keep-alive and other messages, generate random data
        data = generate_random_can_data(8)
        
    return data


def generate_honda_accord_candump():
    """Generates a realistic candump log file for a Honda Accord."""
    try:
        # Create a virtual CAN interface for logging
        bus = can.Bus(channel='vcan0', bustype='virtual')
        
        # Log to file in the candump format
        with can.CanutilsLogWriter(LOG_FILE_NAME, channel='vcan0') as writer:
            print(f"Generating {MESSAGE_COUNT} realistic CAN messages for Honda Accord...")
            
            # Simulate different driving scenarios
            for i in range(MESSAGE_COUNT):
                # Determine current vehicle state
                if i < 50:
                    state = 'idle'  # Car is starting/idling
                elif i < 150:
                    state = 'driving'  # Normal driving
                elif i < 200:
                    state = 'braking'  # Braking
                elif i < 350:
                    state = 'highway'  # Highway driving
                elif i < 400:
                    state = 'driving'  # Back to normal driving
                else:
                    state = 'idle'  # Car is stopping/idling
                    
                # Always send the "keep-alive" message
                writer.on_message_received(can.Message(
                    arbitration_id=CAN_IDS['KEEP_ALIVE'],
                    data=generate_realistic_data(CAN_IDS['KEEP_ALIVE'], state),
                    is_extended_id=False
                ))
                
                # Send vehicle speed message
                writer.on_message_received(can.Message(
                    arbitration_id=CAN_IDS['VEHICLE_SPEED'],
                    data=generate_realistic_data(CAN_IDS['VEHICLE_SPEED'], state),
                    is_extended_id=False
                ))
                
                # Send engine RPM message
                writer.on_message_received(can.Message(
                    arbitration_id=CAN_IDS['ENGINE_RPM'],
                    data=generate_realistic_data(CAN_IDS['ENGINE_RPM'], state),
                    is_extended_id=False
                ))
                
                # Send throttle position message
                writer.on_message_received(can.Message(
                    arbitration_id=CAN_IDS['THROTTLE_POSITION'],
                    data=generate_realistic_data(CAN_IDS['THROTTLE_POSITION'], state),
                    is_extended_id=False
                ))
                
                # Occasionally send brake press
                if random.random() < 0.3:  # 30% chance
                    writer.on_message_received(can.Message(
                        arbitration_id=CAN_IDS['BRAKE_PRESS'],
                        data=generate_realistic_data(CAN_IDS['BRAKE_PRESS'], state),
                        is_extended_id=False
                    ))
                
                # Occasionally send steering angle
                if random.random() < 0.4:  # 40% chance
                    writer.on_message_received(can.Message(
                        arbitration_id=CAN_IDS['STEERING_ANGLE'],
                        data=generate_realistic_data(CAN_IDS['STEERING_ANGLE'], state),
                        is_extended_id=False
                    ))
                
                # Send fuel level periodically
                if i % 20 == 0:
                    writer.on_message_received(can.Message(
                        arbitration_id=CAN_IDS['FUEL_LEVEL'],
                        data=generate_realistic_data(CAN_IDS['FUEL_LEVEL'], state),
                        is_extended_id=False
                    ))
                
                # Send engine temperature periodically
                if i % 15 == 0:
                    writer.on_message_received(can.Message(
                        arbitration_id=CAN_IDS['ENGINE_TEMP'],
                        data=generate_realistic_data(CAN_IDS['ENGINE_TEMP'], state),
                        is_extended_id=False
                    ))
                
                # Send battery voltage periodically
                if i % 25 == 0:
                    writer.on_message_received(can.Message(
                        arbitration_id=CAN_IDS['BATTERY_VOLTAGE'],
                        data=generate_realistic_data(CAN_IDS['BATTERY_VOLTAGE'], state),
                        is_extended_id=False
                    ))
                
                # Simulate a horn press at specific times
                if i == 100 or i == 300:
                    writer.on_message_received(can.Message(
                        arbitration_id=CAN_IDS['HORN_PRESS'],
                        data=bytearray([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
                        is_extended_id=False
                    ))
                    # Send a release message shortly after
                    time.sleep(0.01)
                    writer.on_message_received(can.Message(
                        arbitration_id=CAN_IDS['HORN_PRESS'],
                        data=bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
                        is_extended_id=False
                    ))
                
                # Add a small delay for realistic timestamps
                time.sleep(random.uniform(0.01, 0.05))
            
        print(f"Log file '{LOG_FILE_NAME}' created successfully.")
        print(f"Generated {MESSAGE_COUNT} simulated CAN messages.")
        
    except Exception as e:
        print(f"An error occurred: {e}")


def read_candump_file():
    """Read and display the contents of the generated candump file."""
    try:
        print(f"\nReading generated candump file '{LOG_FILE_NAME}':")
        print("-" * 50)
        
        with open(LOG_FILE_NAME, 'r') as f:
            lines = f.readlines()
            # Show first 10 lines
            for i, line in enumerate(lines[:10]):
                print(line.strip())
            
            if len(lines) > 10:
                print("...")
                # Show last 5 lines
                for line in lines[-5:]:
                    print(line.strip())
                    
        print(f"\nTotal lines in file: {len(lines)}")
        
    except Exception as e:
        print(f"Error reading candump file: {e}")


if __name__ == "__main__":
    generate_honda_accord_candump()
    read_candump_file()