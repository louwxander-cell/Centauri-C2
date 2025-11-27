#!/usr/bin/env python3
"""
Gunner Station Simulator
Simulates a gunner station receiving tracks and sending status
For testing the gunner interface
"""

import socket
import json
import time
import threading
from dataclasses import dataclass, asdict


@dataclass
class GunnerStatus:
    """Gunner status to send to C2"""
    station_id: str
    cued_track_id: int  # -1 if none
    visual_lock: bool
    ready_to_fire: bool
    rws_azimuth_deg: float
    rws_elevation_deg: float
    selected_weapon: str  # "CRx-30", "CRx-40", or ""
    rounds_remaining: int
    weapon_armed: bool
    operator_id: str
    timestamp_ns: int


class GunnerSimulator:
    """Simulates a gunner station"""
    
    def __init__(
        self,
        station_id: str = "GUNNER_1",
        c2_address: str = "192.168.10.10",
        track_port: int = 5100,
        status_port: int = 5101
    ):
        self.station_id = station_id
        self.c2_address = c2_address
        self.track_port = track_port
        self.status_port = status_port
        
        # State
        self.tracks = []
        self.cued_track_id = -1
        self.visual_lock = False
        self.selected_weapon = ""
        self.rws_azimuth = 0.0
        self.rws_elevation = 0.0
        self.rounds_remaining = 120
        self.weapon_armed = False
        self.operator_id = "OPERATOR_1"
        
        # Sockets
        self.receive_socket = None
        self.send_socket = None
        
        # Threading
        self.running = False
        self.receive_thread = None
        self.status_thread = None
        
        print(f"[{self.station_id}] Gunner simulator initialized")
        print(f"  C2 Address: {c2_address}")
        print(f"  Track port: {track_port}")
        print(f"  Status port: {status_port}")
    
    def start(self):
        """Start the simulator"""
        if self.running:
            return
        
        self.running = True
        
        # Set up sockets
        self._setup_receive_socket()
        self._setup_send_socket()
        
        # Start threads
        self.receive_thread = threading.Thread(
            target=self._receive_loop,
            name=f"{self.station_id}_Receive",
            daemon=True
        )
        self.receive_thread.start()
        
        self.status_thread = threading.Thread(
            target=self._status_send_loop,
            name=f"{self.station_id}_Status",
            daemon=True
        )
        self.status_thread.start()
        
        print(f"[{self.station_id}] ✓ Simulator started")
    
    def stop(self):
        """Stop the simulator"""
        print(f"[{self.station_id}] Stopping...")
        self.running = False
        
        if self.receive_thread:
            self.receive_thread.join(timeout=2.0)
        if self.status_thread:
            self.status_thread.join(timeout=2.0)
        
        if self.receive_socket:
            self.receive_socket.close()
        if self.send_socket:
            self.send_socket.close()
        
        print(f"[{self.station_id}] ✓ Stopped")
    
    def _setup_receive_socket(self):
        """Set up socket to receive track broadcasts"""
        try:
            self.receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.receive_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.receive_socket.bind(('', self.track_port))
            self.receive_socket.settimeout(1.0)
            print(f"[{self.station_id}] ✓ Listening for tracks on UDP port {self.track_port}")
        except Exception as e:
            print(f"[{self.station_id}] ✗ Receive socket error: {e}")
            raise
    
    def _setup_send_socket(self):
        """Set up socket to send status to C2"""
        try:
            self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            print(f"[{self.station_id}] ✓ Status socket ready")
        except Exception as e:
            print(f"[{self.station_id}] ✗ Send socket error: {e}")
            raise
    
    def _receive_loop(self):
        """Receive track broadcasts"""
        print(f"[{self.station_id}] Track receiver started")
        
        while self.running:
            try:
                data, address = self.receive_socket.recvfrom(65535)
                
                # Parse JSON
                snapshot = json.loads(data.decode('utf-8'))
                self.tracks = snapshot.get('tracks', [])
                
                # Display tracks periodically
                if len(self.tracks) > 0:
                    self._display_tracks()
                
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"[{self.station_id}] Receive error: {e}")
        
        print(f"[{self.station_id}] Track receiver stopped")
    
    def _status_send_loop(self):
        """Send status to C2 at 1 Hz"""
        print(f"[{self.station_id}] Status sender started")
        
        while self.running:
            try:
                # Build status
                status = GunnerStatus(
                    station_id=self.station_id,
                    cued_track_id=self.cued_track_id,
                    visual_lock=self.visual_lock,
                    ready_to_fire=self.visual_lock and self.weapon_armed,
                    rws_azimuth_deg=self.rws_azimuth,
                    rws_elevation_deg=self.rws_elevation,
                    selected_weapon=self.selected_weapon,
                    rounds_remaining=self.rounds_remaining,
                    weapon_armed=self.weapon_armed,
                    operator_id=self.operator_id,
                    timestamp_ns=time.time_ns()
                )
                
                # Send to C2
                message = json.dumps(asdict(status)).encode('utf-8')
                self.send_socket.sendto(message, (self.c2_address, self.status_port))
                
                time.sleep(1.0)  # 1 Hz
                
            except Exception as e:
                if self.running:
                    print(f"[{self.station_id}] Status send error: {e}")
        
        print(f"[{self.station_id}] Status sender stopped")
    
    def _display_tracks(self):
        """Display current tracks (periodically)"""
        # Only display every 50 frames (~5 seconds at 10 Hz)
        if not hasattr(self, '_display_counter'):
            self._display_counter = 0
        
        self._display_counter += 1
        if self._display_counter % 50 != 0:
            return
        
        print(f"\n{'=' * 70}")
        print(f"  {self.station_id} - TRACK DISPLAY")
        print(f"{'=' * 70}")
        print(f"{'ID':<6} {'TYPE':<6} {'RANGE':<8} {'AZ':<7} {'PRIORITY':<10} {'RECOMMENDED':<15}")
        print(f"{'-' * 70}")
        
        for track in self.tracks:
            print(f"{track['track_id']:<6} "
                  f"{track['type']:<6} "
                  f"{track['range_m']:<8.0f} "
                  f"{track['azimuth_deg']:<7.1f} "
                  f"{track['priority']:<10} "
                  f"{track['recommended_effector']:<15}")
        
        print(f"{'-' * 70}")
        print(f"Total tracks: {len(self.tracks)}")
        print(f"Cued track: {self.cued_track_id if self.cued_track_id != -1 else 'NONE'}")
        print(f"Visual lock: {'YES' if self.visual_lock else 'NO'}")
        print(f"Weapon: {self.selected_weapon if self.selected_weapon else 'NONE'}")
        print(f"{'=' * 70}\n")
    
    def cue_track(self, track_id: int, weapon: str = "CRx-30"):
        """Simulate operator cueing a track"""
        print(f"\n[{self.station_id}] OPERATOR ACTION:")
        print(f"  1. SELECT WEAPON: {weapon}")
        self.selected_weapon = weapon
        
        print(f"  2. CUE TRACK: {track_id}")
        self.cued_track_id = track_id
        
        # Find track and slew RWS
        track = next((t for t in self.tracks if t['track_id'] == track_id), None)
        if track:
            print(f"  3. RWS SLEWING to Az={track['azimuth_deg']:.1f}°, El={track['elevation_deg']:.1f}°")
            self.rws_azimuth = track['azimuth_deg']
            self.rws_elevation = track['elevation_deg']
            
            # Simulate visual acquisition after 2 seconds
            def achieve_lock():
                time.sleep(2.0)
                if self.cued_track_id == track_id:
                    self.visual_lock = True
                    print(f"\n[{self.station_id}] ✓ VISUAL LOCK ACHIEVED on Track {track_id}")
                    print(f"  Ready to fire: {weapon}")
            
            threading.Thread(target=achieve_lock, daemon=True).start()
        else:
            print(f"  ✗ Track {track_id} not found")
    
    def release_track(self):
        """Release current track"""
        print(f"\n[{self.station_id}] RELEASE TRACK {self.cued_track_id}")
        self.cued_track_id = -1
        self.visual_lock = False
        self.selected_weapon = ""
    
    def fire(self):
        """Simulate firing"""
        if not self.visual_lock:
            print(f"\n[{self.station_id}] ✗ Cannot fire - no visual lock")
            return
        
        if not self.selected_weapon:
            print(f"\n[{self.station_id}] ✗ Cannot fire - no weapon selected")
            return
        
        print(f"\n[{self.station_id}] 🔥 FIRING {self.selected_weapon} at Track {self.cued_track_id}")
        print(f"  Range: {self.rws_azimuth:.0f}m")
        print(f"  Position: Az={self.rws_azimuth:.1f}°, El={self.rws_elevation:.1f}°")
        
        self.rounds_remaining -= 5  # Burst of 5
        print(f"  Rounds remaining: {self.rounds_remaining}")


