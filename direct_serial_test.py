#!/usr/bin/env python3
"""
Direct serial communication test
"""
import serial
import time

def test_serial_communication():
    """Test direct serial communication with the OBD adapter"""
    print("Testing direct serial communication with OBD adapter")
    
    try:
        # Open serial connection
        ser = serial.Serial(
            port='/dev/cu.OBDIIADAPTER',
            baudrate=38400,
            timeout=5,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
        )
        
        print("Serial connection opened successfully")
        
        # Flush input
        ser.flushInput()
        time.sleep(1)
        
        # Send reset command
        print("Sending ATZ command...")
        ser.write(b"ATZ\r")
        ser.flush()
        time.sleep(2)
        
        # Read response
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting)
            print(f"Response received: {response}")
            try:
                decoded = response.decode('utf-8', errors='ignore')
                print(f"Decoded response: {repr(decoded)}")
            except Exception as e:
                print(f"Error decoding response: {e}")
        else:
            print("No response received")
            
        # Try another command
        print("Sending ATE0 command...")
        ser.write(b"ATE0\r")
        ser.flush()
        time.sleep(2)
        
        # Read response
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting)
            print(f"Response received: {response}")
            try:
                decoded = response.decode('utf-8', errors='ignore')
                print(f"Decoded response: {repr(decoded)}")
            except Exception as e:
                print(f"Error decoding response: {e}")
        else:
            print("No response received")
            
        ser.close()
        print("Serial connection closed")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_serial_communication()