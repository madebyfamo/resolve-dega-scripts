#!/usr/bin/env python3
"""
DEGA — "The Formula" Builder (Resolve 20.2) — v4.7
Vertical 2160×3840 @ 29.97p • Emoji/Pipe naming • Non-destructive

What's new in v4.7
- Seconds-only pacing: Pure seconds-based cut guidance (no beat math) tailored by lane & tier.
- Butt-joined markers: Adjacent markers extend to touch (1-frame butt) for seamless color bands.
- 6 lanes × 3 tiers: Money, MV, Fashion, Talking, DIL, Cook-Ups each with 12s/22s/30s variants.
- Section-specific guidance: HOOK, DRAW, COMMIT/PAYOFF, etc. get unique seconds ranges per context.
- Applied to ALL timelines: Masters and principle timelines (Segments, ShotFX, Selects, etc.).

What's new in v4.6
- Cut-note enrichment with lane/tier-specific edit pacing guidance
- Tight marker borders (1-frame gaps) for visual clarity

What's new in v4.5
- Tiered marker templates (12s / 22s / 30s) added natively to every lane's Master Build
- Richer marker Notes (research-informed) + explicit timing ranges
- Safe re-seed: markers added only if a timeline has 0 markers (avoids dupes)
"""

import datetime
import logging
import os
import sys
import wave
import struct


# ───────────────────────── Basics / Logging ─────────────────────────
def _script_dir():
    try:
        return os.path.dirname(os.path.realpath(__file__))
    except NameError:
        return os.getcwd()


