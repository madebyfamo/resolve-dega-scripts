#!/usr/bin/env python3
"""Test adding markers WITHOUT the 299s anchor - just 0s, 1s, 2s."""

import DaVinciResolveScript as dvr

resolve = dvr.scriptapp("Resolve")
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()

mp = proj.GetMediaPool()
root = mp.GetRootFolder()

test_name = "TEST_NO_ANCHOR"

# Delete if exists
for i in range(1, int(proj.GetTimelineCount()) + 1):
    tl = proj.GetTimelineByIndex(i)
    if tl and tl.GetName() == test_name:
        mp.DeleteTimelines([tl])
        break

# Create fresh
mp.SetCurrentFolder(root)
tl = mp.CreateEmptyTimeline(test_name)

print(f"✅ Created: {test_name}\n")

# Try markers at 0s, 1s, 2s ONLY (no 299s anchor)
markers = [
    (0, "Purple", "PRINCIPLES — Test", "Frame 0"),
    (30, "Pink", "One second", "Frame 30"),
    (60, "Yellow", "Two seconds", "Frame 60"),
]

print("🏷️ Adding 3 markers (0s, 1s, 2s)...\n")

added = 0
for frame, color, name, note in markers:
    try:
        success = tl.AddMarker(frame, color, name, note, 0)
        if success:
            print(f"  ✅ {name} @ frame {frame}")
            added += 1
        else:
            print(f"  ❌ {name} @ frame {frame}")
    except Exception as e:
        print(f"  ❌ {name} @ frame {frame} - Exception: {e}")

print(f"\n📊 Added {added}/3 markers")

# Check final state
markers_check = tl.GetMarkers()
count = len(markers_check) if markers_check else 0
print(f"📊 Final marker count: {count}")
