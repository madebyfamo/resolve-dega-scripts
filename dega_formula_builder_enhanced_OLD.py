#!/usr/bin/env python3
"""
DEGA — "The Formula" Builder (Resolve 20.2) — v4.4
Vertical 2160×3840 @ 29.97p • Emoji/Pipe naming • Non-destructive

Adds in v4.4:
- (6) Per-pillar "Scene Kits" (tailored sub-bins; no stems for MV)
- (7) Marker packs (default / educational / promo) via env DEGA_MARKER_PACK
- (11) Upgrade/migration: rename existing tracks to standards, add missing (no deletes)

Still includes:
- Track labels with no numeric prefixes
- A/B checkerboarding for A-roll & B-roll (10 video tracks)
- Money Master timelines (12s / 22s / 30s) with exact markers
- Marker Notes carry second ranges (no beat-aware language)
- Safe color fallback for marker API
"""

import datetime
import logging
import os
import sys


# Helper to get full folder path for logging
def get_folder_path(folder):
    names = []
    cur = folder
    for _ in range(10):
        try:
            names.append(cur.GetName())
            cur = cur.GetParent()  # some builds have it, some don’t
            if not cur:
                break
        except Exception:
            break
    return " / ".join(reversed(names))


# DaVinci Resolve scripting API imports (avoid shadowing global `bmd`)
try:
    import DaVinciResolveScript as dvr
except ImportError:
    dvr = None

# Resolve injects a lightweight 'bmd' module at runtime (inside Resolve/Fusion).
# Import it if available so bmd.scriptapp('Resolve') is preferred.
try:
    import bmd  # type: ignore
except Exception:
    bmd = None


# ──────────────────────────────────────────────────────────────
# Idempotent timeline creation
# ──────────────────────────────────────────────────────────────
def timeline_exists(project, name):
    # Preferred: direct list (when available)
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

    # Fallback: index enumeration (most compatible)
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


def create_vertical_timeline_unique(
    mp, project, folder, title, w, h, fps, stats, markers=None, video_tracks=None, audio_tracks=None
):
    if timeline_exists(project, title):
        log.info("   ↺ Timeline already exists: %s (skipping)", title)
        if stats:
            stats.timelines_skipped += 1
        return None
    return create_vertical_timeline(
        mp,
        project,
        folder,
        title,
        w,
        h,
        fps,
        stats,
        markers=markers,
        video_tracks=video_tracks,
        audio_tracks=audio_tracks,
    )


# --- Resolve-safe logging drop-in ---
def _script_dir():
    # Robust even when run from Resolve’s menu
    try:
        return os.path.dirname(os.path.realpath(__file__))
    except NameError:
        return os.getcwd()


def setup_logger(name="dega_builder", level=logging.INFO):
    logger = logging.getLogger(name)
    if logger.handlers:  # avoid duplicate handlers across runs
        return logger
    logger.setLevel(level)

    # logs/ sibling to script
    log_dir = os.path.join(_script_dir(), "logs")
    try:
        os.makedirs(log_dir, exist_ok=True)
    except Exception:
        # fallback to tmp if path is funky
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

    # Prevent double-logging by disabling propagation
    logger.propagate = False

    logger.info("🚀 DEGA Formula Builder starting…")
    logger.info("📝 Log file: %s", log_path)
    return logger


log = setup_logger()

# Mirror handlers to root so module loggers propagate cleanly
root = logging.getLogger()
if not root.handlers:
    for h in log.handlers:
        root.addHandler(h)
    root.setLevel(log.level)


# Enable verbose logging if DEGA_DEBUG=1, and allow routing debug for this module
if os.getenv("DEGA_DEBUG") == "1":
    logging.getLogger(__name__).setLevel(logging.DEBUG)


# ──────────────────────────────────────────────────────────────
# Resolve bootstrap
# ──────────────────────────────────────────────────────────────
def get_resolve():
    """Get Resolve API with enhanced error reporting."""

    # Try bmd.scriptapp first
    _bmd = globals().get("bmd")
    if _bmd:
        try:
            log.debug("🔌 Attempting bmd.scriptapp connection...")
            r = _bmd.scriptapp("Resolve")
            if r:
                log.info("✅ Connected via bmd.scriptapp")
                return r
        except Exception as e:
            log.warning(f"⚠️ bmd.scriptapp failed: {e}")

    # Fallback to DaVinciResolveScript (as dvr)
    try:
        log.debug("🔌 Attempting DaVinciResolveScript fallback...")
        r = dvr.scriptapp("Resolve") if dvr else None  # type: ignore
        if r:
            log.info("✅ Connected via DaVinciResolveScript")
            return r
    except Exception as e:
        log.error(f"❌ DaVinciResolveScript failed: {e}")

    log.error("❌ Could not acquire Resolve API. Run from Resolve (Workspace ▸ Scripts).")
    sys.exit(1)


# ──────────────────────────────────────────────────────────────
# Config
# ──────────────────────────────────────────────────────────────
TODAY = datetime.date.today().strftime("%Y-%m-%d")
# Use only safe characters for project names to avoid corruption
PROJECT_NAME = f"DEGA_VERT_{TODAY.replace('-', '_')}"
PROJECT_NAME_FALLBACK = f"DEGA_Project_{datetime.datetime.now().strftime('%H%M%S')}"

