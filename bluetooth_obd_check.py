#!/usr/bin/env python3
"""
Bluetooth OBD Device Checker

This script checks Bluetooth OBD devices and their connection status.
"""

import subprocess
import time

def check_bluetooth_devices():
    """Check Bluetooth devices and their connection status."""
    print("Bluetooth OBD Device Check")
    print("=" * 26)
    
    try:
        # Get Bluetooth device information
        result = subprocess.run(['system_profiler', 'SPBluetoothDataType'], 
                              capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            output = result.stdout
            lines = output.split('\n')
            
            # Look for OBD devices
            obd_devices = []
            current_device = {}
            in_devices_section = False
            
            for line in lines:
                if 'Devices (Paired, Connected, etc)' in line:
                    in_devices_section = True
                    continue
                
                if in_devices_section:
                    if line.strip().startswith('Device Name:'):
                        # Save previous device if it was an OBD device
                        if current_device and 'OBD' in current_device.get('name', '').upper():
                            obd_devices.append(current_device)
                        
                        # Start new device
                        current_device = {
                            'name': line.replace('Device Name:', '').strip(),
                            'address': '',
                            'connected': False
                        }
                    
                    elif line.strip().startswith('Device Address:'):
                        if current_device:
                            current_device['address'] = line.replace('Device Address:', '').strip()
                    
                    elif line.strip().startswith('Connected:'):
                        if current_device:
                            connected_status = line.replace('Connected:', '').strip().lower()
                            current_device['connected'] = connected_status == 'yes'
            
            # Don't forget the last device
            if current_device and 'OBD' in current_device.get('name', '').upper():
                obd_devices.append(current_device)
            
            if obd_devices:
                print(f"Found {len(obd_devices)} OBD device(s):")
                for i, device in enumerate(obd_devices):
                    status = "CONNECTED" if device['connected'] else "DISCONNECTED"
                    print(f"  {i+1}. {device['name']}")
                    print(f"      Address: {device['address']}")
                    print(f"      Status: {status}")
                    print()
            else:
                print("No OBD devices found in Bluetooth devices list")
                # Show all Bluetooth devices
                print("\nAll Bluetooth devices:")
                current_device = {}
                for line in lines:
                    if line.strip().startswith('Device Name:'):
                        current_device['name'] = line.replace('Device Name:', '').strip()
                    elif line.strip().startswith('Device Address:'):
                        if current_device:
                            current_device['address'] = line.replace('Device Address:', '').strip()
                            print(f"  - {current_device['name']} ({current_device['address']})")
                            current_device = {}
        else:
            print("Failed to get Bluetooth information")
            
    except Exception as e:
        print(f"Error checking Bluetooth devices: {e}")

def check_serial_ports():
    """Check serial ports for OBD devices."""
    print("\nSerial Port Check")
    print("=" * 17)
    
    try:
        import serial.tools.list_ports
        ports = list(serial.tools.list_ports.comports())
        
        if not ports:
            print("No serial ports found!")
            return
        
        print(f"Found {len(ports)} serial port(s):")
        obd_ports = []
        
        for port in ports:
            print(f"  - {port.device}")
            print(f"    Description: {port.description}")
            print(f"    Manufacturer: {port.manufacturer}")
            
            # Check if this looks like an OBD port
            if 'OBD' in port.device.upper() or 'OBD' in port.description.upper():
                obd_ports.append(port.device)
                print("    ⚠️  Potential OBD device")
        
        return obd_ports
        
    except Exception as e:
        print(f"Error checking serial ports: {e}")
        return []

def test_obd_bluetooth_connection():
    """Test connecting to OBD device via Bluetooth."""
    print("\nTesting OBD Bluetooth Connection")
    print("=" * 32)
    
    # First check if we have the OBD port
    try:
        import serial.tools.list_ports
        ports = list(serial.tools.list_ports.comports())
        obd_port = None
        
        for port in ports:
            if 'OBDIIADAPTER' in port.device:
                obd_port = port.device
                break
        
        if not obd_port:
            print("❌ OBD-II adapter port not found")
            return
        
        print(f"Found OBD port: {obd_port}")
        
        # Try to connect
        import serial
        try:
            ser = serial.Serial(
                port=obd_port,
                baudrate=38400,
                timeout=3,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS
            )
            
            print("✓ Serial connection established")
            
            # Send a simple command
            print("Sending ATZ (reset)...")
            ser.write(b'ATZ\r')
            time.sleep(2)
            
            response = ser.read_all()
            if response:
                decoded = response.decode('utf-8', errors='ignore').strip()
                print(f"Response: {repr(decoded)}")
                
                if 'ELM' in decoded.upper():
                    print("✅ ELM327 device detected!")
                else:
                    print("⚠️  Device responded but not recognized")
            else:
                print("⚠️  No response from device")
            
            ser.close()
            
        except Exception as e:
            print(f"❌ Failed to connect to {obd_port}: {e}")
            
    except Exception as e:
        print(f"Error in Bluetooth connection test: {e}")

if __name__ == "__main__":
    print("Bluetooth OBD Device Diagnostic")
    print("=" * 32)
    
    # Check Bluetooth devices
    check_bluetooth_devices()
    
    # Check serial ports
    obd_ports = check_serial_ports()
    
    # Test connection
    test_obd_bluetooth_connection()
    
    print("\n" + "=" * 50)
    print("BLUETOOTH OBD DIAGNOSTIC COMPLETE")
    print("=" * 50)