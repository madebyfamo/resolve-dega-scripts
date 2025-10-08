#!/usr/bin/env python3
"""Inspect existing master timelines to see what markers they actually have."""

import DaVinciResolveScript as dvr

resolve = dvr.scriptapp("Resolve")
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()

print(f"📂 Project: {proj.GetName()}\n")

# Get all timelines
count = int(proj.GetTimelineCount())
print(f"Total timelines: {count}\n")

for i in range(1, count + 1):
    tl = proj.GetTimelineByIndex(i)
    if not tl:
        continue

    name = tl.GetName()
    if "Master" not in name:
        continue

    print(f"━━━ {name} ━━━")

    # Get markers
    markers = tl.GetMarkers()
    if markers:
        print(f"  Marker count: {len(markers)}")
        for frame, data in sorted(markers.items()):
            seconds = frame / 29.97
            print(f"    Frame {frame} ({seconds:.2f}s): [{data.get('color')}] {data.get('name')}")
    else:
        print(f"  No markers")

    # Check timeline duration
    start = tl.GetStartFrame()
    end = tl.GetEndFrame()
    print(f"  Duration: {start} → {end} frames ({(end-start)/29.97:.2f}s)")

    # Check track count
    video_tracks = tl.GetTrackCount("video")
    audio_tracks = tl.GetTrackCount("audio")
    print(f"  Tracks: {video_tracks} video, {audio_tracks} audio")

    print()
