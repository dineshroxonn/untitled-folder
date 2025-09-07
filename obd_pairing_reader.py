#!/usr/bin/env python3
"""
OBD CAN Data Reader with Pairing Approach

This script demonstrates reading CAN data from OBD by first pairing
with the device rather than directly connecting, which can help
avoid resource conflicts.
"""

import asyncio
import serial
import serial.tools.list_ports
import time
import struct
import sys

class OBDPairingReader:
    """OBD CAN data reader using pairing approach."""
    
    def __init__(self):
        self.serial_conn = None
        self.device_path = None
    
    def find_obd_devices(self):
        """Find potential OBD devices."""
        print("Searching for OBD devices...")
        ports = list(serial.tools.list_ports.comports())
        
        obd_devices = []
        for port in ports:
            # Look for common OBD device patterns
            if any(pattern in port.device.upper() for pattern in ['OBD', 'ELM', 'UART', 'SERIAL']):
                obd_devices.append(port.device)
            elif any(pattern in port.description.upper() for pattern in ['OBD', 'ELM', 'UART', 'SERIAL']):
                obd_devices.append(port.device)
        
        # If no obvious OBD devices found, include the specific ones we know
        if not obd_devices:
            for port in ports:
                if 'OBDIIADAPTER' in port.device:
                    obd_devices.append(port.device)
        
        print(f"Found {len(obd_devices)} potential OBD device(s): {obd_devices}")
        return obd_devices
    
    def pair_with_device(self, device_path, baudrate=38400):
        """Pair with OBD device without fully connecting."""
        print(f"Pairing with device: {device_path}")
        
        try:
            # Open serial connection for pairing
            self.serial_conn = serial.Serial(
                port=device_path,
                baudrate=baudrate,
                timeout=2,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS
            )
            
            print("✓ Serial connection established for pairing")
            
            # Flush input/output
            self.serial_conn.flushInput()
            self.serial_conn.flushOutput()
            time.sleep(1)
            
            # Send reset command to establish basic communication
            print("Sending ATZ (reset) command...")
            self.serial_conn.write(b'ATZ\r')
            time.sleep(2)
            
            # Read response
            response = self.serial_conn.read_all()
            if response:
                decoded = response.decode('utf-8', errors='ignore')
                print(f"Device response: {repr(decoded)}")
                
                if 'ELM' in decoded.upper():
                    print("✓ Successfully paired with ELM327 device")
                    self.device_path = device_path
                    return True
                else:
                    print("⚠️  Device responded but doesn't appear to be ELM327")
                    return True
            else:
                print("⚠️  No response from device during pairing")
                return False
                
        except Exception as e:
            print(f"❌ Pairing failed: {e}")
            if self.serial_conn and self.serial_conn.is_open:
                self.serial_conn.close()
            self.serial_conn = None
            return False
    
    def read_can_data(self, timeout=5):
        """Read raw CAN data after pairing."""
        if not self.serial_conn or not self.serial_conn.is_open:
            print("❌ Not paired with device")
            return None
        
        try:
            print("Reading CAN data...")
            
            # Configure for CAN monitoring (if supported)
            commands = [
                ('ATE0', 'Turn off echo'),
                ('ATL1', 'Turn on linefeeds'),
                ('ATS1', 'Turn on spaces'),
                ('ATH1', 'Turn on headers'),
                ('ATCAF0', 'Turn off CAN auto formatting'),
            ]
            
            for cmd, desc in commands:
                print(f"Sending {cmd} ({desc})...")
                self.serial_conn.write(f'{cmd}\r'.encode())
                time.sleep(0.5)
                response = self.serial_conn.read_all()
                if response:
                    print(f"  Response: {repr(response.decode('utf-8', errors='ignore'))}")
            
            # Try to read live data
            print("Monitoring CAN bus for data...")
            start_time = time.time()
            data_packets = []
            
            while time.time() - start_time < timeout:
                if self.serial_conn.in_waiting > 0:
                    data = self.serial_conn.read(self.serial_conn.in_waiting)
                    if data:
                        decoded = data.decode('utf-8', errors='ignore')
                        if decoded.strip():
                            print(f"CAN Data: {repr(decoded)}")
                            data_packets.append(decoded)
                
                time.sleep(0.1)  # Small delay to prevent busy waiting
            
            return data_packets
            
        except Exception as e:
            print(f"❌ Error reading CAN data: {e}")
            return None
    
    def read_basic_obd_data(self):
        """Read basic OBD data after pairing."""
        if not self.serial_conn or not self.serial_conn.is_open:
            print("❌ Not paired with device")
            return None
        
        try:
            # Send a few basic OBD commands to get data
            basic_commands = [
                ('ATI', 'Device information'),
                ('ATRV', 'Vehicle voltage'),
                ('0100', 'Supported PIDs [01-20]'),
                ('010C', 'Engine RPM'),
                ('010D', 'Vehicle Speed'),
                ('0105', 'Coolant Temperature'),
            ]
            
            results = {}
            
            for cmd, desc in basic_commands:
                print(f"Querying {desc} ({cmd})...")
                self.serial_conn.write(f'{cmd}\r'.encode())
                time.sleep(1)
                
                response = self.serial_conn.read_all()
                if response:
                    decoded = response.decode('utf-8', errors='ignore').strip()
                    print(f"  Response: {repr(decoded)}")
                    results[cmd] = decoded
                else:
                    print(f"  No response")
                    results[cmd] = None
                
                time.sleep(0.5)  # Delay between commands
            
            return results
            
        except Exception as e:
            print(f"❌ Error reading OBD data: {e}")
            return None
    
    def disconnect(self):
        """Disconnect from the device."""
        if self.serial_conn and self.serial_conn.is_open:
            try:
                self.serial_conn.write(b'ATZ\r')  # Reset before closing
                time.sleep(0.5)
                self.serial_conn.close()
                print("✓ Disconnected from device")
            except Exception as e:
                print(f"⚠️  Error during disconnect: {e}")
        else:
            print("No active connection to close")

