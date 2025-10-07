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

# ──────────────────────────────────────────────────────────────
# Logging
# ──────────────────────────────────────────────────────────────


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

if os.getenv("DEGA_DEBUG") == "1":
    logging.getLogger(__name__).setLevel(logging.DEBUG)


# ──────────────────────────────────────────────────────────────
# Resolve bootstrap
# ──────────────────────────────────────────────────────────────
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
            log.debug("🔌 Attempting bmd.scriptapp connection…")
            r = _bmd.scriptapp("Resolve")
            if r:
                log.info("✅ Connected via bmd.scriptapp")
                return r
        except Exception as e:
            log.warning(f"⚠️ bmd.scriptapp failed: {e}")
    try:
        log.debug("🔌 Attempting DaVinciResolveScript fallback…")
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
PROJECT_NAME = f"DEGA_VERT_{TODAY.replace('-', '_')}"
PROJECT_NAME_FALLBACK = f"DEGA_Project_{datetime.datetime.now().strftime('%H%M%S')}"

WIDTH, HEIGHT = "2160", "3840"
FPS = "29.97"

TOP_BINS = ["00 | �� Templates", "01 | 💰 The Money", "02 | 🧪 The Formula", "99 | 📦 Exports"]

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

# Pillars (unchanged timeline list) — scene kits added below
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
        "40 | Selects & Stringouts": ["PERF Selects — Best Lines", "B-Roll Selects — Studio"],
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

# ──────────────────────────────────────────────────────────────
# (6) Per-pillar Scene Kits (tailored)
# ──────────────────────────────────────────────────────────────
SCENE_KITS = {
    "🎵 Music-Video Snippets": {
        # Tailored to performance vibe content (no stems here)
        "20 | Scenes & Segments": [
            "PERFORMANCE — A Cam",
            "PERFORMANCE — B Cam / Phone",
            "CUTAWAYS — Hands / Details",
            "TRANSITIONS — Whips / Passes",
            "LOCATIONS — Rooftop / Alley / Studio",
            "ALT TAKES — Safety",
        ],
        # Optional prep bins at the pillar root
        "_ROOT": ["SYNC PREP — Tap/Clap ID", "STYLE REFS — Mood / Color / Fonts"],
    },
    "👗 OOTD • Fashion": {
        "20 | Scenes & Segments": [
            "LOOK — Full Body",
            "LOOK — Details (Accessories / Fabric)",
            "LOOK — Movement / Walk",
            "B-ROLL — Environment",
            "TRANSITIONS — Spin / Whip / Rack",
        ],
        "_ROOT": ["MOOD & PALETTE", "LOCATIONS — Mirror / Rooftop / Street"],
    },
    "🎙️ Talking Head": {
        "20 | Scenes & Segments": [
            "A-ROLL — Primary",
            "B-ROLL — Context / Examples",
            "TEXT SUPPORT — Callouts / Lower Thirds",
            "SCREEN INSERTS — UI / Sites",
        ],
        "_ROOT": ["TOPIC OUTLINE", "B-ROLL LIST"],
    },
    "☕️ Day in the Life": {
        "20 | Scenes & Segments": [
            "CHAPTER — Morning",
            "CHAPTER — Midday",
            "CHAPTER — Evening",
            "TRANSITIONS — Travel / Time",
            "DETAILS — Coffee / Gear / Studio",
        ],
        "_ROOT": ["SHOTLIST — Must-haves"],
    },
    "�� Cook-Ups": {
        "20 | Scenes & Segments": [
            "TAKES — Performance",
            "HANDS — Keys / Pads",
            "UI — DAW / Plugins",
            "GEAR — Overlays / Knobs",
            "BOUNCE — Hook / Beat Preview",
        ],
        "_ROOT": ["SESSION NOTES — Key/Tempo/Markers"],
    },
}


# ──────────────────────────────────────────────────────────────
# Money Master markers + (7) Marker Packs
# ──────────────────────────────────────────────────────────────
def _mm(when, color, name, dur, notes):
    return {"t": float(when), "color": color, "name": name, "dur": float(dur), "notes": notes}