def setup_logger(name="dega_builder", level=logging.INFO):
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(level)
    log_dir = os.path.join(_script_dir(), "logs")
    try:
        os.makedirs(log_dir, exist_ok=True)
    except Exception:
        log_dir = os.path.expanduser("~/tmp/dega_logs")
        os.makedirs(log_dir, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join(log_dir, f"dega_formula_builder_{stamp}.log")

    fmt = logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s")
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(fmt)
    fh = logging.FileHandler(log_path, mode="w", encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(ch)
    logger.addHandler(fh)
    logger.propagate = False
    logger.info("🚀 DEGA Formula Builder v4.7 starting…")
    logger.info("📝 Log file: %s", log_path)
    return logger


log = setup_logger()
root = logging.getLogger()
if not root.handlers:
    for h in log.handlers:
        root.addHandler(h)
    root.setLevel(log.level)

# ───────────────────────── Resolve bootstrap ─────────────────────────
try:
    import DaVinciResolveScript as dvr
except ImportError:
    dvr = None
try:
    import bmd  # type: ignore
except Exception:
    bmd = None


def get_resolve():
    _bmd = globals().get("bmd")
    if _bmd:
        try:
            r = _bmd.scriptapp("Resolve")
            if r:
                log.info("✅ Connected via bmd.scriptapp")
                return r
        except Exception as e:
            log.warning(f"⚠️ bmd.scriptapp failed: {e}")
    try:
        r = dvr.scriptapp("Resolve") if dvr else None  # type: ignore
        if r:
            log.info("✅ Connected via DaVinciResolveScript")
            return r
    except Exception as e:
        log.error(f"❌ DaVinciResolveScript failed: {e}")
    log.error(
        "❌ Could not acquire Resolve API. Run from Resolve (Workspace ▸ Scripts)."
    )
    sys.exit(1)


# ───────────────────────── Config ─────────────────────────
TODAY = datetime.date.today().strftime("%Y-%m-%d")
PROJECT_NAME = f"DEGA_VERT_{TODAY.replace('-', '_')}"
PROJECT_NAME_FALLBACK = f"DEGA_Project_{datetime.datetime.now().strftime('%H%M%S')}"
WIDTH, HEIGHT, FPS = "2160", "3840", "29.97"

TOP_BINS = [
    "00 | 🏗 Templates",
    "01 | 💰 The Money",
    "02 | 🧪 The Formula",
    "99 | 📦 Exports",
]

# Video tracks — TOP → BOTTOM (checkerboarding A-roll & B-roll)
VIDEO_TRACKS_TOP_TO_BOTTOM = [
    "FX TEMP 🧪",
    "SAFETY 🛑 — Guides (Disable for export)",
    "TITLES 🏷️",
    "GFX — Shapes & Callouts 🟦",
    "LIGHTS & TEXTURES ✨ — Leaks/Flares/Dust",
    "ADJUSTMENT 🟩 — Global Polish",
    "B-ROLL B 🎞️",
    "B-ROLL A 🎞️",
    "A-ROLL B 🎥",
    "A-ROLL A 🎥",
]

# Audio tracks — no numeric prefixes
AUDIO_TRACKS = [
    "DX_A",
    "DX_B",
    "VO_A",
    "VO_B",
    "SFX_HARD",
    "WHOOSH_SWISH",
    "RISERS_REVERSE",
    "STINGERS_MUSFX",
    "MX_A",
    "MX_B",
    "FOLEY_HANDS",
    "FOLEY_CLOTH",
    "FOOTSTEPS",
    "UI_CLICKS",
    "AMB_A",
    "AMB_B",
    "PRINT",
]


# ───────────────────────── Marker templates ─────────────────────────
# Helper for concise marker dicts
def _mm(when, color, name, dur, notes):
    return {
        "t": float(when),
        "color": color,
        "name": name,
        "dur": float(dur),
        "notes": notes,
    }


# Color support/fallbacks per Resolve marker API variety
_SUPPORTED_MARKER_COLORS = {
    "Red",
    "Yellow",
    "Green",
    "Cyan",
    "Blue",
    "Purple",
    "Pink",
    "Black",
    "White",
    "Orange",
}
_COLOR_FALLBACK = {"Magenta": "Pink", "Orange": "Yellow"}

# Shared language guidelines reflected in Notes across lanes:
# - Hooks anchor in 0–3s; interrupts are micro pattern breaks; commits/payoffs are clarity bursts
# - Notes include timing *ranges* so you can stretch/contract safely without losing punch

# MONEY (reference set — reused by MV)
MARKERS_12 = [
    _mm(
        0.000,
        "Red",
        "HOOK",
        3.0,
        "Range 0–3s. Open with the clearest value: a visual or line that states *what this is* and *why it matters* in plain language.",
    ),
    _mm(
        3.000,
        "Orange",
        "DRAW",
        5.0,
        "Range 4–6s. Add one new angle or contrast that deepens curiosity; avoid repeating the hook wording.",
    ),
    _mm(
        4.500,
        "Magenta",
        "INTERRUPT #1",
        0.0,
        "Micro pattern break (≤0.7s). Quick visual flip/cut-in that resets attention without derailing flow.",
    ),
    _mm(
        8.000,
        "Green",
        "COMMIT / PAYOFF",
        4.0,
        "Range 3–5s. Deliver the promised clarity: tight demo/result/visual that proves the premise.",
    ),
    _mm(
        9.000,
        "Magenta",
        "INTERRUPT #2",
        0.0,
        "Second micro jolt; invert framing or swap angle to avoid glide to the finish.",
    ),
    _mm(
        11.600,
        "Yellow",
        "LOOP / CTA",
        0.4,
        "Range 0.3–1.0s. Button that either loops cleanly or gives one frictionless action.",
    ),
]
MARKERS_22 = [
    _mm(
        0.000,
        "Red",
        "HOOK",
        3.0,
        "Range 0–3s. Punchy premise stated plainly; no hedging.",
    ),
    _mm(
        3.000,
        "Orange",
        "DRAW",
        5.0,
        "Range 4–6s. Add context or an unexpected contrast that still supports the hook.",
    ),
    _mm(
        6.000,
        "Magenta",
        "INTERRUPT #1",
        0.0,
        "Early micro jolt (≤0.7s). Keeps the mid-section from flattening.",
    ),
    _mm(
        8.000,
        "Green",
        "COMMIT / PAYOFF #1",
        4.0,
        "Range 3–5s. First clean delivery moment—proof, reveal, or tight before/after.",
    ),
    _mm(
        12.000,
        "Blue",
        "SECOND HOOK",
        3.0,
        "Range 2–4s. Re-hook with a sharper angle or upside; avoid redundancy.",
    ),
    _mm(
        13.500,
        "Magenta",
        "INTERRUPT #2",
        0.0,
        "Quick flip after second hook to prevent plateau.",
    ),
    _mm(
        15.000,
        "Purple",
        "DEVELOP",
        7.0,
        "Range 6–8s. Stack 1–2 supporting beats; no rabbit holes.",
    ),
    _mm(18.500, "Magenta", "INTERRUPT #3", 0.0, "Penultimate jolt to prime the close."),
    _mm(
        21.300,
        "Yellow",
        "LOOP / CTA",
        0.7,
        "Range 0.5–1.2s. Clean loop or minimal ask with on-screen affordance.",
    ),
]
MARKERS_30 = [
    _mm(
        0.000,
        "Red",
        "HOOK",
        3.0,
        "Range 0–3s. Plain-speak promise; strong visual identity.",
    ),
    _mm(
        3.000,
        "Orange",
        "DRAW",
        5.0,
        "Range 4–6s. Elevate intrigue via contrast/constraint/benefit.",
    ),
    _mm(6.000, "Magenta", "INTERRUPT #1", 0.0, "Micro reset to avoid 6–10s slump."),
    _mm(
        8.000, "Green", "COMMIT / PAYOFF #1", 4.0, "Range 3–5s. Hard clarity moment #1."
    ),
    _mm(
        12.000,
        "Blue",
        "SECOND HOOK",
        3.0,
        "Range 2–4s. Alternate entry point for scrollers; new phrasing.",
    ),
    _mm(
        13.500, "Magenta", "INTERRUPT #2", 0.0, "Quick subversion; keep rhythm varied."
    ),
    _mm(
        15.000,
        "Purple",
        "DEVELOP A",
        7.0,
        "Range 6–8s. Expand with one concise supporting angle.",
    ),
    _mm(20.000, "Magenta", "INTERRUPT #3", 0.0, "Reset cadence before last stretch."),
    _mm(
        22.000,
        "Purple",
        "DEVELOP B",
        6.0,
        "Range 5–7s. Second support; avoid duplication.",
    ),
    _mm(26.000, "Magenta", "INTERRUPT #4", 0.0, "Final micro jolt before close."),
    _mm(
        28.000,
        "Yellow",
        "FINAL PAYOFF / LOOP",
        2.0,
        "Range 1.5–3.0s. Clean visual loop or crisp CTA.",
    ),
]

# Lane-specific tweaks (wording nudges) while keeping timing architecture aligned
LANE_MARKERS = {
    # Money & MV share the same cadence; MV wording emphasizes performance/visuals
    "money": {"12s": MARKERS_12, "22s": MARKERS_22, "30s": MARKERS_30},
    "mv": {
        "12s": [
            _mm(
                0.000,
                "Red",
                "HOOK (Signature Visual)",
                3.0,
                "Range 0–3s. Iconic pose/move or bold text: instantly tells what vibe this is.",
            ),
            _mm(
                3.000,
                "Orange",
                "DRAW (Aesthetic Lift)",
                5.0,
                "Range 4–6s. Add a quick look change, location shift, or camera energy.",
            ),
            _mm(
                4.500,
                "Magenta",
                "INTERRUPT #1",
                0.0,
                "≤0.7s. Micro cut/whip/push to reset attention.",
            ),
            _mm(
                8.000,
                "Green",
                "COMMIT / PAYOFF",
                4.0,
                "Range 3–5s. Tight performance moment or strong transition that feels 'earned'.",
            ),
            _mm(
                9.000,
                "Magenta",
                "INTERRUPT #2",
                0.0,
                "Second micro flip to avoid slide to credits.",
            ),
            _mm(
                11.600,
                "Yellow",
                "LOOP / CTA",
                0.4,
                "Range 0.3–1.0s. End on a repeatable motion or subtle action prompt.",
            ),
        ],
        "22s": MARKERS_22,
        "30s": MARKERS_30,
    },
    "fashion": {
        "12s": [
            _mm(
                0.000,
                "Red",
                "HOOK (Hero Fit Moment)",
                3.0,
                "Range 0–3s. One striking silhouette or texture close-up that defines the look.",
            ),
            _mm(
                3.000,
                "Orange",
                "DRAW (Detail Contrast)",
                5.0,
                "Range 4–6s. Switch to fabric, accessories, or motion to add dimension.",
            ),
            _mm(
                6.000, "Magenta", "INTERRUPT #1", 0.0, "≤0.7s. Quick angle/tempo flip."
            ),
            _mm(
                8.000,
                "Green",
                "COMMIT / PAYOFF",
                4.0,
                "Range 3–5s. Full-body reveal or clean style transition.",
            ),
            _mm(
                11.600,
                "Yellow",
                "LOOP / CTA",
                0.4,
                "Range 0.3–1.0s. Loopable step/turn or minimal ask.",
            ),
        ],
        "22s": [
            _mm(
                0.000,
                "Red",
                "HOOK (Look Identity)",
                3.0,
                "Range 0–3s. State the vibe: street/clean/retro/etc. via a hero frame.",
            ),
            _mm(
                3.000,
                "Orange",
                "DRAW (Texture/Movement)",
                5.0,
                "Range 4–6s. Fabric motion or accessory interaction.",
            ),
            _mm(
                6.000,
                "Magenta",
                "INTERRUPT #1",
                0.0,
                "≤0.7s. Angle/location micro switch.",
            ),
            _mm(
                8.000,
                "Green",
                "COMMIT / PAYOFF #1",
                4.0,
                "Range 3–5s. Full outfit clarity.",
            ),
            _mm(
                12.000,
                "Blue",
                "SECOND HOOK (Alt Styling)",
                3.0,
                "Range 2–4s. Secondary combo or layer change.",
            ),
            _mm(
                15.000,
                "Purple",
                "DEVELOP",
                7.0,
                "Range 6–8s. 1–2 beats: close-ups, pocket pulls, hem, shoe detail.",
            ),
            _mm(
                21.300,
                "Yellow",
                "LOOP / CTA",
                0.7,
                "Range 0.5–1.2s. Loopable walk-by or glance.",
            ),
        ],
        "30s": [
            _mm(
                0.000,
                "Red",
                "HOOK (Statement Frame)",
                3.0,
                "Range 0–3s. Pose, lensing, or lighting that telegraphs tone.",
            ),
            _mm(
                3.000,
                "Orange",
                "DRAW (Cutaway Detail)",
                5.0,
                "Range 4–6s. Textures, stitching, hardware.",
            ),
            _mm(6.000, "Magenta", "INTERRUPT #1", 0.0, "Micro jolt."),
            _mm(
                8.000,
                "Green",
                "COMMIT / PAYOFF #1",
                4.0,
                "Range 3–5s. Head-to-toe moment.",
            ),
            _mm(
                12.000,
                "Blue",
                "SECOND HOOK",
                3.0,
                "Range 2–4s. Alternate palette/prop.",
            ),
            _mm(
                15.000,
                "Purple",
                "DEVELOP A",
                7.0,
                "Range 6–8s. Movement sequence: walk, turn, sit.",
            ),
            _mm(
                22.000,
                "Purple",
                "DEVELOP B",
                6.0,
                "Range 5–7s. Environment integration.",
            ),
            _mm(
                28.000,
                "Yellow",
                "FINAL PAYOFF / LOOP",
                2.0,
                "Range 1.5–3.0s. Seamless loop or subtle CTA.",
            ),
        ],
    },
    "talking": {
        "12s": [
            _mm(
                0.000,
                "Red",
                "HOOK (Plain-Speak Claim)",
                3.0,
                "Range 0–3s. One-sentence promise with a direct face angle.",
            ),
            _mm(
                3.000,
                "Orange",
                "DRAW (Setup in One Line)",
                5.0,
                "Range 4–6s. Short context that *increases* curiosity.",
            ),
            _mm(
                6.000,
                "Magenta",
                "INTERRUPT #1",
                0.0,
                "≤0.7s. Insert quick B-roll or on-screen receipt.",
            ),
            _mm(
                8.000,
                "Green",
                "COMMIT / PAYOFF",
                4.0,
                "Range 3–5s. The clear takeaway or micro demo.",
            ),
            _mm(
                11.600,
                "Yellow",
                "LOOP / CTA",
                0.4,
                "Range 0.3–1.0s. Frictionless close.",
            ),
        ],
        "22s": [
            _mm(
                0.000,
                "Red",
                "HOOK (Outcome First)",
                3.0,
                "Range 0–3s. Lead with result/benefit plainly.",
            ),
            _mm(
                3.000,
                "Orange",
                "DRAW (Short Context)",
                5.0,
                "Range 4–6s. Add one surprise fact or contrast.",
            ),
            _mm(
                6.000,
                "Magenta",
                "INTERRUPT #1",
                0.0,
                "≤0.7s. Pattern break: quick insert or angle swap.",
            ),
            _mm(
                8.000,
                "Green",
                "COMMIT / PAYOFF #1",
                4.0,
                "Range 3–5s. First clear point.",
            ),
            _mm(
                12.000,
                "Blue",
                "SECOND HOOK",
                3.0,
                "Range 2–4s. Re-articulate upside in fresher words.",
            ),
            _mm(
                15.000,
                "Purple",
                "DEVELOP",
                7.0,
                "Range 6–8s. One supporting example; avoid tangents.",
            ),
            _mm(21.300, "Yellow", "LOOP / CTA", 0.7, "Range 0.5–1.2s. End crisp."),
        ],
        "30s": [
            _mm(0.000, "Red", "HOOK (Punchy Thesis)", 3.0, "Range 0–3s. No hedging."),
            _mm(
                3.000,
                "Orange",
                "DRAW (Angle Boost)",
                5.0,
                "Range 4–6s. Sharpen tension without jargon.",
            ),
            _mm(6.000, "Magenta", "INTERRUPT #1", 0.0, "Micro reset."),
            _mm(
                8.000,
                "Green",
                "COMMIT / PAYOFF #1",
                4.0,
                "Range 3–5s. Clear, specific point.",
            ),
            _mm(
                12.000,
                "Blue",
                "SECOND HOOK",
                3.0,
                "Range 2–4s. New phrasing for late arrivals.",
            ),
            _mm(
                15.000, "Purple", "DEVELOP A", 7.0, "Range 6–8s. Example or tiny case."
            ),
            _mm(
                22.000,
                "Purple",
                "DEVELOP B",
                6.0,
                "Range 5–7s. Short application/implication.",
            ),
            _mm(
                28.000,
                "Yellow",
                "FINAL PAYOFF / LOOP",
                2.0,
                "Range 1.5–3.0s. Tight loop or ask.",
            ),
        ],
    },
    "dil": {  # Day in the Life
        "12s": [
            _mm(
                0.000,
                "Red",
                "HOOK (Moment in Progress)",
                3.0,
                "Range 0–3s. Drop viewer into motion; avoid slow preamble.",
            ),
            _mm(
                3.000,
                "Orange",
                "DRAW (What's Next?)",
                5.0,
                "Range 4–6s. Tease destination/task contrast.",
            ),
            _mm(6.000, "Magenta", "INTERRUPT #1", 0.0, "≤0.7s. Tempo flip."),
            _mm(
                8.000,
                "Green",
                "COMMIT / PAYOFF",
                4.0,
                "Range 3–5s. Satisfying micro-resolution (arrive/complete/transition).",
            ),
            _mm(
                11.600,
                "Yellow",
                "LOOP / CTA",
                0.4,
                "Range 0.3–1.0s. Loopable motion or minimal ask.",
            ),
        ],
        "22s": [
            _mm(0.000, "Red", "HOOK (Drop-In)", 3.0, "Range 0–3s. Start mid-action."),
            _mm(
                3.000,
                "Orange",
                "DRAW (Mini Arc)",
                5.0,
                "Range 4–6s. Set tiny objective/change.",
            ),
            _mm(6.000, "Magenta", "INTERRUPT #1", 0.0, "≤0.7s. Micro reset."),
            _mm(
                8.000,
                "Green",
                "COMMIT / PAYOFF #1",
                4.0,
                "Range 3–5s. Hit a checkpoint.",
            ),
            _mm(12.000, "Blue", "SECOND HOOK", 3.0, "Range 2–4s. New micro-goal."),
            _mm(
                15.000,
                "Purple",
                "DEVELOP",
                7.0,
                "Range 6–8s. Texture beats (ambient, details).",
            ),
            _mm(
                21.300,
                "Yellow",
                "LOOP / CTA",
                0.7,
                "Range 0.5–1.2s. End in motion for loop.",
            ),
        ],
        "30s": [
            _mm(
                0.000,
                "Red",
                "HOOK (Live Snapshot)",
                3.0,
                "Range 0–3s. Immediate immersion.",
            ),
            _mm(
                3.000,
                "Orange",
                "DRAW (Tension/Contrast)",
                5.0,
                "Range 4–6s. Set a tiny tension to resolve.",
            ),
            _mm(6.000, "Magenta", "INTERRUPT #1", 0.0, "Quick changeup."),
            _mm(
                8.000,
                "Green",
                "COMMIT / PAYOFF #1",
                4.0,
                "Range 3–5s. Satisfy the first micro-goal.",
            ),
            _mm(12.000, "Blue", "SECOND HOOK", 3.0, "Range 2–4s. Lure late scrollers."),
            _mm(
                15.000, "Purple", "DEVELOP A", 7.0, "Range 6–8s. Environment & texture."
            ),
            _mm(
                22.000,
                "Purple",
                "DEVELOP B",
                6.0,
                "Range 5–7s. Human beat or detail set.",
            ),
            _mm(
                28.000,
                "Yellow",
                "FINAL PAYOFF / LOOP",
                2.0,
                "Range 1.5–3.0s. Loopable exit/enter.",
            ),
        ],
    },
    "cook": {  # Cook-Ups
        "12s": [
            _mm(
                0.000,
                "Red",
                "HOOK (Signature Sound/Move)",
                3.0,
                "Range 0–3s. Instantly show the identity: pad hit, finger drum, or motif.",
            ),
            _mm(
                3.000,
                "Orange",
                "DRAW (Layer or Constraint)",
                5.0,
                "Range 4–6s. Tease a layer you'll add or a flip you'll attempt.",
            ),
            _mm(
                6.000,
                "Magenta",
                "INTERRUPT #1",
                0.0,
                "≤0.7s. Micro switch to screen/overhead.",
            ),
            _mm(
                8.000,
                "Green",
                "COMMIT / PAYOFF",
                4.0,
                "Range 3–5s. Small but satisfying musical 'click' (layer locks, groove snaps).",
            ),
            _mm(
                11.600,
                "Yellow",
                "LOOP / CTA",
                0.4,
                "Range 0.3–1.0s. Seamless loop or tiny ask.",
            ),
        ],
        "22s": [
            _mm(
                0.000,
                "Red",
                "HOOK (Instant Identity)",
                3.0,
                "Range 0–3s. The 'ohhh' sound/move first.",
            ),
            _mm(
                3.000,
                "Orange",
                "DRAW (What You'll Build)",
                5.0,
                "Range 4–6s. Promise the flip: key/tempo/session context (fast).",
            ),
            _mm(6.000, "Magenta", "INTERRUPT #1", 0.0, "≤0.7s. Angle/UI micro cut."),
            _mm(
                8.000,
                "Green",
                "COMMIT / PAYOFF #1",
                4.0,
                "Range 3–5s. First groove lock.",
            ),
            _mm(12.000, "Blue", "SECOND HOOK", 3.0, "Range 2–4s. Catchier motif/turn."),
            _mm(
                15.000,
                "Purple",
                "DEVELOP",
                7.0,
                "Range 6–8s. Add/remove tension: short fills, mute plays, knob rides.",
            ),
            _mm(21.300, "Yellow", "LOOP / CTA", 0.7, "Range 0.5–1.2s. Clean loop."),
        ],
        "30s": [
            _mm(
                0.000,
                "Red",
                "HOOK (Immediate Sauce)",
                3.0,
                "Range 0–3s. Start at the most *you* sound.",
            ),
            _mm(
                3.000,
                "Orange",
                "DRAW (Set the Game)",
                5.0,
                "Range 4–6s. 'Here's the flip' in one line.",
            ),
            _mm(6.000, "Magenta", "INTERRUPT #1", 0.0, "Micro cut/angle."),
            _mm(
                8.000,
                "Green",
                "COMMIT / PAYOFF #1",
                4.0,
                "Range 3–5s. First lock moment.",
            ),
            _mm(12.000, "Blue", "SECOND HOOK", 3.0, "Range 2–4s. Stronger motif."),
            _mm(15.000, "Purple", "DEVELOP A", 7.0, "Range 6–8s. Arrange mini-arc."),
            _mm(
                22.000,
                "Purple",
                "DEVELOP B",
                6.0,
                "Range 5–7s. Short performance burst.",
            ),
            _mm(
                28.000,
                "Yellow",
                "FINAL PAYOFF / LOOP",
                2.0,
                "Range 1.5–3.0s. Loop land.",
            ),
        ],
    },
}

# ──────────────────────────────────────────────────────────────
# Principle markers (non-interactive reminders for non-master timelines)
# ──────────────────────────────────────────────────────────────


def _mp(t, color, name, notes, dur=0.0):
    # tiny alias - note: _mm takes (t, color, name, dur, notes) so we swap the last two params
    return _mm(t, color, name, dur, notes)


# ───────────────────────── ShotFX variant marker packs ─────────────────────────


def _shotfx_variant_for_title(norm_title: str):
    """Detect which ShotFX variant to use based on timeline name."""
    t = norm_title.lower()
    if "clone" in t:
        return "clone"
    if "clean plate" in t:
        return "clean_plate"
    if "background" in t and "cleanup" in t:
        return "background_cleanup"
    if ("remove" in t and "mic" in t) or "mic cable" in t:
        return "remove_mic_cable"
    if "hand split" in t:
        return "hand_split"
    if "screen insert" in t or "(ui)" in t or ("screen" in t and "insert" in t):
        return "screen_insert"
    return None


SHOTFX_SPECIFIC = {
    # Music-video clone / hallway clone, etc.
    "clone": [
        _mp(
            0.0,
            "Orange",
            "Prep / Plates",
            "Lock-off or perfectly repeatable move. Shoot a clean plate. Keep exposure/WB fixed.",
        ),
        _mp(
            1.0,
            "Blue",
            "Mask strategy",
            "Plan overlap: decide who passes in front. Soft 6–10px feather; avoid hair edges on seams.",
        ),
        _mp(
            2.0,
            "Green",
            "Parallax sanity",
            "If handheld, stabilize BOTH plates before masking. Align on hard verticals (door frames).",
        ),
        _mp(
            3.0,
            "Pink",
            "Seam check (Difference)",
            "Use a Difference/Blend preview to locate seam crawl; nudge mask or warp to match.",
        ),
        _mp(
            4.0,
            "Cyan",
            "Shadows / occlusion",
            "Ensure correct layer order where subjects cross; paint/contact-shadow fix if needed.",
        ),
        _mp(
            5.0,
            "Yellow",
            "Grain / blur match",
            "Match grain and motion blur between plates; add grain last so edges integrate.",
        ),
        _mp(
            6.0,
            "Purple",
            "Continuity glance",
            "Watch hands/feet for pops at the seam during moves; micro-transform if necessary.",
        ),
        _mp(299.0, "Blue", "⏱ 5min anchor", ""),
    ],
    # Beauty cleanup using a clean plate or adjacent frame
    "clean_plate": [
        _mp(
            0.0,
            "Orange",
            "Choose source",
            "Prefer adjacent frames over stills to keep texture; avoid plastic look.",
        ),
        _mp(
            1.0,
            "Blue",
            "Track first",
            "Corner/planar or point track the patch area; stabilize into a working space, then composite.",
        ),
        _mp(
            2.0,
            "Green",
            "Patch blend",
            "Use soft, irregular masks; bias feather into patch. Match local contrast, not global.",
        ),
        _mp(
            3.0,
            "Pink",
            "Skin texture",
            "Do not blur: borrow texture from nearby skin; keep pores. Add tiny monochrome grain if needed.",
        ),
        _mp(
            4.0,
            "Cyan",
            "Temporal sanity",
            "If the head moves, use a short temporal patch (few frames) rather than one still.",
        ),
        _mp(
            5.0,
            "Yellow",
            "Color/Specular",
            "Match micro highlights; reduce spec hotspots with gentle curve, not blur.",
        ),
        _mp(299.0, "Blue", "⏱ 5min anchor", ""),
    ],
    # Removing signs, cables, wall junk, etc.
    "background_cleanup": [
        _mp(
            0.0,
            "Orange",
            "Analyze plane",
            "Is it flat (planar track) or curved (mesh/point)? Choose tracker accordingly.",
        ),
        _mp(
            1.0,
            "Blue",
            "Perspective insert",
            "Corner-pin a clean patch in perspective; match lens distortion if heavy wide.",
        ),
        _mp(
            2.0,
            "Green",
            "Edge contamination",
            "Avoid straight mask edges across textured bricks/tiles; irregular feather sells it.",
        ),
        _mp(
            3.0,
            "Pink",
            "Lighting continuity",
            "Replicate falloff & vignette; add tiny shadow where object was so wall doesn't look 'too clean'.",
        ),
        _mp(
            4.0,
            "Yellow",
            "Grain / noise",
            "Sample target area's noise level; add back after composite to prevent 'cutout' look.",
        ),
        _mp(299.0, "Blue", "⏱ 5min anchor", ""),
    ],
    # Paint-out for a lav/mic cable crossing the hand/arm
    "remove_mic_cable": [
        _mp(
            0.0,
            "Orange",
            "Prep",
            "Stabilize the hand region (temp) to simplify paint/roto; work in stabilized space.",
        ),
        _mp(
            1.0,
            "Blue",
            "Roto contour",
            "Follow knuckle silhouettes; keep feather into skin not into background.",
        ),
        _mp(
            2.0,
            "Green",
            "Clone/patch passes",
            "Borrow from nearby skin frames; track to hand motion; avoid sliding texture.",
        ),
        _mp(
            3.0,
            "Pink",
            "Specular continuity",
            "Rebuild highlight streaks across the patch; tiny dodge/burn beats blur every time.",
        ),
        _mp(
            4.0,
            "Cyan",
            "Motion blur",
            "Match shutter blur on fast finger moves; composite pre-blur, not post.",
        ),
        _mp(
            5.0,
            "Yellow",
            "Final grain",
            "Add matched grain over the composite; check at 100% zoom.",
        ),
        _mp(299.0, "Blue", "⏱ 5min anchor", ""),
    ],
    # Split/duplicate hand at sampler/pads
    "hand_split": [
        _mp(
            0.0,
            "Orange",
            "Plates & timing",
            "Record two performance passes to the same click; clap or beep for sync.",
        ),
        _mp(
            1.0,
            "Blue",
            "Registration",
            "Lock camera; if not, stabilize both plates to the sampler face.",
        ),
        _mp(
            2.0,
            "Green",
            "Mask logic",
            "Choose overlap line along hardware edges; avoid finger edges crossing seam.",
        ),
        _mp(
            3.0,
            "Pink",
            "Pad feedback",
            "Duplicate LED/hit feedback under the correct hand; avoid double-lit pads.",
        ),
        _mp(
            4.0,
            "Cyan",
            "Audio truth",
            "If printing live audio, comp the correct take for each hit; no double hits.",
        ),
        _mp(
            5.0,
            "Yellow",
            "Micro parallax",
            "If hands drift apart, micro-warp one plate to the other near the seam.",
        ),
        _mp(299.0, "Blue", "⏱ 5min anchor", ""),
    ],
    # Screen/UI insert
    "screen_insert": [
        _mp(
            0.0,
            "Orange",
            "Track",
            "Planar track the screen surface; verify track on edges & diagonals, not just corners.",
        ),
        _mp(
            1.0,
            "Blue",
            "Corner pin",
            "Apply corner pin; precomp UI at native aspect; avoid subpixel shimmer by slight defocus.",
        ),
        _mp(
            2.0,
            "Green",
            "Display look",
            "Gamma lift + slight saturation cut; add 1–2 px inner glow and faint reflection pass.",
        ),
        _mp(
            3.0,
            "Pink",
            "Motion blur & flicker",
            "Match shutter blur; optional subtle 0.5–1% luminance flicker to sell emissive panel.",
        ),
        _mp(
            4.0,
            "Cyan",
            "Moire / aliasing",
            "Add tiny grain and 0.2–0.4 px defocus to kill moire while keeping UI crisp enough.",
        ),
        _mp(
            5.0,
            "Yellow",
            "Light spill",
            "Add light wrap onto bezels/fingers at bright frames; very low opacity.",
        ),
        _mp(299.0, "Blue", "⏱ 5min anchor", ""),
    ],
}

# ───────────────────────── Selects & Stringouts packs ─────────────────────────


def _selects_variant_for_title(norm_title: str):
    """Detect which Selects/Stringouts variant to use based on timeline name."""
    t = norm_title.lower()
    # Music-video / general performance selects
    if "perf selects" in t or "performance selects" in t:
        return "mv_perf"
    # General B-Roll selects used across lanes
    if "b-roll selects" in t or "broll selects" in t:
        return "broll"
    # Fashion
    if "look selects" in t:
        return "fashion_look"
    # Talking head
    if "a-roll selects" in t or "aroll selects" in t:
        return "th_aroll"
    # Day in the Life
    if "selects — commute" in t or "selects - commute" in t or "commute" in t:
        return "dil_commute"
    if "coffee" in t:
        return "dil_coffee"
    if t.startswith("selects —") or t.startswith("selects -"):
        return "dil_generic"
    # Cook-Ups
    if "overhead selects" in t:
        return "cook_overhead"
    if "front cam selects" in t or "front-camera selects" in t:
        return "cook_front"
    if "foley/prod selects" in t or "foley selects" in t or "prod selects" in t:
        return "cook_foley"
    # Stringouts (generic)
    if "stringout" in t:
        return "stringout_generic"
    return None


SELECTS_BASE = [
    _mp(
        0.0,
        "Purple",
        "SELECTS — Workflow",
        "Pass 1: reject hard misses. Pass 2: keep only 'A' material. Pass 3: choose alts.",
    ),
    _mp(
        1.0,
        "Orange",
        "Labeling & notes",
        "Use ⭐/color or keywords in Notes: hook, verse, cutaway, reaction, alt, NG.",
    ),
    _mp(
        2.0,
        "Blue",
        "Cut points",
        "Prefer cuts on motion/syllables; add 6–12f handles to each pick for safety.",
    ),
    _mp(
        3.0,
        "Green",
        "Sync sanity",
        "Mark claps/peaks; verify frame-accurate sync against waveform/transients.",
    ),
    _mp(
        4.0,
        "Yellow",
        "Stringout pointers",
        "Range-mark best beats; leave short gaps between ideas to hear pacing honestly.",
    ),
    _mp(299.0, "Blue", "⏱ 5min anchor", ""),
]

SELECTS_SPECIFIC = {
    # ——— Music-Video
    "mv_perf": [
        _mp(
            5.0,
            "Red",
            "Lyric map",
            "Note bar:line references in Notes (e.g., V1L3). Keep best energy + clean lipsync.",
        ),
        _mp(
            6.0,
            "Blue",
            "Angle variety",
            "Favor angle changes on rhyme landings; avoid 3+ consecutive takes of same lens.",
        ),
        _mp(
            7.0,
            "Pink",
            "Micro-ramps",
            "Tag rampable hits (impact/word) for later 90–110% time-micro to sell emphasis.",
        ),
    ],
    "broll": [
        _mp(
            5.0,
            "Orange",
            "Texture diversity",
            "Collect movement textures (hands, lights, environment). Avoid duplicates of same move.",
        ),
        _mp(
            6.0,
            "Cyan",
            "Parallax / depth",
            "Prefer foreground passes & reveals; tag any perfect whip/cover for transitions.",
        ),
        _mp(
            7.0,
            "Green",
            "Cutaway purpose",
            "Each B-roll pick should illustrate a lyric/idea or hide an A-roll cut.",
        ),
    ],
    # ——— Fashion
    "fashion_look": [
        _mp(
            5.0,
            "Red",
            "Silhouette first",
            "Pick one clean full-body read per look; then 2–3 detail shots (fabric, hardware).",
        ),
        _mp(
            6.0,
            "Blue",
            "Motion beauty",
            "Walk/turn/hair moments with flow; reject frames that crush garment shape.",
        ),
        _mp(
            7.0,
            "Yellow",
            "Color/texture continuity",
            "Note lighting shifts; tag candidates for thumbnail/carousel.",
        ),
    ],
    # ——— Talking Head
    "th_aroll": [
        _mp(
            5.0,
            "Red",
            "Message spine",
            "Select crisp claims and proofs; cut fillers/false starts/breath-tails.",
        ),
        _mp(
            6.0,
            "Blue",
            "Cut on gesture",
            "Hide jump cuts under head/hand motion; tag phrases needing B-roll coverage.",
        ),
        _mp(
            7.0,
            "Green",
            "Caption sync",
            "Keep phrase boundaries clean for line breaks; avoid mid-word cuts.",
        ),
    ],
    "th_broll": [
        _mp(
            5.0,
            "Orange",
            "Illustrative matches",
            "Pick visuals that literally prove the sentence; 1–2 per point max.",
        ),
        _mp(
            6.0,
            "Cyan",
            "Readability",
            "Avoid busy frames behind captions; prefer negative space or shallow DOF.",
        ),
    ],
    # ——— Day in the Life
    "dil_generic": [
        _mp(
            5.0,
            "Red",
            "Micro-scenes",
            "Collect clear begin→middle→end beats (3–6s each).",
        ),
        _mp(
            6.0,
            "Blue",
            "Entrances/Exits",
            "Favor shots with natural in/out motion for seamless chaining.",
        ),
    ],
    "dil_commute": [
        _mp(
            5.0,
            "Orange",
            "Travel rhythm",
            "Wheels/doors/steps ambience; grab a few speed & direction variations.",
        ),
        _mp(
            6.0,
            "Green",
            "Landmarks",
            "Tag 1–2 location wides for context; hold for 0.5–1.0s longer.",
        ),
    ],
    "dil_coffee": [
        _mp(
            5.0,
            "Pink",
            "Hands & steam",
            "Close-ups of pour/steam; use them to reset cadence later.",
        ),
        _mp(
            6.0,
            "Yellow",
            "Loop beats",
            "Pick a looping action (stir, sip, door swing) for intros/outros.",
        ),
    ],
    # ——— Cook-Ups
    "cook_overhead": [
        _mp(
            5.0,
            "Red",
            "Clean hits",
            "Choose takes with clear pad contact & stable wrist; reject occluded hits.",
        ),
        _mp(
            6.0,
            "Blue",
            "UI context",
            "Grab short UI pans for key/plugin; make sure values are legible.",
        ),
    ],
    "cook_front": [
        _mp(
            5.0,
            "Orange",
            "Energy & eye line",
            "Prefer takes with micro-groove and camera engagement; avoid dead stares.",
        ),
        _mp(
            6.0,
            "Green",
            "Reveal moments",
            "Pick sequences that set up/pay off arrangement changes.",
        ),
    ],
    "cook_foley": [
        _mp(
            5.0,
            "Cyan",
            "Transient truth",
            "Select crisp knob turns/clicks; align to grid transient if needed.",
        ),
        _mp(
            6.0,
            "Yellow",
            "Variety",
            "Gather a library: short/long whooshes, reverse, button, cloth, hands.",
        ),
    ],
    # ——— Stringout (generic fallback)
    "stringout_generic": [
        _mp(
            5.0,
            "Red",
            "Order",
            "Hook → context → develop → payoff. Keep a 3:1 selects-to-runtime ratio.",
        ),
        _mp(
            6.0,
            "Blue",
            "Air for pacing",
            "Leave tiny gaps between ideas; listen without music first, then add bed.",
        ),
        _mp(
            7.0,
            "Green",
            "Markers to beats",
            "Range-mark final beats to guide transitions and graphics later.",
        ),
    ],
}


PRINCIPLE_PACKS = {
    # ③ Scenes & Segments — narrative rhythm + attention refresh
    "scenes_segments": [
        _mp(
            0.0,
            "Purple",
            "PRINCIPLES — Scenes/Segments",
            "• First-frame clarity (<2s): who/where/what.\n"
            "• Keep trims tight; avoid >1.5s dead air between ideas.\n"
            "• Use bridges for invisible cuts (movement/sound/action).",
        ),
        _mp(
            1.0,
            "Pink",
            "Micro-jolt cadence",
            "Insert a quick change every ~5–8s (angle/motion/graphic) to refresh attention.",
        ),
        _mp(
            2.0,
            "Yellow",
            "Loop seam awareness",
            "Plan an end frame that re-enters cleanly if the video loops on social.",
        ),
        _mp(
            299.0, "Blue", "⏱ 5min anchor", "Timeline duration marker (auto-generated)"
        ),
    ],
    # ④ ShotFX — beauty/compositing/cleanup without overworking the shot
    "shotfx": [
        _mp(
            0.0,
            "Purple",
            "PRINCIPLES — ShotFX",
            "• Composite first, grade after (minimize double processing).\n"
            "• Track → refine → blend: favor natural edges over harsh feather.\n"
            "• Use AI assists sparingly; keep facial texture/natural motion.",
        ),
        _mp(
            1.0,
            "Blue",
            "Mask edge awareness",
            "Mind edges during fast motion; avoid halos/boil. Prefer soft, directional feathering.",
        ),
        _mp(
            2.0,
            "Pink",
            "Look exploration",
            "Try one alternate 'beauty vs grit' treatment for options later.",
        ),
        _mp(
            299.0, "Blue", "⏱ 5min anchor", "Timeline duration marker (auto-generated)"
        ),
    ],
    # ⑤ Talking Head — clarity + retention psychology
    "talking_head": [
        _mp(
            0.0,
            "Purple",
            "PRINCIPLES — Talking Head",
            "• Lead with the point (don't bury context).\n"
            "• Tighten fillers; preserve natural cadence.\n"
            "• Support hard ideas with B-roll overlays; hide jump cuts.",
        ),
        _mp(
            1.0,
            "Blue",
            "B-roll window",
            "Consider an overlay here to illustrate or cover a breath cut.",
        ),
        _mp(
            2.0,
            "Yellow",
            "Pacing & captions",
            "Keep line breaks on phrase boundaries; punch keywords with subtle zoom/audio emphasis.",
        ),
        _mp(
            299.0, "Blue", "⏱ 5min anchor", "Timeline duration marker (auto-generated)"
        ),
    ],
    # ⑥ Fashion — silhouette, detail storytelling, motion aura
    "fashion": [
        _mp(
            0.0,
            "Purple",
            "PRINCIPLES — Fashion",
            "• Silhouette first (clean read, full body).\n"
            "• Then detail: fabric/texture/hardware micro-shots.\n"
            "• Motion beauty: walk/turn/glance for flow & attitude.",
        ),
        _mp(
            1.0,
            "Pink",
            "Motion beauty",
            "Feature a fluid move here (turn/step/hair/garment ripple).",
        ),
        _mp(
            2.0,
            "Green",
            "Thumbnail candidates",
            "Flag strong stills for covers/carousels later.",
        ),
        _mp(
            299.0, "Blue", "⏱ 5min anchor", "Timeline duration marker (auto-generated)"
        ),
    ],
    # ⑦ Day in the Life — micro-story structure
    "day_in_the_life": [
        _mp(
            0.0,
            "Purple",
            "PRINCIPLES — Day in the Life",
            "• Intent fast: what's happening today?\n"
            "• Micro-scenes > montage blur: 3–6s beats with clear purpose.\n"
            "• End each cycle with a small resolution or tease.",
        ),
        _mp(
            1.0,
            "Blue",
            "Atmos pass",
            "Insert textures/hands/ambient to vary pacing without losing thread.",
        ),
        _mp(
            2.0,
            "Yellow",
            "Transition moment",
            "Natural hop to the next micro-scene (movement/sound change).",
        ),
        _mp(
            3.0,
            "Green",
            "Cycle closure",
            "Leave a resolved beat that can loop if needed.",
        ),
        _mp(
            299.0, "Blue", "⏱ 5min anchor", "Timeline duration marker (auto-generated)"
        ),
    ],
    # ⑧ Cook-Ups — show progress & payoff without getting lost
    "cook_ups": [
        _mp(
            0.0,
            "Purple",
            "PRINCIPLES — Cook-Ups",
            "• Introduce motif quickly; show the 'why' of the tweak.\n"
            "• Reveal progress visually (UI, hands, waveform/meter).",
        ),
        _mp(
            1.0,
            "Yellow",
            "Arrangement choice",
            "Commit to a direction; avoid endless A/B meanders.",
        ),
        _mp(
            2.0,
            "Blue",
            "UI / sound insert",
            "Highlight a plugin/knob/waveform moment that sells the change.",
        ),
        _mp(
            3.0,
            "Pink",
            "Vibe spike",
            "Create a small peak (camera move, slow-mo, quick cut burst).",
        ),
        _mp(
            299.0, "Blue", "⏱ 5min anchor", "Timeline duration marker (auto-generated)"
        ),
    ],
}


# ───────────────────────── Seconds-only pacing (lane ▸ tier ▸ section) ─────────────────────────
PACING_S = {
    "money": {
        "12s": {
            "HOOK": "Cut every ~0.8–1.2s; micro-jolt ≤0.7s ok.",
            "DRAW": "Quicker trims ~0.6–0.9s; 1 brisk insert per beat of idea.",
            "COMMIT / PAYOFF": "Let proof breathe 1.2–1.8s; single cut-ins ≤0.5s.",
            "LOOP / CTA": "Button ≤0.7s; avoid extra frames after action lands.",
        },
        "22s": {
            "HOOK": "0.9–1.3s cadence.",
            "DRAW": "0.7–1.0s cadence; allow 1 contrast cut ≤0.5s.",
            "INTERRUPT #1": "≤0.6s burst.",
            "COMMIT / PAYOFF #1": "1.4–2.0s; 1–2 inserts ≤0.5s.",
            "SECOND HOOK": "0.8–1.1s, punchier than first hook.",
            "DEVELOP": "1.0–1.4s trims; chain 2 beats max.",
            "LOOP / CTA": "0.6–0.9s clean loop frame.",
        },
        "30s": {
            "HOOK": "1.0–1.4s cadence.",
            "DRAW": "0.9–1.2s; maintain forward pressure.",
            "COMMIT / PAYOFF #1": "1.5–2.2s; inserts ≤0.6s.",
            "SECOND HOOK": "0.9–1.2s; keep phrasing fresh.",
            "DEVELOP A": "1.1–1.6s trims; avoid meander.",
            "DEVELOP B": "1.1–1.6s trims; escalate or contrast.",
            "FINAL PAYOFF / LOOP": "0.9–1.3s; land on loopable motion.",
        },
    },
    "mv": {
        "12s": {
            "HOOK (Signature Visual)": "0.7–1.0s; snap on motion apex.",
            "DRAW (Aesthetic Lift)": "0.6–0.9s; switch angle/location quickly.",
            "COMMIT / PAYOFF": "1.2–1.6s on best performance bar; cut-ins ≤0.5s.",
            "LOOP / CTA": "≤0.7s with repeatable motion.",
        },
        "22s": {
            "HOOK": "0.9–1.2s; hit downbeat moves.",
            "DRAW": "0.7–1.0s; texture/move alternation.",
            "COMMIT / PAYOFF #1": "1.4–1.9s; preserve groove.",
            "SECOND HOOK": "0.8–1.1s; fresh pose/transition.",
            "DEVELOP": "1.0–1.4s; 2-beat mini-sequence.",
            "LOOP / CTA": "0.6–0.9s.",
        },
        "30s": {
            "HOOK": "1.0–1.3s; signature move early.",
            "DRAW": "0.9–1.2s; keep energy rising.",
            "COMMIT / PAYOFF #1": "1.5–2.1s; show payoff clean.",
            "SECOND HOOK": "0.9–1.2s.",
            "DEVELOP A": "1.1–1.5s per move sequence.",
            "DEVELOP B": "1.1–1.5s, environment interplay.",
            "FINAL PAYOFF / LOOP": "0.9–1.2s loop close.",
        },
    },
    "fashion": {
        "12s": {
            "HOOK (Hero Fit Moment)": "0.7–1.0s; silhouette read first.",
            "DRAW (Detail Contrast)": "0.6–0.9s; alternate texture/motion.",
            "COMMIT / PAYOFF": "1.2–1.6s full-body; detail cut-ins ≤0.5s.",
            "LOOP / CTA": "≤0.7s on a repeatable turn/step.",
        },
        "22s": {
            "HOOK (Look Identity)": "0.8–1.1s.",
            "DRAW (Texture/Movement)": "0.7–1.0s; emphasize fabric motion.",
            "COMMIT / PAYOFF #1": "1.3–1.8s head-to-toe.",
            "SECOND HOOK (Alt Styling)": "0.8–1.1s; new layer/prop.",
            "DEVELOP": "1.0–1.4s; 2 detail beats max.",
            "LOOP / CTA": "0.6–0.9s.",
        },
        "30s": {
            "HOOK (Statement Frame)": "1.0–1.3s.",
            "DRAW (Cutaway Detail)": "0.9–1.2s; stitching/hardware.",
            "COMMIT / PAYOFF #1": "1.5–2.1s.",
            "SECOND HOOK": "0.9–1.2s.",
            "DEVELOP A": "1.1–1.5s per move.",
            "DEVELOP B": "1.1–1.5s; environment read.",
            "FINAL PAYOFF / LOOP": "0.9–1.2s.",
        },
    },
    "talking": {
        "12s": {
            "HOOK (Plain-Speak Claim)": "0.8–1.1s; cut on phrase ends.",
            "DRAW (Setup in One Line)": "0.7–1.0s; keep fillers trimmed.",
            "COMMIT / PAYOFF": "1.2–1.7s; overlay receipts ≤0.5s.",
            "LOOP / CTA": "≤0.7s; clean end breath.",
        },
        "22s": {
            "HOOK (Outcome First)": "0.9–1.2s.",
            "DRAW (Short Context)": "0.8–1.1s; one surprise fact.",
            "COMMIT / PAYOFF #1": "1.4–2.0s.",
            "SECOND HOOK": "0.8–1.1s; new phrasing.",
            "DEVELOP": "1.0–1.4s; single example.",
            "LOOP / CTA": "0.6–0.9s.",
        },
        "30s": {
            "HOOK (Punchy Thesis)": "1.0–1.3s.",
            "DRAW (Angle Boost)": "0.9–1.2s.",
            "COMMIT / PAYOFF #1": "1.5–2.1s.",
            "SECOND HOOK": "0.9–1.2s.",
            "DEVELOP A": "1.1–1.5s.",
            "DEVELOP B": "1.1–1.5s.",
            "FINAL PAYOFF / LOOP": "0.9–1.2s.",
        },
    },
    "dil": {
        "12s": {
            "HOOK (Moment in Progress)": "0.7–1.0s; cut on action changes.",
            "DRAW (What's Next?)": "0.7–1.0s; tease movement.",
            "COMMIT / PAYOFF": "1.2–1.6s micro-resolution.",
            "LOOP / CTA": "≤0.7s.",
        },
        "22s": {
            "HOOK (Drop-In)": "0.9–1.2s.",
            "DRAW (Mini Arc)": "0.8–1.1s.",
            "COMMIT / PAYOFF #1": "1.4–1.9s.",
            "SECOND HOOK": "0.8–1.1s.",
            "DEVELOP": "1.0–1.4s.",
            "LOOP / CTA": "0.6–0.9s.",
        },
        "30s": {
            "HOOK (Live Snapshot)": "1.0–1.3s.",
            "DRAW (Tension/Contrast)": "0.9–1.2s.",
            "COMMIT / PAYOFF #1": "1.5–2.0s.",
            "SECOND HOOK": "0.9–1.2s.",
            "DEVELOP A": "1.1–1.5s.",
            "DEVELOP B": "1.1–1.5s.",
            "FINAL PAYOFF / LOOP": "0.9–1.2s.",
        },
    },
    "cook": {
        "12s": {
            "HOOK (Signature Sound/Move)": "0.7–1.0s; cut on transients.",
            "DRAW (Layer or Constraint)": "0.6–0.9s; UI/hands ~0.5s.",
            "COMMIT / PAYOFF": "1.2–1.6s groove lock.",
            "LOOP / CTA": "≤0.7s.",
        },
        "22s": {
            "HOOK (Instant Identity)": "0.9–1.1s.",
            "DRAW (What You'll Build)": "0.7–1.0s; context fast.",
            "COMMIT / PAYOFF #1": "1.4–1.9s.",
            "SECOND HOOK": "0.8–1.1s.",
            "DEVELOP": "1.0–1.4s; short fills ≤0.5s.",
            "LOOP / CTA": "0.6–0.9s.",
        },
        "30s": {
            "HOOK (Immediate Sauce)": "1.0–1.2s.",
            "DRAW (Set the Game)": "0.9–1.2s.",
            "COMMIT / PAYOFF #1": "1.5–2.0s.",
            "SECOND HOOK": "0.9–1.2s.",
            "DEVELOP A": "1.1–1.5s.",
            "DEVELOP B": "1.1–1.5s.",
            "FINAL PAYOFF / LOOP": "0.9–1.2s.",
        },
    },
}


def _lane_tier_from_title(title: str):
    """Extract lane and tier from timeline title."""
    t = (title or "").lower()
    if "money master" in t:
        return "money", ("12s" if "12s" in t else "22s" if "22s" in t else "30s")
    if "mv master" in t:
        return "mv", ("12s" if "12s" in t else "22s" if "22s" in t else "30s")
    if "fashion master" in t:
        return "fashion", ("12s" if "12s" in t else "22s" if "22s" in t else "30s")
    if "th master" in t:
        return "talking", ("12s" if "12s" in t else "22s" if "22s" in t else "30s")
    if "dil master" in t:
        return "dil", ("12s" if "12s" in t else "22s" if "22s" in t else "30s")
    if "cook-up master" in t:
        return "cook", ("12s" if "12s" in t else "22s" if "22s" in t else "30s")
    # For non-master timelines, infer lane from pillar bucket
    nt = t.replace("—", "-")
    if nt.startswith("segment -"):
        return "mv", "30s"
    if nt.startswith("interview -"):
        return "talking", "30s"
    if nt.startswith("look -"):
        return "fashion", "30s"
    if nt.startswith("chapter -"):
        return "dil", "30s"
    if nt.startswith("section -"):
        return "cook", "30s"
    return None, None


def _enrich_marker_notes(markers, lane, tier):
    """Add seconds-based cut guidance into each marker's notes."""
    if not markers or not lane or not tier:
        return markers
    rules = PACING_S.get(lane, {}).get(tier, {})
    out = []
    for m in markers:
        m2 = dict(m)
        tip = rules.get(m2.get("name", ""), "")
        if tip:
            base = m2.get("notes", "").rstrip()
            if base:
                m2["notes"] = f"{base}\n— Cuts: {tip}"
            else:
                m2["notes"] = f"Cuts: {tip}"
        out.append(m2)
    return out


def _infer_lane_from_pillar_or_title(pillar_name: str, title: str) -> str:
    """Infer the lane (money/mv/fashion/talking/dil/cook) from pillar or title."""
    p = (pillar_name or "").lower()
    t = (title or "").lower()
    if "music-video" in p or t.startswith("segment —") or t.startswith("mv master"):
        return "mv"
    if "fashion" in p or t.startswith("look —") or t.startswith("fashion master"):
        return "fashion"
    if "talking head" in p or t.startswith("interview —") or t.startswith("th master"):
        return "talking"
    if (
        "day in the life" in p
        or t.startswith("chapter —")
        or t.startswith("dil master")
    ):
        return "dil"
    if "cook-ups" in p or t.startswith("section —") or t.startswith("cook-up master"):
        return "cook"
    if "money" in p or "money master" in t:
        return "money"
    return "money"  # safe default


# Map timeline title to a principle pack (skip masters).
def get_principle_markers_for_title(title):
    t = (title or "").lower().replace("—", "-").replace("–", "-")

    # Exclude any master timelines
    if (
        (" money master" in t or t.startswith("money master"))
        or (" master -" in t or t.startswith("mv master"))
        or t.startswith("th master")
        or t.startswith("fashion master")
        or t.startswith("dil master")
        or t.startswith("cook-up master")
    ):
        return []

    # Use contains matching with flexible patterns
    # Selects & Stringouts — check FIRST to avoid collision with keywords like "look"
    if "selects" in t or "stringout" in t:
        base = SELECTS_BASE
        var_key = _selects_variant_for_title(t)
        if var_key and var_key in SELECTS_SPECIFIC:
            return base + SELECTS_SPECIFIC[var_key]
        # fallback: just the base tips
        return base

    # ShotFX - with variant-specific tips
    if ("shotfx" in t) or ("shot fx" in t):
        base = PRINCIPLE_PACKS["shotfx"]
        var_key = _shotfx_variant_for_title(t)
        if var_key and var_key in SHOTFX_SPECIFIC:
            # Combine base principles + the variant-specific tips
            return base + SHOTFX_SPECIFIC[var_key]
        return base
    if "segment" in t:
        return PRINCIPLE_PACKS["scenes_segments"]
    if "interview" in t:
        return PRINCIPLE_PACKS["talking_head"]
    if "look" in t:
        return PRINCIPLE_PACKS["fashion"]
    if "chapter" in t:
        return PRINCIPLE_PACKS["day_in_the_life"]
    if "section" in t:
        return PRINCIPLE_PACKS["cook_ups"]

    # Leave sync and other utility timelines untagged by default
    return []


# ───────────────────────── Data / Stats helpers ─────────────────────────
def get_folder_path(folder):
    names = []
    cur = folder
    for _ in range(10):
        try:
            names.append(cur.GetName())
            cur = cur.GetParent()
            if not cur:
                break
        except Exception:
            break
    return " / ".join(reversed(names))


class BuildStats:
    def __init__(self):
        self.folders_created = 0
        self.folders_found = 0
        self.timelines_created = 0
        self.timelines_failed = 0
        self.timelines_skipped = 0
        self.tracks_created = 0
        self.errors = []
        self.start_time = datetime.datetime.now()

    def log_error(self, op, err):
        self.errors.append(f"{op}: {err}")

    def summary(self):
        d = datetime.datetime.now() - self.start_time
        return {
            "duration": d.total_seconds(),
            "folders_created": self.folders_created,
            "folders_found": self.folders_found,
            "timelines_created": self.timelines_created,
            "timelines_failed": self.timelines_failed,
            "timelines_skipped": self.timelines_skipped,
            "tracks_created": self.tracks_created,
            "error_count": len(self.errors),
            "errors": self.errors,
        }


# ───────────────────────── Folder helpers ─────────────────────────
def _iter_subfolders(folder):
    for accessor in ("GetSubFolders", "GetSubFolderList"):
        f = getattr(folder, accessor, None)
        if not f:
            continue
        try:
            res = f()
            if isinstance(res, dict):
                return list(res.values())
            if isinstance(res, list):
                return res
        except Exception:
            pass
    return []


def get_or_create_folder(mp, parent, name, stats):
    for sub in _iter_subfolders(parent):
        try:
            if sub.GetName() == name:
                log.info("  📂 Found: %s (under %s)", name, get_folder_path(parent))
                stats.folders_found += 1
                return sub
        except Exception:
            pass
    folder = None
    try:
        folder = mp.AddSubFolder(parent, name)
        if isinstance(folder, tuple):
            folder = folder[0]
        if folder:
            log.info(
                "  ✅ Created (MediaPool.AddSubFolder): %s (under %s)",
                name,
                get_folder_path(parent),
            )
            stats.folders_created += 1
    except Exception:
        try:
            add = getattr(parent, "AddSubFolder", None)
            if callable(add):
                folder = add(name)
                if folder:
                    log.info(
                        "  ✅ Created (parent.AddSubFolder): %s (under %s)",
                        name,
                        get_folder_path(parent),
                    )
                    stats.folders_created += 1
        except Exception as e2:
            log.error("  ❌ All creation methods failed for %s: %s", name, e2)
            stats.log_error(f"Folder creation: {name}", str(e2))
    if not folder:
        log.error("  ❌ Could not create: %s", name)
        stats.log_error(f"Folder creation: {name}", "All methods failed")
    return folder


# ───────────────────────── Timeline helpers ─────────────────────────
def timeline_exists(project, name):
    try:
        tls = project.GetTimelines()
        if isinstance(tls, list):
            for tl in tls:
                try:
                    if tl and tl.GetName() == name:
                        return True
                except Exception:
                    pass
    except Exception:
        pass
    try:
        count = int(project.GetTimelineCount())
        for i in range(1, count + 1):
            try:
                tl = project.GetTimelineByIndex(i)
                if tl and tl.GetName() == name:
                    return True
            except Exception:
                continue
    except Exception:
        pass
    return False


def ensure_tracks_named(
    tl, kind, names_top_to_bottom=None, names_left_to_right=None, stats=None
):
    if kind == "video":
        target = list(reversed(names_top_to_bottom or []))
    else:
        target = names_left_to_right or []
    try:
        have = int(tl.GetTrackCount(kind))
    except Exception:
        have = 0
    need = len(target) - have
    for _ in range(max(0, need)):
        try:
            tl.AddTrack(kind)
            if stats:
                stats.tracks_created += 1
        except Exception as e:
            log.error("❌ Failed to add %s track: %s", kind, e)
            if stats:
                stats.log_error(f"Track creation: {kind}", str(e))
    # Name tracks
    if kind == "video":
        for i, label in enumerate(target, 1):
            try:
                tl.SetTrackName("video", i, label)
            except Exception:
                pass
    else:
        for i, label in enumerate(target, 1):
            try:
                tl.SetTrackName("audio", i, label)
            except Exception:
                pass
        # subtitle once
        try:
            subcnt = int(tl.GetTrackCount("subtitle"))
        except Exception:
            subcnt = 0
        if subcnt == 0:
            try:
                tl.AddTrack("subtitle")
                tl.SetTrackName("subtitle", 1, "CC | English")
                if stats:
                    stats.tracks_created += 1
            except Exception:
                pass


def safe_set_current_folder(mp, folder):
    try:
        ok = mp.SetCurrentFolder(folder)
        if ok is False:
            log.debug("⚠️ SetCurrentFolder returned False")
        return True
    except Exception:
        return False


# ───────────────────────── Markers add/re-seed ─────────────────────────
def _sec_to_frames(sec, fps_float):
    return int(round(sec * fps_float))


def _butt_join_markers(markers, fps_str):
    """Ensure consecutive duration markers visually abut (extend earlier by 1 frame if needed)."""
    try:
        fps = float(fps_str)
    except Exception:
        fps = 29.97
    if not markers:
        return markers
    # Work on a copy sorted by time
    ms = sorted((dict(m) for m in markers), key=lambda x: x.get("t", 0.0))
    for i in range(len(ms) - 1):
        cur, nxt = ms[i], ms[i + 1]
        cur_t = float(cur.get("t", 0.0))
        cur_d = float(cur.get("dur", 0.0))
        nxt_t = float(nxt.get("t", 0.0))
        if cur_d <= 0.0:
            continue
        # desired end = cur_t + cur_d
        gap = nxt_t - (cur_t + cur_d)
        if gap > 0:
            # stretch current by min(gap, 1 frame) to close hairline gap without overlap
            cur["dur"] = cur_d + min(gap, 1.0 / fps)
    return ms


def ensure_min_duration(dur_frames):
    """Guard for Resolve 20.2+ which requires duration >= 1 frame."""
    return max(1, int(dur_frames or 1))


def _add_marker_safe(tl, frame, color, name, note, dur_frames):
    # CRITICAL: Ensure duration >= 1 for Resolve 20.2+
    dur_frames = ensure_min_duration(dur_frames)

    try:
        ok = tl.AddMarker(frame, color, name, note, dur_frames, "")
        if ok:
            return True
        log.debug(
            f"      ⚠️  AddMarker failed (6-arg): frame={frame}, color={color}, name={name}"
        )
        fb = _COLOR_FALLBACK.get(color)
        if fb:
            ok2 = tl.AddMarker(frame, fb, name, note, dur_frames, "")
            if ok2:
                log.debug(f"      ✓ AddMarker succeeded with fallback color: {fb}")
                return True
    except Exception as e:
        log.debug(f"      ⚠️  AddMarker exception (6-arg): {e}")
        try:
            ok3 = tl.AddMarker(frame, color, name, note, dur_frames)
            if ok3:
                log.debug(f"      ✓ AddMarker succeeded (5-arg)")
                return True
            log.debug(
                f"      ⚠️  AddMarker failed (5-arg): frame={frame}, color={color}"
            )
            fb = _COLOR_FALLBACK.get(color)
            if fb:
                ok4 = tl.AddMarker(frame, fb, name, note, dur_frames)
                if ok4:
                    log.debug(
                        f"      ✓ AddMarker succeeded (5-arg) with fallback: {fb}"
                    )
                    return True
        except Exception as e2:
            log.debug(f"      ⚠️  AddMarker exception (5-arg): {e2}")
    log.warning(f"      ❌ ALL AddMarker attempts failed for: {name} @ frame {frame}")
    return False


def _ensure_silence_asset(seconds=2.0, sr=48000, channels=2, bits=16):
    """Create (once) a silent WAV we can append so AddMarker works on empty timelines."""
    try:
        assets_dir = os.path.join(_script_dir(), "assets")
    except Exception:
        assets_dir = os.path.expanduser("~/tmp/dega_assets")
    os.makedirs(assets_dir, exist_ok=True)
    wav_path = os.path.join(assets_dir, f"_dega_silence_{int(seconds*1000)}ms.wav")
    if not os.path.exists(wav_path):
        nframes = int(sr * seconds)
        with wave.open(wav_path, "wb") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(bits // 8)
            wf.setframerate(sr)
            silence = struct.pack("<h", 0)  # 16-bit little-endian zero
            wf.writeframes(silence * nframes * channels)
    return wav_path


def ensure_timeline_nonempty_with_silence(mp, project, tl, seconds=2.0):
    """Append a tiny silent audio clip if timeline has no items, so markers can be added."""
    # quick existence check: if any track has items, we're done
    try:
        for kind in ("video", "audio", "subtitle"):
            try:
                tracks = int(tl.GetTrackCount(kind))
            except Exception:
                tracks = 0
            for idx in range(1, tracks + 1):
                try:
                    items = tl.GetItemListInTrack(kind, idx)
                except Exception:
                    items = []
                if items:
                    return True
    except Exception:
        pass

    wav_path = _ensure_silence_asset(seconds=seconds)
    items = mp.ImportMedia([wav_path]) or []
    if isinstance(items, dict):
        items = list(items.values())
    if not items:
        raise RuntimeError("ImportMedia returned no items")

    # Set timeline as current and append the silent clip
    project.SetCurrentTimeline(tl)
    ok = mp.AppendToTimeline([items[0]])
    return bool(ok)


def _count_markers(tl):
    # Resolve API has GetMarkers() on some builds; fall back if not present.
    try:
        mk = tl.GetMarkers()
        if isinstance(mk, dict):
            return len(mk)
        if isinstance(mk, list):
            return len(mk)
    except Exception:
        pass
    # If unknown, return 0 to allow seeding (safe: markers are harmless)
    return 0


def add_markers_to_timeline_if_empty(tl, fps_str, markers, force=False):
    try:
        fps_float = float(fps_str)
    except Exception:
        fps_float = 29.97
    existing = _count_markers(tl)
    if existing > 0 and not force:
        log.info("   ↻ Markers present (%d) — skipping re-seed", existing)
        return 0

    # Debug: log what markers were provided
    marker_count = len(markers or [])
    if marker_count == 0:
        log.debug("   ⚠️  No markers provided for: %s", tl.GetName())
        return 0

    log.info("   🏷️  Adding %d principle markers to: %s", marker_count, tl.GetName())

    # CRITICAL: Add markers in REVERSE time order (furthest first)
    # This ensures the anchor marker at 299s establishes timeline duration FIRST
    sorted_markers = sorted(markers or [], key=lambda m: m["t"], reverse=True)

    added = 0
    for m in sorted_markers:
        frame = _sec_to_frames(m["t"], fps_float)
        dur = _sec_to_frames(m.get("dur", 0.0), fps_float)
        # CRITICAL: Resolve 20.2 requires duration >= 1, cannot be 0
        if dur < 1:
            dur = 1
        color = m["color"]
        if color not in _SUPPORTED_MARKER_COLORS:
            color = _COLOR_FALLBACK.get(color, "Red")
        if _add_marker_safe(tl, frame, color, m["name"], m.get("notes", ""), dur):
            added += 1

    if added == 0 and marker_count > 0:
        log.warning(
            "   ⚠️  Timeline appears empty (0 duration) - markers cannot be added until clips are present"
        )
    log.info("   ✅ Markers added: %d", added)
    return added


def set_project_defaults(project, w, h, fps):
    keys = [
        "timelineResolutionWidth",
        "timelineResolutionHeight",
        "timelinePlaybackFrameRate",
        "timelineFrameRate",
        "timelineDropFrameTimecode",
        "timelineInterlaceProcessing",
    ]
    prev = {}
    for k in keys:
        try:
            prev[k] = project.GetSetting(k)
        except Exception:
            prev[k] = None
    try:
        project.SetSetting("timelineResolutionWidth", str(w))
        project.SetSetting("timelineResolutionHeight", str(h))
        project.SetSetting("timelinePlaybackFrameRate", str(fps))
        project.SetSetting("timelineFrameRate", str(fps))
        project.SetSetting("timelineDropFrameTimecode", "0")
        project.SetSetting("timelineInterlaceProcessing", "0")
    except Exception as e:
        log.error("❌ Failed to set project defaults: %s", e)
    return prev


def restore_project_defaults(project, prev):
    for k, v in prev.items():
        if v is None:
            continue
        try:
            project.SetSetting(k, v)
        except Exception:
            pass


def create_vertical_timeline(
    mp, project, folder, title, w, h, fps, stats, markers=None
):
    if not folder:
        stats.timelines_failed += 1
        stats.log_error(f"Timeline creation: {title}", "No target folder")
        return None
    log.info(f"🎬 Creating timeline: {title}")
    prev = set_project_defaults(project, w, h, fps)
    safe_set_current_folder(mp, folder)
    try:
        tl = mp.CreateEmptyTimeline(title)
        if not tl:
            stats.timelines_failed += 1
            stats.log_error(
                f"Timeline creation: {title}", "CreateEmptyTimeline returned None"
            )
            restore_project_defaults(project, prev)
            return None
    except Exception as e:
        stats.timelines_failed += 1
        stats.log_error(f"Timeline creation: {title}", str(e))
        restore_project_defaults(project, prev)
        return None
    restore_project_defaults(project, prev)
    try:
        ensure_tracks_named(
            tl, "video", names_top_to_bottom=VIDEO_TRACKS_TOP_TO_BOTTOM, stats=stats
        )
        ensure_tracks_named(tl, "audio", names_left_to_right=AUDIO_TRACKS, stats=stats)
        stats.timelines_created += 1
        log.info(f"   ✅ Timeline ready: {title}")
    except Exception as e:
        stats.log_error(f"Track setup: {title}", str(e))
    if markers:
        try:
            add_markers_to_timeline_if_empty(tl, FPS, markers)
        except Exception as e:
            log.debug(f"⚠️ Marker add failed for {title}: {e}")
    return tl


def upgrade_existing_track_labels(tl):
    try:
        ensure_tracks_named(tl, "video", names_top_to_bottom=VIDEO_TRACKS_TOP_TO_BOTTOM)
        ensure_tracks_named(tl, "audio", names_left_to_right=AUDIO_TRACKS)
        log.info("    🔧 Upgraded track labels on existing: %s", tl.GetName())
    except Exception:
        pass


def create_vertical_timeline_unique(
    mp, project, folder, title, w, h, fps, stats, markers=None
):
    # If exists: upgrade labels and seed markers (only if empty)
    if timeline_exists(project, title):
        log.info("    ↺ Timeline exists: %s", title)
        # get the existing timeline object to upgrade/seed
        try:
            count = int(project.GetTimelineCount())
            for i in range(1, count + 1):
                tl = project.GetTimelineByIndex(i)
                if tl and tl.GetName() == title:
                    upgrade_existing_track_labels(tl)
                    if markers:
                        add_markers_to_timeline_if_empty(tl, FPS, markers)
                    break
        except Exception:
            pass
        stats.timelines_skipped += 1
        return None
    return create_vertical_timeline(
        mp, project, folder, title, w, h, fps, stats, markers=markers
    )


# ───────────────────────── Build structure ─────────────────────────
PILLARS = {
    "🎵 Music-Video Snippets": {
        "10 | Master Build": ["MV Master — ⏱ 29.97p • 📐 2160×3840"],
        "20 | Scenes & Segments": [
            "Segment — Hook Performance",
            "Segment — Verse Performance",
            "Segment — B-Roll Montage",
            "Segment — Intro/Outro",
        ],
        "30 | Shot FX & Clones": [
            "ShotFX — Clone in Hallway (feather 6–10px)",
            "ShotFX — Clean Plate Patch",
        ],
        "40 | Selects & Stringouts": [
            "PERF Selects — Best Lines",
            "B-Roll Selects — Studio",
        ],
        "50 | Sync & Multicam": ["SYNC MAP — Performance"],
    },
    "👗 OOTD • Fashion": {
        "10 | Master Build": ["Fashion Master — ⏱ 29.97p • 📐 2160×3840"],
        "20 | Scenes & Segments": [
            "LOOK — (Generic)",
            "LOOK — Rooftop Golden Hour",
            "LOOK — Studio Mirror",
        ],
        "30 | Shot FX & Clones": ["ShotFX — Clean Plate Patch (skin/hair)"],
        "40 | Selects & Stringouts": [
            "LOOK Selects — (Generic)",
            "LOOK Selects — Rooftop",
            "LOOK Selects — Studio",
        ],
        "50 | Sync & Multicam": [],
    },
    "🎙️ Talking Head": {
        "10 | Master Build": ["TH Master — ⏱ 29.97p • 📐 2160×3840"],
        "20 | Scenes & Segments": ["Interview — Radio Cut + B-Roll"],
        "30 | Shot FX & Clones": ["ShotFX — Background Cleanup"],
        "40 | Selects & Stringouts": [
            "A-Roll Selects — (Generic)",
            "B-Roll Selects — (Generic)",
            "B-Roll Selects — Studio",
        ],
        "50 | Sync & Multicam": [],
    },
    "☕️ Day in the Life": {
        "10 | Master Build": ["DIL Master — ⏱ 29.97p • 📐 2160×3840"],
        "20 | Scenes & Segments": [
            "Chapter — (Generic)",
            "Chapter — Coffee Run",
            "Chapter — Studio Session",
        ],
        "30 | Shot FX & Clones": ["ShotFX — Hand Remove Mic Cable"],
        "40 | Selects & Stringouts": [
            "Selects — (Generic)",
            "Selects — Commute",
            "Selects — Coffee Shop",
        ],
        "50 | Sync & Multicam": [],
    },
    "🎹 Cook-Ups": {
        "10 | Master Build": ["Cook-Up Master — ⏱ 29.97p • 📐 2160×3840"],
        "20 | Scenes & Segments": [
            "Section — (Generic)",
            "Section — Teaser / Hook Preview",
            "Section — Setup (Key • Tempo • Session)",
            "Section — Drums Build",
            "Section — Bass Drop",
            "Section — Melody Layering",
            "Section — Arrangement Flip",
            "Section — Performance Take",
            "Section — Mix Touches / Print",
        ],
        "30 | Shot FX & Clones": [
            "ShotFX — Hand Split at Sampler",
            "ShotFX — Screen Insert (UI)",
        ],
        "40 | Selects & Stringouts": [
            "Overhead Selects — Keys",
            "Front Cam Selects — Takes",
            "Foley/Prod Selects — (Buttons • Knobs • Pads)",
        ],
        "50 | Sync & Multicam": ["Multicam — Overhead + Front"],
    },
}


def seed_principle_markers_across_project(project, mp):
    """Seed principle markers on all matching non-master timelines with enrichment."""
    # optional env toggle to force reseed: 1/true/yes/on
    force_env = os.getenv("DEGA_PRINCIPLE_FORCE_RESEED", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    cnt = int(project.GetTimelineCount() or 0)

    log.info("🏷️  Seeding principle markers across project...")

    for i in range(1, cnt + 1):
        tl = project.GetTimelineByIndex(i)
        if not tl:
            continue
        title = tl.GetName() or ""
        pack = get_principle_markers_for_title(title)
        if not pack:  # masters return []
            continue

        # Infer lane and enrich markers with cut notes & butt-join borders
        lane, tier = _lane_tier_from_title(title)
        if not lane:
            lane = _infer_lane_from_pillar_or_title("", title)
        if not tier:
            tier = (
                "selects"
                if ("selects" in title.lower() or "stringouts" in title.lower())
                else "30s"
            )
        enriched = _enrich_marker_notes(pack, lane, tier)
        markers = _butt_join_markers(enriched, FPS)

        # Set timeline as current for operations
        project.SetCurrentTimeline(tl)

        added = add_markers_to_timeline_if_empty(tl, FPS, markers, force=force_env)
        if added > 0:
            log.info(
                f"   🏷️ Seeded {added} markers on '{title}' (lane={lane}, tier={tier}, force={force_env})"
            )
        elif added == 0 and _count_markers(tl) == 0:
            # empty timeline + no markers -> Resolve quirk: use silent-clip fallback
            try:
                log.info(f"   🔧 Adding silent clip to enable markers on: {title}")
                if ensure_timeline_nonempty_with_silence(mp, project, tl, seconds=2.0):
                    added = add_markers_to_timeline_if_empty(
                        tl, FPS, markers, force=True
                    )
                    if added > 0:
                        log.info(f"   ✅ Fallback seeded {added} markers on: {title}")
            except Exception as e:
                log.warning(f"   ⚠️  Fallback failed on '{title}': {e}")


def main():
    stats = BuildStats()

    resolve = get_resolve()
    pm = resolve.GetProjectManager()

    # Use the currently open project instead of switching projects
    proj = pm.GetCurrentProject()
    if not proj:
        log.error("❌ No project is currently open. Please open a project first.")
        return False

    project_name = proj.GetName()
    log.info(f"🎯 Project: {project_name}")
    log.info(f"� Format: {WIDTH}×{HEIGHT} @ {FPS}fps")
    log.info(f"📊 Structure: {len(TOP_BINS)} top bins, {len(PILLARS)} pillars")

    mp = proj.GetMediaPool()
    root = mp.GetRootFolder()
    if not root:
        log.error("❌ MediaPool root missing")
        return False

    # Top bins
    log.info("📂 Creating top-level bins…")
    top = {}
    for name in TOP_BINS:
        top[name] = get_or_create_folder(mp, root, name, stats)

    # Money timelines (legacy + tiered)
    money_folder = top.get("01 | 💰 The Money")

    # Legacy references
    create_vertical_timeline_unique(
        mp,
        proj,
        money_folder,
        "01 | 💰 The Money — ⏱ 29.97p • ⌁ 709/2.4 • 📐 2160×3840 • 🎚 v01",
        WIDTH,
        HEIGHT,
        FPS,
        stats,
    )
    create_vertical_timeline_unique(
        mp,
        proj,
        money_folder,
        "01 | 💰 The Money (Render-Only Nest) — QC • burn-ins",
        WIDTH,
        HEIGHT,
        FPS,
        stats,
    )

    # Money Masters with markers (enriched with cut notes & tight borders)
    for _name, _tier in [
        ("Money Master — 12s (IG short) — 2160×3840 • 29.97p", "12s"),
        ("Money Master — 22s (IG mid) — 2160×3840 • 29.97p", "22s"),
        ("Money Master — 30s (IG upper) — 2160×3840 • 29.97p", "30s"),
    ]:
        _raw = LANE_MARKERS["money"][_tier]
        enriched = _enrich_marker_notes(_raw, "money", _tier)
        _paced = _butt_join_markers(enriched, FPS)
        create_vertical_timeline_unique(
            mp, proj, money_folder, _name, WIDTH, HEIGHT, FPS, stats, markers=_paced
        )

    # Formula lanes
    log.info("🧪 Creating Formula pillar structure…")
    formula_root = top.get("02 | 🧪 The Formula")

    # Utility: master build tiered names per lane
    def _tier_names(prefix):
        return [
            f"{prefix} — 12s — 2160×3840 • 29.97p",
            f"{prefix} — 22s — 2160×3840 • 29.97p",
            f"{prefix} — 30s — 2160×3840 • 29.97p",
        ]

    for pillar_name, subbins in PILLARS.items():
        log.info(f"🎯 Pillar: {pillar_name}")
        pillar_folder = get_or_create_folder(mp, formula_root, pillar_name, stats)

        for subbin_name, timeline_names in subbins.items():
            log.info(f"  📂 {subbin_name}")
            sub_folder = get_or_create_folder(mp, pillar_folder, subbin_name, stats)

            # seed standard timelines (principle/selects/segments/shotfx etc.)
            for base in timeline_names:
                title = base if "— ⏱" in base else f"{base} — ⏱ 29.97p • 📐 2160×3840"
                lane_guess = _infer_lane_from_pillar_or_title(pillar_name, title)

                # Pull the appropriate principle pack (if any), then enrich & tighten
                _pm = get_principle_markers_for_title(title)
                if _pm:
                    # Use v4.7 lane/tier system
                    lane, tier = _lane_tier_from_title(title)
                    if not lane:
                        lane = lane_guess
                    if not tier:
                        tier = (
                            "selects"
                            if (
                                "selects" in title.lower()
                                or "stringouts" in title.lower()
                            )
                            else "30s"
                        )
                    enriched = _enrich_marker_notes(_pm, lane, tier)
                    _pm = _butt_join_markers(enriched, FPS)
                    log.debug(
                        "   🏷️  Timeline: %s → %d markers (lane=%s, tier=%s)",
                        title,
                        len(_pm),
                        lane,
                        tier,
                    )

                create_vertical_timeline_unique(
                    mp,
                    proj,
                    sub_folder,
                    title,
                    WIDTH,
                    HEIGHT,
                    FPS,
                    stats,
                    markers=_pm,
                )

            # add tiered Master Build timelines with lane-specific markers
            if subbin_name.startswith("10 | Master Build"):
                lane_key = (
                    "mv"
                    if "Music-Video" in pillar_name
                    else (
                        "fashion"
                        if "Fashion" in pillar_name
                        else (
                            "talking"
                            if "Talking Head" in pillar_name
                            else (
                                "dil"
                                if "Day in the Life" in pillar_name
                                else "cook" if "Cook-Ups" in pillar_name else None
                            )
                        )
                    )
                )
                if lane_key:
                    base_prefix = (
                        "MV Master"
                        if lane_key == "mv"
                        else (
                            "Fashion Master"
                            if lane_key == "fashion"
                            else (
                                "TH Master"
                                if lane_key == "talking"
                                else (
                                    "DIL Master"
                                    if lane_key == "dil"
                                    else "Cook-Up Master"
                                )
                            )
                        )
                    )
                    names = _tier_names(base_prefix)
                    # Map to marker sets with enrichment & tightening
                    tier_keys = ["12s", "22s", "30s"]
                    for name, tier in zip(names, tier_keys, strict=False):
                        raw = LANE_MARKERS[lane_key][tier]
                        enriched = _enrich_marker_notes(raw, lane_key, tier)
                        paced = _butt_join_markers(enriched, FPS)
                        create_vertical_timeline_unique(
                            mp,
                            proj,
                            sub_folder,
                            name,
                            WIDTH,
                            HEIGHT,
                            FPS,
                            stats,
                            markers=paced,
                        )

    # Seed principle markers across all matching timelines
    seed_principle_markers_across_project(proj, mp)

    # Summary + save
    s = stats.summary()
    log.info("================================================")
    log.info("📊 BUILD COMPLETE")
    log.info("⏱ Duration: %.1f s", s["duration"])
    log.info(
        "📂 Folders: %d created, %d found", s["folders_created"], s["folders_found"]
    )
    log.info(
        "🎬 Timelines: %d created, %d skipped",
        s["timelines_created"],
        s["timelines_skipped"],
    )
    log.info("❌ Errors: %d", s["error_count"])
    if s["errors"]:
        log.info("🚨 Error Details:")
        [log.info("   • %s", e) for e in s["errors"]]
    try:
        proj.Save() if hasattr(proj, "Save") else None
        log.info("💾 Project saved")
    except Exception:
        pass
    return s["error_count"] == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
