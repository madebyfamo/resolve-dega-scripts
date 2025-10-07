#!/usr/bin/env python3
"""
Verify Selects & Stringouts variant-specific markers.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import Resolve
try:
    import DaVinciResolveScript as dvr_script
    resolve = dvr_script.scriptapp("Resolve")
    pm = resolve.GetProjectManager()
    proj = pm.GetCurrentProject()
    if not proj:
        print("❌ No project open")
        sys.exit(1)
except Exception as e:
    print(f"❌ Cannot connect to DaVinci Resolve: {e}")
    sys.exit(1)

# Import variant detector
from dega_formula_builder_enhanced import _selects_variant_for_title, SELECTS_BASE, SELECTS_SPECIFIC

# Get all timelines
tl_count = proj.GetTimelineCount()
selects_timelines = []

for i in range(1, tl_count + 1):
    tl = proj.GetTimelineByIndex(i)
    if not tl:
        continue
    
    name = tl.GetName()
    name_lower = name.lower()
    
    # Filter for Selects & Stringouts
    if "selects" in name_lower or "stringout" in name_lower:
        markers = tl.GetMarkers()
        marker_count = len(markers) if markers else 0
        
        # Detect variant
        variant = _selects_variant_for_title(name_lower)
        
        # Determine expected
        if variant:
            expected_min = len(SELECTS_BASE) + 2  # Base + at least 2 variant markers
            status = "Enhanced" if marker_count >= expected_min else "Base only"
        else:
            expected_min = len(SELECTS_BASE)
            status = "Base only"
        
        selects_timelines.append({
            'name': name,
            'markers': marker_count,
            'variant': variant or 'none',
            'status': status
        })

# Sort by name
selects_timelines.sort(key=lambda x: x['name'])

# Print table
print("\n📊 SELECTS & STRINGOUTS VARIANT VERIFICATION")
print(f"Project: {proj.GetName()}")
print()
print(f"{'Timeline':<50} | Markers | Variant          | Status")
print("=" * 95)

for tl in selects_timelines:
    # Truncate name if too long
    name = tl['name'][:48] + '...' if len(tl['name']) > 50 else tl['name']
    
    status_icon = "✅" if tl['status'] == "Enhanced" else "⚠️"
    variant_display = tl['variant'][:16]
    
    print(f"{status_icon} {name:<48} | {tl['markers']:7} | {variant_display:<16} | {tl['status']}")

print("=" * 95)
print()

# Summary
total = len(selects_timelines)
enhanced = len([t for t in selects_timelines if t['status'] == 'Enhanced'])
base_only = total - enhanced

print(f"📈 Summary:")
print(f"  Total Selects/Stringouts timelines: {total}")
print(f"  Enhanced with variants: {enhanced}/{total}")
print(f"  Base only: {base_only}/{total}")
print()

if enhanced == total:
    print("🎉 All Selects timelines are enhanced with formula-specific tips!")
elif enhanced > 0:
    print(f"✅ {enhanced} timelines enhanced, {base_only} with base tips only")
else:
    print("⚠️  No variant enhancements detected")
