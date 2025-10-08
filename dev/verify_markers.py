#!/usr/bin/env python3
"""Verify markers were added to principle timelines."""

import DaVinciResolveScript as dvr

resolve = dvr.scriptapp("Resolve")
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()

print(f"📊 Checking principle timeline markers:\n")

target_timelines = [
    "Segment — Verse Performance",
    "ShotFX — Clone in Hallway",
    "Interview — Radio Cut",
    "LOOK — Rooftop Golden Hour",
    "Chapter — Coffee Run",
    "Section — Teaser / Hook Preview",
]

for i in range(1, int(proj.GetTimelineCount()) + 1):
    tl = proj.GetTimelineByIndex(i)
    if not tl:
        continue

    name = tl.GetName()

    # Check if it matches any target
    for target in target_timelines:
        if target in name:
            markers = tl.GetMarkers()
            count = len(markers) if markers else 0

            print(f"{'✅' if count > 0 else '❌'} {name}")
            print(f"  Markers: {count}")

            if markers and count <= 6:  # Show all if not too many
                for frame, data in sorted(markers.items()):
                    seconds = frame / 29.97
                    print(f"    {seconds:.1f}s: [{data.get('color')}] {data.get('name')}")

            print()
            break
