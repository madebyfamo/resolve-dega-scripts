#!/usr/bin/env python3
"""Delete one principle timeline so the script can recreate it with markers."""

import DaVinciResolveScript as dvr

resolve = dvr.scriptapp("Resolve")
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()

mp = proj.GetMediaPool()

# Delete a test timeline
target = "Segment — Hook Performance — ⏱ 29.97p • 📐 2160×3840"

for i in range(1, int(proj.GetTimelineCount()) + 1):
    tl = proj.GetTimelineByIndex(i)
    if tl and tl.GetName() == target:
        print(f"🗑️  Deleting: {target}")
        mp.DeleteTimelines([tl])
        print(f"✅ Deleted")
        break
else:
    print(f"⚠️  Timeline not found: {target}")
