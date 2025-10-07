#!/usr/bin/env python3
"""Check actual timeline names to see what patterns we need to match."""

import DaVinciResolveScript as dvr

resolve = dvr.scriptapp("Resolve")
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()

print(f"📂 Project: {proj.GetName()}\n")

# Get all non-master timelines
count = int(proj.GetTimelineCount())
print(f"Total timelines: {count}\n")

principle_timelines = []

for i in range(1, count + 1):
    tl = proj.GetTimelineByIndex(i)
    if not tl:
        continue

    name = tl.GetName()

    # Skip masters
    if "Master" in name:
        continue

    # Get marker count
    markers = tl.GetMarkers()
    marker_count = len(markers) if markers else 0

    principle_timelines.append({"name": name, "markers": marker_count})

print(f"Found {len(principle_timelines)} principle timelines:\n")

for tl_info in principle_timelines[:20]:  # Show first 20
    status = "✅" if tl_info["markers"] > 0 else "❌"
    print(f"{status} [{tl_info['markers']} markers] {tl_info['name']}")

if len(principle_timelines) > 20:
    print(f"\n... and {len(principle_timelines) - 20} more")

# Analyze naming patterns
print("\n" + "=" * 60)
print("🔍 Naming pattern analysis:\n")

patterns = {
    "Segment": [],
    "ShotFX": [],
    "Interview": [],
    "LOOK": [],
    "Chapter": [],
    "Section": [],
    "Other": [],
}

for tl_info in principle_timelines:
    name = tl_info["name"]
    name_lower = name.lower()

    if "segment" in name_lower:
        patterns["Segment"].append(name)
    elif "shotfx" in name_lower or "shot fx" in name_lower:
        patterns["ShotFX"].append(name)
    elif "interview" in name_lower:
        patterns["Interview"].append(name)
    elif "look" in name_lower:
        patterns["LOOK"].append(name)
    elif "chapter" in name_lower:
        patterns["Chapter"].append(name)
    elif "section" in name_lower:
        patterns["Section"].append(name)
    else:
        patterns["Other"].append(name)

for category, names in patterns.items():
    if names:
        print(f"{category}: {len(names)} timelines")
        for name in names[:3]:  # Show first 3 examples
            print(f"  • {name}")
        if len(names) > 3:
            print(f"  ... and {len(names) - 3} more\n")
