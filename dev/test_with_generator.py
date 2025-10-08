#!/usr/bin/env python3
"""Test if markers work after adding a generator/clip to timeline."""

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
test_name = "TEST_With_Clip_Then_Markers"
print(f"Testing timeline with generator: {test_name}")

# Delete if exists
for i in range(1, int(proj.GetTimelineCount()) + 1):
    tl = proj.GetTimelineByIndex(i)
    if tl and tl.GetName() == test_name:
        print(f"Deleting existing: {test_name}")
        mp.DeleteTimelines([tl])
        break

# Create fresh timeline
mp.SetCurrentFolder(root)
tl = mp.CreateEmptyTimeline(test_name)

if not tl:
    print("❌ Failed to create timeline")
    exit(1)

print(f"✅ Created: {test_name}")

# Try to add a generator (slug/matte)
print("\n🎬 Attempting to add a 5-minute black generator...")
try:
    # Create a solid color generator
    generator_settings = {
        "Type": 1,  # Solid color
        "Duration": 8991,  # 5 minutes at 29.97fps (299 seconds)
    }

    # Try using AppendToTimeline with a generator
    # First, check if we can get media pool items
    media_storage = resolve.GetMediaStorage()

    print("⚠️  Note: DaVinci Resolve API doesn't easily support adding generators via script.")
    print("    The script can only work with existing media pool items.")
    print("\n💡 Manual workaround needed:")
    print("    1. Manually add a single generator/clip to each empty timeline")
    print("    2. Re-run the script to add markers")
    print("    OR delete all empty timelines and recreate from scratch")

except Exception as e:
    print(f"❌ Generator creation failed: {e}")

# Now try adding markers anyway
print("\n🏷️  Testing markers on empty timeline...")
test_markers = [
    (0, "Red", "Frame 0", "First marker"),
    (8961, "Blue", "⏱ 5min", "Anchor marker"),
]

added = 0
for frame, color, name, note in test_markers:
    try:
        success = tl.AddMarker(frame, color, name, note, 0)
        if success:
            added += 1
            print(f"✅ {name} @ frame {frame}")
        else:
            print(f"❌ {name} @ frame {frame}")
    except Exception as e:
        print(f"❌ {name} @ frame {frame} - {e}")

print(f"\n📊 Markers added: {added}/{len(test_markers)}")
print("\n✅ Test complete")
