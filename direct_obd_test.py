#!/usr/bin/env python3
"""
Direct OBD Connection Test
"""
import serial
import time

def test_obd_direct():
    try:
        print("Connecting to /dev/cu.OBDIIADAPTER...")
        ser = serial.Serial('/dev/cu.OBDIIADAPTER', 38400, timeout=2)
        print("Connected!")
        
        # Send reset command
        print("Sending ATZ...")
        ser.write(b'ATZ\r')
        time.sleep(1)
        response = ser.read_all()
        print(f"Response: {response}")
        
        # Send echo off command
        print("Sending ATE0...")
        ser.write(b'ATE0\r')
        time.sleep(1)
        response = ser.read_all()
        print(f"Response: {response}")
        
        # Send version command
        print("Sending ATI...")
        ser.write(b'ATI\r')
        time.sleep(1)
        response = ser.read_all()
        print(f"Response: {response}")
        
        ser.close()
        print("Connection closed.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_obd_direct()