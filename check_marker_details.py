#!/usr/bin/env python3
"""Quick check of marker details on first segment timeline."""

import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

try:
    import DaVinciResolveScript as dvr
except ImportError:
    print("❌ Cannot import DaVinciResolveScript")
    sys.exit(1)

resolve = dvr.scriptapp("Resolve")
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()

cnt = int(proj.GetTimelineCount() or 0)
for i in range(1, cnt + 1):
    tl = proj.GetTimelineByIndex(i)
    if not tl:
        continue
    title = tl.GetName() or ""
    
    if "Segment" in title and "Money Master" not in title:
        print(f"Timeline: {title}")
        
        fps_obj = tl.GetSetting("timelineFrameRate")
        fps = float(fps_obj or 29.97)
        print(f"FPS: {fps}")
        
        markers = tl.GetMarkers() or {}
        print(f"\nTotal markers: {len(markers)}")
        print("\nMarker details:")
        print(f"{'Frame':<10} | {'Time (s)':<10} | {'Color':<10} | Name")
        print("-" * 70)
        
        for frame_num in sorted(markers.keys(), key=lambda x: int(x)):
            marker = markers[frame_num]
            frame_int = int(frame_num)
            time_sec = frame_int / fps
            color = marker.get("color", "")
            name = marker.get("name", "")
            print(f"{frame_int:<10} | {time_sec:<10.2f} | {color:<10} | {name}")
        
        # Check expected positions
        print("\n✅ Expected markers:")
        print(f"   0s = frame 0")
        print(f"   1s = frame {int(fps)}")
        print(f"   2s = frame {int(fps * 2)}")
        print(f"   299s = frame {int(fps * 299)}")
        
        break
