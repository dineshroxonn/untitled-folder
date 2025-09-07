#!/usr/bin/env python3
"""
Test different baud rates for OBD communication
"""
import serial
import time

def test_baud_rates():
    """Test different baud rates to find one that works"""
    baud_rates = [9600, 19200, 38400, 57600, 115200]
    
    for baudrate in baud_rates:
        print(f"\n--- Testing baud rate: {baudrate} ---")
        
        try:
            ser = serial.Serial(
                port='/dev/cu.OBDIIADAPTER',
                baudrate=baudrate,
                timeout=3,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS
            )
            
            print(f"Connected at {baudrate}")
            
            # Flush and wait
            ser.flushInput()
            time.sleep(1)
            
            # Try different line endings
            for cmd in ["ATZ\r", "ATZ\n", "ATZ\r\n"]:
                print(f"Sending with ending: {repr(cmd)}")
                ser.write(cmd.encode())
                ser.flush()
                time.sleep(2)
                
                if ser.in_waiting > 0:
                    response = ser.read(ser.in_waiting)
                    print(f"Response: {response}")
                    try:
                        decoded = response.decode('utf-8', errors='ignore')
                        print(f"Decoded: {repr(decoded)}")
                        if "ELM" in decoded.upper() or ">" in decoded:
                            print(f"*** FOUND WORKING CONFIGURATION ***")
                            print(f"Baudrate: {baudrate}")
                            print(f"Line ending: {repr(cmd)}")
                            ser.close()
                            return baudrate, cmd
                    except Exception as e:
                        print(f"Decode error: {e}")
                else:
                    print("No response")
                    
            ser.close()
            
        except Exception as e:
            print(f"Error at {baudrate}: {e}")
    
    print("No working configuration found")
    return None, None

if __name__ == "__main__":
    test_baud_rates()