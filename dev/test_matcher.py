#!/usr/bin/env python3
"""Test the improved matcher on actual timeline names."""

import sys

sys.path.insert(
    0,
    "/Users/rodneywright/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility",
)

from the_dega_template_full import get_principle_markers_for_title, PRINCIPLE_PACKS

test_names = [
    "Segment — Verse Performance — ⏱ 29.97p • 📐 2160×3840",
    "ShotFX — Clone in Hallway (feather 6–10px) — ⏱ 29.97p • 📐 2160×3840",
    "Interview — Radio Cut + B-Roll — ⏱ 29.97p • 📐 2160×3840",
    "LOOK — Rooftop Golden Hour — ⏱ 29.97p • 📐 2160×3840",
    "Chapter — Coffee Run — ⏱ 29.97p • 📐 2160×3840",
    "Section — Teaser / Hook Preview — ⏱ 29.97p • 📐 2160×3840",
    "Money Master — 12s (IG short) — 2160×3840 • 29.97p",
    "PERF Selects — Best Lines — ⏱ 29.97p • 📐 2160×3840",
]

print("🧪 Testing improved matcher:\n")

for name in test_names:
    markers = get_principle_markers_for_title(name)
    marker_count = len(markers) if markers else 0

    status = "✅" if marker_count > 0 else "⚪️"
    pack_name = ""

    if markers:
        # Find which pack it matched
        for pack_key, pack_markers in PRINCIPLE_PACKS.items():
            if pack_markers == markers:
                pack_name = f" → {pack_key}"
                break

    print(f"{status} {marker_count} markers{pack_name}")
    print(f"   {name}\n")

print("\n📊 Summary:")
print("✅ = Markers found (should be added)")
print("⚪️ = No markers (masters or utility timelines, correctly excluded)")