# Base timings (authoritative); names may be transformed by pack
BASE_MONEY_MARKERS = {
    "12s": [
        _mm(0.000, "Red", "HOOK", 3.0, "Range 0–3s"),
        _mm(3.000, "Orange", "DRAW", 5.0, "Range 4–6s"),
        _mm(4.500, "Magenta", "INTERRUPT #1", 0.0, "Micro pattern break"),
        _mm(8.000, "Green", "COMMIT / PAYOFF", 4.0, "Range 3–5s"),
        _mm(9.000, "Magenta", "INTERRUPT #2", 0.0, "Second micro jolt"),
        _mm(11.600, "Yellow", "LOOP/CTA", 0.4, "Range 0.3–1.0s"),
    ],
    "22s": [
        _mm(0.000, "Red", "HOOK", 3.0, "Range 0–3s"),
        _mm(3.000, "Orange", "DRAW", 5.0, "Range 4–6s"),
        _mm(6.000, "Magenta", "INTERRUPT #1", 0.0, "Early micro jolt"),
        _mm(8.000, "Green", "COMMIT / PAYOFF #1", 4.0, "Range 3–5s"),
        _mm(12.000, "Blue", "SECOND HOOK", 3.0, "Range 2–4s"),
        _mm(13.500, "Magenta", "INTERRUPT #2", 0.0, "Quick flip"),
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
        _mm(13.500, "Magenta", "INTERRUPT #2", 0.0, "Quick flip"),
        _mm(15.000, "Purple", "DEVELOP A", 7.0, "Range 6–8s"),
        _mm(20.000, "Magenta", "INTERRUPT #3", 0.0, "Reset cadence"),
        _mm(22.000, "Purple", "DEVELOP B", 6.0, "Range 5–7s"),
        _mm(26.000, "Magenta", "INTERRUPT #4", 0.0, "Final jolt"),
        _mm(28.000, "Yellow", "FINAL PAYOFF / LOOP", 2.0, "Range 1.5–3.0s"),
    ],
}

# Pack name → keyword mapping for labels
_MARKER_PACKS = {
    "default": {
        "HOOK": "HOOK",
        "SECOND HOOK": "SECOND HOOK",
        "DRAW": "DRAW",
        "COMMIT": "COMMIT / PAYOFF",
        "DEVELOP": "DEVELOP",
        "FINAL": "FINAL PAYOFF / LOOP",
        "LOOP/CTA": "LOOP/CTA",
        "INTERRUPT": "INTERRUPT",
    },
    "educational": {
        "HOOK": "PROMISE (Hook)",
        "SECOND HOOK": "RE-PROMISE",
        "DRAW": "SETUP (Context)",
        "COMMIT": "PROOF / DEMO",
        "DEVELOP": "HOW-TO / INSIGHT",
        "FINAL": "RECAP / LOOP",
        "LOOP/CTA": "LOOP / CTA",
        "INTERRUPT": "PATTERN BREAK",
    },
    "promo": {
        "HOOK": "SCROLL-STOP (Hook)",
        "SECOND HOOK": "HOOK 2.0",
        "DRAW": "PROBLEM / DESIRE",
        "COMMIT": "OFFER / VALUE HIT",
        "DEVELOP": "BENEFITS / SOCIAL PROOF",
        "FINAL": "CTA / LOOP",
        "LOOP/CTA": "CTA / LOOP",
        "INTERRUPT": "JOLT",
    },
}

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


def _transform_label(base_name: str, pack: str) -> str:
    rules = _MARKER_PACKS.get(pack, _MARKER_PACKS["default"])
    name = base_name

    # Keyed replacements while preserving suffixes like "#1"
    def rep(tok, key):
        nonlocal name
        if tok in name:
            name = name.replace(tok, rules.get(key, tok))

    if "SECOND HOOK" in name:
        rep("SECOND HOOK", "SECOND HOOK")
    if "FINAL PAYOFF" in name:
        rep("FINAL PAYOFF", "FINAL")
    if "COMMIT" in name:
        rep("COMMIT", "COMMIT")
    if "DEVELOP" in name:
        rep("DEVELOP", "DEVELOP")
    if "DRAW" in name:
        rep("DRAW", "DRAW")
    if "HOOK" in name:
        rep("HOOK", "HOOK")
    if "LOOP/CTA" in name:
        rep("LOOP/CTA", "LOOP/CTA")
    if "INTERRUPT" in name:
        rep("INTERRUPT", "INTERRUPT")

    return name


