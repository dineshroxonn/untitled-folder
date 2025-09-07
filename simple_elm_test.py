#!/usr/bin/env python3
"""
Simple ELM327 Communication Test
"""
import serial
import time

def test_elm327(port, baudrate=38400):
    print(f"Testing ELM327 on {port} at {baudrate} baud")
    
    try:
        # Open serial connection
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            timeout=2,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
        )
        
        print("Serial connection opened successfully")
        
        # Flush input
        ser.flushInput()
        time.sleep(0.5)
        
        # Send reset command
        print("Sending ATZ (reset)...")
        ser.write(b"ATZ\r")
        time.sleep(1)
        
        # Read response
        response = ser.read_all()
        if response:
            print(f"ATZ Response: {response}")
            try:
                decoded = response.decode('utf-8')
                print(f"Decoded: {decoded}")
            except:
                print("Could not decode response")
        else:
            print("No response to ATZ")
            
        # Send echo off
        print("Sending ATE0 (echo off)...")
        ser.write(b"ATE0\r")
        time.sleep(1)
        
        # Read response
        response = ser.read_all()
        if response:
            print(f"ATE0 Response: {response}")
            try:
                decoded = response.decode('utf-8')
                print(f"Decoded: {decoded}")
            except:
                print("Could not decode response")
        else:
            print("No response to ATE0")
            
        # Send protocol search
        print("Sending ATSP0 (auto protocol)...")
        ser.write(b"ATSP0\r")
        time.sleep(1)
        
        # Read response
        response = ser.read_all()
        if response:
            print(f"ATSP0 Response: {response}")
            try:
                decoded = response.decode('utf-8')
                print(f"Decoded: {decoded}")
            except:
                print("Could not decode response")
        else:
            print("No response to ATSP0")
            
        # Try to get supported PIDs
        print("Sending 0100 (supported PIDs)...")
        ser.write(b"0100\r")
        time.sleep(2)
        
        # Read response
        response = ser.read_all()
        if response:
            print(f"0100 Response: {response}")
            try:
                decoded = response.decode('utf-8')
                print(f"Decoded: {decoded}")
            except:
                print("Could not decode response")
        else:
            print("No response to 0100")
            
        ser.close()
        print("Test completed")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Test with the port from your output
    test_elm327("/dev/cu.OBDIIADAPTER")