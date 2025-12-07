#!/usr/bin/env python3
"""
Echodyne EchoGuard Radar - Connection Test Script
Tests TCP connection and displays raw binary data
"""

import socket
import struct
import time
import sys

def test_radar_connection(host, port, duration=30):
    """
    Test connection to Echodyne EchoGuard radar
    
    Args:
        host: Radar IP address
        port: Radar TCP port (usually 23000)
        duration: How long to monitor (seconds)
    """
    
    print("=" * 70)
    print("  ECHODYNE ECHOGUARD RADAR - CONNECTION TEST")
    print("=" * 70)
    print(f"Target: {host}:{port}")
    print(f"Duration: {duration} seconds")
    print("=" * 70)
    print()
    
    # Test network connectivity first
    print("[1] Testing network connectivity...")
    try:
        import subprocess
        result = subprocess.run(['ping', '-c', '1', '-W', '2', host], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"    ✓ Radar is reachable at {host}")
        else:
            print(f"    ✗ Cannot reach {host} - Check network connection")
            return
    except Exception as e:
        print(f"    ⚠ Ping test failed: {e}")
        print(f"    Continuing anyway...")
    
    print()
    print("[2] Connecting to radar...")
    
    try:
        # Create TCP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10.0)
        
        # Connect to radar
        sock.connect((host, port))
        print(f"    ✓ Connected successfully!")
        print()
        
        # Monitor incoming data
        print("[3] Monitoring data stream...")
        print("    (Press Ctrl+C to stop)")
        print("-" * 70)
        
        start_time = time.time()
        packet_count = 0
        total_bytes = 0
        last_display = time.time()
        
        while time.time() - start_time < duration:
            try:
                # Receive data
                data = sock.recv(4096)
                
                if not data:
                    print("    Connection closed by radar")
                    break
                
                packet_count += 1
                total_bytes += len(data)
                
                # Display stats every 2 seconds
                now = time.time()
                if now - last_display >= 2.0:
                    elapsed = now - start_time
                    rate = packet_count / elapsed
                    bytes_per_sec = total_bytes / elapsed
                    
                    print(f"    [{int(elapsed):3d}s] Packets: {packet_count:4d} | "
                          f"Rate: {rate:5.1f} pkt/s | "
                          f"Data: {bytes_per_sec/1024:.1f} KB/s")
                    
                    # Show first few bytes of data (hex)
                    if packet_count <= 3:
                        hex_data = ' '.join(f'{b:02X}' for b in data[:32])
                        print(f"           Sample data: {hex_data}...")
                    
                    last_display = now
                
            except socket.timeout:
                print("    No data received (timeout)")
                continue
        
        print("-" * 70)
        print()
        print("📊 Summary:")
        print(f"    Total packets: {packet_count}")
        print(f"    Total bytes: {total_bytes:,}")
        print(f"    Average rate: {total_bytes/duration/1024:.1f} KB/s")
        print()
        
        if packet_count > 0:
            print("✅ SUCCESS: Radar is transmitting data!")
            print()
            print("Next steps:")
            print("  1. Verify data format matches BNET protocol")
            print("  2. Parse track packets (248 bytes per track)")
            print("  3. Extract azimuth, elevation, range")
            print()
        else:
            print("⚠️  WARNING: No data received")
            print()
            print("Possible issues:")
            print("  - Radar may not be configured to stream data")
            print("  - Wrong port number")
            print("  - Radar is in standby mode")
            print("  - Firewall blocking connection")
            print()
        
        sock.close()
        
    except ConnectionRefusedError:
        print(f"    ✗ Connection refused")
        print()
        print("Possible issues:")
        print("  - Radar is not running")
        print("  - Wrong port number")
        print("  - Firewall blocking connection")
        print()
        
    except socket.timeout:
        print(f"    ✗ Connection timeout")
        print()
        print("Possible issues:")
        print("  - Wrong IP address")
        print("  - Radar not on network")
        print("  - Network configuration issue")
        print()
        
    except Exception as e:
        print(f"    ✗ Error: {e}")
        print()


def parse_track_header(data):
    """
    Parse BNET track packet header (28 bytes)
    """
    if len(data) < 28:
        return None
    
    try:
        # Header format: 12 byte magic + 7 uint32 fields
        header_format = '<12sIIIIIII'
        fields = struct.unpack(header_format, data[:28])
        
        return {
            'magic': fields[0],
            'field1': fields[1],
            'field2': fields[2],
            'field3': fields[3],
            'field4': fields[4],
            'field5': fields[5],
            'field6': fields[6],
            'field7': fields[7],
        }
    except Exception as e:
        return None


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 test_radar_connection.py <ip_address> <port>")
        print()
        print("Example:")
        print("  python3 test_radar_connection.py 192.168.1.100 23000")
        print()
        sys.exit(1)
    
    host = sys.argv[1]
    port = int(sys.argv[2])
    
    try:
        test_radar_connection(host, port, duration=30)
    except KeyboardInterrupt:
        print()
        print("Test interrupted by user")
        sys.exit(0)
