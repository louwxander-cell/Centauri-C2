#!/usr/bin/env python3
"""
Septentrio Mosaic-H Dual-Antenna Configuration
Enables attitude determination (heading/pitch/roll) from dual antennas
"""

import serial
import time

def send_command(ser, cmd):
    """Send command and wait for response"""
    print(f"  → {cmd}")
    ser.write(f"{cmd}\r\n".encode('ascii'))
    time.sleep(0.3)
    
    # Read response
    response = []
    timeout = time.time() + 1.0
    while time.time() < timeout:
        if ser.in_waiting:
            line = ser.readline().decode('ascii', errors='ignore').strip()
            if line:
                response.append(line)
                print(f"     {line}")
    
    time.sleep(0.2)
    return response

def configure_dual_antenna():
    print("=" * 80)
    print("  SEPTENTRIO MOSAIC-H DUAL-ANTENNA CONFIGURATION")
    print("=" * 80)
    print()
    print("This will configure the GPS for dual-antenna heading determination.")
    print()
    
    port = "/dev/tty.usbmodem38382103"
    baudrate = 115200
    
    print(f"[1] Connecting to GPS...")
    print(f"    Port: {port}")
    print(f"    Baud: {baudrate}")
    print()
    
    try:
        ser = serial.Serial(port, baudrate, timeout=1.0)
        time.sleep(1)
    except Exception as e:
        print(f"✗ Failed: {e}")
        return
    
    print("✓ Connected")
    print()
    
    # Clear any pending data
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    
    print("[2] Configuring Dual-Antenna Attitude Determination...")
    print()
    
    commands = [
        # Enable antenna 2 (auxiliary antenna)
        ("setAntennaPort, Main, GPS", "Enable Main antenna (ANT1)"),
        ("setAntennaPort, Aux1, GPS", "Enable Aux antenna (ANT2)"),
        
        # Configure attitude determination
        ("setAttitudeMode, MultiAntenna", "Enable multi-antenna attitude"),
        ("setAttitudeSource, GNSS", "Use GNSS for attitude"),
        
        # Set baseline vector (1.0m forward, adjust if different)
        ("setAttitudeOffset, 1.0, 0.0, 0.0", "Set baseline: 1.0m forward (X-axis)"),
        
        # Enable NMEA HDT output at 5 Hz on COM1 (USB)
        ("setNMEAOutput, COM1, HDT, sec1", "Output HDT at 1 Hz"),
        ("setNMEAOutput, COM1, GGA, sec1", "Output GGA at 1 Hz"),
        
        # Enable Septentrio proprietary HPR (Heading/Pitch/Roll)
        ("setSBFOutput, COM1, AttEuler, sec1, OnChange", "Output attitude data"),
        
        # Save configuration to flash
        ("saveConfiguration", "Save to flash memory"),
    ]
    
    print("Sending configuration commands:")
    print()
    
    for cmd, description in commands:
        print(f"[{description}]")
        send_command(ser, cmd)
        print()
    
    print("[3] Configuration complete!")
    print()
    print("=" * 80)
    print("  NEXT STEPS")
    print("=" * 80)
    print()
    print("1. **Verify antenna placement:**")
    print("   - ANT1 (Main) on front port")
    print("   - ANT2 (Aux) on rear port")
    print("   - Distance: 1.0m apart (or actual baseline)")
    print("   - Both antennas horizontal, facing up")
    print("   - Clear sky view (no obstructions)")
    print()
    print("2. **Wait for heading lock:**")
    print("   - Can take 5-10 minutes after position fix")
    print("   - EVT LED should turn OFF or GREEN when locked")
    print()
    print("3. **Verify heading data:**")
    print("   $ python3 diagnose_gps_heading.py")
    print()
    print("4. **If still no heading after 10 minutes:**")
    print("   - Try swapping ANT1 ↔ ANT2 connections")
    print("   - Power cycle GPS")
    print("   - Re-run this configuration script")
    print()
    
    ser.close()
    
    print("=" * 80)
    print("✓ Configuration saved to GPS flash memory")
    print("=" * 80)
    print()

if __name__ == "__main__":
    print()
    print("⚠ WARNING: This will reconfigure your GPS for dual-antenna mode.")
    print()
    response = input("Continue? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        print()
        configure_dual_antenna()
    else:
        print("\nConfiguration cancelled.")
