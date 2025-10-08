#!/usr/bin/env python3
"""Test creating a master timeline with markers like the script does."""

import DaVinciResolveScript as dvr

resolve = dvr.scriptapp("Resolve")
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()

if not proj:
    print("❌ No project open")
    exit(1)

mp = proj.GetMediaPool()
root = mp.GetRootFolder()

# Test timeline name
test_name = "TEST_Master — 12s — 2160×3840 • 29.97p"
print(f"Testing master timeline creation: {test_name}")

# Delete if exists
for i in range(1, int(proj.GetTimelineCount()) + 1):
    tl = proj.GetTimelineByIndex(i)
    if tl and tl.GetName() == test_name:
        print(f"❌ Deleting existing: {test_name}")
        mp.DeleteTimelines([tl])
        break

# Create fresh with project settings
print("\nSetting project defaults for 2160×3840 @ 29.97fps...")
proj.SetSetting("timelineResolutionWidth", "2160")
proj.SetSetting("timelineResolutionHeight", "3840")
proj.SetSetting("timelinePlaybackFrameRate", "29.97")
proj.SetSetting("timelineFrameRate", "29.97")

mp.SetCurrentFolder(root)
tl = mp.CreateEmptyTimeline(test_name)

if not tl:
    print("❌ Failed to create timeline")
    exit(1)

print(f"✅ Created empty timeline: {test_name}")

# Try adding markers like MARKERS_12 from the script
# MARKERS_12 has markers at: 0s, 3s, 4.5s, 8s, 9s, 11.6s
test_markers = [
    (0, "Red", "HOOK", "0.0s - Range 0–3s"),
    (90, "Orange", "DRAW", "3.0s - Range 4–6s"),
    (135, "Magenta", "INTERRUPT #1", "4.5s - ≤0.7s micro cut"),
    (240, "Green", "COMMIT / PAYOFF", "8.0s - Range 3–5s"),
    (270, "Magenta", "INTERRUPT #2", "9.0s - Second micro flip"),
    (348, "Yellow", "LOOP / CTA", "11.6s - Range 0.3–1.0s"),
]

print("\nAttempting to add markers...")
added = 0
for frame, color, name, note in test_markers:
    try:
        success = tl.AddMarker(frame, color, name, note, 0)
        if success:
            added += 1
            print(f"✅ Frame {frame:5d} ({frame/29.97:5.1f}s): {name}")
        else:
            print(f"❌ Frame {frame:5d} ({frame/29.97:5.1f}s): {name}")
    except Exception as e:
        print(f"❌ Frame {frame:5d} ({frame/29.97:5.1f}s): {name} - Exception: {e}")

# Check final state
try:
    markers = tl.GetMarkers()
    count = len(markers) if markers else 0
    print(f"\n📊 Final marker count: {count} (attempted: {len(test_markers)}, added: {added})")

    # Check timeline duration
    try:
        end_frame = tl.GetEndFrame()
        print(f"📏 Timeline end frame: {end_frame}")
    except:
        print(f"📏 Timeline end frame: Unknown")

except Exception as e:
    print(f"\n⚠️ Could not get markers: {e}")

print("\n✅ Test complete")
print("\n💡 If markers failed, it confirms empty timelines cannot accept markers.")
print("💡 If markers succeeded, check if timeline now has duration from the last marker.")
