#!/usr/bin/env python3
"""Test: Add ONLY the 299s anchor marker to see if it establishes duration."""

import DaVinciResolveScript as dvr

resolve = dvr.scriptapp("Resolve")
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()

mp = proj.GetMediaPool()
root = mp.GetRootFolder()

test_name = "TEST_ONLY_ANCHOR"

# Delete if exists
for i in range(1, int(proj.GetTimelineCount()) + 1):
    tl = proj.GetTimelineByIndex(i)
    if tl and tl.GetName() == test_name:
        mp.DeleteTimelines([tl])
        break

# Create fresh
mp.SetCurrentFolder(root)
tl = mp.CreateEmptyTimeline(test_name)

print(f"✅ Created: {test_name}")

# Try ONLY the anchor
frame_299s = int(299 * 29.97)
print(f"\nAdding ONLY anchor marker at frame {frame_299s} (299s)...")

try:
    success = tl.AddMarker(frame_299s, "Blue", "⏱ 5min anchor", "Timeline duration marker", 0)
    if success:
        print(f"✅ Anchor marker added successfully!")

        # Now check timeline duration
        end_frame = tl.GetEndFrame()
        print(f"📏 Timeline end frame: {end_frame}")

        # Try adding a marker at frame 0
        print(f"\nNow trying to add marker at frame 0...")
        success2 = tl.AddMarker(0, "Red", "Frame 0", "Test after anchor", 0)
        if success2:
            print(f"✅ Frame 0 marker added!")
        else:
            print(f"❌ Frame 0 marker failed")

    else:
        print(f"❌ Anchor marker failed")
except Exception as e:
    print(f"❌ Exception: {e}")

# Check final state
markers = tl.GetMarkers()
count = len(markers) if markers else 0
print(f"\n📊 Final marker count: {count}")
