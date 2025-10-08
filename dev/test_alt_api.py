#!/usr/bin/env python3
"""Test alternative marker API methods."""

import DaVinciResolveScript as dvr

resolve = dvr.scriptapp("Resolve")
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()

mp = proj.GetMediaPool()
root = mp.GetRootFolder()

test_name = "TEST_ALT_MARKER_API"

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

# Test 1: Try setting markers dictionary directly
print("🧪 Test 1: Try DeleteMarkersByColor (might initialize marker system)")
try:
    result = tl.DeleteMarkersByColor("Purple")
    print(f"  DeleteMarkersByColor result: {result}")
except Exception as e:
    print(f"  Exception: {e}")

# Test 2: Try GetMarkers first to initialize
print("\n🧪 Test 2: Call GetMarkers first")
try:
    markers = tl.GetMarkers()
    print(f"  GetMarkers returned: {markers}")
except Exception as e:
    print(f"  Exception: {e}")

# Test 3: Now try adding after GetMarkers
print("\n🧪 Test 3: Try AddMarker after GetMarkers")
try:
    success = tl.AddMarker(0, "Red", "After GetMarkers", "Test", 0)
    print(f"  AddMarker result: {success}")
except Exception as e:
    print(f"  Exception: {e}")

# Test 4: Try setting current timeline first
print("\n🧪 Test 4: Set as current timeline then add marker")
try:
    proj.SetCurrentTimeline(tl)
    success = tl.AddMarker(30, "Blue", "After SetCurrent", "Test", 0)
    print(f"  AddMarker result: {success}")
except Exception as e:
    print(f"  Exception: {e}")

# Test 5: Try getting the timeline item and adding there
print("\n🧪 Test 5: Check if timeline has GetMarker (singular)")
try:
    # Some APIs have GetMarker vs GetMarkers
    if hasattr(tl, "GetMarker"):
        marker = tl.GetMarker(0)
        print(f"  GetMarker result: {marker}")
    else:
        print(f"  No GetMarker method")
except Exception as e:
    print(f"  Exception: {e}")

# Test 6: Try ApplyGradeFromDRX or other timeline methods
print("\n🧪 Test 6: List all timeline methods")
methods = [m for m in dir(tl) if not m.startswith("_") and "marker" in m.lower()]
print(f"  Marker-related methods: {methods}")

# Test 7: Try adding marker with different parameter combinations
print("\n🧪 Test 7: Try 4-parameter AddMarker")
try:
    success = tl.AddMarker(60, "Green", "Four Params", "Test")
    print(f"  4-param AddMarker result: {success}")
except Exception as e:
    print(f"  Exception: {e}")

print("\n🧪 Test 8: Try 3-parameter AddMarker")
try:
    success = tl.AddMarker(90, "Yellow", "Three Params")
    print(f"  3-param AddMarker result: {success}")
except Exception as e:
    print(f"  Exception: {e}")

# Check final state
print("\n📊 Final state:")
markers = tl.GetMarkers()
count = len(markers) if markers else 0
print(f"  Marker count: {count}")
if markers:
    for frame, data in sorted(markers.items()):
        print(f"    Frame {frame}: {data}")