def get_money_markers_for_pack(pack: str):
    """Return deep-copied markers with names transformed per pack."""
    out = {}
    for tier, lst in BASE_MONEY_MARKERS.items():
        new_list = []
        for m in lst:
            nm = copy.deepcopy(m)
            nm["name"] = _transform_label(nm["name"], pack)
            new_list.append(nm)
        out[tier] = new_list
    return out


# ──────────────────────────────────────────────────────────────
# Stats
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


# ──────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────
def get_folder_path(folder):
    names, cur = [], folder
    for _ in range(10):
        try:
            names.append(cur.GetName())
            cur = cur.GetParent()
            if not cur:
                break
        except Exception:
            break
    return " / ".join(reversed(names))


def _iter_subfolders(folder):
    logger = logging.getLogger(__name__)
    for acc in ("GetSubFolders", "GetSubFolderList"):
        f = getattr(folder, acc, None)
        if not f:
            continue
        try:
            res = f()
            if isinstance(res, dict):
                logger.debug(f"📁 {acc}: {len(res)} (dict)")
                return list(res.values())
            if isinstance(res, list):
                logger.debug(f"📁 {acc}: {len(res)} (list)")
                return res
        except Exception as e:
            logger.debug(f"⚠️ {acc} failed: {e}")
    logger.debug("📁 No subfolders found")
    return []


def get_or_create_folder(mp, parent, name, stats):
    logger = logging.getLogger(__name__)
    for sub in _iter_subfolders(parent):
        try:
            if sub.GetName() == name:
                logger.info("  📂 Found: %s (under %s)", name, get_folder_path(parent))
                stats.folders_found += 1
                return sub
        except Exception as e:
            logger.debug(f"⚠️ check name: {e}")
    folder = None
    try:
        logger.debug(f"🔨 Creating folder: {name} under {get_folder_path(parent)}")
        folder = mp.AddSubFolder(parent, name)
        if isinstance(folder, tuple):
            folder = folder[0]
        if folder:
            logger.info("  ✅ Created: %s (under %s)", name, get_folder_path(parent))
            stats.folders_created += 1
        else:
            logger.warning("  ❌ AddSubFolder returned None: %s", name)
    except Exception as e:
        logger.debug(f"⚠️ mp.AddSubFolder failed: {e}")
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


def set_project_defaults(project, w, h, fps):
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
            logger.debug(f"📋 Save {k}: {prev[k]}")
        except Exception as e:
            logger.debug(f"⚠️ get setting {k}: {e}")
            prev[k] = None
    try:
        project.SetSetting("timelineResolutionWidth", str(w))
        project.SetSetting("timelineResolutionHeight", str(h))
        project.SetSetting("timelinePlaybackFrameRate", str(fps))
        project.SetSetting("timelineFrameRate", str(fps))
        project.SetSetting("timelineDropFrameTimecode", "0")
        project.SetSetting("timelineInterlaceProcessing", "0")
        logger.debug(f"📐 Defaults set: {w}×{h} @ {fps}")
    except Exception as e:
        logger.error(f"❌ set defaults: {e}")
    return prev


def restore_project_defaults(project, prev):
    logger = logging.getLogger(__name__)
    for k, v in prev.items():
        if v is None:
            continue
        try:
            project.SetSetting(k, v)
            logger.debug(f"🔄 Restored {k}: {v}")
        except Exception as e:
            logger.debug(f"⚠️ restore {k}: {e}")


def safe_set_current_folder(mp, folder):
    try:
        ok = mp.SetCurrentFolder(folder)
        if ok is False:
            log.debug("⚠️ SetCurrentFolder returned False")
        return True
    except Exception as e:
        log.debug(f"⚠️ SetCurrentFolder raised: {e}")
        return False


# ──────────────────────────────────────────────────────────────
# Project targeting: default = use current; explicit opt-in to switch
# ──────────────────────────────────────────────────────────────
def _env(key, default=None):
    v = os.getenv(key)
    return v if v is not None else default


