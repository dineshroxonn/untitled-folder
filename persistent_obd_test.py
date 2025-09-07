#!/usr/bin/env python3
"""
Persistent OBD Connection Test

This script tests different approaches to maintain a persistent OBD connection
and identifies why connections might not be staying connected.
"""

import obd
import time
import serial
import threading

class PersistentOBDConnection:
    def __init__(self, port="/dev/cu.OBDIIADAPTER", baudrate=38400):
        self.port = port
        self.baudrate = baudrate
        self.connection = None
        self.is_connected = False
        self.keep_alive = False
        self.keep_alive_thread = None
        
    def connect(self):
        """Establish OBD connection"""
        print(f"Connecting to {self.port}...")
        try:
            self.connection = obd.OBD(
                portstr=self.port,
                baudrate=self.baudrate,
                protocol=None,
                fast=False,
                timeout=10.0
            )
            
            self.is_connected = self.connection.is_connected()
            if self.is_connected:
                print("✓ Connection established")
                print(f"  Protocol: {self.connection.protocol_name()}")
                print(f"  Port: {self.connection.port_name()}")
            else:
                print("✗ Connection failed")
                
            return self.is_connected
        except Exception as e:
            print(f"✗ Connection error: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """Close OBD connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
        self.is_connected = False
        self.stop_keep_alive()
        print("Connection closed")
    
    def start_keep_alive(self, interval=30):
        """Start keep-alive thread to maintain connection"""
        if not self.is_connected:
            print("Cannot start keep-alive: not connected")
            return False
            
        self.keep_alive = True
        self.keep_alive_thread = threading.Thread(target=self._keep_alive_worker, args=(interval,))
        self.keep_alive_thread.daemon = True
        self.keep_alive_thread.start()
        print(f"Keep-alive started (interval: {interval}s)")
        return True
    
    def stop_keep_alive(self):
        """Stop keep-alive thread"""
        self.keep_alive = False
        if self.keep_alive_thread and self.keep_alive_thread.is_alive():
            self.keep_alive_thread.join(timeout=5)
        print("Keep-alive stopped")
    
    def _keep_alive_worker(self, interval):
        """Worker function for keep-alive thread"""
        while self.keep_alive and self.is_connected:
            try:
                # Send a simple command to keep connection alive
                response = self.connection.query(obd.commands.ELM_VERSION)
                print(f"[Keep-alive] ELM Version: {response}")
                
                # Check connection status
                if not self.connection.is_connected():
                    print("[Keep-alive] Connection lost!")
                    self.is_connected = False
                    break
                    
            except Exception as e:
                print(f"[Keep-alive] Error: {e}")
                self.is_connected = False
                break
                
            time.sleep(interval)
    
    def is_still_connected(self):
        """Check if connection is still active"""
        if not self.connection:
            return False
        try:
            # Quick check with a simple command
            response = self.connection.query(obd.commands.ELM_VERSION, force=True)
            still_connected = not response.is_null()
            self.is_connected = still_connected
            return still_connected
        except:
            self.is_connected = False
            return False
    
    def query(self, command):
        """Query OBD command with reconnection if needed"""
        if not self.is_connected:
            print("Not connected. Attempting to reconnect...")
            if not self.connect():
                return None
        
        try:
            response = self.connection.query(command)
            return response
        except Exception as e:
            print(f"Query error: {e}")
            self.is_connected = False
            return None

def test_persistent_connection():
    """Test persistent connection behavior"""
    print("Testing Persistent OBD Connection")
    print("=" * 40)
    
    # Create persistent connection object
    obd_conn = PersistentOBDConnection()
    
    # Connect
    if not obd_conn.connect():
        print("Failed to establish initial connection")
        return
    
    # Start keep-alive
    obd_conn.start_keep_alive(interval=10)  # Send keep-alive every 10 seconds
    
    # Test multiple commands over time
    commands = [
        ("ELM Version", obd.commands.ELM_VERSION),
        ("Supported PIDs", obd.commands.PIDS_A),
        ("RPM", obd.commands.RPM),
        ("Speed", obd.commands.SPEED),
        ("Coolant Temp", obd.commands.COOLANT_TEMP),
    ]
    
    try:
        for i in range(3):  # Test 3 rounds
            print(f"\n--- Round {i+1} ---")
            
            # Check connection status
            if not obd_conn.is_still_connected():
                print("Connection lost. Reconnecting...")
                if not obd_conn.connect():
                    print("Reconnection failed")
                    break
            
            # Execute commands
            for name, cmd in commands:
                print(f"Querying {name}...")
                response = obd_conn.query(cmd)
                if response:
                    print(f"  {name}: {response}")
                else:
                    print(f"  {name}: No response")
                
                time.sleep(2)  # Wait between commands
            
            print(f"Round {i+1} completed. Waiting 5 seconds...")
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    finally:
        # Cleanup
        obd_conn.disconnect()

def test_manual_keep_alive():
    """Test manual keep-alive approach"""
    print("\nTesting Manual Keep-Alive Approach")
    print("=" * 40)
    
    try:
        # Establish connection
        connection = obd.OBD(
            portstr="/dev/cu.OBDIIADAPTER",
            baudrate=38400,
            protocol=None,
            fast=False,
            timeout=10.0
        )
        
        if not connection.is_connected():
            print("Failed to connect")
            return
        
        print("Connected successfully")
        
        # Function to send keep-alive command
        def send_keep_alive():
            try:
                response = connection.query(obd.commands.ELM_VERSION)
                print(f"[Keep-alive] Response: {response}")
                return True
            except Exception as e:
                print(f"[Keep-alive] Error: {e}")
                return False
        
        # Test connection longevity
        for i in range(5):
            print(f"\n--- Test Cycle {i+1} ---")
            
            # Send keep-alive
            if not send_keep_alive():
                print("Keep-alive failed")
                break
            
            # Check connection status
            if not connection.is_connected():
                print("Connection lost!")
                break
            
            # Wait before next cycle
            time.sleep(15)
        
        connection.close()
        print("Test completed")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Test persistent connection
    test_persistent_connection()
    
    # Test manual keep-alive
    test_manual_keep_alive()