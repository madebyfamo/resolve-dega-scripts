#!/usr/bin/env python3
"""Test: Try to create a master timeline exactly like the script does."""

import DaVinciResolveScript as dvr

resolve = dvr.scriptapp("Resolve")
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()

mp = proj.GetMediaPool()
root = mp.GetRootFolder()

# Use exact same LANE_MARKERS data from the script
LANE_MARKERS_12 = [
    {"t": 0.0, "color": "Red", "name": "HOOK", "dur": 0.0, "notes": "Attention Spike"},
    {"t": 3.0, "color": "Orange", "name": "DRAW", "dur": 0.0, "notes": "Retain"},
    {
        "t": 4.5,
        "color": "Magenta",
        "name": "INTERRUPT #1",
        "dur": 0.0,
        "notes": "Re-Hook / Visual Cue",
    },
    {
        "t": 8.0,
        "color": "Green",
        "name": "COMMIT / PAYOFF",
        "dur": 0.0,
        "notes": "Value Delivery / First Resolution",
    },
    {
        "t": 9.0,
        "color": "Magenta",
        "name": "INTERRUPT #2",
        "dur": 0.0,
        "notes": "Re-Hook / Visual Cue",
    },
    {
        "t": 11.6,
        "color": "Yellow",
        "name": "LOOP / CTA",
        "dur": 0.0,
        "notes": "Repeatable Ending / CTA",
    },
]

test_name = "TEST_NEW_MASTER_12s"

# Delete if exists
for i in range(1, int(proj.GetTimelineCount()) + 1):
    tl = proj.GetTimelineByIndex(i)
    if tl and tl.GetName() == test_name:
        mp.DeleteTimelines([tl])
        break

# Create fresh timeline
mp.SetCurrentFolder(root)
tl = mp.CreateEmptyTimeline(test_name)

print(f"✅ Created: {test_name}")

# Now try adding markers
print(f"\n🏷️ Adding {len(LANE_MARKERS_12)} markers...")
added = 0

for marker in LANE_MARKERS_12:
    frame = int(marker["t"] * 29.97)
    try:
        success = tl.AddMarker(frame, marker["color"], marker["name"], marker["notes"], 0)
        if success:
            print(f"  ✅ {marker['name']} @ {marker['t']}s (frame {frame})")
            added += 1
        else:
            print(f"  ❌ {marker['name']} @ {marker['t']}s (frame {frame})")
    except Exception as e:
        print(f"  ❌ {marker['name']} @ {marker['t']}s - Exception: {e}")

print(f"\n📊 Added {added}/{len(LANE_MARKERS_12)} markers")

# Check final state
markers = tl.GetMarkers()
count = len(markers) if markers else 0
print(f"📊 Final marker count in timeline: {count}")