def _switch_allowed():
    return _env("DEGA_NO_SWITCH", "0") != "1"


def resolve_target_project(pm, log, default_dated_name, fallback_simple_name):
    """
    Returns a Project object to operate on, without surprising switches.

    Target modes:
      - DEGA_TARGET=current (default): use the currently open project. No switching.
      - DEGA_TARGET=dated: load/create the dated DEGA project (legacy behavior).
      - DEGA_TARGET=name:<Project Name>: load/create that exact project.

    Safety:
      - If DEGA_NO_SWITCH=1, we never switch projects. We only use current.
    """
    target = _env("DEGA_TARGET", "current").strip()
    no_switch = _env("DEGA_NO_SWITCH", "0") == "1"

    cur = pm.GetCurrentProject()
    cur_name = cur.GetName() if cur else None

    def _use_current(reason):
        if not cur:
            log.error("❌ No current project open (%s). Open a project or set DEGA_TARGET.", reason)
            return None
        log.info(f"📌 Using CURRENT project (no switch): {cur_name}  [{reason}]")
        return cur

    # 1) Default/current behavior
    if target == "current":
        return _use_current("DEGA_TARGET=current")

    # 2) Safety override: forbid switching
    if no_switch:
        log.warning("🛑 DEGA_NO_SWITCH=1 — refusing to switch projects.")
        return _use_current("NO_SWITCH")

    # 3) dated mode (legacy DEGA_VERT_YYYY_MM_DD)
    if target == "dated":
        name = default_dated_name
        log.info(f"🏗️ Targeting dated project: {name}")
        try:
            if pm.LoadProject(name):
                proj = pm.GetCurrentProject()
                if proj:
                    log.info(f"✅ Loaded existing: {proj.GetName()}")
                    return proj
        except Exception as e:
            log.debug(f"Load failed (expected if new): {e}")

        # Create if not found
        try:
            proj = pm.CreateProject(name)
            if proj:
                log.info(f"✅ Created new project: {proj.GetName()}")
                return proj
            # One more attempt: very simple fallback name
            log.warning(
                f"⚠️ CreateProject(None) for dated name returned None. Trying fallback: {fallback_simple_name}"
            )
            proj = pm.CreateProject(fallback_simple_name)
            if proj:
                log.info(f"✅ Created fallback project: {proj.GetName()}")
                return proj
        except Exception as e:
            log.error(f"❌ Failed to create dated/fallback project: {e}")
        return None

    # 4) name:<Project Name>
    if target.startswith("name:"):
        name = target[len("name:") :].strip()
        if not name:
            log.error("❌ DEGA_TARGET=name:<Project Name> provided without a name.")
            return None
        log.info(f"🏗️ Targeting named project: {name}")
        try:
            if pm.LoadProject(name):
                proj = pm.GetCurrentProject()
                if proj:
                    log.info(f"✅ Loaded existing: {proj.GetName()}")
                    return proj
        except Exception as e:
            log.debug(f"Load failed (expected if new): {e}")

        # Create if not found
        try:
            proj = pm.CreateProject(name)
            if proj:
                log.info(f"✅ Created new project: {proj.GetName()}")
                return proj
        except Exception as e:
            log.error(f"❌ Failed to create project '{name}': {e}")
        return None

    # 5) Unknown mode → fall back to current (no switch)
    log.warning(f"⚠️ Unknown DEGA_TARGET='{target}'. Falling back to current project.")
    return _use_current("unknown_target")


