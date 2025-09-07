#!/usr/bin/env python3
"""
OBD-II Connection Diagnostic
"""
import serial
import time
import serial.tools.list_ports

def check_bluetooth_connection():
    """Check if the Bluetooth device is properly connected"""
    print("=== Checking Bluetooth Connection ===")
    ports = list(serial.tools.list_ports.comports())
    
    for port in ports:
        if "OBD" in port.device.upper() or "OBD" in port.description.upper():
            print(f"Found OBD device: {port.device}")
            print(f"  Description: {port.description}")
            print(f"  Manufacturer: {port.manufacturer}")
            print(f"  Product: {port.product}")
            return port.device
    
    print("No OBD device found in port list")
    return None

def test_with_longer_timeout(port):
    """Test with longer timeouts and more detailed debugging"""
    print(f"\n=== Testing with longer timeout ===")
    
    baudrates = [38400, 9600, 19200, 57600, 115200]
    
    for baudrate in baudrates:
        print(f"\n--- Testing at {baudrate} baud ---")
        
        try:
            ser = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=5,  # Longer timeout
                write_timeout=5,  # Write timeout
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS
            )
            
            print(f"Connected at {baudrate} baud")
            
            # Flush and wait
            ser.flushInput()
            ser.flushOutput()
            time.sleep(2)
            
            # Send reset with different approaches
            print("Sending ATZ...")
            ser.write(b"ATZ\r")
            ser.flush()
            time.sleep(3)
            
            # Check if there's data available
            if ser.in_waiting > 0:
                response = ser.read(ser.in_waiting)
                print(f"Raw response: {response}")
                try:
                    decoded = response.decode('utf-8', errors='ignore')
                    print(f"Decoded: {repr(decoded)}")
                except Exception as e:
                    print(f"Decode error: {e}")
            else:
                print("No data available")
                
            ser.close()
            
        except Exception as e:
            print(f"Error at {baudrate} baud: {e}")

def check_system_bluetooth():
    """Check system Bluetooth status (macOS)"""
    print("\n=== Checking System Bluetooth ===")
    try:
        import subprocess
        result = subprocess.run(['system_profiler', 'SPBluetoothDataType'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            # Look for connected devices
            lines = result.stdout.split('\n')
            in_devices_section = False
            for line in lines:
                if 'Devices (Paired, Connected, etc)' in line:
                    in_devices_section = True
                    print("Bluetooth devices section found:")
                elif in_devices_section and line.strip() and not line.startswith(' ' * 4):
                    in_devices_section = False
                elif in_devices_section and 'Connected: Yes' in line:
                    print(f"  Connected device found: {line.strip()}")
                elif in_devices_section and 'OBD' in line or 'ELM' in line:
                    print(f"  OBD device: {line.strip()}")
        else:
            print("Could not get Bluetooth information")
    except Exception as e:
        print(f"Error checking Bluetooth: {e}")

if __name__ == "__main__":
    print("OBD-II Connection Diagnostic")
    print("=" * 40)
    
    # Check Bluetooth connection
    port = check_bluetooth_connection()
    
    if port:
        # Check system Bluetooth
        check_system_bluetooth()
        
        # Test with longer timeout
        test_with_longer_timeout(port)
    else:
        print("No OBD device found. Please check:")
        print("1. Is your OBD-II adapter plugged into the car?")
        print("2. Is the car's ignition ON?")
        print("3. Is the adapter paired with your computer?")
        print("4. Is Bluetooth enabled on your computer?")
