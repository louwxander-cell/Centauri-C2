#!/usr/bin/env python3
"""
Configure Septentrio Mosaic-H for dual-antenna heading
Sends commands via serial port to enable heading mode
"""

import serial
import time
import sys

def configure_gps(port, baudrate=115200):
    """Configure GPS for dual-antenna heading"""
    
    print("=" * 70)
    print("  Septentrio Mosaic-H Configuration")
    print("=" * 70)
    print(f"  Port: {port}")
    print(f"  Baud: {baudrate}")
    print("=" * 70)
    print()
    
    try:
        # Open serial port
        print("[1/5] Opening serial port...")
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            timeout=2.0
        )
        print("✓ Port opened")
        time.sleep(0.5)
        
        # Clear any pending data
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        
        print()
        print("[2/5] Configuring NMEA output (GGA, RMC, HDT, VTG at 5 Hz)...")
        
        commands = [
            # Enable key NMEA sentences at 5 Hz (msec200 = 0.2 seconds = 5 Hz)
            "sno, Stream1, USB1, GGA, msec200\r\n",
            "sno, Stream1, USB1, RMC, msec200\r\n",
            "sno, Stream1, USB1, HDT, msec200\r\n",
            "sno, Stream1, USB1, VTG, msec200\r\n",
        ]
        
        for cmd in commands:
            ser.write(cmd.encode('ascii'))
            time.sleep(0.2)
            # Read response
            response = ser.read(ser.in_waiting).decode('ascii', errors='ignore')
            if response:
                print(f"  → {cmd.strip()}")
        
        print("✓ NMEA output configured")
        
        print()
        print("[3/5] Setting dual-antenna baseline (1.0m forward)...")
        
        # Configure heading baseline
        # Syntax: setHeadingBaseline, Length(m), Orientation(deg)
        baseline_cmd = "setHeadingBaseline, 1.0, 0.0\r\n"
        ser.write(baseline_cmd.encode('ascii'))
        time.sleep(0.5)
        response = ser.read(ser.in_waiting).decode('ascii', errors='ignore')
        print(f"  → Baseline: 1.0m, Orientation: 0° (forward)")
        print("✓ Baseline configured")
        
        print()
        print("[4/5] Enabling dual-antenna mode...")
        
        # Enable attitude/heading mode
        attitude_cmd = "setAttitudeMode, on\r\n"
        ser.write(attitude_cmd.encode('ascii'))
        time.sleep(0.5)
        response = ser.read(ser.in_waiting).decode('ascii', errors='ignore')
        print("✓ Attitude mode enabled")
        
        print()
        print("[5/5] Saving configuration to flash...")
        
        # Save to boot configuration
        save_cmd = "saveConfiguration, Boot\r\n"
        ser.write(save_cmd.encode('ascii'))
        time.sleep(1.0)
        response = ser.read(ser.in_waiting).decode('ascii', errors='ignore')
        print("✓ Configuration saved")
        
        # Close port
        ser.close()
        
        print()
        print("=" * 70)
        print("  ✓ CONFIGURATION COMPLETE")
        print("=" * 70)
        print()
        print("Next steps:")
        print("  1. Place antennas outside with clear sky view")
        print("  2. Wait 30-60 seconds for satellite acquisition")
        print("  3. Wait 30-60 seconds for heading lock")
        print("  4. Run test script again:")
        print(f"     python3 test_gps_connection.py {port} {baudrate}")
        print()
        
        return 0
        
    except serial.SerialException as e:
        print(f"✗ Serial error: {e}")
        return 1
    except Exception as e:
        print(f"✗ Error: {e}")
        return 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 configure_gps.py <port> [baudrate]")
        print()
        print("Example:")
        print("  python3 configure_gps.py /dev/tty.usbmodem38382103 115200")
        sys.exit(1)
    
    port = sys.argv[1]
    baudrate = int(sys.argv[2]) if len(sys.argv) > 2 else 115200
    
    sys.exit(configure_gps(port, baudrate))