# ──────────────────────────────────────────────────────────────
# (11) Upgrade/Migration-aware track ensure
# ──────────────────────────────────────────────────────────────
def ensure_tracks_named(
    tl, kind, names_top_to_bottom=None, names_left_to_right=None, stats=None, upgrade=True
):
    """Ensure tracks exist and are named. If upgrade=True: rename existing tracks to target labels, add missing; no deletes."""
    logger = logging.getLogger(__name__)
    if kind == "video":
        target = list(reversed(names_top_to_bottom or []))  # index1 = bottom V1
        logger.debug(f"🎬 Target video tracks: {len(target)}")
    else:
        target = names_left_to_right or []
        logger.debug(f"🎵 Target audio tracks: {len(target)}")
    try:
        have = int(tl.GetTrackCount(kind))
        logger.debug(f"📊 Current {kind} tracks: {have}")
    except Exception as e:
        logger.debug(f"⚠️ get {kind} count: {e}")
        have = 0

    # Rename pass (migration)
    if upgrade and have > 0:
        for i in range(1, min(have, len(target)) + 1):
            try:
                # If API supports read current name:
                try:
                    cur = tl.GetTrackName(kind, i)
                except Exception:
                    cur = None
                if cur != target[i - 1]:
                    tl.SetTrackName(kind, i, target[i - 1])
                    logger.debug(f"  🏷️ Rename {kind} {i}: {cur} → {target[i-1]}")
            except Exception as e:
                logger.debug(f"⚠️ rename {kind} {i}: {e}")

    # Add missing
    need = len(target) - have
    for _ in range(max(0, need)):
        try:
            tl.AddTrack(kind)
            if stats:
                stats.tracks_created += 1
        except Exception as e:
            logger.error(f"❌ add {kind} track: {e}")
            if stats:
                stats.log_error(f"Track creation: {kind}", str(e))

    # Name all targets (covers fresh + post-add)
    total_to_name = len(target)
    for i in range(1, total_to_name + 1):
        try:
            tl.SetTrackName(kind, i, target[i - 1])
            logger.debug(f"  🏷️ {kind.upper()} {i}: {target[i-1]}")
        except Exception as e:
            logger.debug(f"⚠️ set name {kind} {i}: {e}")

    # Subtitle once
    if kind == "audio":
        try:
            try:
                subcnt = int(tl.GetTrackCount("subtitle"))
            except Exception:
                subcnt = 0
            if subcnt == 0:
                tl.AddTrack("subtitle")
                tl.SetTrackName("subtitle", 1, "CC | English")
                if stats:
                    stats.tracks_created += 1
                logger.debug("📝 Subtitle added")
        except Exception as e:
            logger.debug(f"⚠️ subtitle add: {e}")


# ──────────────────────────────────────────────────────────────
# Timeline creation + markers
# ──────────────────────────────────────────────────────────────
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


def find_timeline(project, name):
    # helper for migration: get the timeline object by name
    try:
        count = int(project.GetTimelineCount())
        for i in range(1, count + 1):
            tl = project.GetTimelineByIndex(i)
            if tl and tl.GetName() == name:
                return tl
    except Exception:
        pass
    try:
        tls = project.GetTimelines()
        if isinstance(tls, list):
            for tl in tls:
                if tl and tl.GetName() == name:
                    return tl
    except Exception:
        pass
    return None


def _sec_to_frames(sec, fps_float):
    return int(round(sec * fps_float))


def _add_marker_safe(tl, frame, color, name, note, dur_frames):
    try:
        ok = tl.AddMarker(frame, color, name, note, dur_frames, "")
        if ok:
            return True
        fb = _COLOR_FALLBACK.get(color)
        if fb and tl.AddMarker(frame, fb, name, note, dur_frames, ""):
            log.debug(f"   🎯 Marker color '{color}' → '{fb}'")
            return True
    except Exception:
        try:
            ok2 = tl.AddMarker(frame, color, name, note, dur_frames)
            if ok2:
                return True
            fb = _COLOR_FALLBACK.get(color)
            if fb and tl.AddMarker(frame, fb, name, note, dur_frames):
                log.debug(f"   🎯 Marker color '{color}' → '{fb}' (5-param)")
                return True
        except Exception as e2:
            log.debug(f"   ❌ AddMarker raised: {e2}")
    return False


def add_markers_to_timeline(tl, fps_str, markers):
    try:
        fps_float = float(fps_str)
    except Exception:
        fps_float = 29.97
    added = 0
    for m in markers or []:
        frame = _sec_to_frames(m["t"], fps_float)
        dur_frames = _sec_to_frames(m.get("dur", 0.0), fps_float)
        color = m["color"]
        color = color if color in _SUPPORTED_MARKER_COLORS else _COLOR_FALLBACK.get(color, "Red")
        if _add_marker_safe(tl, frame, color, m["name"], m.get("notes", ""), dur_frames):
            added += 1
    log.info(f"   🏷️ Markers added: {added}")
    return added


