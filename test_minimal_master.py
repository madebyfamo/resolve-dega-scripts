#!/usr/bin/env python3
"""
Minimal test: Create ONE master timeline with markers from scratch.
This replicates exactly what the main script does for Money Master.
"""

import DaVinciResolveScript as dvr
import logging

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

resolve = dvr.scriptapp("Resolve")
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()

if not proj:
    log.error("❌ No project open")
    exit(1)

mp = proj.GetMediaPool()
root = mp.GetRootFolder()


# Use the exact MARKERS_12 from the script
def _mm(t, color, name, dur, note):
    return {"t": t, "color": color, "name": name, "dur": dur, "notes": note}


MARKERS_12 = [
    _mm(
        0.000,
        "Red",
        "HOOK (Attention Spike)",
        3.0,
        "Range 0–3s. Lead with tension/payoff question or bold visual.",
    ),
    _mm(
        3.000,
        "Orange",
        "DRAW (Retain)",
        5.0,
        "Range 4–6s. Layer intrigue (micro plot reveal, tease solution, micro-jolt).",
    ),
    _mm(
        4.500,
        "Magenta",
        "INTERRUPT #1",
        0.0,
        "≤0.7s. Mandatory micro-cut or whip to reset attention.",
    ),
    _mm(
        8.000,
        "Green",
        "COMMIT / PAYOFF",
        4.0,
        "Range 3–5s. Deliver on the hook promise. Make it tight and earned.",
    ),
    _mm(
        9.000,
        "Magenta",
        "INTERRUPT #2",
        0.0,
        "Avoid passive slide to credits—insert a quick reminder (CTA, visual flip, or loop seam).",
    ),
    _mm(
        11.600,
        "Yellow",
        "LOOP / CTA",
        0.4,
        "Range 0.3–1.0s. End on a repeatable motion or micro-tension for replay.",
    ),
]

test_name = "MINIMAL_TEST_Master_12s"
log.info(f"Creating: {test_name}")

# Delete if exists
for i in range(1, int(proj.GetTimelineCount()) + 1):
    tl = proj.GetTimelineByIndex(i)
    if tl and tl.GetName() == test_name:
        log.info(f"Deleting existing: {test_name}")
        mp.DeleteTimelines([tl])
        break

# Set project defaults (exactly like the script)
proj.SetSetting("timelineResolutionWidth", "2160")
proj.SetSetting("timelineResolutionHeight", "3840")
proj.SetSetting("timelinePlaybackFrameRate", "29.97")
proj.SetSetting("timelineFrameRate", "29.97")

# Create timeline
mp.SetCurrentFolder(root)
tl = mp.CreateEmptyTimeline(test_name)

if not tl:
    log.error("❌ CreateEmptyTimeline failed")
    exit(1)

log.info(f"✅ Timeline created: {test_name}")

# Add markers (exactly like the script does)
log.info(f"Adding {len(MARKERS_12)} markers...")


def _sec_to_frames(sec, fps=29.97):
    return int(round(sec * fps))


added = 0
failed = 0
for m in MARKERS_12:
    frame = _sec_to_frames(m["t"])
    dur_frames = _sec_to_frames(m["dur"])

    try:
        success = tl.AddMarker(frame, m["color"], m["name"], m["notes"], dur_frames)
        if success:
            added += 1
            log.info(f"  ✅ {m['name']} @ {m['t']}s (frame {frame})")
        else:
            failed += 1
            log.warning(f"  ❌ {m['name']} @ {m['t']}s (frame {frame})")
    except Exception as e:
        failed += 1
        log.warning(f"  ❌ {m['name']} @ {m['t']}s - Exception: {e}")

log.info(f"\n📊 Results: {added} added, {failed} failed")

# Check final state
try:
    markers = tl.GetMarkers()
    count = len(markers) if markers else 0
    log.info(f"📊 Final marker count: {count}")
except:
    pass

log.info("\n✅ Test complete")
log.info("\n💡 This is the EXACT same process the main script uses for master timelines.")
log.info("💡 If this fails, then master timelines also cannot get markers on creation.")