WIDTH, HEIGHT = "2160", "3840"  # vertical 4K
FPS = "29.97"  # string for SetSetting

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

PILLARS = {
    "🎵 Music-Video Snippets": {
        "10 | Master Build": [
            "MV Master — ⏱ 29.97p • 📐 2160×3840",
        ],
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
        "50 | Sync & Multicam": [
            "SYNC MAP — Performance",
        ],
    },
    "👗 OOTD • Fashion": {
        "10 | Master Build": [
            "Fashion Master — ⏱ 29.97p • 📐 2160×3840",
        ],
        "20 | Scenes & Segments": [
            "LOOK — (Generic)",
            "LOOK — Rooftop Golden Hour",
            "LOOK — Studio Mirror",
        ],
        "30 | Shot FX & Clones": [
            "ShotFX — Clean Plate Patch (skin/hair)",
        ],
        "40 | Selects & Stringouts": [
            "LOOK Selects — (Generic)",
            "LOOK Selects — Rooftop",
            "LOOK Selects — Studio",
        ],
        "50 | Sync & Multicam": [],
    },
    "🎙️ Talking Head": {
        "10 | Master Build": [
            "TH Master — ⏱ 29.97p • 📐 2160×3840",
        ],
        "20 | Scenes & Segments": [
            "Interview — Radio Cut + B-Roll",
        ],
        "30 | Shot FX & Clones": [
            "ShotFX — Background Cleanup",
        ],
        "40 | Selects & Stringouts": [
            "A-Roll Selects — (Generic)",
            "B-Roll Selects — (Generic)",
            "B-Roll Selects — Studio",
        ],
        "50 | Sync & Multicam": [],
    },
    "☕️ Day in the Life": {
        "10 | Master Build": [
            "DIL Master — ⏱ 29.97p • 📐 2160×3840",
        ],
        "20 | Scenes & Segments": [
            "Chapter — (Generic)",
            "Chapter — Coffee Run",
            "Chapter — Studio Session",
        ],
        "30 | Shot FX & Clones": [
            "ShotFX — Hand Remove Mic Cable",
        ],
        "40 | Selects & Stringouts": [
            "Selects — (Generic)",
            "Selects — Commute",
            "Selects — Coffee Shop",
        ],
        "50 | Sync & Multicam": [],
    },
    "🎹 Cook-Ups": {
        "10 | Master Build": [
            "Cook-Up Master — ⏱ 29.97p • 📐 2160×3840",
        ],
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
        "50 | Sync & Multicam": [
            "Multicam — Overhead + Front",
        ],
    },
}


# Specialized per-pillar layouts (video differences; audio uses common template)
LAYOUTS = {
    "DEFAULT": {
        "video": VIDEO_TRACKS_TOP_TO_BOTTOM,
        "audio": AUDIO_TRACKS,
    },
    "MV": {  # Music-Video Snippets
        "video": [
            "FX TEMP 🧪",
            "SAFETY 🛑 — Guides (Disable for export)",
            "TITLES 🏷️",
            "GFX — Shapes & Callouts 🟦",
            "LIGHTS & TEXTURES ✨ — Leaks/Flares/Dust",
            "ADJUSTMENT 🟩 — Global Polish",
            "PERF SELECTS (alt)",
            "PERF MCAM (main)",
            "B-ROLL B 🎞️",
            "B-ROLL A 🎞️",
        ],
        "audio": AUDIO_TRACKS,
    },
    "FASHION": {
        "video": [
            "FX TEMP 🧪",
            "SAFETY 🛑 — Guides (Disable for export)",
            "TITLES 🏷️",
            "GFX — Shapes & Callouts 🟦",
            "LIGHTS & TEXTURES ✨ — Leaks/Flares/Dust",
            "ADJUSTMENT 🟩 — Global Polish",
            "LOOK DETAILS (close-ups)",
            "LOOK A (primary)",
            "LOOK B (alt)",
            "TRANSITIONS",
        ],
        "audio": AUDIO_TRACKS,
    },
    "TALKING": {
        "video": [
            "FX TEMP 🧪",
            "SAFETY 🛑 — Guides (Disable for export)",
            "TITLES 🏷️",
            "GFX — Shapes & Callouts 🟦",
            "ADJUSTMENT 🟩 — Global Polish",
            "CUTAWAYS (B-roll)",
            "SCREEN INSERTS (UI)",
            "B-CAM (alt)",
            "A-CAM (main)",
            "EMPTY",
        ],
        "audio": AUDIO_TRACKS,
    },
    "DIL": {  # Day in the Life
        "video": [
            "FX TEMP 🧪",
            "SAFETY 🛑 — Guides (Disable for export)",
            "TITLES 🏷️",
            "GFX — Shapes & Callouts 🟦",
            "ADJUSTMENT 🟩 — Global Polish",
            "MONTAGE B",
            "MONTAGE A",
            "CHAPTER CARDS",
            "TRANSITIONS",
            "EMPTY",
        ],
        "audio": AUDIO_TRACKS,
    },
    "COOK": {  # Cook-Ups
        "video": [
            "FX TEMP 🧪",
            "SAFETY 🛑 — Guides (Disable for export)",
            "TITLES 🏷️",
            "GFX — Shapes & Callouts 🟦",
            "ADJUSTMENT 🟩 — Global Polish",
            "SCREEN INSERTS (DAW/UI)",
            "OVERHEAD CAM (keys/pads)",
            "FRONT CAM (performance)",
            "CLOSE CAM (hands/gear)",
            "ALT",
        ],
        "audio": AUDIO_TRACKS,
    },
}