def create_vertical_timeline(
    mp, project, folder, title, w, h, fps, stats, markers=None, upgrade=True
):
    logger = logging.getLogger(__name__)
    if not folder:
        logger.warning(f"⚠️ No folder for timeline: {title}")
        stats.timelines_failed += 1
        stats.log_error(f"Timeline creation: {title}", "No target folder")
        return None
    logger.info(f"🎬 Creating timeline: {title}")
    prev = set_project_defaults(project, w, h, fps)
    try:
        safe_set_current_folder(mp, folder)
        tl = mp.CreateEmptyTimeline(title)
        if not tl:
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
    restore_project_defaults(project, prev)

    # Tracks (migration-aware)
    try:
        ensure_tracks_named(
            tl,
            "video",
            names_top_to_bottom=VIDEO_TRACKS_TOP_TO_BOTTOM,
            stats=stats,
            upgrade=upgrade,
        )
        ensure_tracks_named(
            tl, "audio", names_left_to_right=AUDIO_TRACKS, stats=stats, upgrade=upgrade
        )
        stats.timelines_created += 1
        logger.info(f"   ✅ Timeline ready: {title}")
    except Exception as e:
        logger.error(f"❌ Track setup failed for {title}: {e}")
        stats.log_error(f"Track setup: {title}", str(e))

    # Markers
    try:
        if markers:
            add_markers_to_timeline(tl, FPS, markers)
    except Exception as e:
        logger.debug(f"⚠️ Marker add failed for {title}: {e}")
    return tl


def create_vertical_timeline_unique(
    mp, project, folder, title, w, h, fps, stats, markers=None, upgrade=True
):
    if timeline_exists(project, title):
        log.info("   ↺ Timeline exists: %s", title)
        # (11) Migration pass if enabled: rename + add missing tracks
        if upgrade:
            tl = find_timeline(project, title)
            if tl:
                try:
                    ensure_tracks_named(
                        tl,
                        "video",
                        names_top_to_bottom=VIDEO_TRACKS_TOP_TO_BOTTOM,
                        stats=stats,
                        upgrade=True,
                    )
                    ensure_tracks_named(
                        tl, "audio", names_left_to_right=AUDIO_TRACKS, stats=stats, upgrade=True
                    )
                    log.info("   🔧 Upgraded track labels on existing: %s", title)
                except Exception as e:
                    log.debug(f"⚠️ upgrade on existing '{title}' failed: {e}")
        stats.timelines_skipped += 1
        return None
    return create_vertical_timeline(
        mp, project, folder, title, w, h, fps, stats, markers=markers, upgrade=upgrade
    )


# ──────────────────────────────────────────────────────────────
# Scene Kit applier
# ──────────────────────────────────────────────────────────────
def apply_scene_kits(mp, pillar_name, pillar_folder, stats):
    kit = SCENE_KITS.get(pillar_name)
    if not kit:
        return
    # root extras
    for extra in kit.get("_ROOT", []):
        get_or_create_folder(mp, pillar_folder, extra, stats)
    # segment additions
    seg_name = "20 | Scenes & Segments"
    # find/create the base segments folder (already created earlier in flow)
    seg_folder = None
    for sub in _iter_subfolders(pillar_folder):
        try:
            if sub.GetName() == seg_name:
                seg_folder = sub
                break
        except Exception:
            pass
    if not seg_folder:
        seg_folder = get_or_create_folder(mp, pillar_folder, seg_name, stats)
    for subb in kit.get(seg_name, []):
        get_or_create_folder(mp, seg_folder, subb, stats)