# Interactive simulator
def main():
    import sys
    
    print("=" * 70)
    print("  TriAD Gunner Station Simulator")
    print("=" * 70)
    print()
    
    # Configuration
    station_id = input("Enter station ID [GUNNER_1]: ").strip() or "GUNNER_1"
    c2_address = input("Enter C2 IP address [192.168.10.10]: ").strip() or "192.168.10.10"
    
    # For local testing, use broadcast
    if c2_address == "localhost" or c2_address == "127.0.0.1":
        c2_address = "255.255.255.255"
    
    sim = GunnerSimulator(
        station_id=station_id,
        c2_address=c2_address,
        track_port=5100,
        status_port=5101
    )
    
    sim.start()
    
    print()
    print("=" * 70)
    print("  Simulator Running")
    print("=" * 70)
    print("  Commands:")
    print("    cue <track_id> <weapon>  - Cue track (e.g., 'cue 2001 CRx-30')")
    print("    release                  - Release current track")
    print("    fire                     - Fire at cued track")
    print("    status                   - Show current status")
    print("    tracks                   - Show track list")
    print("    quit                     - Exit simulator")
    print("=" * 70)
    print()
    
    try:
        while True:
            cmd = input(f"[{station_id}]> ").strip().lower()
            
            if cmd == 'quit':
                break
            
            elif cmd.startswith('cue'):
                parts = cmd.split()
                if len(parts) >= 2:
                    track_id = int(parts[1])
                    weapon = parts[2] if len(parts) > 2 else "CRx-30"
                    sim.cue_track(track_id, weapon)
                else:
                    print("Usage: cue <track_id> <weapon>")
            
            elif cmd == 'release':
                sim.release_track()
            
            elif cmd == 'fire':
                sim.fire()
            
            elif cmd == 'status':
                print(f"\nStation: {sim.station_id}")
                print(f"Cued track: {sim.cued_track_id if sim.cued_track_id != -1 else 'NONE'}")
                print(f"Visual lock: {sim.visual_lock}")
                print(f"Weapon: {sim.selected_weapon if sim.selected_weapon else 'NONE'}")
                print(f"RWS: Az={sim.rws_azimuth:.1f}°, El={sim.rws_elevation:.1f}°")
                print(f"Rounds: {sim.rounds_remaining}")
            
            elif cmd == 'tracks':
                sim._display_tracks()
            
            else:
                print("Unknown command. Type 'quit' to exit.")
    
    except KeyboardInterrupt:
        print("\n\nInterrupted...")
    finally:
        sim.stop()
        print("Simulator stopped.")


if __name__ == "__main__":
    main()
