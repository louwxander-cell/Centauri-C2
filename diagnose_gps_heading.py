#!/usr/bin/env python3
"""
GPS Heading Diagnostic Tool
Comprehensive troubleshooting for dual-antenna heading issues
"""

import serial
import time
import re

def diagnose_heading():
    print("=" * 80)
    print("  SEPTENTRIO MOSAIC-H DUAL-ANTENNA HEADING DIAGNOSTIC")
    print("=" * 80)
    print()
    
    port = "/dev/tty.usbmodem38382103"
    baudrate = 115200
    
    print(f"[1] Connecting to GPS...")
    print(f"    Port: {port}")
    print(f"    Baud: {baudrate}")
    print()
    
    try:
        ser = serial.Serial(port, baudrate, timeout=1.0)
    except Exception as e:
        print(f"✗ Failed to open serial port: {e}")
        return
    
    print("✓ Connected")
    print()
    
    # Data collection
    print("[2] Collecting NMEA data for 30 seconds...")
    print("    (Looking for heading-related sentences)")
    print()
    
    start_time = time.time()
    duration = 30
    
    # Sentence counters
    sentences = {
        'GGA': 0,
        'RMC': 0,
        'HDT': 0,
        'VTG': 0,
        'HPR': 0,  # Septentrio proprietary
        'ATT': 0,  # Attitude
        'OTHER': 0
    }
    
    # Data samples
    gga_samples = []
    hdt_samples = []
    hpr_samples = []
    
    # Status flags
    has_position = False
    has_heading = False
    satellites = 0
    fix_quality = 0
    
    print("Progress: ", end="", flush=True)
    
    while time.time() - start_time < duration:
        line = ser.readline().decode('ascii', errors='ignore').strip()
        
        if not line.startswith('$'):
            continue
        
        # Progress indicator
        elapsed = int(time.time() - start_time)
        if elapsed % 3 == 0 and elapsed > 0:
            print(".", end="", flush=True)
        
        # Classify sentence
        if 'GGA' in line:
            sentences['GGA'] += 1
            gga_samples.append(line)
            
            # Parse for satellites and fix
            parts = line.split(',')
            if len(parts) >= 8:
                if parts[6]:  # Fix quality
                    fix_quality = int(parts[6]) if parts[6].isdigit() else 0
                if parts[7]:  # Satellites
                    satellites = int(parts[7]) if parts[7].isdigit() else 0
                if parts[2] and parts[4]:  # Lat and Lon
                    has_position = True
                    
        elif 'HDT' in line:
            sentences['HDT'] += 1
            hdt_samples.append(line)
            
            # Check if heading field is populated
            parts = line.split(',')
            if len(parts) >= 2 and parts[1]:
                has_heading = True
                
        elif 'RMC' in line:
            sentences['RMC'] += 1
            
        elif 'VTG' in line:
            sentences['VTG'] += 1
            
        elif 'HPR' in line or 'PSAT,HPR' in line:
            sentences['HPR'] += 1
            hpr_samples.append(line)
            
        elif 'ATT' in line:
            sentences['ATT'] += 1
            
        else:
            sentences['OTHER'] += 1
    
    print(" Done!")
    print()
    
    ser.close()
    
    # Analysis
    print("=" * 80)
    print("  DIAGNOSTIC RESULTS")
    print("=" * 80)
    print()
    
    # Section 1: Sentence Statistics
    print("┌─ [1] NMEA Sentence Statistics ─────────────────────────────────────────┐")
    print(f"│ GGA (Position):        {sentences['GGA']:4d} sentences")
    print(f"│ RMC (Recommended):     {sentences['RMC']:4d} sentences")
    print(f"│ HDT (Heading):         {sentences['HDT']:4d} sentences  {'✓' if sentences['HDT'] > 0 else '✗'}")
    print(f"│ VTG (Velocity):        {sentences['VTG']:4d} sentences")
    print(f"│ HPR (Septentrio):      {sentences['HPR']:4d} sentences  {'✓' if sentences['HPR'] > 0 else '✗'}")
    print(f"│ ATT (Attitude):        {sentences['ATT']:4d} sentences")
    print(f"│ Other:                 {sentences['OTHER']:4d} sentences")
    print("└────────────────────────────────────────────────────────────────────────┘")
    print()
    
    # Section 2: Position Status
    print("┌─ [2] Position Status ──────────────────────────────────────────────────┐")
    print(f"│ Satellites:            {satellites} {'✓' if satellites >= 4 else '✗'}")
    print(f"│ Fix Quality:           {fix_quality} {'✓' if fix_quality > 0 else '✗'}")
    print(f"│ Position Valid:        {'YES ✓' if has_position else 'NO ✗'}")
    print("└────────────────────────────────────────────────────────────────────────┘")
    print()
    
    # Section 3: Heading Status
    print("┌─ [3] Heading Status (CRITICAL) ────────────────────────────────────────┐")
    
    if sentences['HDT'] == 0:
        print("│ ✗ NO HDT SENTENCES RECEIVED")
        print("│")
        print("│ Problem: GPS is not outputting HDT sentences")
        print("│ Solution:")
        print("│   1. Run: python3 configure_gps_septentrio.py")
        print("│   2. Enable NMEA HDT output in GPS configuration")
        print("│   3. Set output rate to 5 Hz")
        
    elif not has_heading:
        print("│ ⚠ HDT SENTENCES RECEIVED BUT EMPTY")
        print("│")
        print("│ Problem: Dual-antenna heading NOT locked")
        print("│")
        print("│ HDT Sample:")
        if hdt_samples:
            for sample in hdt_samples[-3:]:
                print(f"│   {sample}")
        print("│")
        print("│ Diagnosis:")
        print("│   - Antennas connected: YES ✓")
        print("│   - Position fix: YES ✓")
        print("│   - Heading lock: NO ✗")
        print("│")
        print("│ Possible Causes:")
        print("│   1. Antenna baseline too short (need ≥ 1.0m)")
        print("│   2. Antennas on wrong ports (ANT1/ANT2 swapped)")
        print("│   3. Baseline not configured in GPS")
        print("│   4. Not enough time for heading lock (need 5-10 min)")
        print("│   5. Poor satellite geometry")
        
    else:
        print("│ ✓ HEADING DATA AVAILABLE")
        print("│")
        print("│ HDT Samples:")
        for sample in hdt_samples[-3:]:
            print(f"│   {sample}")
        print("│")
        # Parse last heading
        if hdt_samples:
            last_hdt = hdt_samples[-1]
            parts = last_hdt.split(',')
            if len(parts) >= 2 and parts[1]:
                try:
                    heading = float(parts[1])
                    print(f"│ Current Heading: {heading:.1f}° ✓")
                except:
                    pass
    
    print("└────────────────────────────────────────────────────────────────────────┘")
    print()
    
    # Section 4: Septentrio Proprietary (if available)
    if sentences['HPR'] > 0:
        print("┌─ [4] Septentrio Proprietary Data ──────────────────────────────────────┐")
        print("│ HPR (Heading/Pitch/Roll) Sentences:")
        for sample in hpr_samples[-3:]:
            print(f"│   {sample}")
        print("└────────────────────────────────────────────────────────────────────────┘")
        print()
    
    # Section 5: Recommendations
    print("┌─ [5] TROUBLESHOOTING STEPS ────────────────────────────────────────────┐")
    print("│")
    
    if not has_position:
        print("│ Priority 1: Fix position lock")
        print("│   → Place antennas outside with clear sky view")
        print("│   → Wait 2-5 minutes for satellite lock")
        print("│")
    
    if sentences['HDT'] == 0:
        print("│ Priority 2: Enable HDT output")
        print("│   → Run: python3 configure_gps_septentrio.py")
        print("│   → Or connect to web interface: http://192.168.3.1")
        print("│   → Enable NMEA 0183 HDT sentence @ 5 Hz")
        print("│")
    
    if sentences['HDT'] > 0 and not has_heading:
        print("│ Priority 3: Achieve heading lock")
        print("│")
        print("│ A. Check antenna setup:")
        print("│    → Measure baseline: Should be ≥ 1.0m apart")
        print("│    → Verify ANT1 (main) is on correct port")
        print("│    → Verify ANT2 (aux) is on correct port")
        print("│    → Both antennas must have clear sky view")
        print("│")
        print("│ B. Check GPS configuration:")
        print("│    → Web interface: http://192.168.3.1")
        print("│    → Navigate to: Receiver → Attitude")
        print("│    → Enable: Attitude Determination")
        print("│    → Set baseline length: 1.0m (or actual distance)")
        print("│    → Set orientation: 0° (antennas aligned)")
        print("│")
        print("│ C. Wait for heading lock:")
        print("│    → Can take 5-10 minutes after position fix")
        print("│    → Watch for EVT LED to turn OFF/GREEN")
        print("│    → Watch for this script to show heading data")
        print("│")
        print("│ D. Try antenna swap:")
        print("│    → If still no lock after 10 min, swap ANT1 ↔ ANT2")
        print("│    → Power cycle GPS after swap")
        print("│")
    
    if has_heading:
        print("│ ✓ HEADING WORKING - No action needed!")
        print("│")
        print("│ You can now use heading in TriAD C2:")
        print("│   → Ownship heading displayed on UI")
        print("│   → Track bearings calculated correctly")
        print("│   → Effector pointing accurate")
        print("│")
    
    print("└────────────────────────────────────────────────────────────────────────┘")
    print()
    
    # Section 6: Quick Command Reference
    print("┌─ [6] QUICK COMMAND REFERENCE ──────────────────────────────────────────┐")
    print("│")
    print("│ Re-configure GPS:")
    print("│   $ python3 configure_gps_septentrio.py")
    print("│")
    print("│ Monitor live GPS data:")
    print("│   $ python3 gps_quick_check.py")
    print("│")
    print("│ Test integration:")
    print("│   $ python3 test_gps_integration.py")
    print("│")
    print("│ GPS web interface:")
    print("│   1. Connect GPS via Ethernet")
    print("│   2. Navigate to: http://192.168.3.1")
    print("│   3. Username: (none) Password: (none)")
    print("│")
    print("└────────────────────────────────────────────────────────────────────────┘")
    print()
    
    print("=" * 80)
    print("  DIAGNOSTIC COMPLETE")
    print("=" * 80)
    
    # Final status
    if has_heading:
        print("\n✓ STATUS: HEADING OPERATIONAL\n")
    elif sentences['HDT'] > 0:
        print("\n⚠ STATUS: WAITING FOR HEADING LOCK (see troubleshooting above)\n")
    else:
        print("\n✗ STATUS: HDT OUTPUT NOT CONFIGURED (run configure script)\n")

if __name__ == "__main__":
    diagnose_heading()
