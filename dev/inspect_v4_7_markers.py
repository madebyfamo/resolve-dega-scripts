#!/usr/bin/env python3
"""
Inspect actual marker content to see what v4.7 is generating
"""

import sys

sys.path.append(
    "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules/"
)

try:
    import DaVinciResolveScript as dvr
    resolve = dvr.scriptapp("Resolve")
    proj = resolve.GetProjectManager().GetCurrentProject()
except Exception as e:
    print(f"❌ Failed: {e}")
    sys.exit(1)

print(f"📂 Project: {proj.GetName()}\n")

# Check a Master timeline
for i in range(proj.GetTimelineCount()):
    tl = proj.GetTimelineByIndex(i + 1)
    name = tl.GetName()
    
    if "Money Master — 12s" in name:
        print(f"🎯 Inspecting: {name}")
        print("=" * 80)
        markers = tl.GetMarkers()
        
        for frame_id in sorted(markers.keys(), key=lambda x: int(x))[:5]:
            marker = markers[frame_id]
            print(f"\nFrame {frame_id}: {marker.get('name', 'NO NAME')}")
            print(f"  Color: {marker.get('color', 'NO COLOR')}")
            print(f"  Duration: {marker.get('duration', 0)} frames")
            note = marker.get('note', '')
            print(f"  Note ({len(note)} chars):")
            if note:
                print(f"    {note[:300]}")
            else:
                print("    (empty)")
        break

# Check a principle timeline
print("\n\n")
for i in range(proj.GetTimelineCount()):
    tl = proj.GetTimelineByIndex(i + 1)
    name = tl.GetName()
    
    if "Segment — Hook Performance" in name:
        print(f"🎯 Inspecting: {name}")
        print("=" * 80)
        markers = tl.GetMarkers()
        
        for frame_id in sorted(markers.keys(), key=lambda x: int(x))[:5]:
            marker = markers[frame_id]
            print(f"\nFrame {frame_id}: {marker.get('name', 'NO NAME')}")
            print(f"  Color: {marker.get('color', 'NO COLOR')}")
            print(f"  Duration: {marker.get('duration', 0)} frames")
            note = marker.get('note', '')
            print(f"  Note ({len(note)} chars):")
            if note:
                print(f"    {note[:300]}")
            else:
                print("    (empty)")
        break
