#!/usr/bin/env python3
"""
Enhanced ELM327 Communication Test
"""
import serial
import time

def test_elm327_enhanced(port, baudrates=[38400, 9600, 19200, 57600, 115200]):
    print(f"Enhanced ELM327 Test on {port}")
    
    for baudrate in baudrates:
        print(f"\n--- Testing at {baudrate} baud ---")
        
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
            
            print(f"Serial connection opened at {baudrate} baud")
            
            # Flush input
            ser.flushInput()
            time.sleep(1)
            
            # Try different line endings
            line_endings = ["\r", "\n", "\r\n"]
            
            for ending in line_endings:
                print(f"Trying line ending: {repr(ending)}")
                
                # Send reset command
                cmd = "ATZ" + ending
                print(f"Sending: {repr(cmd)}")
                ser.write(cmd.encode())
                time.sleep(2)
                
                # Read response
                response = ser.read_all()
                if response:
                    print(f"Response: {response}")
                    try:
                        decoded = response.decode('utf-8', errors='ignore')
                        print(f"Decoded: {repr(decoded)}")
                        if "ELM" in decoded.upper() or "OBD" in decoded.upper():
                            print(f"*** FOUND ELM327 at {baudrate} baud with {repr(ending)} ending! ***")
                            ser.close()
                            return baudrate, ending
                    except:
                        print("Could not decode response")
                else:
                    print("No response")
                    
            ser.close()
            
        except Exception as e:
            print(f"Error at {baudrate} baud: {e}")
    
    print("No working configuration found")
    return None, None

def test_with_working_config(port, baudrate, line_ending):
    """Test with the working configuration found"""
    print(f"\n=== Testing with confirmed settings ===")
    print(f"Port: {port}")
    print(f"Baudrate: {baudrate}")
    print(f"Line ending: {repr(line_ending)}")
    
    try:
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            timeout=2,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
        )
        
        ser.flushInput()
        time.sleep(1)
        
        # Test sequence
        commands = [
            ("ATZ", "Reset"),
            ("ATE0", "Echo off"),
            ("ATSP0", "Auto protocol"),
            ("ATDP", "Describe protocol"),
            ("0100", "Supported PIDs")
        ]
        
        for cmd, desc in commands:
            full_cmd = cmd + line_ending
            print(f"\n{desc} ({cmd}):")
            ser.write(full_cmd.encode())
            time.sleep(1)
            
            response = ser.read_all()
            if response:
                print(f"  Raw: {response}")
                try:
                    decoded = response.decode('utf-8', errors='ignore')
                    print(f"  Decoded: {repr(decoded)}")
                    lines = decoded.strip().split('\n')
                    for line in lines:
                        clean_line = line.strip()
                        if clean_line and not clean_line.startswith(cmd):
                            print(f"  Response: {clean_line}")
                except Exception as e:
                    print(f"  Decode error: {e}")
            else:
                print("  No response")
        
        ser.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Test with the port from your output
    baudrate, line_ending = test_elm327_enhanced("/dev/cu.OBDIIADAPTER")
    
    if baudrate and line_ending:
        test_with_working_config("/dev/cu.OBDIIADAPTER", baudrate, line_ending)
    else:
        print("Could not establish communication with ELM327 adapter")