# Map per-pillar marker labels (times/durations reused from Money Masters)
PILLAR_CONFIG = {
    "🎵 Music-Video Snippets": {
        "layout": "MV",
        "master_name": "MV Master",
        "marker_labels": {
            "HOOK": "OPEN ON ARTIST",
            "DRAW": "INTRO MOVE / ANGLE CHANGE",
            "COMMIT / PAYOFF": "CHORUS MOMENT",
            "COMMIT / PAYOFF #1": "CHORUS MOMENT",
            "SECOND HOOK": "SECOND ANGLE POP",
            "DEVELOP": "CUTAWAYS / TEXTURE",
            "DEVELOP A": "CUTAWAYS / TEXTURE",
            "DEVELOP B": "CUTAWAYS / TEXTURE",
            "FINAL PAYOFF / LOOP": "OUTRO BUTTON / LOOP",
            "LOOP/CTA": "OUTRO BUTTON / LOOP",
            "INTERRUPT #1": "MICRO JOLT",
            "INTERRUPT #2": "MICRO JOLT",
            "INTERRUPT #3": "MICRO JOLT",
            "INTERRUPT #4": "MICRO JOLT",
        },
    },
    "👗 OOTD • Fashion": {
        "layout": "FASHION",
        "master_name": "Fashion Master",
        "marker_labels": {
            "HOOK": "LOOK REVEAL",
            "DRAW": "FIT WALK-IN / FRAME",
            "COMMIT / PAYOFF": "SIGNATURE TRANSITION",
            "COMMIT / PAYOFF #1": "SIGNATURE TRANSITION",
            "SECOND HOOK": "SECOND LOOK POP",
            "DEVELOP": "DETAIL PASSES",
            "DEVELOP A": "DETAIL PASSES",
            "DEVELOP B": "DETAIL PASSES",
            "FINAL PAYOFF / LOOP": "FINAL POSE / LOOP",
            "LOOP/CTA": "FINAL POSE / LOOP",
            "INTERRUPT #1": "MICRO JOLT",
            "INTERRUPT #2": "MICRO JOLT",
            "INTERRUPT #3": "MICRO JOLT",
            "INTERRUPT #4": "MICRO JOLT",
        },
    },
    "🎙️ Talking Head": {
        "layout": "TALKING",
        "master_name": "TH Master",
        "marker_labels": {
            "HOOK": "TEASER CLAIM",
            "DRAW": "SETUP / CONTEXT",
            "COMMIT / PAYOFF": "KEY TAKEAWAY",
            "COMMIT / PAYOFF #1": "KEY TAKEAWAY",
            "SECOND HOOK": "SECOND PROOF / EXAMPLE",
            "DEVELOP": "ELABORATE / APPLY",
            "DEVELOP A": "ELABORATE / APPLY",
            "DEVELOP B": "ELABORATE / APPLY",
            "FINAL PAYOFF / LOOP": "CTA / LOOP",
            "LOOP/CTA": "CTA / LOOP",
            "INTERRUPT #1": "PATTERN BREAK",
            "INTERRUPT #2": "PATTERN BREAK",
            "INTERRUPT #3": "PATTERN BREAK",
            "INTERRUPT #4": "PATTERN BREAK",
        },
    },
    "☕️ Day in the Life": {
        "layout": "DIL",
        "master_name": "DIL Master",
        "marker_labels": {
            "HOOK": "OPENING MOMENT",
            "DRAW": "SET THE PLACE",
            "COMMIT / PAYOFF": "CORE MOMENT",
            "COMMIT / PAYOFF #1": "CORE MOMENT",
            "SECOND HOOK": "SECOND POP MOMENT",
            "DEVELOP": "CONNECTIVE BITS",
            "DEVELOP A": "CONNECTIVE BITS",
            "DEVELOP B": "CONNECTIVE BITS",
            "FINAL PAYOFF / LOOP": "BUTTON / LOOP",
            "LOOP/CTA": "BUTTON / LOOP",
            "INTERRUPT #1": "MICRO JOLT",
            "INTERRUPT #2": "MICRO JOLT",
            "INTERRUPT #3": "MICRO JOLT",
            "INTERRUPT #4": "MICRO JOLT",
        },
    },
    "🎹 Cook-Ups": {
        "layout": "COOK",
        "master_name": "Cook-Up Master",
        "marker_labels": {
            "HOOK": "INSTANT PAYOFF",
            "DRAW": "SETUP THE IDEA",
            "COMMIT / PAYOFF": "MAIN MOMENT",
            "COMMIT / PAYOFF #1": "MAIN MOMENT",
            "SECOND HOOK": "SECOND LIFT",
            "DEVELOP": "LAYER / ARRANGE",
            "DEVELOP A": "LAYER / ARRANGE",
            "DEVELOP B": "LAYER / ARRANGE",
            "FINAL PAYOFF / LOOP": "OUTRO / LOOP",
            "LOOP/CTA": "OUTRO / LOOP",
            "INTERRUPT #1": "MICRO JOLT",
            "INTERRUPT #2": "MICRO JOLT",
            "INTERRUPT #3": "MICRO JOLT",
            "INTERRUPT #4": "MICRO JOLT",
        },
    },
}


