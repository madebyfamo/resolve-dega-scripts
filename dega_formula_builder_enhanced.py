#!/usr/bin/env python3
"""
DEGA — "The Formula" Builder (Resolve 20.2) — v4.5
Vertical 2160×3840 @ 29.97p • Emoji/Pipe naming • Non-destructive

What's new in v4.5
- Tiered marker templates (12s / 22s / 30s) added natively to *every* lane's Master Build:
  • Money, MV Snippets, Fashion, Talking Head, Day in the Life, Cook-Ups
- Richer marker Notes (research-informed) + explicit timing ranges
- Safe re-seed: markers added only if a timeline has 0 markers (avoids dupes)
- Still upgrades track labels/checkerboarding on existing timelines
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
    logger.info("🚀 DEGA Formula Builder v4.5 starting…")
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
    log.error("❌ Could not acquire Resolve API. Run from Resolve (Workspace ▸ Scripts).")
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
    return {"t": float(when), "color": color, "name": name, "dur": float(dur), "notes": notes}


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
    _mm(0.000, "Red", "HOOK", 3.0, "Range 0–3s. Punchy premise stated plainly; no hedging."),
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
    _mm(13.500, "Magenta", "INTERRUPT #2", 0.0, "Quick flip after second hook to prevent plateau."),
    _mm(
        15.000, "Purple", "DEVELOP", 7.0, "Range 6–8s. Stack 1–2 supporting beats; no rabbit holes."
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
    _mm(0.000, "Red", "HOOK", 3.0, "Range 0–3s. Plain-speak promise; strong visual identity."),
    _mm(
        3.000,
        "Orange",
        "DRAW",
        5.0,
        "Range 4–6s. Elevate intrigue via contrast/constraint/benefit.",
    ),
    _mm(6.000, "Magenta", "INTERRUPT #1", 0.0, "Micro reset to avoid 6–10s slump."),
    _mm(8.000, "Green", "COMMIT / PAYOFF #1", 4.0, "Range 3–5s. Hard clarity moment #1."),
    _mm(
        12.000,
        "Blue",
        "SECOND HOOK",
        3.0,
        "Range 2–4s. Alternate entry point for scrollers; new phrasing.",
    ),
    _mm(13.500, "Magenta", "INTERRUPT #2", 0.0, "Quick subversion; keep rhythm varied."),
    _mm(
        15.000, "Purple", "DEVELOP A", 7.0, "Range 6–8s. Expand with one concise supporting angle."
    ),
    _mm(20.000, "Magenta", "INTERRUPT #3", 0.0, "Reset cadence before last stretch."),
    _mm(22.000, "Purple", "DEVELOP B", 6.0, "Range 5–7s. Second support; avoid duplication."),
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
            _mm(6.000, "Magenta", "INTERRUPT #1", 0.0, "≤0.7s. Quick angle/tempo flip."),
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
            _mm(6.000, "Magenta", "INTERRUPT #1", 0.0, "≤0.7s. Angle/location micro switch."),
            _mm(8.000, "Green", "COMMIT / PAYOFF #1", 4.0, "Range 3–5s. Full outfit clarity."),
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
            _mm(21.300, "Yellow", "LOOP / CTA", 0.7, "Range 0.5–1.2s. Loopable walk-by or glance."),
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
            _mm(8.000, "Green", "COMMIT / PAYOFF #1", 4.0, "Range 3–5s. Head-to-toe moment."),
            _mm(12.000, "Blue", "SECOND HOOK", 3.0, "Range 2–4s. Alternate palette/prop."),
            _mm(
                15.000,
                "Purple",
                "DEVELOP A",
                7.0,
                "Range 6–8s. Movement sequence: walk, turn, sit.",
            ),
            _mm(22.000, "Purple", "DEVELOP B", 6.0, "Range 5–7s. Environment integration."),
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
            _mm(11.600, "Yellow", "LOOP / CTA", 0.4, "Range 0.3–1.0s. Frictionless close."),
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
            _mm(8.000, "Green", "COMMIT / PAYOFF #1", 4.0, "Range 3–5s. First clear point."),
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
            _mm(8.000, "Green", "COMMIT / PAYOFF #1", 4.0, "Range 3–5s. Clear, specific point."),
            _mm(12.000, "Blue", "SECOND HOOK", 3.0, "Range 2–4s. New phrasing for late arrivals."),
            _mm(15.000, "Purple", "DEVELOP A", 7.0, "Range 6–8s. Example or tiny case."),
            _mm(22.000, "Purple", "DEVELOP B", 6.0, "Range 5–7s. Short application/implication."),
            _mm(28.000, "Yellow", "FINAL PAYOFF / LOOP", 2.0, "Range 1.5–3.0s. Tight loop or ask."),
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
            _mm(3.000, "Orange", "DRAW (Mini Arc)", 5.0, "Range 4–6s. Set tiny objective/change."),
            _mm(6.000, "Magenta", "INTERRUPT #1", 0.0, "≤0.7s. Micro reset."),
            _mm(8.000, "Green", "COMMIT / PAYOFF #1", 4.0, "Range 3–5s. Hit a checkpoint."),
            _mm(12.000, "Blue", "SECOND HOOK", 3.0, "Range 2–4s. New micro-goal."),
            _mm(15.000, "Purple", "DEVELOP", 7.0, "Range 6–8s. Texture beats (ambient, details)."),
            _mm(21.300, "Yellow", "LOOP / CTA", 0.7, "Range 0.5–1.2s. End in motion for loop."),
        ],
        "30s": [
            _mm(0.000, "Red", "HOOK (Live Snapshot)", 3.0, "Range 0–3s. Immediate immersion."),
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
            _mm(15.000, "Purple", "DEVELOP A", 7.0, "Range 6–8s. Environment & texture."),
            _mm(22.000, "Purple", "DEVELOP B", 6.0, "Range 5–7s. Human beat or detail set."),
            _mm(
                28.000, "Yellow", "FINAL PAYOFF / LOOP", 2.0, "Range 1.5–3.0s. Loopable exit/enter."
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
            _mm(6.000, "Magenta", "INTERRUPT #1", 0.0, "≤0.7s. Micro switch to screen/overhead."),
            _mm(
                8.000,
                "Green",
                "COMMIT / PAYOFF",
                4.0,
                "Range 3–5s. Small but satisfying musical 'click' (layer locks, groove snaps).",
            ),
            _mm(11.600, "Yellow", "LOOP / CTA", 0.4, "Range 0.3–1.0s. Seamless loop or tiny ask."),
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
            _mm(8.000, "Green", "COMMIT / PAYOFF #1", 4.0, "Range 3–5s. First groove lock."),
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
            _mm(8.000, "Green", "COMMIT / PAYOFF #1", 4.0, "Range 3–5s. First lock moment."),
            _mm(12.000, "Blue", "SECOND HOOK", 3.0, "Range 2–4s. Stronger motif."),
            _mm(15.000, "Purple", "DEVELOP A", 7.0, "Range 6–8s. Arrange mini-arc."),
            _mm(22.000, "Purple", "DEVELOP B", 6.0, "Range 5–7s. Short performance burst."),
            _mm(28.000, "Yellow", "FINAL PAYOFF / LOOP", 2.0, "Range 1.5–3.0s. Loop land."),
        ],
    },
}

# ──────────────────────────────────────────────────────────────
# Principle markers (non-interactive reminders for non-master timelines)
# ──────────────────────────────────────────────────────────────


def _mp(t, color, name, notes, dur=0.0):
    # tiny alias - note: _mm takes (t, color, name, dur, notes) so we swap the last two params
    return _mm(t, color, name, dur, notes)


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
        _mp(299.0, "Blue", "⏱ 5min anchor", "Timeline duration marker (auto-generated)"),
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
        _mp(299.0, "Blue", "⏱ 5min anchor", "Timeline duration marker (auto-generated)"),
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
        _mp(299.0, "Blue", "⏱ 5min anchor", "Timeline duration marker (auto-generated)"),
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
        _mp(2.0, "Green", "Thumbnail candidates", "Flag strong stills for covers/carousels later."),
        _mp(299.0, "Blue", "⏱ 5min anchor", "Timeline duration marker (auto-generated)"),
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
        _mp(3.0, "Green", "Cycle closure", "Leave a resolved beat that can loop if needed."),
        _mp(299.0, "Blue", "⏱ 5min anchor", "Timeline duration marker (auto-generated)"),
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
        _mp(299.0, "Blue", "⏱ 5min anchor", "Timeline duration marker (auto-generated)"),
    ],
}


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
    if ("shotfx" in t) or ("shot fx" in t):
        return PRINCIPLE_PACKS["shotfx"]
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

    # Leave selects, sync, and utility timelines untagged by default
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


def ensure_tracks_named(tl, kind, names_top_to_bottom=None, names_left_to_right=None, stats=None):
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
        log.debug(f"      ⚠️  AddMarker failed (6-arg): frame={frame}, color={color}, name={name}")
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
            log.debug(f"      ⚠️  AddMarker failed (5-arg): frame={frame}, color={color}")
            fb = _COLOR_FALLBACK.get(color)
            if fb:
                ok4 = tl.AddMarker(frame, fb, name, note, dur_frames)
                if ok4:
                    log.debug(f"      ✓ AddMarker succeeded (5-arg) with fallback: {fb}")
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
        log.warning("   ⚠️  Timeline appears empty (0 duration) - markers cannot be added until clips are present")
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


def create_vertical_timeline(mp, project, folder, title, w, h, fps, stats, markers=None):
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
            stats.log_error(f"Timeline creation: {title}", "CreateEmptyTimeline returned None")
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


def create_vertical_timeline_unique(mp, project, folder, title, w, h, fps, stats, markers=None):
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
    return create_vertical_timeline(mp, project, folder, title, w, h, fps, stats, markers=markers)


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
        "30 | Shot FX & Clones": ["ShotFX — Hand Split at Sampler", "ShotFX — Screen Insert (UI)"],
        "40 | Selects & Stringouts": [
            "Overhead Selects — Keys",
            "Front Cam Selects — Takes",
            "Foley/Prod Selects — (Buttons • Knobs • Pads)",
        ],
        "50 | Sync & Multicam": ["Multicam — Overhead + Front"],
    },
}


def seed_principle_markers_across_project(project, mp):
    """Seed principle markers on all matching non-master timelines."""
    # optional env toggle to force reseed: 1/true/yes/on
    force_env = os.getenv("DEGA_PRINCIPLE_FORCE_RESEED", "").strip().lower() in {"1", "true", "yes", "on"}
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

        # Set timeline as current for operations
        project.SetCurrentTimeline(tl)

        added = add_markers_to_timeline_if_empty(tl, FPS, pack, force=force_env)
        if added == 0 and _count_markers(tl) == 0:
            # empty timeline + no markers -> Resolve quirk: use silent-clip fallback
            try:
                log.info(f"   🔧 Adding silent clip to enable markers on: {title}")
                if ensure_timeline_nonempty_with_silence(mp, project, tl, seconds=2.0):
                    added = add_markers_to_timeline_if_empty(tl, FPS, pack, force=True)
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

    # Money Masters with markers
    create_vertical_timeline_unique(
        mp,
        proj,
        money_folder,
        "Money Master — 12s (IG short) — 2160×3840 • 29.97p",
        WIDTH,
        HEIGHT,
        FPS,
        stats,
        markers=LANE_MARKERS["money"]["12s"],
    )
    create_vertical_timeline_unique(
        mp,
        proj,
        money_folder,
        "Money Master — 22s (IG mid) — 2160×3840 • 29.97p",
        WIDTH,
        HEIGHT,
        FPS,
        stats,
        markers=LANE_MARKERS["money"]["22s"],
    )
    create_vertical_timeline_unique(
        mp,
        proj,
        money_folder,
        "Money Master — 30s (IG upper) — 2160×3840 • 29.97p",
        WIDTH,
        HEIGHT,
        FPS,
        stats,
        markers=LANE_MARKERS["money"]["30s"],
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

            # seed standard timelines
            for base in timeline_names:
                title = base if "— ⏱" in base else f"{base} — ⏱ 29.97p • 📐 2160×3840"
                principle_markers = get_principle_markers_for_title(title)
                log.debug(
                    "   📋 Timeline: %s → %d principle markers", title, len(principle_markers or [])
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
                    markers=principle_markers,
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
                                else "DIL Master" if lane_key == "dil" else "Cook-Up Master"
                            )
                        )
                    )
                    names = _tier_names(base_prefix)
                    # Map to marker sets
                    tier_keys = ["12s", "22s", "30s"]
                    for name, tier in zip(names, tier_keys, strict=False):
                        create_vertical_timeline_unique(
                            mp,
                            proj,
                            sub_folder,
                            name,
                            WIDTH,
                            HEIGHT,
                            FPS,
                            stats,
                            markers=LANE_MARKERS[lane_key][tier],
                        )

    # Seed principle markers across all matching timelines
    seed_principle_markers_across_project(proj, mp)

    # Summary + save
    s = stats.summary()
    log.info("================================================")
    log.info("📊 BUILD COMPLETE")
    log.info("⏱ Duration: %.1f s", s["duration"])
    log.info("📂 Folders: %d created, %d found", s["folders_created"], s["folders_found"])
    log.info("🎬 Timelines: %d created, %d skipped", s["timelines_created"], s["timelines_skipped"])
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
