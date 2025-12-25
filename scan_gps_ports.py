#!/usr/bin/env python3
"""
GPS Port Scanner
Scans all available COM ports to find the Septentrio GPS
"""

import serial
import serial.tools.list_ports
import time

def scan_ports():
    """Scan all available COM ports for GPS"""
    print("=" * 70)
    print("  GPS Port Scanner - Septentrio Mosaic-H")
    print("=" * 70)
    print()
    
    # List all available ports
    ports = list(serial.tools.list_ports.comports())
    
    if not ports:
        print("No COM ports found!")
        return
    
    print(f"Found {len(ports)} COM port(s):")
    print("-" * 70)
    for port in ports:
        print(f"  {port.device}: {port.description}")
        if port.manufacturer:
            print(f"    Manufacturer: {port.manufacturer}")
        if port.serial_number:
            print(f"    Serial: {port.serial_number}")
        print()
    
    print("=" * 70)
    print("Testing each port for NMEA data...")
    print("=" * 70)
    print()
    
    # Test each port
    for port in ports:
        test_port(port.device)
    
    print("=" * 70)
    print("Scan complete!")
    print("=" * 70)

def test_port(port_name):
    """Test a specific port for GPS data"""
    print(f"Testing {port_name}...")
    
    baudrates = [115200, 9600, 38400, 19200, 4800]
    
    for baud in baudrates:
        try:
            ser = serial.Serial(
                port=port_name,
                baudrate=baud,
                timeout=2.0
            )
            
            # Read for 3 seconds
            start = time.time()
            nmea_count = 0
            gps_found = False
            
            while time.time() - start < 3.0:
                try:
                    line = ser.readline().decode('ascii', errors='ignore').strip()
                    if line.startswith('$'):
                        nmea_count += 1
                        if nmea_count == 1:
                            print(f"  [OK] NMEA data found at {baud} baud!")
                            print(f"       First sentence: {line[:60]}...")
                            gps_found = True
                            break
                except:
                    pass
            
            ser.close()
            
            if gps_found:
                print(f"  [SUCCESS] GPS found on {port_name} at {baud} baud")
                print()
                return True
                
        except Exception as e:
            # Port not accessible or in use
            pass
    
    print(f"  [--] No GPS data on {port_name}")
    print()
    return False

if __name__ == "__main__":
    scan_ports()
