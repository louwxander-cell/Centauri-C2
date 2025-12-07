#!/usr/bin/env python3
"""
GPS Connection Test Script
Tests dual-antenna GPS connectivity and NMEA output before full integration.

Usage:
    python3 test_gps_connection.py /dev/ttyUSB0 9600
    python3 test_gps_connection.py COM3 115200
"""

import sys
import time
import serial

def test_gps_connection(port, baudrate):
    """Test GPS serial connection and parse NMEA sentences"""
    
    print("=" * 70)
    print("  GPS Connection Test")
    print("=" * 70)
    print(f"  Port: {port}")
    print(f"  Baud Rate: {baudrate}")
    print("=" * 70)
    print()
    
    try:
        # Open serial port
        print(f"[1/4] Opening serial port {port}...")
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=2.0
        )
        print(f"✓ Serial port opened successfully")
        print()
        
        # Read raw data
        print(f"[2/4] Reading raw NMEA data (10 seconds)...")
        print("-" * 70)
        
        sentence_count = 0
        sentence_types = {}
        start_time = time.time()
        position_found = False
        heading_found = False
        
        lat, lon, alt, heading = None, None, None, None
        
        while time.time() - start_time < 10.0:
            try:
                line = ser.readline().decode('ascii', errors='ignore').strip()
                
                if line.startswith('$'):
                    sentence_count += 1
                    
                    # Extract sentence type (e.g., GPGGA, GPHDT)
                    parts = line.split(',')
                    if parts:
                        sentence_type = parts[0]
                        sentence_types[sentence_type] = sentence_types.get(sentence_type, 0) + 1
                        
                        # Parse key sentences
                        if 'GGA' in sentence_type:
                            # Position fix
                            try:
                                if len(parts) > 6 and parts[2] and parts[4]:
                                    # Convert DDMM.MMMM to DD.DDDDDD
                                    lat_str = parts[2]
                                    lat_deg = float(lat_str[:2])
                                    lat_min = float(lat_str[2:])
                                    lat = lat_deg + (lat_min / 60.0)
                                    if parts[3] == 'S':
                                        lat = -lat
                                    
                                    lon_str = parts[4]
                                    lon_deg = float(lon_str[:3])
                                    lon_min = float(lon_str[3:])
                                    lon = lon_deg + (lon_min / 60.0)
                                    if parts[5] == 'W':
                                        lon = -lon
                                    
                                    if len(parts) > 9 and parts[9]:
                                        alt = float(parts[9])
                                    
                                    position_found = True
                            except (ValueError, IndexError):
                                pass
                        
                        elif 'HDT' in sentence_type:
                            # True heading (dual-antenna)
                            try:
                                if len(parts) > 1 and parts[1]:
                                    heading = float(parts[1])
                                    heading_found = True
                            except (ValueError, IndexError):
                                pass
                    
                    # Print first 5 sentences as examples
                    if sentence_count <= 5:
                        print(f"  {line}")
            
            except serial.SerialTimeoutException:
                pass
            except Exception as e:
                print(f"  Error reading: {e}")
        
        print("-" * 70)
        print()
        
        # Report statistics
        print(f"[3/4] Statistics:")
        print(f"  Total sentences: {sentence_count}")
        print(f"  Update rate: ~{sentence_count / 10:.1f} Hz")
        print()
        
        print(f"[4/4] Sentence types received:")
        for stype, count in sorted(sentence_types.items()):
            print(f"  {stype}: {count} sentences")
        print()
        
        # Validation
        print("=" * 70)
        print("  VALIDATION RESULTS")
        print("=" * 70)
        
        all_good = True
        
        # Check for NMEA output
        if sentence_count > 0:
            print("✓ GPS is outputting NMEA sentences")
        else:
            print("✗ NO NMEA sentences received")
            print("  → Check GPS power, cable, and baud rate")
            all_good = False
        
        # Check for position data
        if position_found and lat and lon:
            print(f"✓ Position fix acquired")
            print(f"  → Latitude: {lat:.6f}°")
            print(f"  → Longitude: {lon:.6f}°")
            if alt:
                print(f"  → Altitude: {alt:.1f}m")
        else:
            print("✗ NO position fix")
            print("  → Wait for satellite acquisition (1-2 minutes)")
            print("  → Verify clear sky view")
            all_good = False
        
        # Check for heading data (critical for dual-antenna)
        if heading_found and heading is not None:
            print(f"✓ True heading available (dual-antenna mode)")
            print(f"  → Heading: {heading:.1f}°")
        else:
            print("⚠ NO true heading (HDT sentence)")
            print("  → This may be a single-antenna GPS")
            print("  → Enable dual-antenna mode in GPS configuration")
            print("  → Check that $GPHDT sentence is enabled")
        
        # Check update rate
        if sentence_count >= 5:
            print(f"✓ Update rate is adequate ({sentence_count / 10:.1f} Hz)")
        else:
            print(f"⚠ Low update rate ({sentence_count / 10:.1f} Hz)")
            all_good = False
        
        print()
        
        if all_good and heading_found:
            print("=" * 70)
            print("  ✓ GPS READY FOR INTEGRATION")
            print("=" * 70)
            print()
            print("Next steps:")
            print("  1. Note your port and baud rate settings")
            print("  2. Update config/settings.json with these values")
            print("  3. Follow GPS_INTEGRATION_GUIDE.md for full integration")
        elif position_found:
            print("=" * 70)
            print("  ⚠ GPS PARTIALLY READY")
            print("=" * 70)
            print()
            print("Issues:")
            if not heading_found:
                print("  • No dual-antenna heading detected")
                print("    → Check GPS configuration for HDT output")
                print("    → Verify both antennas are connected")
            print()
            print("You can proceed with position-only integration,")
            print("but heading will be computed from motion (less accurate).")
        else:
            print("=" * 70)
            print("  ✗ GPS NOT READY")
            print("=" * 70)
            print()
            print("Troubleshooting:")
            print("  1. Check GPS power supply")
            print("  2. Verify serial cable connections")
            print("  3. Try different baud rates (4800, 9600, 19200, 38400, 115200)")
            print("  4. Allow 1-2 minutes for satellite acquisition")
            print("  5. Ensure clear sky view (4+ satellites needed)")
        
        print()
        
        # Close serial port
        ser.close()
        
    except serial.SerialException as e:
        print(f"✗ Serial port error: {e}")
        print()
        print("Common causes:")
        print("  • Port already in use by another program")
        print("  • Incorrect port name")
        print("  • Insufficient permissions (try: sudo usermod -a -G dialout $USER)")
        print("  • USB cable not connected")
        return 1
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        return 0
    except Exception as e:
        print(f"✗ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 test_gps_connection.py <port> [baudrate]")
        print()
        print("Examples:")
        print("  python3 test_gps_connection.py /dev/ttyUSB0 9600")
        print("  python3 test_gps_connection.py /dev/ttyACM0 115200")
        print("  python3 test_gps_connection.py COM3 9600")
        print()
        print("Common ports:")
        print("  Linux: /dev/ttyUSB0, /dev/ttyACM0, /dev/ttyS0")
        print("  Mac: /dev/tty.usbserial-XXXX")
        print("  Windows: COM3, COM4, COM5")
        print()
        print("Common baud rates:")
        print("  4800, 9600 (most common), 19200, 38400, 115200")
        sys.exit(1)
    
    port = sys.argv[1]
    baudrate = int(sys.argv[2]) if len(sys.argv) > 2 else 9600
    
    sys.exit(test_gps_connection(port, baudrate))
