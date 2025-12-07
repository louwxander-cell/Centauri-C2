#!/usr/bin/env python3
"""Quick GPS status check - shows real-time satellite count"""

import serial
import sys
import time

def check_gps_status(port='/dev/tty.usbmodem38382103', baudrate=115200, duration=30):
    """Monitor GPS for satellite acquisition"""
    
    print("=" * 70)
    print("  GPS Quick Status Check")
    print("=" * 70)
    print(f"  Monitoring for {duration} seconds...")
    print(f"  Press Ctrl+C to stop")
    print("=" * 70)
    print()
    
    try:
        ser = serial.Serial(port, baudrate, timeout=1.0)
        start_time = time.time()
        last_print = 0
        
        satellites = 0
        fix_type = 0
        has_position = False
        has_heading = False
        
        while time.time() - start_time < duration:
            line = ser.readline().decode('ascii', errors='ignore').strip()
            
            if line.startswith('$GNGGA') or line.startswith('$GPGGA'):
                parts = line.split(',')
                if len(parts) >= 8:
                    # Check for position data
                    if parts[2] and parts[4]:  # Lat and Lon
                        has_position = True
                    if parts[7]:  # Number of satellites
                        try:
                            satellites = int(parts[7])
                        except:
                            pass
                    if parts[6]:  # Fix type
                        try:
                            fix_type = int(parts[6])
                        except:
                            pass
            
            elif line.startswith('$GNHDT') or line.startswith('$GPHDT'):
                parts = line.split(',')
                if len(parts) >= 2 and parts[1]:  # Heading value
                    has_heading = True
            
            # Print status every 2 seconds
            now = time.time()
            if now - last_print >= 2.0:
                elapsed = int(now - start_time)
                status = []
                
                if satellites > 0:
                    status.append(f"🛰️  Satellites: {satellites}")
                else:
                    status.append("🛰️  Satellites: 0 (NO SKY VIEW)")
                
                if fix_type == 0:
                    status.append("📍 Fix: NONE")
                elif fix_type == 1:
                    status.append("📍 Fix: GPS ✓")
                elif fix_type == 2:
                    status.append("📍 Fix: DGPS ✓")
                elif fix_type == 4:
                    status.append("📍 Fix: RTK Fixed ✓")
                elif fix_type == 5:
                    status.append("📍 Fix: RTK Float ✓")
                
                if has_position:
                    status.append("🌍 Position: YES ✓")
                else:
                    status.append("🌍 Position: NO")
                
                if has_heading:
                    status.append("🧭 Heading: YES ✓")
                else:
                    status.append("🧭 Heading: NO")
                
                print(f"[{elapsed:02d}s] " + " | ".join(status))
                last_print = now
        
        ser.close()
        
        print()
        print("=" * 70)
        print("  Final Status:")
        print("=" * 70)
        print(f"  Satellites: {satellites}")
        print(f"  Fix Type: {fix_type}")
        print(f"  Position: {'YES ✓' if has_position else 'NO ✗'}")
        print(f"  Heading: {'YES ✓' if has_heading else 'NO ✗'}")
        print("=" * 70)
        
        if satellites == 0:
            print()
            print("⚠️  NO SATELLITES - Antennas need clear sky view!")
            print()
        elif satellites < 4:
            print()
            print(f"⚠️  Only {satellites} satellites - Need 4+ for position fix")
            print()
        elif not has_position:
            print()
            print("⏳ Satellites visible but no fix yet - wait 30-60 more seconds")
            print()
        else:
            print()
            print("✅ GPS READY FOR INTEGRATION!")
            print()
        
    except KeyboardInterrupt:
        print("\n\nStopped by user")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_gps_status()
