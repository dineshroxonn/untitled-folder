#!/usr/bin/env python3
"""
Mac OBD Connector - Complete Solution for Connecting ELM327 OBD2 Scanner to MacBook Air

Features:
- Automatic detection of Bluetooth OBD devices (excluding macOS placeholders)
- Proper serial port path identification for macOS
- Connection with optimized parameters for Bluetooth devices
- Comprehensive testing and diagnostics
"""

import obd
import serial
import serial.tools.list_ports
import subprocess
import time
import sys
from typing import List, Dict, Optional


class MacOBDConnector:
    """Complete solution for connecting ELM327 OBD2 scanners to MacBook Air"""

    def __init__(self):
        self.obd_port: Optional[str] = None
        self.connection: Optional[obd.OBD] = None

    def scan_bluetooth_devices(self) -> List[Dict[str, str]]:
        print("🔍 Scanning for Bluetooth OBD devices...")
        try:
            result = subprocess.run(
                ['system_profiler', 'SPBluetoothDataType'],
                capture_output=True, text=True, timeout=15
            )
            if result.returncode != 0:
                print("⚠️  Failed to get Bluetooth information")
                return []
            lines = result.stdout.split('\n')
            obd_devices, current = [], {}
            in_section = False
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if 'Devices' in line and ('Paired' in line or 'Connected' in line):
                    in_section = True
                    continue
                if in_section:
                    if 'Device Name:' in line:
                        if current and self._is_obd_device(current.get('name', '')):
                            obd_devices.append(current)
                        current = {
                            'name': line.split(':',1)[1].strip(),
                            'address': '',
                            'connected': False
                        }
                    elif 'Device Address:' in line and current:
                        current['address'] = line.split(':',1)[1].strip()
                    elif 'Connected:' in line and current:
                        current['connected'] = 'yes' in line.split(':',1)[1].strip().lower()
            if current and self._is_obd_device(current.get('name', '')):
                obd_devices.append(current)
            return obd_devices
        except Exception as e:
            print(f"❌ Error scanning Bluetooth devices: {e}")
            return []

    def _is_obd_device(self, name: str) -> bool:
        return any(k in name.upper() for k in ['OBD', 'ELM327', 'OBDII', 'BLUE DRIVER', 'VGATE'])

    def scan_serial_ports(self) -> List[Dict[str, str]]:
        print("🔌 Scanning for serial ports...")
        try:
            ports = list(serial.tools.list_ports.comports())
            result = []
            for p in ports:
                info = {
                    'device': p.device,
                    'description': p.description or "n/a",
                    'manufacturer': p.manufacturer or "Unknown",
                    'is_obd': self._is_obd_serial_port(p)
                }
                result.append(info)
            return result
        except Exception as e:
            print(f"❌ Error scanning serial ports: {e}")
            return []

    def _is_obd_serial_port(self, port) -> bool:
        name = port.device.upper()
        desc = (port.description or "").upper()
        patterns = ['OBD', 'ELM327', 'BLUETOOTH', 'USB SERIAL', 'FTDI', 'CH340', 'CP2102', 'PL2303']
        return any(pat in name or pat in desc for pat in patterns)

    def find_obd_serial_port(self) -> Optional[str]:
        print("🔍 Looking for OBD serial port...")
        ports = self.scan_serial_ports()
        for p in ports:
            dn = p['device'].upper()
            if p['is_obd'] and 'INCOMING-PORT' not in dn:
                print(f"✅ Found OBD port: {p['device']}")
                return p['device']
        print("⚠️  No specific OBD port found; listing all:")
        for p in ports:
            print(f"  - {p['device']} ({'OBD' if p['is_obd'] else 'non-OBD'})")
        return None

    def test_serial_connection(self, port: str, baudrate: int = 38400) -> bool:
        print(f"🧪 Testing serial connection to {port} at {baudrate} baud...")
        try:
            ser = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=3,
                write_timeout=3,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS
            )
            time.sleep(1)
            ser.reset_input_buffer()
            ser.write(b"ATZ\r")
            ser.flush()
            time.sleep(2)
            resp = ser.read(ser.in_waiting or 128)
            ser.close()
            if resp and any(x in resp.decode(errors='ignore').upper() for x in ['ELM', 'OK', '>']):
                print("✅ ELM327 response detected")
                return True
            print("⚠️  No valid response")
            return False
        except Exception as e:
            print(f"❌ Serial connection failed: {e}")
            return False

    def connect_with_obd_library(self, port: str) -> bool:
        print(f"🔌 Connecting with python-obd to {port}...")
        try:
            # Add delay to ensure Bluetooth connection is fully established
            time.sleep(2)
            
            # Convert /dev/cu.* to /dev/tty.* for python-obd compatibility
            tty_port = port.replace('/dev/cu.', '/dev/tty.')
            self.connection = obd.OBD(
                portstr=tty_port,
                baudrate=38400,
                fast=False,
                timeout=45
            )
            if self.connection.is_connected():
                print("✅ Connected with python-obd")
                print(f"📡 Protocol: {self.connection.protocol_name()}")
                return True
            print("❌ python-obd connection failed")
            return False
        except Exception as e:
            print(f"❌ Error connecting with python-obd: {e}")
            return False

    def test_obd_commands(self) -> bool:
        if not self.connection or not self.connection.is_connected():
            return False
        print("🧪 Testing basic OBD commands...")
        for cmd in [obd.commands.ELM_VERSION, obd.commands.ELM_VOLTAGE, obd.commands.RPM]:
            resp = self.connection.query(cmd)
            tag = cmd.name
            if not resp.is_null():
                print(f"✅ {tag}: {resp.value}")
            else:
                print(f"⚠️  {tag}: no data")
        return True

    def disconnect(self):
        if self.connection:
            self.connection.close()
            print("🔌 Disconnected")

    def run_diagnostics(self) -> bool:
        print("="*60)
        print("🚗 Mac OBD Connector - Diagnostics")
        print("="*60)
        bt = self.scan_bluetooth_devices()
        if bt:
            print(f"✅ Found {len(bt)} Bluetooth devices")
        else:
            print("⚠️  No Bluetooth OBD devices found")
        sp = self.scan_serial_ports()
        if not sp:
            print("❌ No serial ports found")
            return False
        port = self.find_obd_serial_port()
        if not port:
            return False
        if not self.test_serial_connection(port):
            return False
        if not self.connect_with_obd_library(port):
            return False
        return self.test_obd_commands()


def main():
    connector = MacOBDConnector()
    try:
        if connector.run_diagnostics():
            print("\n🎉 SUCCESS: Connected to OBD device!")
            choice = input("Keep connection alive? (y/n): ")
            if choice.lower() == 'y':
                print("Press Ctrl+C to exit")
                while True:
                    time.sleep(1)
        else:
            print("\n❌ FAILED: Could not connect to OBD device.")
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user")
    finally:
        connector.disconnect()


if __name__ == "__main__":
    main()
