#!/usr/bin/env python3
"""Test: Add a generator clip first, THEN add markers."""

import DaVinciResolveScript as dvr

resolve = dvr.scriptapp("Resolve")
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()

mp = proj.GetMediaPool()
root = mp.GetRootFolder()

test_name = "TEST_WITH_CLIP_FIRST"

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

# Add a generator (solid color) to establish duration
# Create a 10-second solid color generator
print(f"\n📝 Adding 10-second solid color generator...")

# Generators are in the Effects library
# Let's try to append a simple generator clip
try:
    # Get the first video track
    # Try adding with AppendToTimeline
    generator_props = {
        "timelineItem": {
            "mediaPoolItem": None,  # Generator
            "startFrame": 0,
            "endFrame": int(10 * 29.97),
        }
    }

    # Actually, let's try a different approach - add through MediaPool
    # First create a fusion composition or use CreateTimelineFromClips

    # Simplest: Just try to set the timeline duration by setting in/out
    success = tl.SetSetting("timelineOutputResModeX", "2160")
    print(f"Setting result: {success}")

except Exception as e:
    print(f"Error: {e}")

# Alternative: Try adding markers at negative frames relative to 108000
print(f"\n🏷️ Trying to add marker at frame 0 (relative)...")
success = tl.AddMarker(0, "Red", "Frame 0", "Test", 0)
print(f"  Frame 0: {'✅' if success else '❌'}")

print(f"\n🏷️ Trying to add marker at absolute frame 108000...")
success = tl.AddMarker(108000, "Blue", "Frame 108000", "Test", 0)
print(f"  Frame 108000: {'✅' if success else '❌'}")

print(f"\n🏷️ Trying to add marker at frame 108348 (108000 + 348)...")
success = tl.AddMarker(108348, "Yellow", "Frame 108348", "Test", 0)
print(f"  Frame 108348: {'✅' if success else '❌'}")

# Check final state
markers = tl.GetMarkers()
count = len(markers) if markers else 0
print(f"\n📊 Final marker count: {count}")
if markers:
    for frame, data in sorted(markers.items()):
        print(f"  Frame {frame}: {data.get('name')}")
