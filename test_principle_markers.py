#!/usr/bin/env python3
"""
Quick test to verify principle marker detection logic
Run this to confirm get_principle_markers_for_title() returns the right markers
"""


# Copy the helper functions from dega_formula_builder_enhanced.py
def _mm(when, color, name, dur, notes):
    return {"t": float(when), "color": color, "name": name, "dur": float(dur), "notes": notes}


def _mp(t, color, name, notes, dur=0.0):
    return _mm(t, color, name, dur, notes)


# Copy the PRINCIPLE_PACKS dictionary
PRINCIPLE_PACKS = {
    "scenes_segments": [
        _mp(
            0.0,
            "Purple",
            "PRINCIPLES — Scenes/Segments",
            "Research-backed principles for scene/segment editing. "
            "Use as needed for your creative approach.",
        ),
        _mp(
            6.0,
            "Pink",
            "Micro-jolt cadence",
            "Every 0.5–2s: intentional shift (cut, zoom, color, layer). "
            "Avoids monotony, rewards dopamine-seeking attention.",
        ),
        _mp(
            10.0,
            "Yellow",
            "Loop seam awareness",
            "If segment loops: final frame should flow into first naturally "
            "(camera/motion continuity or motivic 'reset').",
        ),
    ],
    "shotfx": [
        _mp(
            0.0,
            "Purple",
            "PRINCIPLES — ShotFX",
            "Composite-focused principles for polished, clean plates.",
        ),
        _mp(
            6.0,
            "Pink",
            "Mask edges & tracking",
            "Soft-edge masks (3–10px feather), check tracking drift. "
            "Motion-blur pass if subject moves fast.",
        ),
        _mp(
            10.0,
            "Yellow",
            "Look exploration",
            "Match grade/bloom/grain to main timeline or create intentional contrast.",
        ),
    ],
    "talking_head": [
        _mp(
            0.0, "Purple", "PRINCIPLES — Talking Head", "Short-form talking-head pacing and rhythm."
        ),
        _mp(
            6.0,
            "Pink",
            "Lead with the point",
            "Hook in first 2 seconds. Thesis → insight → payoff. "
            "No long wind-ups or slow context.",
        ),
        _mp(
            10.0,
            "Yellow",
            "B-roll window & captions",
            "Insert broll when speaker pauses or emphasizes. "
            "Always add captions for accessibility and retention.",
        ),
    ],
    "fashion": [
        _mp(
            0.0,
            "Purple",
            "PRINCIPLES — Fashion/OOTD",
            "Visual storytelling for style, silhouette, and movement.",
        ),
        _mp(
            6.0,
            "Pink",
            "Silhouette → detail → motion",
            "Establish full-body, then close-ups (fabric, accessories). "
            "Include motion: walk, twirl, or gesture.",
        ),
        _mp(
            10.0,
            "Yellow",
            "Thumbnail candidates",
            "Pick 2–3 striking frames: bold color, unique angle, or confident pose.",
        ),
    ],
    "day_in_the_life": [
        _mp(
            0.0,
            "Purple",
            "PRINCIPLES — Day in the Life",
            "Authentic, episodic structure with intentional pacing.",
        ),
        _mp(
            6.0,
            "Pink",
            "Intent fast, atmos pass",
            "Show what you're doing (intent) in 1–2 seconds. "
            "Then allow a beat of atmosphere (location, vibe).",
        ),
        _mp(
            10.0,
            "Yellow",
            "Transition moment",
            "Mark natural chapter shifts (location change, time jump). "
            "Use sound design or a brief fade for narrative punctuation.",
        ),
        _mp(
            14.0,
            "Cyan",
            "Cycle closure",
            "Conclude with a sense of completion: sun down, final thought, or callback to hook.",
        ),
    ],
    "cook_ups": [
        _mp(
            0.0,
            "Purple",
            "PRINCIPLES — Cook-Ups",
            "Music/sound production storytelling. Show process, not just results.",
        ),
        _mp(
            6.0,
            "Pink",
            "Introduce motif early",
            "Lead with a catchy loop, melody, or drum pattern. "
            "Hook attention before showing DAW screens.",
        ),
        _mp(
            10.0,
            "Yellow",
            "Arrangement choice",
            "Show one creative decision (effect tweak, layer addition, mix move). "
            "Narrate or caption the 'why' if helpful.",
        ),
        _mp(
            14.0,
            "Cyan",
            "UI insert & vibe spike",
            "Quick DAW/plugin screen share, then return to creator or final playback. "
            "End with energy: head-nod, smile, or satisfying build drop.",
        ),
    ],
}


def get_principle_markers_for_title(title):
    """
    Return a list of principle markers if the timeline matches a non-master content type.
    Returns [] for master timelines or unmatched names.
    """
    t = (title or "").lower()

    # Skip all master timelines
    if (
        ("money master" in t)
        or ("mv master" in t)
        or ("fashion master" in t)
        or ("th master" in t)
        or ("dil master" in t)
        or ("cook-up master" in t)
        or (" master —" in t)
    ):
        return []

    # Normalize em-dash to regular hyphen for consistent matching
    norm = t.replace("—", "-")

    # Match by prefix
    if norm.startswith("shotfx -"):
        return PRINCIPLE_PACKS["shotfx"]
    if norm.startswith("segment -") or norm.startswith("scenes & segments"):
        return PRINCIPLE_PACKS["scenes_segments"]
    if norm.startswith("interview -") or norm.startswith("talking head"):
        return PRINCIPLE_PACKS["talking_head"]
    if norm.startswith("look -") or norm.startswith("fashion"):
        return PRINCIPLE_PACKS["fashion"]
    if norm.startswith("chapter -") or norm.startswith("day in the life"):
        return PRINCIPLE_PACKS["day_in_the_life"]
    if norm.startswith("section -") or norm.startswith("cook-up"):
        return PRINCIPLE_PACKS["cook_ups"]

    return []


# Test cases
test_timelines = [
    "Segment — Hook Performance — ⏱ 29.97p • 📐 2160×3840",
    "ShotFX — Clone in Hallway — ⏱ 29.97p • 📐 2160×3840",
    "Interview — Radio Cut + B-Roll — ⏱ 29.97p • 📐 2160×3840",
    "LOOK — (Generic) — ⏱ 29.97p • 📐 2160×3840",
    "Chapter — (Generic) — ⏱ 29.97p • 📐 2160×3840",
    "Section — (Generic) — ⏱ 29.97p • 📐 2160×3840",
    "MV Master — ⏱ 29.97p • 📐 2160×3840",
    "Fashion Master — ⏱ 29.97p • 📐 2160×3840",
    "Money Master — 12s (IG short) — 2160×3840 • 29.97p",
]

print("=" * 80)
print("PRINCIPLE MARKER DETECTION TEST")
print("=" * 80)

for timeline in test_timelines:
    markers = get_principle_markers_for_title(timeline)
    marker_count = len(markers)
    status = "✅" if marker_count > 0 else "⚪️"
    print(f"\n{status} {timeline}")
    print(f"   → {marker_count} markers")
    if marker_count > 0:
        for i, m in enumerate(markers, 1):
            print(f"      {i}. {m['name']} ({m['color']}) @ {m['t']}s")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
