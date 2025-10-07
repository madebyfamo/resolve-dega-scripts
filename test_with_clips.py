#!/usr/bin/env python3
"""Test with a delay after adding clip."""

import DaVinciResolveScript as dvr
import time

resolve = dvr.scriptapp("Resolve")
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()

# Use an existing timeline that has a clip
print("🔍 Looking for a timeline with clips...\n")

for i in range(1, int(proj.GetTimelineCount()) + 1):
    tl = proj.GetTimelineByIndex(i)
    if not tl:
        continue

    name = tl.GetName()

    # Check if it has clips
    audio_tracks = tl.GetTrackCount("audio")
    has_clips = False

    for idx in range(1, audio_tracks + 1):
        items = tl.GetItemListInTrack("audio", idx)
        if items and len(items) > 0:
            has_clips = True
            break

    if not has_clips:
        video_tracks = tl.GetTrackCount("video")
        for idx in range(1, video_tracks + 1):
            items = tl.GetItemListInTrack("video", idx)
            if items and len(items) > 0:
                has_clips = True
                break

    if has_clips:
        print(f"✅ Found timeline with clips: {name}")

        # Check current markers
        markers = tl.GetMarkers()
        marker_count = len(markers) if markers else 0
        print(f"  Current markers: {marker_count}\n")

        # Try adding a new marker
        print("🏷️ Trying to add marker @ frame 100...")
        success = tl.AddMarker(100, "Cocoa", "Test API Marker", "Testing on timeline with clips", 0)

        if success:
            print("  ✅ SUCCESS! Marker added to timeline with clips!")
        else:
            print("  ❌ Failed even on timeline with clips")

        # Check final count
        markers = tl.GetMarkers()
        new_count = len(markers) if markers else 0
        print(f"  Final markers: {new_count}")

        break
