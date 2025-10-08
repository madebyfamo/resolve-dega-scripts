#!/usr/bin/env python3
"""Try different AddMarker parameter combinations."""

import DaVinciResolveScript as dvr

resolve = dvr.scriptapp("Resolve")
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()

# Get first timeline with clips
for i in range(1, int(proj.GetTimelineCount()) + 1):
    tl = proj.GetTimelineByIndex(i)
    if tl:
        name = tl.GetName()
        if "Verse" in name:  # Use the one we know has a clip
            print(f"🧪 Testing on: {name}\n")

            # Test 1: Basic 3-param
            print("Test 1: AddMarker(frame, color, name)")
            try:
                result = tl.AddMarker(200, "Red", "Test 1")
                print(f"  Result: {result}, Type: {type(result)}\n")
            except Exception as e:
                print(f"  Exception: {e}\n")

            # Test 2: 4-param
            print("Test 2: AddMarker(frame, color, name, note)")
            try:
                result = tl.AddMarker(210, "Blue", "Test 2", "Note 2")
                print(f"  Result: {result}, Type: {type(result)}\n")
            except Exception as e:
                print(f"  Exception: {e}\n")

            # Test 3: 5-param
            print("Test 3: AddMarker(frame, color, name, note, duration)")
            try:
                result = tl.AddMarker(220, "Green", "Test 3", "Note 3", 30)
                print(f"  Result: {result}, Type: {type(result)}\n")
            except Exception as e:
                print(f"  Exception: {e}\n")

            # Test 4: 6-param
            print("Test 4: AddMarker(frame, color, name, note, duration, customData)")
            try:
                result = tl.AddMarker(230, "Yellow", "Test 4", "Note 4", 30, "custom=data")
                print(f"  Result: {result}, Type: {type(result)}\n")
            except Exception as e:
                print(f"  Exception: {e}\n")

            # Check what actually got added
            markers = tl.GetMarkers()
            print(f"📊 Final marker count: {len(markers) if markers else 0}")
            if markers:
                print(f"Markers: {list(markers.keys())}")

            break
