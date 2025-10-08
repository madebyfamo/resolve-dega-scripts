#!/usr/bin/env python3
"""Test custom data marker methods - maybe these work differently."""

import DaVinciResolveScript as dvr

resolve = dvr.scriptapp("Resolve")
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()

mp = proj.GetMediaPool()
root = mp.GetRootFolder()

# Use an EXISTING timeline that HAS markers
print("🔍 Looking for existing master timeline with markers...\n")

for i in range(1, int(proj.GetTimelineCount()) + 1):
    tl = proj.GetTimelineByIndex(i)
    if tl and "Money Master — 12s" in tl.GetName():
        print(f"✅ Found: {tl.GetName()}\n")

        markers = tl.GetMarkers()
        if markers:
            print(f"📊 Timeline has {len(markers)} markers\n")

            # Test custom data methods
            for frame, data in sorted(markers.items()):
                print(f"Frame {frame}: {data.get('name')}")

                # Try to get custom data
                custom_data = tl.GetMarkerCustomData(frame)
                print(f"  Custom data: {custom_data}")

                # Try to update custom data
                result = tl.UpdateMarkerCustomData(frame, "test_key=test_value")
                print(f"  UpdateMarkerCustomData result: {result}")

                # Get it again
                custom_data2 = tl.GetMarkerCustomData(frame)
                print(f"  Custom data after update: {custom_data2}\n")

                break  # Just test first marker

        # Now test GetMarkerByCustomData
        print("\n🧪 Test GetMarkerByCustomData:")
        marker = tl.GetMarkerByCustomData("test_key=test_value")
        print(f"  Result: {marker}")

        break

# Now test on a FRESH timeline
print("\n" + "=" * 60)
print("🧪 Testing on FRESH timeline\n")

test_name = "TEST_CUSTOM_DATA_MARKERS"

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

# Try to update custom data at frame 0 (maybe this creates a marker?)
print("🧪 Test: UpdateMarkerCustomData without existing marker")
result = tl.UpdateMarkerCustomData(0, "test_marker=first")
print(f"  UpdateMarkerCustomData(0) result: {result}")

# Check if marker was created
markers = tl.GetMarkers()
print(f"  Markers after update: {markers}")

# Try to get by custom data
marker = tl.GetMarkerByCustomData("test_marker=first")
print(f"  GetMarkerByCustomData result: {marker}")

print(f"\n📊 Final marker count: {len(markers) if markers else 0}")
