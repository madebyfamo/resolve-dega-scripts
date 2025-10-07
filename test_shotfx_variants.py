#!/usr/bin/env python3
"""Test the variant-specific ShotFX marker detection."""

import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

try:
    import DaVinciResolveScript as dvr
except ImportError:
    print("❌ Cannot import DaVinciResolveScript")
    sys.exit(1)

# Import the functions from the main script
sys.path.insert(0, script_dir)
exec(open("dega_formula_builder_enhanced.py").read(), globals())

resolve = dvr.scriptapp("Resolve")
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()

print("=" * 80)
print("🧪 SHOTFX VARIANT-SPECIFIC MARKERS TEST")
print("=" * 80)
print()

cnt = int(proj.GetTimelineCount() or 0)
shotfx_timelines = []

for i in range(1, cnt + 1):
    tl = proj.GetTimelineByIndex(i)
    if not tl:
        continue
    title = tl.GetName() or ""
    t_lower = title.lower()
    
    if ("shotfx" in t_lower) or ("shot fx" in t_lower):
        if " money master" not in t_lower and not t_lower.startswith("money master"):
            shotfx_timelines.append(title)

if not shotfx_timelines:
    print("⚠️  No ShotFX timelines found")
    sys.exit(0)

print(f"Found {len(shotfx_timelines)} ShotFX timelines:\n")

for title in shotfx_timelines:
    markers = get_principle_markers_for_title(title)
    
    # Check if it's getting variant-specific markers
    variant = _shotfx_variant_for_title(title.lower())
    
    print(f"📋 {title}")
    print(f"   Variant detected: {variant or 'none (base ShotFX only)'}")
    print(f"   Total markers: {len(markers)}")
    
    if len(markers) > 4:  # More than base pack
        print(f"   ✅ Enhanced with variant-specific tips!")
        # Show first few variant markers
        print(f"   Sample tips:")
        for i, m in enumerate(markers[4:7], 1):  # Show 3 variant tips
            name = m.get("name", "")
            print(f"      {i}. {name}")
    else:
        print(f"   📌 Base ShotFX principles only")
    
    print()

print("=" * 80)
print("✨ Test complete!")
