#!/usr/bin/env python3
"""
Minimal Mobile Approach

This script uses the absolute minimal approach that mobile apps use.
"""

import serial
import time

def minimal_mobile_approach():
    """Use the absolute minimal approach like mobile apps."""
    print("Minimal Mobile Approach")
    print("=" * 21)
    
    try:
        # Exactly like mobile apps - minimal settings
        ser = serial.Serial('/dev/cu.OBDIIADAPTER', 38400)
        
        print("✅ Serial connection opened")
        
        # Mobile apps do this exact sequence:
        # 1. Wait after opening (critical!)
        print("Waiting 2 seconds (critical step)...")
        time.sleep(2)
        
        # 2. Send single reset
        print("Sending single reset...")
        ser.write(b'ATZ\r')
        
        # 3. Wait for response
        print("Waiting for response...")
        time.sleep(1)
        
        # 4. Read response
        response = ser.read_all()
        if response:
            decoded = response.decode('utf-8', errors='ignore').strip()
            print(f"Response: {repr(decoded)}")
            
            # Check if it's a valid ELM327 response
            if 'ELM' in decoded.upper() or 'V1.' in decoded.upper():
                print("✅ ELM327 adapter confirmed!")
                adapter_confirmed = True
            else:
                print("⚠️  Got response but not clearly ELM327")
                adapter_confirmed = True
        else:
            print("⚠️  No response to reset")
            adapter_confirmed = False
        
        # 5. If adapter confirmed, try vehicle detection
        if adapter_confirmed:
            print("\nTesting vehicle detection...")
            
            # Send vehicle voltage query
            ser.flushInput()
            ser.write(b'ATRV\r')
            time.sleep(2)
            
            response = ser.read_all()
            if response:
                decoded = response.decode('utf-8', errors='ignore').strip()
                print(f"Voltage response: {repr(decoded)}")
                
                # Look for voltage reading
                if any(c.isdigit() for c in decoded) and ('V' in decoded.upper() or '.' in decoded):
                    print("✅ Vehicle detected via voltage!")
                    vehicle_detected = True
                elif 'NO DATA' in decoded.upper():
                    print("⚠️  Adapter works but no vehicle data (ignition off?)")
                    vehicle_detected = False
                else:
                    print("⚠️  Unclear response")
                    vehicle_detected = False
            else:
                print("⚠️  No voltage response")
                vehicle_detected = False
        
        # Clean up
        ser.close()
        print("\n✅ Minimal approach completed")
        return adapter_confirmed, vehicle_detected
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, False

def try_different_delays():
    """Try different timing approaches."""
    print("Different Timing Approaches")
    print("=" * 25)
    
    delays = [0.5, 1.0, 1.5, 2.0, 3.0]
    
    for delay in delays:
        print(f"\nTesting with {delay} second delay...")
        
        try:
            ser = serial.Serial('/dev/cu.OBDIIADAPTER', 38400, timeout=1)
            time.sleep(delay)
            
            ser.write(b'ATZ\r')
            time.sleep(1)
            
            response = ser.read_all()
            if response:
                decoded = response.decode('utf-8', errors='ignore').strip()
                print(f"  Response with {delay}s delay: {repr(decoded)}")
                if 'ELM' in decoded.upper():
                    print(f"  ✅ Success with {delay} second delay!")
                    ser.close()
                    return delay
            
            ser.close()
        except Exception as e:
            print(f"  Failed with {delay}s delay: {e}")
    
    print("❌ No delay worked")
    return None

def direct_prompt_test():
    """Test sending just carriage return like many mobile apps do."""
    print("Direct Prompt Test")
    print("=" * 17)
    
    try:
        ser = serial.Serial('/dev/cu.OBDIIADAPTER', 38400, timeout=1)
        time.sleep(2)  # Critical wait
        
        # Many mobile apps just send carriage return to see if there's a prompt
        print("Sending carriage return to check for prompt...")
        ser.write(b'\r')
        time.sleep(0.5)
        
        response = ser.read_all()
        if response:
            decoded = response.decode('utf-8', errors='ignore').strip()
            print(f"Prompt response: {repr(decoded)}")
            
            if '>' in decoded:
                print("✅ Found ELM327 prompt character!")
                prompt_found = True
            else:
                print("⚠️  Got response but no prompt character")
                prompt_found = False
        else:
            print("⚠️  No prompt response")
            prompt_found = False
        
        ser.close()
        return prompt_found
        
    except Exception as e:
        print(f"❌ Prompt test failed: {e}")
        return False

if __name__ == "__main__":
    print("OBD Minimal Mobile Approach Test")
    print("=" * 32)
    
    print("Mobile apps succeed because they use minimal, focused approaches.")
    print()
    
    # Try direct prompt test first (many mobile apps do this)
    print("Step 1: Direct prompt test...")
    prompt_found = direct_prompt_test()
    
    print()
    
    # Try minimal approach
    print("Step 2: Minimal mobile approach...")
    adapter_ok, vehicle_ok = minimal_mobile_approach()
    
    print()
    
    # Try different delays if needed
    if not adapter_ok:
        print("Step 3: Testing different timing...")
        best_delay = try_different_delays()
        if best_delay:
            print(f"✅ Best delay found: {best_delay} seconds")
    
    print("\n" + "=" * 50)
    print("MINIMAL MOBILE APPROACH RESULTS")
    print("=" * 50)
    print(f"Prompt found: {'Yes' if prompt_found else 'No'}")
    print(f"Adapter OK: {'Yes' if adapter_ok else 'No'}")
    print(f"Vehicle detected: {'Yes' if vehicle_ok else 'No (check ignition)'}")
    print()
    print("Key insight: Mobile apps work because they:")
    print("1. Use minimal initialization")
    print("2. Wait the right amount of time")
    print("3. Send simple commands")
    print("4. Don't over-complicate the connection")