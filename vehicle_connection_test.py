#!/usr/bin/env python3
"""
Vehicle Connection Test
"""
import serial
import time

def test_vehicle_connection():
    try:
        print("Connecting to /dev/cu.OBDIIADAPTER...")
        ser = serial.Serial('/dev/cu.OBDIIADAPTER', 38400, timeout=2)
        print("Connected!")
        
        # Send echo off
        ser.write(b'ATE0\r')
        time.sleep(1)
        ser.read_all()
        
        # Send headers on (for debugging)
        ser.write(b'ATH1\r')
        time.sleep(1)
        ser.read_all()
        
        # Try to read engine RPM (010C)
        print("Attempting to read engine RPM...")
        ser.write(b'010C\r')
        time.sleep(1)
        response = ser.read_all()
        print(f"RPM Response: {response}")
        
        # Try to read vehicle speed (010D)
        print("Attempting to read vehicle speed...")
        ser.write(b'010D\r')
        time.sleep(1)
        response = ser.read_all()
        print(f"Speed Response: {response}")
        
        # Try to read coolant temperature (0105)
        print("Attempting to read coolant temperature...")
        ser.write(b'0105\r')
        time.sleep(1)
        response = ser.read_all()
        print(f"Coolant Temp Response: {response}")
        
        ser.close()
        print("Connection closed.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_vehicle_connection()