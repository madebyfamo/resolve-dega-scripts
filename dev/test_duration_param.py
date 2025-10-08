#!/usr/bin/env python3
"""Test if duration=0 vs duration>0 makes a difference."""

import DaVinciResolveScript as dvr

resolve = dvr.scriptapp("Resolve")
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()

# Get timeline with clips
for i in range(1, int(proj.GetTimelineCount()) + 1):
    tl = proj.GetTimelineByIndex(i)
    if tl:
        name = tl.GetName()
        if "Verse" in name:
            print(f"🧪 Testing duration parameter on: {name}\n")

            print("Test 1: duration=0")
            result = tl.AddMarker(300, "Red", "Dur=0", "Test", 0)
            print(f"  Result: {result}\n")

            print("Test 2: duration=1")
            result = tl.AddMarker(310, "Blue", "Dur=1", "Test", 1)
            print(f"  Result: {result}\n")

            print("Test 3: duration=30")
            result = tl.AddMarker(320, "Green", "Dur=30", "Test", 30)
            print(f"  Result: {result}\n")

            markers = tl.GetMarkers()
            print(f"📊 Markers added: {len(markers) if markers else 0}")
            if markers:
                for frame, data in sorted(markers.items()):
                    print(f"  Frame {frame}: {data.get('name')} (duration: {data.get('duration')})")

            break
