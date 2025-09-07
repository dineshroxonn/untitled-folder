#!/usr/bin/env python3
"""
Explicit Connection Then Data Retrieval

This script implements the pattern you requested:
1. Send explicit connection request first
2. Then retrieve all data using the established connection
"""

import serial
import time
import sys

class OBDConnection:
    """Manages OBD connection with explicit connect/disconnect."""
    
    def __init__(self, port='/dev/cu.OBDIIADAPTER', baudrate=38400):
        self.port = port
        self.baudrate = baudrate
        self.serial_conn = None
        self.is_connected = False
    
    def connect(self):
        """Step 1: Send explicit connection request."""
        print("Step 1: Sending explicit connection request...")
        
        try:
            # Open serial connection (this is the connection request)
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=2,
                write_timeout=2,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                xonxoff=False,
                rtscts=False,
                dsrdtr=False
            )
            
            print(f"✅ Serial connection established to {self.port}")
            
            # Important delay after opening connection
            time.sleep(1.5)
            
            # Flush buffers
            self.serial_conn.flushInput()
            self.serial_conn.flushOutput()
            
            # Send initialization sequence to "wake up" the adapter
            print("Initializing OBD adapter...")
            
            # Mobile apps typically send these commands in sequence
            init_commands = [
                ('ATZ', 'Reset adapter'),
                ('ATE0', 'Disable echo'),
                ('ATL0', 'Disable linefeeds'),
                ('ATS0', 'Disable spaces'),
                ('ATH0', 'Disable headers'),
                ('ATAT0', 'Adaptive timing off'),
                ('ATSP0', 'Automatic protocol selection'),
            ]
            
            for cmd, desc in init_commands:
                print(f"Sending {cmd} ({desc})...")
                self._send_command(cmd)
                time.sleep(0.5)  # Brief pause between commands
            
            self.is_connected = True
            print("✅ Connection request completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Connection request failed: {e}")
            self.is_connected = False
            return False
    
    def _send_command(self, command):
        """Send command and read response."""
        if not self.serial_conn:
            return None
        
        try:
            # Clear input buffer
            self.serial_conn.flushInput()
            
            # Send command
            self.serial_conn.write(f'{command}\r'.encode())
            
            # Wait for response
            time.sleep(1)
            
            # Read response
            response = self.serial_conn.read_all()
            if response:
                decoded = response.decode('utf-8', errors='ignore').strip()
                return decoded
            return None
            
        except Exception as e:
            print(f"Error sending command {command}: {e}")
            return None
    
    def retrieve_data(self):
        """Step 2: Retrieve all data using established connection."""
        print("\nStep 2: Retrieving data with established connection...")
        
        if not self.is_connected or not self.serial_conn:
            print("❌ Not connected to OBD adapter")
            return False
        
        try:
            # List of data to retrieve (in order of importance)
            data_queries = [
                ('ATI', 'Adapter Information'),
                ('ATRV', 'Vehicle Battery Voltage'),
                ('0100', 'Supported PIDs [01-20]'),
                ('010C', 'Engine RPM'),
                ('010D', 'Vehicle Speed'),
                ('0105', 'Coolant Temperature'),
                ('0104', 'Calculated Engine Load'),
                ('010B', 'Intake Manifold Pressure'),
                ('010F', 'Intake Air Temperature'),
                ('0111', 'Throttle Position'),
                ('03', 'Stored Diagnostic Codes'),
            ]
            
            results = {}
            
            for cmd, desc in data_queries:
                print(f"Querying {desc} ({cmd})...")
                
                response = self._send_command(cmd)
                if response:
                    print(f"  Response: {repr(response)}")
                    results[cmd] = response
                    
                    # Check if this looks like valid data
                    if 'NO DATA' in response.upper():
                        print(f"  ⚠️  No data available for {desc}")
                    elif 'ERROR' in response.upper():
                        print(f"  ⚠️  Error querying {desc}")
                    else:
                        print(f"  ✅ Valid data received for {desc}")
                else:
                    print(f"  ⚠️  No response for {desc}")
                    results[cmd] = None
                
                # Small delay between queries
                time.sleep(0.5)
            
            print(f"\n📊 Retrieved {len([r for r in results.values() if r])} responses out of {len(data_queries)} queries")
            return True
            
        except Exception as e:
            print(f"❌ Error retrieving data: {e}")
            return False
    
    def disconnect(self):
        """Cleanly disconnect from OBD adapter."""
        print("\nStep 3: Disconnecting from OBD adapter...")
        
        if self.serial_conn and self.serial_conn.is_open:
            try:
                # Send reset command before closing
                self._send_command('ATZ')
                time.sleep(0.5)
                
                # Close connection
                self.serial_conn.close()
                print("✅ Disconnected successfully")
            except Exception as e:
                print(f"⚠️  Error during disconnect: {e}")
        else:
            print("No active connection to close")
        
        self.is_connected = False

def main():
    """Main function implementing the two-step process."""
    print("OBD Data Retrieval - Two-Step Process")
    print("=" * 38)
    
    # Create OBD connection manager
    obd_conn = OBDConnection()
    
    try:
        # Step 1: Send explicit connection request
        if not obd_conn.connect():
            print("\n❌ Failed to establish connection")
            return
        
        # Step 2: Retrieve all data using established connection
        success = obd_conn.retrieve_data()
        
        if success:
            print("\n✅ Data retrieval completed successfully!")
        else:
            print("\n⚠️  Data retrieval completed with issues")
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Step 3: Always disconnect
        obd_conn.disconnect()

if __name__ == "__main__":
    main()