#!/usr/bin/env python3
"""
Set Baseline Vector for Septentrio Dual-Antenna Heading
Configures the antenna geometry for attitude determination
"""

import serial
import time

def set_baseline():
    print("=" * 80)
    print("  SEPTENTRIO BASELINE VECTOR CONFIGURATION")
    print("=" * 80)
    print()
    print("This will configure the antenna baseline geometry.")
    print()
    
    # Get antenna configuration from user
    print("Antenna Configuration:")
    print()
    print("How are your antennas arranged?")
    print("  1) Front-to-Back (1m forward, 0m sideways)")
    print("  2) Left-to-Right (0m forward, 1m sideways)")
    print("  3) Custom (enter X, Y, Z manually)")
    print()
    
    choice = input("Enter choice (1/2/3): ").strip()
    
    if choice == '1':
        x, y, z = 1.0, 0.0, 0.0
        print(f"\n→ Setting baseline: Front-to-Back, 1m")
    elif choice == '2':
        x, y, z = 0.0, 1.0, 0.0
        print(f"\n→ Setting baseline: Left-to-Right, 1m")
    elif choice == '3':
        print("\nEnter baseline vector (in meters):")
        x = float(input("  X (forward/back): "))
        y = float(input("  Y (left/right): "))
        z = float(input("  Z (up/down): "))
        print(f"\n→ Setting baseline: X={x}m, Y={y}m, Z={z}m")
    else:
        print("Invalid choice")
        return
    
    print()
    print(f"[1] Connecting to GPS...")
    port = "/dev/tty.usbmodem38382103"
    
    try:
        ser = serial.Serial(port, 115200, timeout=2.0)
        time.sleep(0.5)
    except Exception as e:
        print(f"✗ Failed: {e}")
        return
    
    print("✓ Connected")
    print()
    
    # Clear buffer
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    time.sleep(0.2)
    
    print("[2] Sending baseline configuration...")
    print()
    
    # Septentrio command to set attitude offset (baseline vector)
    # Format: setAttitudeOffset, X, Y, Z
    cmd = f"setAttitudeOffset, {x}, {y}, {z}"
    
    print(f"Command: {cmd}")
    ser.write(f"{cmd}\r\n".encode('ascii'))
    time.sleep(1.0)
    
    # Read response
    response = []
    start = time.time()
    while time.time() - start < 2.0:
        if ser.in_waiting:
            line = ser.readline().decode('ascii', errors='ignore').strip()
            if line and not line.startswith('$'):  # Skip NMEA sentences
                response.append(line)
                print(f"  Response: {line}")
    
    print()
    
    # Try alternative command format
    print("[3] Trying alternative command format...")
    cmd2 = f"setAntennaOffset, Aux1, {x}, {y}, {z}"
    print(f"Command: {cmd2}")
    ser.write(f"{cmd2}\r\n".encode('ascii'))
    time.sleep(1.0)
    
    # Read response
    start = time.time()
    while time.time() - start < 2.0:
        if ser.in_waiting:
            line = ser.readline().decode('ascii', errors='ignore').strip()
            if line and not line.startswith('$'):
                print(f"  Response: {line}")
    
    print()
    
    # Save configuration
    print("[4] Attempting to save configuration...")
    for save_cmd in ["eccf, Current, Boot", "ecc, Current, Boot"]:
        print(f"Command: {save_cmd}")
        ser.write(f"{save_cmd}\r\n".encode('ascii'))
        time.sleep(1.0)
        
        start = time.time()
        while time.time() - start < 2.0:
            if ser.in_waiting:
                line = ser.readline().decode('ascii', errors='ignore').strip()
                if line and not line.startswith('$'):
                    print(f"  Response: {line}")
        print()
    
    ser.close()
    
    print("=" * 80)
    print("  CONFIGURATION SENT")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. Wait 5 minutes for heading to initialize")
    print("2. Run: python3 diagnose_gps_heading.py")
    print("3. Check for heading data in HDT sentences")
    print()
    print("If still no heading:")
    print("  → Check web interface for baseline vector settings")
    print("  → Try power cycling the GPS")
    print("  → Try swapping ANT1 ↔ ANT2 cables")
    print()

if __name__ == "__main__":
    set_baseline()
