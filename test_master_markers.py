#!/usr/bin/env python3
"""Quick test to verify master timeline markers are intact."""

import sys
import os

# Add parent dir to path for DaVinciResolveScript
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

try:
    import DaVinciResolveScript as dvr
except ImportError:
    print("❌ Cannot import DaVinciResolveScript")
    sys.exit(1)

resolve = dvr.scriptapp("Resolve")
if not resolve:
    print("❌ Cannot connect to DaVinci Resolve")
    sys.exit(1)

pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()
if not proj:
    print("❌ No project open")
    sys.exit(1)

print(f"📊 MASTER TIMELINE MARKERS AUDIT")
print(f"Project: {proj.GetName()}\n")

cnt = int(proj.GetTimelineCount() or 0)
master_timelines = []

for i in range(1, cnt + 1):
    tl = proj.GetTimelineByIndex(i)
    if not tl:
        continue
    title = tl.GetName() or ""
    
    # Check if it's a master timeline
    t_lower = title.lower()
    if " money master" in t_lower or t_lower.startswith("money master"):
        marker_count = len(tl.GetMarkers() or {})
        master_timelines.append((title, marker_count))

if not master_timelines:
    print("⚠️  No master timelines found")
else:
    print(f"{'Timeline':<60} | Markers")
    print("=" * 72)
    for title, count in master_timelines:
        status = "✅" if count >= 4 else "⚠️"
        # Truncate long titles
        display_title = title[:57] + "..." if len(title) > 60 else title
        print(f"{status} {display_title:<58} | {count:>7}")
    
    print("\n📈 Summary:")
    print(f"  Master timelines found: {len(master_timelines)}")
    with_markers = sum(1 for _, c in master_timelines if c > 0)
    print(f"  With markers: {with_markers}/{len(master_timelines)}")
    
    if with_markers == len(master_timelines):
        print("\n🎉 All master timelines have markers!")
    else:
        print(f"\n⚠️  {len(master_timelines) - with_markers} master timeline(s) missing markers")