# ──────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────
def main():
    """Main execution with comprehensive logging and statistics."""
    stats = BuildStats()

    # Marker pack selection
    marker_pack = os.getenv("DEGA_MARKER_PACK", "default").strip().lower()
    if marker_pack not in _MARKER_PACKS:
        log.info("ℹ️ Unknown DEGA_MARKER_PACK=%s → using 'default'", marker_pack)
        marker_pack = "default"
    money_markers = get_money_markers_for_pack(marker_pack)

    try:
        log.info("🚀 DEGA Formula Builder v4.5 starting…")
        log.info(f"📐 Format: {WIDTH}×{HEIGHT} @ {FPS}fps")
        log.info(f"🏷 Marker pack: {marker_pack}")
        log.info(f"📊 Structure: {len(TOP_BINS)} top bins, {len(PILLARS)} pillars")

        # Connect to Resolve
        resolve = get_resolve()
        pm = resolve.GetProjectManager()

        # Target resolution: default CURRENT, opt-in switching via DEGA_TARGET
        dated_name = f"DEGA_VERT_{TODAY.replace('-', '_')}"
        fallback_simple = f"DEGA_Project_{datetime.datetime.now().strftime('%H%M%S')}"

        # Banner: show mode and switch settings
        target_mode = _env("DEGA_TARGET", "current").strip()
        switch_ok = _switch_allowed()
        log.info(f"🎛 Mode: DEGA_TARGET={target_mode} • SwitchAllowed={str(switch_ok)}")

        proj = resolve_target_project(pm, log, dated_name, fallback_simple)
        if not proj:
            log.error("❌ Could not acquire a project to operate on. Aborting.")
            return False

        log.info(f"🎯 Operating on project: {proj.GetName()}")

        # Get MediaPool
        mp = proj.GetMediaPool()
        root = mp.GetRootFolder()
        if not root:
            log.error("❌ MediaPool root missing")
            return False

        # Top-level bins
        log.info("📂 Creating top-level bins…")
        top = {}
        for name in TOP_BINS:
            top[name] = get_or_create_folder(mp, root, name, stats)

        # Money Masters (legacy + new packs)
        money_folder = top.get("01 | 💰 The Money")

        create_vertical_timeline_unique(
            mp,
            proj,
            money_folder,
            "01 | 💰 The Money — ⏱ 29.97p • ⌁ 709/2.4 • 📐 2160×3840 • 🎚 v01",
            WIDTH,
            HEIGHT,
            FPS,
            stats,
            markers=None,
            upgrade=True,
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
            markers=None,
            upgrade=True,
        )

        # New Money Masters (markers depend on pack; timings stable)
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
            markers=money_markers["12s"],
            upgrade=True,
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
            markers=money_markers["22s"],
            upgrade=True,
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
            markers=money_markers["30s"],
            upgrade=True,
        )

        # Formula structure + (6) Scene Kits
        log.info("🧪 Creating Formula pillar structure…")
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
                        mp, proj, sub_folder, title, WIDTH, HEIGHT, FPS, stats, upgrade=True
                    )
            # Scene kits tailored per pillar
            apply_scene_kits(mp, pillar_name, pillar_folder, stats)

        # Summary
        summary = stats.get_summary()
        log.info("=" * 60)
        log.info("📊 BUILD COMPLETE")
        log.info("⏱ Duration: %.1f s", summary["duration"])
        log.info(
            "📂 Folders: %d created, %d found", summary["folders_created"], summary["folders_found"]
        )
        log.info(
            "🎬 Timelines: %d created, %d skipped",
            summary["timelines_created"],
            summary["timelines_skipped"],
        )
        log.info("❌ Errors: %d", summary["error_count"])
        if summary["errors"]:
            log.info("🚨 Error Details:")
            for e in summary["errors"]:
                log.info("   • %s", e)
        log.info("🎯 Done. Non-destructive. View ▸ Stacked Timelines to bounce between levels.")

        # Save project
        try:
            if hasattr(proj, "Save"):
                proj.Save()
                log.info("💾 Project saved")
            elif hasattr(pm, "SaveProject"):
                pm.SaveProject(proj.GetName())
                log.info("💾 Project saved (PM)")
        except Exception:
            pass

        return summary["error_count"] == 0

    except Exception as e:
        log.error(f"💥 Fatal error: {e}", exc_info=True)
        stats.log_error("Fatal error", str(e))
        summary = stats.get_summary()
        log.info("=" * 60)
        log.info("📊 BUILD COMPLETE (with fatal error)")
        log.info("⏱ Duration: %.1f s", summary["duration"])
        log.info("❌ Errors: %d", summary["error_count"])
        if summary["errors"]:
            log.info("🚨 Error Details:")
            for err in summary["errors"]:
                log.info("   • %s", err)
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
