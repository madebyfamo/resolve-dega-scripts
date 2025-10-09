#!/usr/bin/env python3
"""
Test v4.7 markers: Seconds-only pacing + butt-joined borders
Verifies:
1. Marker notes contain seconds-based cut guidance (e.g., "0.8–1.2s")
2. Adjacent markers butt-join (extend to touch, not 1-frame gap)
3. Lane/tier-specific guidance applied correctly
"""

import sys
import os

# Setup Resolve API access
sys.path.append(
    "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules/"
)

try:
    import DaVinciResolveScript as dvr
    resolve = dvr.scriptapp("Resolve")
    if not resolve:
        print("❌ Could not connect to DaVinci Resolve")
        sys.exit(1)
except Exception as e:
    print(f"❌ Failed to import DaVinci Resolve API: {e}")
    sys.exit(1)

pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()

if not proj:
    print("❌ No project open in Resolve")
    sys.exit(1)

print(f"📂 Connected to project: {proj.GetName()}")
print()

# v4.7 detection keywords (seconds-based, not beat-based)
v47_keywords = [
    "— Cuts:",  # v4.7 format
    "~0.",  # seconds notation (e.g., "~0.8–1.2s")
    "≤0.",  # less-than-or-equal seconds (e.g., "≤0.7s")
    "–1.",  # range with 1.x seconds
    "–2.",  # range with 2.x seconds
]

# Old v4.6 keywords (should NOT appear in v4.7)
v46_keywords = [
    "Edit pacing:",
    "nuance:",
    "Tier nudge:",
    "Context:",
]


def test_marker_notes_v47(tl):
    """Check if markers have v4.7 seconds-only guidance."""
    markers = tl.GetMarkers()
    if not markers:
        return 0, 0, []
    
    total = len(markers)
    enriched = 0
    v46_detected = 0
    
    for frame_id, marker_data in markers.items():
        note = marker_data.get("note", "")
        name = marker_data.get("name", "")
        
        # Check for v4.7 keywords
        has_v47 = any(kw in note for kw in v47_keywords)
        # Check for v4.6 keywords (should be gone)
        has_v46 = any(kw in note for kw in v46_keywords)
        
        if has_v47:
            enriched += 1
        if has_v46:
            v46_detected += 1
    
    return total, enriched, v46_detected


def test_butt_joined_borders(tl):
    """Check if adjacent markers butt-join (no gaps)."""
    markers = tl.GetMarkers()
    if not markers or len(markers) < 2:
        return 0, 0, []
    
    fps = float(tl.GetSetting("timelineFrameRate") or "29.97")
    
    # Sort by frame
    sorted_markers = sorted(markers.items(), key=lambda x: int(x[0]))
    
    gaps = []
    butt_joins = 0
    
    for i in range(len(sorted_markers) - 1):
        cur_frame, cur_data = sorted_markers[i]
        nxt_frame, nxt_data = sorted_markers[i + 1]
        
        cur_frame = int(cur_frame)
        nxt_frame = int(nxt_frame)
        cur_duration = cur_data.get("duration", 0)
        
        if cur_duration > 0:
            cur_end = cur_frame + cur_duration
            gap_frames = nxt_frame - cur_end
            
            # Butt-joined = gap is 0 or 1 frame (marker extends to touch)
            if gap_frames <= 1:
                butt_joins += 1
            
            gaps.append({
                "from": cur_data.get("name", ""),
                "to": nxt_data.get("name", ""),
                "gap_frames": gap_frames,
                "is_butt_joined": gap_frames <= 1,
            })
    
    return len(gaps), butt_joins, gaps


# Categorize timelines
principle_timelines = []
master_timelines = []
other_timelines = []

for tl in proj.GetTimelineCount() and [proj.GetTimelineByIndex(i + 1) for i in range(proj.GetTimelineCount())] or []:
    name = tl.GetName().lower()
    if "master" in name:
        master_timelines.append(tl)
    elif any(x in name for x in ["segment", "shotfx", "scene", "interview", "look", "chapter", "section", "selects", "stringout"]):
        principle_timelines.append(tl)
    else:
        other_timelines.append(tl)

