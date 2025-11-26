#!/usr/bin/env python3
"""
Analyze Echoguard binary track data to understand packet structure
"""

import struct
import sys
from pathlib import Path

def parse_track_header(data):
    """Parse track packet header"""
    # From daa_track.h:
    # char packet_tag[12]
    # uint32_t packetSize
    # uint32_t nTracks
    # uint32_t sys_time_days
    # uint32_t sys_time_ms
    # uint32_t profile_atracker
    # uint32_t profile_atracker_main
    # uint32_t packet_type
    
    header_format = '<12sIIIIIII'  # Little-endian
    header_size = struct.calcsize(header_format)
    
    if len(data) < header_size:
        return None
    
    fields = struct.unpack(header_format, data[:header_size])
    
    return {
        'packet_tag': fields[0].decode('ascii', errors='ignore'),
        'packetSize': fields[1],
        'nTracks': fields[2],
        'sys_time_days': fields[3],
        'sys_time_ms': fields[4],
        'profile_atracker': fields[5],
        'profile_atracker_main': fields[6],
        'packet_type': fields[7],
        'header_size': header_size
    }

def parse_track_data(data):
    """Parse single track data structure"""
    # From daa_track.h - track_data structure
    # Total size: 248 bytes (62 fields * 4 bytes each)
    
    track_format = '<'  # Little-endian
    track_format += 'I'   # ID
    track_format += 'I'   # state
    track_format += 'fff' # azest, elest, rest
    track_format += 'fff' # xest, yest, zest
    track_format += 'fff' # velxest, velyest, velzest
    track_format += 'III' # assocMeas_id_main[3]
    track_format += 'fff' # assocMeas_chi2_main[3]
    track_format += 'ii'  # TOCA_days, TOCA_ms
    track_format += 'f'   # DOCA
    track_format += 'f'   # lifetime
    track_format += 'II'  # lastUpdateTime_days, lastUpdateTime_ms
    track_format += 'II'  # lastAssociatedDataTime_days, lastAssociatedDataTime_ms
    track_format += 'II'  # acquiredTime_days, acquiredTime_ms
    track_format += 'f'   # estConfidence
    track_format += 'I'   # numAssocMeasurements
    track_format += 'f'   # estRCS
    track_format += 'ff'  # probabilityOther, probabilityUAV
    
    track_size = struct.calcsize(track_format)
    
    if len(data) < track_size:
        return None, 0
    
    fields = struct.unpack(track_format, data[:track_size])
    
    track = {
        'ID': fields[0],
        'state': fields[1],
        'azest': fields[2],
        'elest': fields[3],
        'rest': fields[4],
        'xest': fields[5],
        'yest': fields[6],
        'zest': fields[7],
        'velxest': fields[8],
        'velyest': fields[9],
        'velzest': fields[10],
        'TOCA_days': fields[17],
        'TOCA_ms': fields[18],
        'DOCA': fields[19],
        'lifetime': fields[20],
        'lastUpdateTime_days': fields[21],
        'lastUpdateTime_ms': fields[22],
        'estConfidence': fields[27],
        'numAssocMeasurements': fields[28],
        'estRCS': fields[29],
        'probabilityOther': fields[30],
        'probabilityUAV': fields[31]
    }
    
    return track, track_size

def analyze_track_file(filepath):
    """Analyze a binary track file"""
    print(f"\n{'='*70}")
    print(f"Analyzing: {filepath}")
    print(f"{'='*70}\n")
    
    with open(filepath, 'rb') as f:
        data = f.read()
    
    print(f"File size: {len(data)} bytes\n")
    
    offset = 0
    packet_count = 0
    total_tracks = 0
    
    while offset < len(data):
        # Parse header
        header = parse_track_header(data[offset:])
        if not header:
            break
        
        packet_count += 1
        print(f"Packet #{packet_count}:")
        print(f"  Tag: {header['packet_tag']}")
        print(f"  Packet Size: {header['packetSize']} bytes")
        print(f"  Number of Tracks: {header['nTracks']}")
        print(f"  System Time: Day {header['sys_time_days']}, {header['sys_time_ms']} ms")
        print(f"  Packet Type: {header['packet_type']}")
        
        offset += header['header_size']
        
        # Parse tracks
        for i in range(header['nTracks']):
            track, track_size = parse_track_data(data[offset:])
            if not track:
                break
            
            total_tracks += 1
            
            if i < 3:  # Show first 3 tracks per packet
                print(f"\n  Track #{i+1}:")
                print(f"    ID: {track['ID']}")
                print(f"    State: {track['state']}")
                print(f"    Position (Az/El/Range): {track['azest']:.2f}° / {track['elest']:.2f}° / {track['rest']:.1f}m")
                print(f"    Position (X/Y/Z): {track['xest']:.1f} / {track['yest']:.1f} / {track['zest']:.1f} m")
                print(f"    Velocity (X/Y/Z): {track['velxest']:.2f} / {track['velyest']:.2f} / {track['velzest']:.2f} m/s")
                print(f"    Lifetime: {track['lifetime']:.2f} sec")
                print(f"    Confidence: {track['estConfidence']:.3f}")
                print(f"    RCS: {track['estRCS']:.6f} m²")
                print(f"    Prob UAV: {track['probabilityUAV']:.3f}")
                print(f"    Prob Other: {track['probabilityOther']:.3f}")
            
            offset += track_size
        
        if header['nTracks'] > 3:
            print(f"\n  ... and {header['nTracks'] - 3} more tracks")
        
        print()
        
        # Safety check
        if packet_count > 100:
            print("(Stopping after 100 packets for brevity)")
            break
    
    print(f"\n{'='*70}")
    print(f"Summary:")
    print(f"  Total Packets: {packet_count}")
    print(f"  Total Tracks: {total_tracks}")
    print(f"{'='*70}\n")

if __name__ == '__main__':
    # Analyze the sample track file
    track_file = Path('/tmp/echoguard_samples/900238_rev01_SW16.3_Sample_Data/bnet_data/MESA-001002/2021-06-23T121211/tracks/track_1.bin')
    
    if track_file.exists():
        analyze_track_file(track_file)
    else:
        print(f"Error: File not found: {track_file}")
        sys.exit(1)
