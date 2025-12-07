#!/usr/bin/env python3
"""
Detailed GPS diagnostic - shows what GPS is actually seeing
"""

import serial
import time
import sys

def diagnose_gps(port, baudrate=115200):
    """Show detailed GPS information"""
    
    print("=" * 70)
    print("  GPS Detailed Diagnostic")
    print("=" * 70)
    print(f"  Port: {port}")
    print(f"  Baud: {baudrate}")
    print("=" * 70)
    print()
    
    try:
        ser = serial.Serial(port=port, baudrate=baudrate, timeout=1.0)
        print("✓ Serial port opened")
        print()
        print("Reading GPS data for 30 seconds...")
        print("Looking for: Satellite info, fix status, error messages")
        print("-" * 70)
        
        start_time = time.time()
        sentences_seen = {}
        gga_count = 0
        satellites_visible = 0
        fix_type = 0
        
        while time.time() - start_time < 30:
            line = ser.readline().decode('ascii', errors='ignore').strip()
            
            if line.startswith('$'):
                # Count sentence types
                parts = line.split(',')
                sentence_type = parts[0]
                
                if sentence_type not in sentences_seen:
                    sentences_seen[sentence_type] = 0
                    print(f"\n[NEW] {sentence_type}")
                
                sentences_seen[sentence_type] += 1
                
                # Parse GGA for satellite info
                if 'GGA' in sentence_type and len(parts) >= 8:
                    if parts[7]:  # Number of satellites
                        try:
                            satellites_visible = int(parts[7])
                            if parts[6]:  # Fix quality
                                fix_type = int(parts[6])
                            
                            # Print every 5 seconds
                            if gga_count % 25 == 0:  # Assuming 5 Hz
                                print(f"\n[GGA] Satellites: {satellites_visible}, Fix Type: {fix_type}")
                                if fix_type == 0:
                                    print("      Fix Type 0 = No fix (not seeing enough satellites)")
                                elif fix_type == 1:
                                    print("      Fix Type 1 = GPS fix (standard accuracy)")
                                elif fix_type == 2:
                                    print("      Fix Type 2 = DGPS fix (differential)")
                                elif fix_type == 4:
                                    print("      Fix Type 4 = RTK fixed")
                                elif fix_type == 5:
                                    print("      Fix Type 5 = RTK float")
                            gga_count += 1
                        except:
                            pass
                
                # Show any error or status messages
                if 'ERROR' in line or 'error' in line:
                    print(f"\n⚠️  ERROR: {line}")
                
                if gga_count > 0 and gga_count % 100 == 0:
                    print(f"\n[{int(time.time() - start_time)}s] Still monitoring...")
        
        ser.close()
        
        print()
        print("-" * 70)
        print("\n📊 Summary:")
        print(f"   Satellites visible: {satellites_visible}")
        print(f"   Fix type: {fix_type}")
        print(f"   Sentence types seen: {len(sentences_seen)}")
        print()
        print("Sentences received:")
        for sentence, count in sorted(sentences_seen.items()):
            print(f"   {sentence}: {count}")
        
        print()
        print("=" * 70)
        
        if satellites_visible == 0:
            print("⚠️  PROBLEM: Not seeing ANY satellites")
            print()
            print("This means:")
            print("  - Antennas have no sky view")
            print("  - Antennas pointing wrong direction")
            print("  - Antenna cable disconnected")
            print("  - Antennas are indoors/blocked")
            print()
            print("Solutions:")
            print("  1. Check antennas point UP (flat surface to sky)")
            print("  2. Move to completely open area")
            print("  3. Check both antenna cables connected")
            print("  4. Try on flat roof or open field")
        elif satellites_visible < 4:
            print(f"⚠️  PROBLEM: Only seeing {satellites_visible} satellites (need 4+)")
            print()
            print("  - Partial sky view")
            print("  - Move to more open area")
        else:
            print(f"✓ Seeing {satellites_visible} satellites!")
            if fix_type == 0:
                print("  But no fix yet - wait a bit longer")
            else:
                print("  ✓ Has position fix!")
        
        print("=" * 70)
        
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 diagnose_gps.py <port> [baudrate]")
        print("Example: python3 diagnose_gps.py /dev/tty.usbmodem38382103 115200")
        sys.exit(1)
    
    port = sys.argv[1]
    baudrate = int(sys.argv[2]) if len(sys.argv) > 2 else 115200
    
    sys.exit(diagnose_gps(port, baudrate))