# ──────────────────────────────────────────────────────────────
# Money Master marker definitions
# ──────────────────────────────────────────────────────────────
def _mm(when, color, name, dur, notes):
    return {"t": float(when), "color": color, "name": name, "dur": float(dur), "notes": notes}


MONEY_MASTER_MARKERS = {
    "12s": [
        _mm(0.000, "Red", "HOOK", 3.0, "Range 0–3s"),
        _mm(3.000, "Orange", "DRAW", 5.0, "Range 4–6s"),
        _mm(4.500, "Magenta", "INTERRUPT #1", 0.0, "Micro pattern break target"),
        _mm(8.000, "Green", "COMMIT / PAYOFF", 4.0, "Range 3–5s"),
        _mm(9.000, "Magenta", "INTERRUPT #2", 0.0, "Second micro jolt before close"),
        _mm(11.600, "Yellow", "LOOP/CTA", 0.4, "Range 0.3–1.0s"),
    ],
    "22s": [
        _mm(0.000, "Red", "HOOK", 3.0, "Range 0–3s"),
        _mm(3.000, "Orange", "DRAW", 5.0, "Range 4–6s"),
        _mm(6.000, "Magenta", "INTERRUPT #1", 0.0, "Early micro jolt"),
        _mm(8.000, "Green", "COMMIT / PAYOFF #1", 4.0, "Range 3–5s"),
        _mm(12.000, "Blue", "SECOND HOOK", 3.0, "Range 2–4s"),
        _mm(13.500, "Magenta", "INTERRUPT #2", 0.0, "Quick flip after second hook"),
        _mm(15.000, "Purple", "DEVELOP", 7.0, "Range 6–8s"),
        _mm(18.500, "Magenta", "INTERRUPT #3", 0.0, "Penultimate jolt"),
        _mm(21.300, "Yellow", "LOOP/CTA", 0.7, "Range 0.5–1.2s"),
    ],
    "30s": [
        _mm(0.000, "Red", "HOOK", 3.0, "Range 0–3s"),
        _mm(3.000, "Orange", "DRAW", 5.0, "Range 4–6s"),
        _mm(6.000, "Magenta", "INTERRUPT #1", 0.0, "Early micro jolt"),
        _mm(8.000, "Green", "COMMIT / PAYOFF #1", 4.0, "Range 3–5s"),
        _mm(12.000, "Blue", "SECOND HOOK", 3.0, "Range 2–4s"),
        _mm(13.500, "Magenta", "INTERRUPT #2", 0.0, "Quick flip after second hook"),
        _mm(15.000, "Purple", "DEVELOP A", 7.0, "Range 6–8s"),
        _mm(20.000, "Magenta", "INTERRUPT #3", 0.0, "Reset cadence"),
        _mm(22.000, "Purple", "DEVELOP B", 6.0, "Range 5–7s"),
        _mm(26.000, "Magenta", "INTERRUPT #4", 0.0, "Final jolt"),
        _mm(28.000, "Yellow", "FINAL PAYOFF / LOOP", 2.0, "Range 1.5–3.0s"),
    ],
}

# Colors Resolve most consistently accepts; we'll map others to nearest
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
_COLOR_FALLBACK = {"Magenta": "Pink", "Orange": "Yellow"}  # retry if needed


# ──────────────────────────────────────────────────────────────
# Statistics tracking
# ──────────────────────────────────────────────────────────────
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

    def log_error(self, operation, error):
        self.errors.append(f"{operation}: {error}")

    def get_summary(self):
        duration = datetime.datetime.now() - self.start_time
        return {
            "duration": duration.total_seconds(),
            "folders_created": self.folders_created,
            "folders_found": self.folders_found,
            "timelines_created": self.timelines_created,
            "timelines_failed": self.timelines_failed,
            "timelines_skipped": self.timelines_skipped,
            "tracks_created": self.tracks_created,
            "error_count": len(self.errors),
            "errors": self.errors,
        }


