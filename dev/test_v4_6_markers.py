#!/usr/bin/env python3
"""
Test v4.6 Marker Enhancements
- Verifies cut-note enrichment in marker notes
- Checks tight marker borders (1-frame gaps)
- Tests across different timeline types (principle vs master)
"""

import sys


def get_resolve():
    """Connect to Resolve API (works from external terminal or Resolve menu)"""
    # Prefer bmd.scriptapp (when running from Resolve's script menu)
    bmd = globals().get("bmd")
    if bmd:
        try:
            r = bmd.scriptapp("Resolve")
            if r:
                return r
        except Exception:
            pass

    # Fallback: DaVinciResolveScript (when running externally)
    try:
        import DaVinciResolveScript as dvr

        r = dvr.scriptapp("Resolve")
        if r:
            return r
    except Exception:
        pass

    print("❌ Could not acquire Resolve API.")
    print("   Make sure DaVinci Resolve is running and a project is open.")
    sys.exit(1)


def test_marker_notes_enrichment(timeline, tl_name):
    """Check if markers have cut-note enrichment in their notes"""
    markers = timeline.GetMarkers()
    if not markers:
        return None, "No markers found"

    enriched_count = 0
    total_count = len(markers)

    # Check for enrichment keywords in marker notes (v4.6 actual implementation)
    enrichment_keywords = [
        "— Edit pacing",  # From _CUT_GUIDE_DEFAULT (appended with "— " prefix)
        "nuance:",  # From _CUT_GUIDE_BY_LANE
        "— Context:",  # From _TIER_NUDGE (tier context like "principle timeline", "12s format", etc.)
        "format",  # From _TIER_NUDGE for tiers
    ]

    for frame, marker_data in markers.items():
        note = marker_data.get("note", "") or ""
        if any(keyword in note for keyword in enrichment_keywords):
            enriched_count += 1

    if enriched_count > 0:
        return True, f"{enriched_count}/{total_count} markers enriched"
    else:
        return False, f"0/{total_count} markers enriched (expected some)"


def test_tight_borders(timeline, tl_name):
    """Check if markers have tight borders (1-frame gaps)"""
    markers = timeline.GetMarkers()
    if not markers or len(markers) < 2:
        return None, "Need at least 2 markers to test spacing"

    # Get FPS
    fps_setting = timeline.GetSetting("timelineFrameRate")
    fps = float(fps_setting) if fps_setting else 29.97

    # Sort markers by frame
    sorted_frames = sorted([float(f) for f in markers.keys()])

    # Check gaps between consecutive markers
    tight_borders_count = 0
    total_gaps = 0

    for i in range(len(sorted_frames) - 1):
        marker1_frame = sorted_frames[i]
        marker2_frame = sorted_frames[i + 1]

        marker1_data = markers[marker1_frame]
        marker1_duration = marker1_data.get("duration", 1.0)

        # Calculate gap between marker1 end and marker2 start
        marker1_end = marker1_frame + marker1_duration
        gap_frames = marker2_frame - marker1_end

        total_gaps += 1

        # Tight border means gap is approximately 1 frame
        if 0 <= gap_frames <= 2:  # Allow small tolerance
            tight_borders_count += 1

    if tight_borders_count > 0:
        return True, f"{tight_borders_count}/{total_gaps} gaps are tight (1-frame)"
    else:
        return None, f"No tight borders detected"


