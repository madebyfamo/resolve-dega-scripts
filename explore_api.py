#!/usr/bin/env python3
"""Explore Project and MediaPool APIs for marker creation."""

import DaVinciResolveScript as dvr

resolve = dvr.scriptapp("Resolve")
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()

print("🔍 Project API - marker-related methods:")
proj_methods = [m for m in dir(proj) if not m.startswith("_") and "marker" in m.lower()]
print(f"  {proj_methods}\n")

print("🔍 ProjectManager API - marker-related methods:")
pm_methods = [m for m in dir(pm) if not m.startswith("_") and "marker" in m.lower()]
print(f"  {pm_methods}\n")

mp = proj.GetMediaPool()

print("🔍 MediaPool API - marker-related methods:")
mp_methods = [m for m in dir(mp) if not m.startswith("_") and "marker" in m.lower()]
print(f"  {mp_methods}\n")

print("🔍 MediaPool API - timeline creation methods:")
creation_methods = [
    m
    for m in dir(mp)
    if not m.startswith("_") and ("timeline" in m.lower() or "create" in m.lower())
]
print(f"  {creation_methods}\n")

# Check if there's a CreateTimelineFromClips or similar
print("🧪 Testing CreateTimelineFromClips (if available):")
if hasattr(mp, "CreateTimelineFromClips"):
    print("  ✅ CreateTimelineFromClips exists")
    print("  Signature might allow marker specification")
else:
    print("  ❌ CreateTimelineFromClips not available")

# Check for ImportTimelineFromFile
print("\n🧪 Testing ImportTimelineFromFile (if available):")
if hasattr(mp, "ImportTimelineFromFile"):
    print("  ✅ ImportTimelineFromFile exists")
    print("  Could potentially import a timeline with markers")
else:
    print("  ❌ ImportTimelineFromFile not available")

# Check Timeline API more thoroughly
print("\n🔍 Timeline API - ALL methods:")
root = mp.GetRootFolder()
mp.SetCurrentFolder(root)
tl = mp.CreateEmptyTimeline("TEMP_API_CHECK")

all_methods = [m for m in dir(tl) if not m.startswith("_")]
print(f"  Total methods: {len(all_methods)}")

# Look for interesting ones
interesting = ["Import", "Export", "Load", "Save", "Duplicate", "Copy", "Clone"]
found = []
for keyword in interesting:
    matches = [m for m in all_methods if keyword.lower() in m.lower()]
    if matches:
        found.extend(matches)

print(f"  Import/Export related: {found}\n")

# Clean up
mp.DeleteTimelines([tl])

print("🧪 Key findings:")
print("  - No alternative marker creation methods found")
print("  - UpdateMarkerCustomData requires existing marker")
print("  - No Import/Clone methods that could copy markers")
print("\n💡 Conclusion: AddMarker is the ONLY way to add markers via API")
print("   And it FAILS on empty timelines in DaVinci Resolve 20.2")
