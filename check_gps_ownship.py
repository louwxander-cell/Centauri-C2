#!/usr/bin/env python3
"""Check if GPS data is flowing to ownship in TriAD C2"""

import time
from src.drivers.gps_septentrio import SeptentrioMosaicDriver

def main():
    print("="*70)
    print("  GPS → Ownship Data Flow Test")
    print("="*70)
    
    # Start GPS
    gps = SeptentrioMosaicDriver(port="/dev/tty.usbmodem38382103", baudrate=115200)
    gps.start_driver()
    
    print("\nMonitoring GPS position updates for 20 seconds...")
    print("(This confirms data flow from GPS → Bridge → Ownship)\n")
    
    last_lat = None
    last_lon = None
    update_count = 0
    
    for i in range(20):
        time.sleep(1)
        data = gps.get_latest_position()
        
        if data['valid']:
            lat = data['latitude']
            lon = data['longitude']
            alt = data['altitude']
            hdg = data['heading']
            spd = data['speed_mps']
            
            # Check if position changed
            if last_lat != lat or last_lon != lon:
                update_count += 1
                last_lat = lat
                last_lon = lon
            
            print(f"[{i+1:02d}s] GPS: {lat:.6f}°, {lon:.6f}° | Alt: {alt:.1f}m | Hdg: {hdg:.1f}° | Spd: {spd:.1f}m/s")
        else:
            print(f"[{i+1:02d}s] GPS: No fix")
    
    gps.stop_driver()
    
    print("\n" + "="*70)
    print(f"  Position updates detected: {update_count}/20")
    if update_count > 0:
        print("  ✓ GPS data is flowing correctly!")
    else:
        print("  ⚠ GPS position appears static (may be stationary)")
    print("="*70)

if __name__ == "__main__":
    main()