# ──────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────
def _iter_subfolders(folder):
    """Iterate subfolders with fallback methods."""
    logger = logging.getLogger(__name__)

    for accessor in ("GetSubFolders", "GetSubFolderList"):
        f = getattr(folder, accessor, None)
        if not f:
            continue
        try:
            res = f()
            if isinstance(res, dict):
                logger.debug(f"📁 Found {len(res)} subfolders via {accessor} (dict)")
                return list(res.values())
            if isinstance(res, list):
                logger.debug(f"📁 Found {len(res)} subfolders via {accessor} (list)")
                return res
        except Exception as e:
            logger.debug(f"⚠️ {accessor} failed: {e}")

    logger.debug("📁 No subfolders found")
    return []


def get_or_create_folder(mp, parent, name, stats):
    """Get existing folder or create new one with enhanced logging."""
    logger = logging.getLogger(__name__)

    # Check if folder exists
    for sub in _iter_subfolders(parent):
        try:
            if sub.GetName() == name:
                logger.info("  📂 Found: %s (under %s)", name, get_folder_path(parent))
                stats.folders_found += 1
                return sub
        except Exception as e:
            logger.debug(f"⚠️ Error checking folder name: {e}")

    # Try to create folder
    folder = None
    try:
        logger.debug(f"🔨 Creating folder: {name} under {get_folder_path(parent)}")
        folder = mp.AddSubFolder(parent, name)
        if isinstance(folder, tuple):
            folder = folder[0]
        if folder:
            logger.info(
                "  ✅ Created (MediaPool.AddSubFolder): %s (under %s)",
                name,
                get_folder_path(parent),
            )
            stats.folders_created += 1
        else:
            logger.warning(
                f"  ❌ AddSubFolder returned None: {name} (under {get_folder_path(parent)})"
            )
    except Exception as e:
        logger.debug(f"⚠️ mp.AddSubFolder failed: {e}")
        # Try alternative method
        try:
            add = getattr(parent, "AddSubFolder", None)
            if callable(add):
                folder = add(name)
                if folder:
                    logger.info(
                        "  ✅ Created (parent.AddSubFolder): %s (under %s)",
                        name,
                        get_folder_path(parent),
                    )
                    stats.folders_created += 1
        except Exception as e2:
            logger.error(
                "  ❌ All creation methods failed for %s (under %s): %s",
                name,
                get_folder_path(parent),
                e2,
            )
            stats.log_error(f"Folder creation: {name}", str(e2))

    if not folder:
        logger.error("  ❌ Could not create: %s", name)
        stats.log_error(f"Folder creation: {name}", "All methods failed")

    return folder


def get_or_create_path(mp, root_folder, names, stats):
    """Walk a list of folder names, creating as needed, and return the final folder."""
    cur = root_folder
    for n in names:
        cur = get_or_create_folder(mp, cur, n, stats)
        if not cur:
            break
    return cur


def set_project_defaults(project, w, h, fps):
    """Set project timeline defaults with logging."""
    logger = logging.getLogger(__name__)

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
            logger.debug(f"📋 Saved setting {k}: {prev[k]}")
        except Exception as e:
            logger.debug(f"⚠️ Could not get setting {k}: {e}")
            prev[k] = None

    # Set new values
    try:
        project.SetSetting("timelineResolutionWidth", str(w))
        project.SetSetting("timelineResolutionHeight", str(h))
        project.SetSetting("timelinePlaybackFrameRate", str(fps))
        project.SetSetting("timelineFrameRate", str(fps))
        project.SetSetting("timelineDropFrameTimecode", "0")
        project.SetSetting("timelineInterlaceProcessing", "0")
        logger.debug(f"📐 Set timeline defaults: {w}×{h} @ {fps}fps")
    except Exception as e:
        logger.error(f"❌ Failed to set project defaults: {e}")

    return prev


def restore_project_defaults(project, prev):
    """Restore previous project defaults with logging."""
    logger = logging.getLogger(__name__)

    for k, v in prev.items():
        if v is None:
            continue
        try:
            project.SetSetting(k, v)
            logger.debug(f"🔄 Restored setting {k}: {v}")
        except Exception as e:
            logger.debug(f"⚠️ Could not restore setting {k}: {e}")


