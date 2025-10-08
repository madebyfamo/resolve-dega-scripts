#!/usr/bin/env python3
"""Delete a timeline so the main script can recreate it fresh with principle markers."""

import DaVinciResolveScript as dvr

resolve = dvr.scriptapp("Resolve")
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()

if not proj:
    print("❌ No project open")
    exit(1)

mp = proj.GetMediaPool()

# Timeline to delete and test
test_timeline = "Segment — Hook Performance — ⏱ 29.97p • 📐 2160×3840"

print(f"Searching for: {test_timeline}")

# Find and delete
found = False
for i in range(1, int(proj.GetTimelineCount()) + 1):
    tl = proj.GetTimelineByIndex(i)
    if tl and tl.GetName() == test_timeline:
        print(f"✅ Found: {test_timeline}")
        print(f"🗑️  Deleting...")
        mp.DeleteTimelines([tl])
        found = True
        print(f"✅ Deleted successfully")
        break

if not found:
    print(f"⚠️  Timeline not found: {test_timeline}")

print("\n✅ Now run the main script to recreate it fresh with principle markers!")
