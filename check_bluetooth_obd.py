#!/usr/bin/env python3
"""
Bluetooth OBD Device Scanner

This script scans for Bluetooth devices and identifies which ones
might be OBD-II adapters that are not currently connected.
"""

import subprocess
import sys
import time
import serial.tools.list_ports
import re

def scan_bluetooth_devices():
    """Scan for Bluetooth devices using system tools"""
    print("=== Scanning for Bluetooth devices ===")
    
    try:
        # For macOS, use system_profiler to get Bluetooth devices
        result = subprocess.run([
            'system_profiler', 'SPBluetoothDataType'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✓ Successfully scanned Bluetooth devices")
            return result.stdout
        else:
            print("✗ Failed to scan Bluetooth devices")
            print(f"Error: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        print("✗ Bluetooth scan timed out")
        return None
    except Exception as e:
        print(f"✗ Error scanning Bluetooth devices: {e}")
        return None

def parse_bluetooth_devices(output):
    """Parse Bluetooth device information from system_profiler output"""
    if not output:
        return []
    
    devices = []
    current_device = {}
    
    # Parse the system_profiler output
    lines = output.split('\n')
    device_section = False
    
    for line in lines:
        line = line.strip()
        
        # Look for device sections
        if 'Devices (Paired, Configured, etc):' in line:
            device_section = True
            continue
            
        if device_section and line.startswith('Device Address:'):
            # Save previous device if exists
            if current_device:
                devices.append(current_device)
            # Start new device
            current_device = {
                'address': line.replace('Device Address:', '').strip(),
                'name': 'Unknown',
                'connected': False,
                'services': []
            }
        elif device_section and current_device:
            if line.startswith('Device Name:'):
                current_device['name'] = line.replace('Device Name:', '').strip()
            elif line.startswith('Connectable:'):
                connectable = line.replace('Connectable:', '').strip().lower()
                current_device['connected'] = connectable == 'yes'
            elif line.startswith('Services:'):
                # Parse services
                services_line = line.replace('Services:', '').strip()
                if services_line and services_line != 'None':
                    current_device['services'] = [s.strip() for s in services_line.split(',')]
    
    # Add last device
    if current_device:
        devices.append(current_device)
    
    return devices

def list_serial_ports():
    """List all available serial ports"""
    print("\n=== Listing Serial Ports ===")
    ports = list(serial.tools.list_ports.comports())
    
    serial_devices = []
    for port in ports:
        device_info = {
            'device': port.device,
            'description': port.description,
            'manufacturer': port.manufacturer,
            'hwid': port.hwid
        }
        serial_devices.append(device_info)
        print(f"Device: {port.device}")
        print(f"  Description: {port.description}")
        print(f"  Manufacturer: {port.manufacturer}")
        print(f"  HWID: {port.hwid}")
        print()
    
    return serial_devices

def identify_obd_devices(devices, serial_ports):
    """Identify which Bluetooth devices might be OBD-II adapters"""
    print("=== Identifying Potential OBD-II Devices ===")
    
    obd_keywords = [
        'OBD', 'ELM327', 'OBDII', 'ODB', 'Vgate', 'BlueDriver', 
        'ScanTool', 'Torque', 'Carista', 'LELink', 'OBDLink'
    ]
    
    potential_obd_devices = []
    
    # Check Bluetooth devices
    for device in devices:
        is_obd_candidate = False
        device_name = device.get('name', '').upper()
        
        # Check if device name contains OBD-related keywords
        for keyword in obd_keywords:
            if keyword.upper() in device_name:
                is_obd_candidate = True
                break
        
        # Also check services for serial or communication services
        if not is_obd_candidate:
            for service in device.get('services', []):
                service_upper = service.upper()
                if 'SERIAL' in service_upper or 'COM' in service_upper or 'RFCOMM' in service_upper:
                    is_obd_candidate = True
                    break
        
        if is_obd_candidate:
            potential_obd_devices.append(device)
            print(f"✓ Potential OBD Device: {device.get('name')} ({device.get('address')})")
            print(f"  Connected: {'Yes' if device.get('connected') else 'No'}")
            if device.get('services'):
                print(f"  Services: {', '.join(device.get('services'))}")
            print()
    
    # Check serial ports for OBD patterns
    print("=== Checking Serial Ports for OBD Patterns ===")
    obd_patterns = [
        "OBD", "ELM327", "BLUETOOTH", "USB SERIAL", 
        "FTDI", "CH340", "CP2102", "PL2303", "UART"
    ]
    
    for port in serial_ports:
        is_obd_port = False
        description = port['description'].upper() if port['description'] else ""
        manufacturer = port['manufacturer'].upper() if port['manufacturer'] else ""
        device_name = port['device'].upper()
        
        for pattern in obd_patterns:
            if (pattern in description or 
                pattern in manufacturer or 
                pattern in device_name):
                is_obd_port = True
                break
        
        if is_obd_port:
            print(f"✓ Potential OBD Serial Port: {port['device']}")
            print(f"  Description: {port['description']}")
            print(f"  Manufacturer: {port['manufacturer']}")
            print()
    
    return potential_obd_devices

def check_unconnected_obd_devices(obd_devices):
    """Filter for OBD devices that are not currently connected"""
    print("=== Checking for Unconnected OBD Devices ===")
    
    unconnected_devices = []
    for device in obd_devices:
        if not device.get('connected', False):
            unconnected_devices.append(device)
            print(f"⚠️  Unconnected OBD Device: {device.get('name')} ({device.get('address')})")
    
    if not unconnected_devices:
        print("✓ No unconnected OBD devices found")
    
    return unconnected_devices

def main():
    """Main function to scan and identify unconnected OBD devices"""
    print("Bluetooth OBD Device Scanner")
    print("=" * 50)
    
    # Scan Bluetooth devices
    bt_output = scan_bluetooth_devices()
    
    if not bt_output:
        print("Could not scan Bluetooth devices. Exiting.")
        return
    
    # Parse Bluetooth devices
    bt_devices = parse_bluetooth_devices(bt_output)
    
    print(f"\nFound {len(bt_devices)} Bluetooth devices:")
    for device in bt_devices:
        print(f"  - {device.get('name')} ({device.get('address')})")
        print(f"    Connected: {'Yes' if device.get('connected') else 'No'}")
        if device.get('services'):
            print(f"    Services: {', '.join(device.get('services'))}")
        print()
    
    # List serial ports
    serial_ports = list_serial_ports()
    
    # Identify potential OBD devices
    potential_obd_devices = identify_obd_devices(bt_devices, serial_ports)
    
    # Check for unconnected OBD devices
    unconnected_obd_devices = check_unconnected_obd_devices(potential_obd_devices)
    
    print("\n" + "=" * 50)
    print("SCAN COMPLETE")
    print("=" * 50)
    
    if unconnected_obd_devices:
        print(f"\nFound {len(unconnected_obd_devices)} unconnected OBD device(s):")
        for device in unconnected_obd_devices:
            print(f"  - {device.get('name')} ({device.get('address')})")
        print("\nTo connect to these devices, you may need to:")
        print("1. Ensure the device is powered on")
        print("2. Pair it with your computer if not already paired")
        print("3. Check if it appears in the serial ports list")
        print("4. Use an OBD test script to verify connection")
    else:
        print("\nNo unconnected OBD devices found.")
        print("All identified OBD devices appear to be connected, or")
        print("no OBD devices were detected in your system.")

if __name__ == "__main__":
    main()