#!/usr/bin/env python3
"""Check LAS tiles for coordinate outliers that cause zoom issues in Potree."""

import argparse
from pathlib import Path
import numpy as np
import laspy


def check_tiles(tiles_path):
    """Scan LAS tiles and identify outliers based on spatial distance."""
    tiles_path = Path(tiles_path)
    
    if not tiles_path.exists():
        raise FileNotFoundError(f"Path not found: {tiles_path}")
    
    # Collect all tile bounds
    tiles = []
    for las_file in sorted(tiles_path.glob('tile_*.las')):
        with laspy.open(las_file) as f:
            h = f.header
            cx = (h.x_min + h.x_max) / 2
            cy = (h.y_min + h.y_max) / 2
            tiles.append({
                'file': las_file.name,
                'bounds': (h.x_min, h.x_max, h.y_min, h.y_max, h.z_min, h.z_max),
                'center': (cx, cy)
            })
    
    if not tiles:
        print(f"No tile_*.las files found in {tiles_path}")
        return
    
    # Calculate median center and find outliers
    centers = np.array([t['center'] for t in tiles])
    median = np.median(centers, axis=0)
    
    print(f"Found {len(tiles)} tiles")
    print(f"Median center: X={median[0]:.2f}, Y={median[1]:.2f}\n")
    
    outliers = []
    for t in tiles:
        dist = np.linalg.norm(np.array(t['center']) - median)
        status = "⚠️  OUTLIER" if dist > 1000 else "✓ OK"
        
        print(f"{status:12} {t['file']:20} dist={dist:8.2f}m  "
              f"X=[{t['bounds'][0]:.1f}, {t['bounds'][1]:.1f}]  "
              f"Y=[{t['bounds'][2]:.1f}, {t['bounds'][3]:.1f}]")
        
        if dist > 1000:
            outliers.append(t['file'])
    
    if outliers:
        print(f"\n⚠️  Found {len(outliers)} outlier(s): {', '.join(outliers)}")
    else:
        print("\n✓ No outliers detected")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path', help='Path to directory containing tile_*.las files')
    args = parser.parse_args()
    
    check_tiles(args.path)