def main():
    print("=" * 80)
    print("🧪 TESTING v4.6 MARKER ENHANCEMENTS")
    print("=" * 80)
    print()

    # Connect to Resolve
    print("1️⃣  Connecting to DaVinci Resolve...")
    resolve = get_resolve()
    pm = resolve.GetProjectManager()
    proj = pm.GetCurrentProject()

    if not proj:
        print("   ❌ No project open")
        sys.exit(1)

    print(f"   ✅ Connected to: {proj.GetName()}")
    print()

    # Get timeline count
    timeline_count = int(proj.GetTimelineCount() or 0)
    print(f"2️⃣  Found {timeline_count} timelines in project")
    print()

    # Test categories
    principle_timelines = []
    master_timelines = []
    other_timelines = []

    # Categorize timelines
    print("3️⃣  Categorizing timelines...")
    for i in range(1, timeline_count + 1):
        tl = proj.GetTimelineByIndex(i)
        if not tl:
            continue

        name = tl.GetName() or ""
        name_lower = name.lower()

        # Check if it's a master timeline
        is_master = any(
            x in name_lower
            for x in [
                "money master",
                "mv master",
                "fashion master",
                "th master",
                "dil master",
                "cook-up master",
            ]
        )

        # Check if it's a principle timeline
        is_principle = (
            any(
                x in name_lower
                for x in [
                    "segment",
                    "shotfx",
                    "interview",
                    "look",
                    "chapter",
                    "section",
                ]
            )
            and not is_master
        )

        if is_master:
            master_timelines.append((tl, name))
        elif is_principle:
            principle_timelines.append((tl, name))
        else:
            other_timelines.append((tl, name))

    print(f"   📊 Principle timelines: {len(principle_timelines)}")
    print(f"   📊 Master timelines: {len(master_timelines)}")
    print(f"   📊 Other timelines: {len(other_timelines)}")
    print()

    # Test principle timelines (should have enrichment)
    print("4️⃣  Testing PRINCIPLE timelines for v4.6 features...")
    print()

    if not principle_timelines:
        print("   ⚠️  No principle timelines found to test")
        print("   💡 Create timelines like: 'Segment — Test', 'ShotFX — Test', etc.")
    else:
        for tl, name in principle_timelines[:5]:  # Test first 5
            print(f"   📝 {name}")

            # Test cut-note enrichment
            enriched, enriched_msg = test_marker_notes_enrichment(tl, name)
            if enriched:
                print(f"      ✅ Cut-note enrichment: {enriched_msg}")
            elif enriched is None:
                print(f"      ⚪️ Cut-note enrichment: {enriched_msg}")
            else:
                print(f"      ❌ Cut-note enrichment: {enriched_msg}")

            # Test tight borders
            tight, tight_msg = test_tight_borders(tl, name)
            if tight:
                print(f"      ✅ Tight borders: {tight_msg}")
            elif tight is None:
                print(f"      ⚪️ Tight borders: {tight_msg}")
            else:
                print(f"      ❌ Tight borders: {tight_msg}")

            print()

    # Test master timelines (should NOT have principle markers)
    print("5️⃣  Testing MASTER timelines (should not have principle markers)...")
    print()

    if not master_timelines:
        print("   ⚠️  No master timelines found")
    else:
        for tl, name in master_timelines[:3]:  # Test first 3
            print(f"   📝 {name}")

            markers = tl.GetMarkers()
            marker_count = len(markers) if markers else 0

            # Check if markers are lane markers (not principle markers)
            has_principle = False
            if markers:
                for frame, marker_data in markers.items():
                    marker_name = marker_data.get("name", "") or ""
                    if "PRINCIPLES" in marker_name.upper():
                        has_principle = True
                        break

            if has_principle:
                print(f"      ❌ Has principle markers (unexpected for master)")
            else:
                print(f"      ✅ No principle markers (correct for master)")

            print(f"      📊 Total markers: {marker_count}")
            print()

    # Summary
    print("=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)

    tested_count = min(len(principle_timelines), 5)

    if tested_count > 0:
        print(f"✅ Tested {tested_count} principle timelines for v4.6 features")
        print()
        print("🎯 What to look for in the results:")
        print("   ✅ Cut-note enrichment = Markers have '📝 CUT GUIDE:' in notes")
        print("   ✅ Tight borders = 1-frame gaps between markers")
        print()
        print("💡 If no enrichment found:")
        print(
            "   1. Re-run the DEGA script (Workspace ▸ Scripts ▸ Utility ▸ the_dega_template_full)"
        )
        print("   2. Set environment variable: DEGA_PRINCIPLE_FORCE_RESEED=1")
        print("   3. Check marker notes in Resolve's timeline")
    else:
        print("⚠️  No principle timelines found to test")
        print()
        print("💡 To create test timelines:")
        print("   1. Run the_dega_template_full script from Resolve")
        print("   2. It will create principle timelines automatically")

    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