def ensure_tracks_named(tl, kind, names_top_to_bottom=None, names_left_to_right=None, stats=None):
    """Ensure tracks exist and are properly named with logging."""
    logger = logging.getLogger(__name__)

    if kind == "video":
        target = list(reversed(names_top_to_bottom or []))  # index 1 = V1 bottom
        logger.debug(f"🎬 Setting up {len(target)} video tracks")
    else:
        target = names_left_to_right or []
        logger.debug(f"🎵 Setting up {len(target)} audio tracks")

    # Ensure track count
    try:
        have = int(tl.GetTrackCount(kind))
        logger.debug(f"📊 Current {kind} tracks: {have}")
    except Exception as e:
        logger.debug(f"⚠️ Could not get {kind} track count: {e}")
        have = 0

    need = len(target) - have
    logger.debug(f"🔢 Need to add {max(0, need)} {kind} tracks")

    for i in range(max(0, need)):
        try:
            tl.AddTrack(kind)
            if stats:
                stats.tracks_created += 1
            logger.debug(f"  ➕ Added {kind} track {have + i + 1}")
        except Exception as e:
            logger.error(f"❌ Failed to add {kind} track: {e}")
            if stats:
                stats.log_error(f"Track creation: {kind}", str(e))

    # Name the tracks
    named_count = 0
    if kind == "video":
        for i, label in enumerate(target, start=1):
            try:
                tl.SetTrackName("video", i, label)
                named_count += 1
                logger.debug(f"  🏷️ V{i}: {label}")
            except Exception as e:
                logger.debug(f"⚠️ Could not name video track {i}: {e}")
    else:
        for i, label in enumerate(target, start=1):
            try:
                tl.SetTrackName("audio", i, label)
                named_count += 1
                logger.debug(f"  🏷️ A{i}: {label}")
            except Exception as e:
                logger.debug(f"⚠️ Could not name audio track {i}: {e}")

    logger.debug(f"✅ Named {named_count}/{len(target)} {kind} tracks")

    # Add subtitle track once if it doesn't already exist
    if kind == "audio":
        try:
            try:
                subcnt = int(tl.GetTrackCount("subtitle"))
            except Exception:
                subcnt = 0
            if subcnt == 0:
                tl.AddTrack("subtitle")
                tl.SetTrackName("subtitle", 1, "CC | English")
                logger.debug("📝 Added subtitle track")
                if stats:
                    stats.tracks_created += 1
        except Exception as e:
            logger.debug(f"⚠️ Could not add subtitle track: {e}")


def safe_set_current_folder(mp, folder):
    try:
        ok = mp.SetCurrentFolder(folder)
        if ok is False:
            log.debug("⚠️ SetCurrentFolder returned False (continuing anyway)")
        return True
    except Exception as e:
        log.debug(f"⚠️ SetCurrentFolder raised: {e}")
        return False


def create_vertical_timeline(
    mp, project, folder, title, w, h, fps, stats, markers=None, video_tracks=None, audio_tracks=None
):
    """Create timeline with comprehensive error handling and logging."""
    logger = logging.getLogger(__name__)

    if not folder:
        logger.warning(f"⚠️ No folder for timeline: {title}")
        stats.timelines_failed += 1
        stats.log_error(f"Timeline creation: {title}", "No target folder")
        return None

    logger.info(f"🎬 Creating timeline: {title}")

    # Set project defaults → create → restore
    prev = set_project_defaults(project, w, h, fps)
    logger.debug("   prev defaults: %s", prev)

    try:
        safe_set_current_folder(mp, folder)
        logger.debug(f"📁 Set current folder for: {title}")
    except Exception as e:
        logger.debug(f"⚠️ Could not set current folder: {e}")

    try:
        tl = mp.CreateEmptyTimeline(title)
        if tl:
            logger.debug(f"✅ Timeline created: {title}")
        else:
            logger.error(f"❌ CreateEmptyTimeline returned None: {title}")
            stats.timelines_failed += 1
            stats.log_error(f"Timeline creation: {title}", "CreateEmptyTimeline returned None")
            restore_project_defaults(project, prev)
            return None
    except Exception as e:
        logger.error(f"❌ CreateEmptyTimeline failed: {title} - {e}")
        stats.timelines_failed += 1
        stats.log_error(f"Timeline creation: {title}", str(e))
        restore_project_defaults(project, prev)
        return None

    # Restore project defaults
    restore_project_defaults(project, prev)
    logger.debug("   restored defaults: %s", prev)

    # Setup tracks
    try:
        ensure_tracks_named(
            tl,
            "video",
            names_top_to_bottom=(video_tracks or VIDEO_TRACKS_TOP_TO_BOTTOM),
            stats=stats,
        )
        ensure_tracks_named(
            tl, "audio", names_left_to_right=(audio_tracks or AUDIO_TRACKS), stats=stats
        )
        stats.timelines_created += 1
        logger.info(f"   ✅ Timeline ready: {title}")
    except Exception as e:
        logger.error(f"❌ Track setup failed for {title}: {e}")
        stats.log_error(f"Track setup: {title}", str(e))

    # Add markers if requested
    try:
        if markers:
            add_markers_to_timeline(tl, FPS, markers)
    except Exception as e:
        logger.debug(f"⚠️ Marker add failed for {title}: {e}")

    return tl


# ──────────────────────────────────────────────────────────────
# Marker helpers
# ──────────────────────────────────────────────────────────────
def _sec_to_frames(sec, fps_float):
    return int(round(sec * fps_float))


def _add_marker_safe(tl, frame, color, name, note, dur_frames):
    """Try adding a marker; if it fails due to color, retry with fallback."""
    try:
        ok = tl.AddMarker(frame, color, name, note, dur_frames, "")
        if ok:
            return True
        # retry if we have a mapping
        fb = _COLOR_FALLBACK.get(color)
        if fb:
            ok2 = tl.AddMarker(frame, fb, name, note, dur_frames, "")
            if ok2:
                log.debug(f"   🎯 Marker color '{color}' fell back to '{fb}'")
                return True
        log.debug(f"   ⚠️ AddMarker returned False for '{name}' at frame {frame}")
    except Exception:
        # some builds want 5 params; try again
        try:
            ok3 = tl.AddMarker(frame, color, name, note, dur_frames)
            if ok3:
                return True
            fb = _COLOR_FALLBACK.get(color)
            if fb:
                ok4 = tl.AddMarker(frame, fb, name, note, dur_frames)
                if ok4:
                    log.debug(f"   🎯 Marker color '{color}' fell back to '{fb}' (5-param)")
                    return True
        except Exception as e2:
            log.debug(f"   ❌ AddMarker raised: {e2}")
    return False