async def main():
    """Main function to demonstrate pairing approach."""
    print("OBD CAN Data Reader - Pairing Approach")
    print("=" * 40)
    
    reader = OBDPairingReader()
    
    try:
        # Step 1: Find OBD devices
        devices = reader.find_obd_devices()
        
        if not devices:
            print("❌ No OBD devices found")
            return
        
        # Step 2: Try pairing with each device
        paired = False
        for device in devices:
            print(f"\nAttempting to pair with {device}...")
            if reader.pair_with_device(device):
                paired = True
                break
            else:
                print(f"Failed to pair with {device}")
        
        if not paired:
            print("❌ Failed to pair with any OBD device")
            return
        
        print("\n✓ Successfully paired with OBD device!")
        
        # Step 3: Read basic OBD data
        print("\nReading basic OBD data...")
        basic_data = reader.read_basic_obd_data()
        
        if basic_data:
            print("\nBasic OBD Data Results:")
            for cmd, response in basic_data.items():
                if response:
                    print(f"  {cmd}: {response}")
                else:
                    print(f"  {cmd}: No response")
        
        # Step 4: Try reading CAN data
        print("\nAttempting to read CAN data...")
        can_data = reader.read_can_data(timeout=10)
        
        if can_data:
            print(f"\n✓ Read {len(can_data)} CAN data packets")
            for i, packet in enumerate(can_data[:5]):  # Show first 5 packets
                print(f"  Packet {i+1}: {repr(packet)}")
            if len(can_data) > 5:
                print(f"  ... and {len(can_data) - 5} more packets")
        else:
            print("⚠️  No CAN data received")
        
        print("\n✅ Pairing approach completed successfully!")
        
    except Exception as e:
        print(f"❌ Error in main execution: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Always disconnect
        reader.disconnect()

if __name__ == "__main__":
    asyncio.run(main())