#!/usr/bin/env python3
"""Test the silent clip fallback manually."""

import DaVinciResolveScript as dvr
import os
import wave
import struct

resolve = dvr.scriptapp("Resolve")
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()

mp = proj.GetMediaPool()
root = mp.GetRootFolder()


# Create silent WAV
def create_silence(seconds=2.0):
    assets_dir = os.path.expanduser("~/tmp/dega_assets")
    os.makedirs(assets_dir, exist_ok=True)
    wav_path = os.path.join(assets_dir, "_test_silence_2s.wav")

    if not os.path.exists(wav_path):
        sr = 48000
        channels = 2
        bits = 16
        nframes = int(sr * seconds)

        with wave.open(wav_path, "wb") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(bits // 8)
            wf.setframerate(sr)
            silence = struct.pack("<h", 0)
            wf.writeframes(silence * nframes * channels)

    return wav_path


test_name = "TEST_SILENCE_FALLBACK"

# Delete if exists
for i in range(1, int(proj.GetTimelineCount()) + 1):
    tl = proj.GetTimelineByIndex(i)
    if tl and tl.GetName() == test_name:
        mp.DeleteTimelines([tl])
        break

# Create fresh timeline
mp.SetCurrentFolder(root)
tl = mp.CreateEmptyTimeline(test_name)

print(f"✅ Created: {test_name}\n")

# Check initial state
print("📊 Initial state:")
audio_tracks = tl.GetTrackCount("audio")
print(f"  Audio tracks: {audio_tracks}")
for idx in range(1, audio_tracks + 1):
    items = tl.GetItemListInTrack("audio", idx)
    print(f"  Track A{idx} items: {len(items) if items else 0}")

# Import and append silent clip
print("\n🔧 Adding silent clip...")
wav_path = create_silence(2.0)
print(f"  WAV path: {wav_path}")

items = mp.ImportMedia([wav_path])
print(f"  ImportMedia result: {items}")

if items:
    if isinstance(items, dict):
        items = list(items.values())

    print(f"  Items to append: {len(items)}")

    # Set timeline as current
    proj.SetCurrentTimeline(tl)

    # Append to timeline
    ok = mp.AppendToTimeline([items[0]])
    print(f"  AppendToTimeline result: {ok}")

# Check state after adding clip
print("\n📊 State after adding clip:")
for idx in range(1, audio_tracks + 1):
    items = tl.GetItemListInTrack("audio", idx)
    print(f"  Track A{idx} items: {len(items) if items else 0}")

# NOW try adding markers
print("\n🏷️ Adding markers after clip...")

markers = [
    (0, "Purple", "Frame 0"),
    (30, "Pink", "Frame 30"),
    (60, "Yellow", "Frame 60"),
]

added = 0
for frame, color, name in markers:
    success = tl.AddMarker(frame, color, name, "Test", 0)
    status = "✅" if success else "❌"
    print(f"  {status} {name} @ frame {frame}")
    if success:
        added += 1

print(f"\n📊 Added {added}/3 markers")

# Check final marker count
markers_check = tl.GetMarkers()
count = len(markers_check) if markers_check else 0
print(f"📊 Final marker count: {count}")
