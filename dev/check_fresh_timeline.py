#!/usr/bin/env python3
"""Check the start/end frames of a freshly created empty timeline."""

import DaVinciResolveScript as dvr

resolve = dvr.scriptapp("Resolve")
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()

mp = proj.GetMediaPool()
root = mp.GetRootFolder()

test_name = "FRESH_TIMELINE_CHECK"

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

start = tl.GetStartFrame()
end = tl.GetEndFrame()
duration = end - start

print(f"  Start frame: {start}")
print(f"  End frame: {end}")
print(f"  Duration: {duration} frames ({duration/29.97:.2f}s)")

print(f"\n  Start time (s): {start/29.97:.2f}")
print(f"  End time (s): {end/29.97:.2f}")
