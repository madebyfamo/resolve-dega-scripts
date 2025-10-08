#!/usr/bin/env python3
"""Test if a freshly created timeline can accept markers with an anchor at 299s."""

import DaVinciResolveScript as dvr

resolve = dvr.scriptapp("Resolve")
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()

if not proj:
    print("❌ No project open")
    exit(1)

mp = proj.GetMediaPool()
root = mp.GetRootFolder()

# Create test timeline
test_name = "TEST_MARKER_ANCHOR_299s"
print(f"Creating test timeline: {test_name}")

# Delete if exists
for i in range(1, int(proj.GetTimelineCount()) + 1):
    tl = proj.GetTimelineByIndex(i)
    if tl and tl.GetName() == test_name:
        print(f"Deleting existing: {test_name}")
        mp.DeleteTimelines([tl])
        break

# Create fresh
mp.SetCurrentFolder(root)
tl = mp.CreateEmptyTimeline(test_name)

if not tl:
    print("❌ Failed to create timeline")
    exit(1)

print(f"✅ Created: {test_name}")

# Try adding markers
markers_to_add = [
    (0, "Red", "Frame 0", "First marker"),
    (30, "Blue", "Frame 30", "Second marker"),
    (60, "Green", "Frame 60", "Third marker"),
    (8961, "Yellow", "⏱ 5min anchor", "Anchor at 299s"),
]

print("\nAttempting to add markers...")
for frame, color, name, note in markers_to_add:
    try:
        success = tl.AddMarker(frame, color, name, note, 0)
        status = "✅" if success else "❌"
        print(f"{status} Frame {frame:5d}: {name}")
    except Exception as e:
        print(f"❌ Frame {frame:5d}: {name} - Exception: {e}")

# Check final marker count
try:
    markers = tl.GetMarkers()
    count = len(markers) if markers else 0
    print(f"\n📊 Final marker count: {count}")
    if markers and isinstance(markers, dict):
        for frame_id, marker_data in sorted(markers.items()):
            print(f"   Frame {frame_id}: {marker_data.get('name', 'Unknown')}")
except Exception as e:
    print(f"\n⚠️ Could not get markers: {e}")

print("\n✅ Test complete")
