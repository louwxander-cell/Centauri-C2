#!/usr/bin/env python3
"""
Download offline map tiles for TriAD C2 system
Run this script once to download map tiles for offline use
"""

from src.ui.map_tile_downloader import download_default_area

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("TriAD C2 - Offline Map Tile Downloader")
    print("=" * 70)
    print("\nThis will download map tiles for:")
    print("  Location: Pretoria, South Africa")
    print("  Coordinates: -25.841105, 28.180340")
    print("  Radius: 50 km")
    print("  Zoom levels: 10, 11, 12, 13, 14")
    print("\nThis may take 10-30 minutes depending on your connection.")
    print("The tiles will be cached in the 'map_cache' directory.")
    print("\nPress Ctrl+C to cancel at any time.")
    print("=" * 70 + "\n")
    
    input("Press Enter to start download...")
    
    try:
        download_default_area()
        print("\n" + "=" * 70)
        print("✅ Download complete!")
        print("=" * 70)
        print("\nYou can now run the C2 system with offline maps.")
        print("The maps are cached in: map_cache/")
        print("\n")
    except KeyboardInterrupt:
        print("\n\n[Cancelled] Download interrupted by user")
    except Exception as e:
        print(f"\n\n[Error] Download failed: {e}")
        import traceback
        traceback.print_exc()