def add_markers_to_timeline(tl, fps_str, markers):
    """markers: list of dicts {t, color, name, dur, notes}"""
    try:
        fps_float = float(fps_str)
    except Exception:
        fps_float = 29.97
    added = 0
    for m in markers or []:
        frame = _sec_to_frames(m["t"], fps_float)
        dur_frames = _sec_to_frames(m.get("dur", 0.0), fps_float)
        color = m["color"]
        if color not in _SUPPORTED_MARKER_COLORS:
            color = _COLOR_FALLBACK.get(color, "Red")
        ok = _add_marker_safe(
            tl,
            frame,
            color,
            m["name"],
            m.get("notes", ""),
            dur_frames,
        )
        if ok:
            added += 1
    log.info(f"   🏷️ Markers added: {added}")
    return added


def apply_label_map(base_markers, label_map):
    """Return a deep-copied marker list with names remapped per pillar."""
    mapped = []
    for m in base_markers:
        nm = dict(m)
        nm["name"] = label_map.get(m["name"], m["name"])
        mapped.append(nm)
    return mapped


# ──────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────
def main():
    """Main execution with comprehensive logging and statistics."""
    stats = BuildStats()

    try:
        log.info(f"🎯 Project: {PROJECT_NAME}")
        log.info(f"📐 Format: {WIDTH}×{HEIGHT} @ {FPS}fps")
        log.info(f"📊 Structure: {len(TOP_BINS)} top bins, {len(PILLARS)} pillars")

        # Connect to Resolve
        resolve = get_resolve()
        pm = resolve.GetProjectManager()

        # Create or load project - safer approach with fallback
        log.info(f"🏗️ Creating/loading project: {PROJECT_NAME}")

        # Check if there's already a current project
        current_proj = pm.GetCurrentProject()
        if current_proj:
            current_name = current_proj.GetName()
            log.debug(f"Current project: {current_name}")

            # If it's the same project we want, use it
            if current_name == PROJECT_NAME:
                log.info(f"✅ Already using target project: {current_name}")
                proj = current_proj
            elif current_name == PROJECT_NAME_FALLBACK:
                log.info(f"✅ Already using fallback project: {current_name}")
                proj = current_proj
            else:
                log.debug(f"Different project loaded: {current_name}")
                proj = None
        else:
            proj = None

        # Try to load target project if not already current
        if not proj:
            try:
                if pm.LoadProject(PROJECT_NAME):
                    proj = pm.GetCurrentProject()
                    if proj:
                        log.info(f"✅ Loaded existing project: {proj.GetName()}")
            except Exception as e:
                log.debug(f"Load attempt failed (expected if new): {e}")

        # Try fallback project if main one failed
        if not proj:
            try:
                if pm.LoadProject(PROJECT_NAME_FALLBACK):
                    proj = pm.GetCurrentProject()
                    if proj:
                        log.info(f"✅ Loaded existing fallback project: {proj.GetName()}")
            except Exception as e:
                log.debug(f"Fallback load attempt failed: {e}")

        # If loading failed, create new project
        if not proj:
            try:
                log.debug(f"Attempting to create project: {PROJECT_NAME}")
                proj = pm.CreateProject(PROJECT_NAME)
                if proj:
                    log.info(f"✅ Created new project: {proj.GetName()}")
                else:
                    log.warning(f"❌ CreateProject returned None for: {PROJECT_NAME}")
                    # Try fallback name without special characters
                    log.info(f"🔄 Trying fallback name: {PROJECT_NAME_FALLBACK}")
                    proj = pm.CreateProject(PROJECT_NAME_FALLBACK)
                    if proj:
                        log.info(f"✅ Created new project with fallback name: {proj.GetName()}")
                    else:
                        log.error("❌ CreateProject failed even with fallback name")

                        # Try creating with a simple test name
                        test_name = f"TestProject_{datetime.datetime.now().strftime('%H%M%S')}"
                        log.info(f"🔄 Trying simple test name: {test_name}")
                        proj = pm.CreateProject(test_name)
                        if proj:
                            log.info(f"✅ Created test project: {proj.GetName()}")
                        else:
                            log.error("❌ Even simple project creation failed - API issue")
                            return False
            except Exception as e:
                log.error(f"❌ Failed to create project: {e}")
                return False

        if not proj:
            log.error("❌ Could not create or load project")
            return False

        # Get MediaPool
        mp = proj.GetMediaPool()
        root = mp.GetRootFolder()
        if not root:
            log.error("❌ MediaPool root missing")
            return False

        log.info("📂 Creating top-level bins...")
        top = {}
        for name in TOP_BINS:
            top[name] = get_or_create_folder(mp, root, name, stats)

        # Create delivery master timelines
        log.info("🧭 Creating delivery master timelines...")
        money_folder = top.get("01 | 💰 The Money")

        # Legacy/reference timelines (kept)
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

        # New Money Masters with markers
        mm_12 = "Money Master — 12s (IG short) — 2160×3840 • 29.97p"
        mm_22 = "Money Master — 22s (IG mid) — 2160×3840 • 29.97p"
        mm_30 = "Money Master — 30s (IG upper) — 2160×3840 • 29.97p"

        create_vertical_timeline_unique(
            mp,
            proj,
            money_folder,
            mm_12,
            WIDTH,
            HEIGHT,
            FPS,
            stats,
            markers=MONEY_MASTER_MARKERS["12s"],
        )
        create_vertical_timeline_unique(
            mp,
            proj,
            money_folder,
            mm_22,
            WIDTH,
            HEIGHT,
            FPS,
            stats,
            markers=MONEY_MASTER_MARKERS["22s"],
        )
        create_vertical_timeline_unique(
            mp,
            proj,
            money_folder,
            mm_30,
            WIDTH,
            HEIGHT,
            FPS,
            stats,
            markers=MONEY_MASTER_MARKERS["30s"],
        )

        # Create Formula structure
        log.info("🧪 Creating Formula pillar structure...")
        formula_root = top.get("02 | 🧪 The Formula")

        for pillar_name, subbins in PILLARS.items():
            log.info(f"🎯 Pillar: {pillar_name}")
            pillar_folder = get_or_create_folder(mp, formula_root, pillar_name, stats)

            for subbin_name, timeline_names in subbins.items():
                log.info(f"  📂 {subbin_name}")
                sub_folder = get_or_create_folder(mp, pillar_folder, subbin_name, stats)

                for base in timeline_names:
                    title = base if "— ⏱" in base else f"{base} — ⏱ 29.97p • 📐 2160×3840"
                    create_vertical_timeline_unique(
                        mp, proj, sub_folder, title, WIDTH, HEIGHT, FPS, stats
                    )

        # Create pillar-specific Master variants with markers and layouts
        log.info("🎛 Creating pillar master variants with markers...")
        for pillar, cfg in PILLAR_CONFIG.items():
            try:
                mb_folder = get_or_create_path(
                    mp, formula_root, [pillar, "10 | Master Build"], stats
                )
                if not mb_folder:
                    continue
                layout = LAYOUTS.get(cfg["layout"], LAYOUTS["DEFAULT"])
                base = cfg["master_name"]
                for tier_key, tier_label in (("12s", "12s"), ("22s", "22s"), ("30s", "30s")):
                    title = f"{base} — {tier_label} — 2160×3840 • 29.97p"
                    tier_markers = apply_label_map(
                        MONEY_MASTER_MARKERS[tier_key], cfg["marker_labels"]
                    )
                    create_vertical_timeline_unique(
                        mp,
                        proj,
                        mb_folder,
                        title,
                        WIDTH,
                        HEIGHT,
                        FPS,
                        stats,
                        markers=tier_markers,
                        video_tracks=layout["video"],
                        audio_tracks=layout["audio"],
                    )
            except Exception as e:
                log.debug(f"⚠️ Pillar master variants failed for {pillar}: {e}")

        # Crisp summary and exit code for automation
        summary = stats.get_summary()
        errors = summary["error_count"]
        duration_secs = summary["duration"]
        created_count = summary["folders_created"]
        found_count = summary["folders_found"]
        created_tl = summary["timelines_created"]
        skipped_tl = summary.get("timelines_skipped", 0)

        log.info("=" * 60)
        log.info("📊 BUILD COMPLETE")
        log.info("⏱ Duration: %.1f s", duration_secs)
        log.info("📂 Folders: %d created, %d found", created_count, found_count)
        log.info("🎬 Timelines: %d created, %d skipped", created_tl, skipped_tl)
        log.info("❌ Errors: %d", errors)

        if summary["errors"]:
            log.info("🚨 Error Details:")
            for error in summary["errors"]:
                log.info("   • %s", error)

        log.info("🎯 Done. Non-destructive. View ▸ Stacked Timelines to bounce between levels.")

        # Save the project at the end of the build process
        try:
            # newer builds
            if hasattr(proj, "Save"):
                proj.Save()
                log.info("💾 Project saved")
            # some builds expose SaveProject on ProjectManager
            elif hasattr(pm, "SaveProject"):
                pm.SaveProject(proj.GetName())
                log.info("💾 Project saved (PM)")
        except Exception:
            pass

        return errors == 0

    except Exception as e:
        log.error(f"💥 Fatal error: {e}", exc_info=True)
        stats.log_error("Fatal error", str(e))
        log.info("=" * 60)
        log.info("📊 BUILD COMPLETE (with fatal error)")
        summary = stats.get_summary()
        log.info("⏱ Duration: %.1f s", summary["duration"])
        log.info("❌ Errors: %d", summary["error_count"])
        if summary["errors"]:
            log.info("🚨 Error Details:")
            for error in summary["errors"]:
                log.info("   • %s", error)
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
