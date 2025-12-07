#!/usr/bin/env python3
"""Test GPS integration with TriAD C2"""

import time
from src.drivers.gps_septentrio import SeptentrioMosaicDriver

def test_gps():
    print("="*70)
    print("  GPS Integration Test")
    print("="*70)
    
    # Initialize GPS
    port = "/dev/tty.usbmodem38382103"
    baudrate = 115200
    
    print(f"\n[1] Initializing GPS driver...")
    print(f"    Port: {port}")
    print(f"    Baud: {baudrate}")
    
    try:
        gps = SeptentrioMosaicDriver(port=port, baudrate=baudrate)
        gps.start_driver()  # Use start_driver() not start()
        print("[2] GPS driver started successfully ✓")
    except Exception as e:
        print(f"[2] GPS driver failed: {e} ✗")
        return
    
    # Wait for position fix
    print("\n[3] Waiting for GPS position fix...")
    print("    (This may take 30-60 seconds)")
    
    for i in range(30):
        time.sleep(2)
        data = gps.get_latest_position()
        
        if data['valid']:
            print(f"\n[4] GPS Position Acquired! ✓")
            print(f"    Latitude:  {data['latitude']:.6f}°")
            print(f"    Longitude: {data['longitude']:.6f}°")
            print(f"    Altitude:  {data['altitude']:.1f}m")
            print(f"    Heading:   {data['heading']:.1f}°")
            print(f"    Speed:     {data['speed_mps']:.1f} m/s")
            print(f"    Fix Quality: {data['fix_quality']}")
            print(f"    Heading Available: {data['heading_available']}")
            break
        else:
            print(f"    [{i*2:02d}s] Waiting... (no fix yet)")
    else:
        print("\n[4] Timeout - No GPS fix acquired ✗")
        print("    Check antenna placement and sky view")
    
    # Test continuous updates
    if data['valid']:
        print("\n[5] Testing continuous updates (10 seconds)...")
        start = time.time()
        update_count = 0
        
        while time.time() - start < 10:
            data = gps.get_latest_position()
            if data['valid']:
                update_count += 1
            time.sleep(0.1)
        
        print(f"    Updates received: {update_count} in 10 seconds")
        print(f"    Update rate: ~{update_count/10:.1f} Hz ✓")
    
    # Stop driver
    print("\n[6] Stopping GPS driver...")
    gps.stop_driver()
    print("    GPS driver stopped ✓")
    
    print("\n" + "="*70)
    print("  GPS Integration Test Complete")
    print("="*70)

if __name__ == "__main__":
    test_gps()
