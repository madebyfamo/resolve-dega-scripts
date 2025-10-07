#!/usr/bin/env python3
"""
Fix the one rogue timeline (Segment — Verse Performance) that has test markers.
Replaces them with correct PRINCIPLES markers.
"""

import DaVinciResolveScript as dvr


def sec_to_frame(sec, fps):
    return int(round(sec * fps))


def add_marker_safe(tl, frame, name, color, note="", dur_frames=1):
    """Resolve 20.2+ requires duration >= 1 frame."""
    if dur_frames < 1:
        dur_frames = 1
    return tl.AddMarker(frame, color, name, note, dur_frames)


def main():
    resolve = dvr.scriptapp("Resolve")
    pm = resolve.GetProjectManager()
    proj = pm.GetCurrentProject()
    
    if not proj:
        print("❌ No project open")
        return
    
    TARGET_NAME = "Segment — Verse Performance"
    
    # Find the timeline
    tl = None
    for i in range(1, int(proj.GetTimelineCount()) + 1):
        t = proj.GetTimelineByIndex(i)
        if t and TARGET_NAME in t.GetName():
            tl = t
            break
    
    if not tl:
        print(f"❌ Timeline not found: {TARGET_NAME}")
        return
    
    print(f"✅ Found: {tl.GetName()}\n")
    
    fps = 29.97
    
    # Clear existing test markers
    existing = tl.GetMarkers() or {}
    print(f"🗑️  Clearing {len(existing)} existing markers...")
    for frame in list(existing.keys()):
        tl.DeleteMarkerAtFrame(frame)
    
    # Add correct PRINCIPLES markers
    PRINCIPLES_MARKERS = [
        (0.0, "PRINCIPLES — Scenes/Segments", "Purple", "Range 0-∞s. Your core workflow guidance for segment-based content."),
        (1.0, "Micro-jolt cadence", "Pink", "Every 3–5s, introduce a small visual/audio shift to maintain retention."),
        (2.0, "Loop seam awareness", "Yellow", "Plan edit around clean loop point (if needed) for repeatable shorts."),
        (299.0, "⏱ 5min anchor", "Blue", "Timeline duration marker (auto-generated)"),
    ]
    
    print(f"\n🏷️  Adding {len(PRINCIPLES_MARKERS)} PRINCIPLES markers...\n")
    
    added = 0
    for seconds, name, color, note in PRINCIPLES_MARKERS:
        frame = sec_to_frame(seconds, fps)
        if add_marker_safe(tl, frame, name, color, note=note, dur_frames=1):
            print(f"  ✅ {seconds}s: {name}")
            added += 1
        else:
            print(f"  ❌ {seconds}s: {name}")
    
    # Verify
    final_markers = tl.GetMarkers() or {}
    print(f"\n📊 Final marker count: {len(final_markers)}")
    print(f"✅ Successfully added {added}/{len(PRINCIPLES_MARKERS)} markers")


if __name__ == "__main__":
    main()