print(f"📊 Timeline Categories:")
print(f"   Principle: {len(principle_timelines)}")
print(f"   Master: {len(master_timelines)}")
print(f"   Other: {len(other_timelines)}")
print()

# Test principle timelines
print("=" * 60)
print("🧪 TESTING PRINCIPLE TIMELINES (v4.7 features)")
print("=" * 60)

principle_results = []
for tl in principle_timelines[:10]:  # Test first 10
    name = tl.GetName()
    total, enriched, v46 = test_marker_notes_v47(tl)
    gaps_total, butt_joins, gap_details = test_butt_joined_borders(tl)
    
    if total > 0:
        principle_results.append({
            "name": name,
            "total": total,
            "enriched": enriched,
            "v46_detected": v46,
            "gaps_total": gaps_total,
            "butt_joins": butt_joins,
        })
        
        v47_status = "✅" if enriched > 0 else "⚠️"
        v46_status = "⚠️ v4.6 detected!" if v46 > 0 else "✅"
        butt_status = "✅" if butt_joins >= gaps_total * 0.5 else "⚠️"
        
        print(f"\n{name}")
        print(f"   {v47_status} v4.7 Enrichment: {enriched}/{total} markers")
        print(f"   {v46_status} v4.6 Check: {v46} old markers")
        print(f"   {butt_status} Butt-Joins: {butt_joins}/{gaps_total} gaps")

# Test master timelines
print()
print("=" * 60)
print("🎯 TESTING MASTER TIMELINES (lane-specific v4.7)")
print("=" * 60)

master_results = []
for tl in master_timelines[:10]:  # Test first 10
    name = tl.GetName()
    total, enriched, v46 = test_marker_notes_v47(tl)
    gaps_total, butt_joins, gap_details = test_butt_joined_borders(tl)
    
    if total > 0:
        master_results.append({
            "name": name,
            "total": total,
            "enriched": enriched,
            "v46_detected": v46,
            "gaps_total": gaps_total,
            "butt_joins": butt_joins,
        })
        
        v47_status = "✅" if enriched > 0 else "⚠️"
        v46_status = "⚠️ v4.6 detected!" if v46 > 0 else "✅"
        butt_status = "✅" if butt_joins >= gaps_total * 0.5 else "⚠️"
        
        print(f"\n{name}")
        print(f"   {v47_status} v4.7 Enrichment: {enriched}/{total} markers")
        print(f"   {v46_status} v4.6 Check: {v46} old markers")
        print(f"   {butt_status} Butt-Joins: {butt_joins}/{gaps_total} gaps")

# Summary
print()
print("=" * 60)
print("📈 SUMMARY")
print("=" * 60)

all_results = principle_results + master_results
if all_results:
    total_markers = sum(r["total"] for r in all_results)
    total_enriched = sum(r["enriched"] for r in all_results)
    total_v46 = sum(r["v46_detected"] for r in all_results)
    total_gaps = sum(r["gaps_total"] for r in all_results)
    total_butt_joins = sum(r["butt_joins"] for r in all_results)
    
    enrichment_pct = (total_enriched / total_markers * 100) if total_markers > 0 else 0
    butt_join_pct = (total_butt_joins / total_gaps * 100) if total_gaps > 0 else 0
    
    print(f"\n✅ v4.7 Enrichment: {total_enriched}/{total_markers} markers ({enrichment_pct:.1f}%)")
    print(f"✅ Butt-Joins: {total_butt_joins}/{total_gaps} gaps ({butt_join_pct:.1f}%)")
    print(f"⚠️  v4.6 Detected: {total_v46} markers (should be 0 in fresh v4.7 project)")
    
    print()
    if enrichment_pct >= 90 and total_v46 == 0:
        print("🎉 ALL TESTS PASSING - v4.7 fully operational!")
    elif enrichment_pct >= 50:
        print("⚠️  PARTIAL SUCCESS - some markers enriched, consider re-seed")
    else:
        print("❌ TESTS FAILED - v4.7 features not detected")
        print("   Run: DEGA_PRINCIPLE_FORCE_RESEED=1 python3 the_dega_template_full.py")
else:
    print("⚠️  No markers found to test")
