#!/usr/bin/env python3
"""
Audit principle markers across all timelines.
Quick sanity check to verify marker counts and names.
"""

import DaVinciResolveScript as dvr


def audit_principle_markers():
    """Fast audit to sanity-check markers in 3 seconds."""
    resolve = dvr.scriptapp("Resolve")
    pm = resolve.GetProjectManager()
    proj = pm.GetCurrentProject()

    if not proj:
        print("❌ No project open")
        return

    print(f"📊 PRINCIPLE MARKERS AUDIT")
    print(f"Project: {proj.GetName()}\n")
    print(f"{'Timeline':<50} | Total | Purple | Pink | Yellow | Blue | Green")
    print("=" * 100)

    expected_names = {
        "PRINCIPLES — Scenes/Segments",
        "PRINCIPLES — ShotFX",
        "PRINCIPLES — Talking Head",
        "PRINCIPLES — Fashion",
        "PRINCIPLES — Day in the Life",
        "PRINCIPLES — Cook-Ups",
        "Micro-jolt cadence",
        "Loop seam awareness",
        "Mask edge awareness",
        "Look exploration",
        "Motion beauty",
        "Thumbnail candidates",
        "B-roll window",
        "Pacing & captions",
        "Atmos pass",
        "Transition moment",
        "Cycle closure",
        "Arrangement choice",
        "UI / sound insert",
        "Vibe spike",
        "⏱ 5min anchor",
    }

    principle_timelines = []

    for i in range(1, int(proj.GetTimelineCount()) + 1):
        tl = proj.GetTimelineByIndex(i)
        if not tl:
            continue

        name = tl.GetName()

        # Skip masters and utility timelines
        if "Master" in name or "Selects" in name or "SYNC MAP" in name:
            continue

        # Check for principle timelines
        name_lower = name.lower()
        is_principle = any(
            x in name_lower
            for x in ["segment", "shotfx", "interview", "look", "chapter", "section"]
        )

        if not is_principle:
            continue

        markers = tl.GetMarkers() or {}
        total = len(markers)

        # Count by color
        color_counts = {"Purple": 0, "Pink": 0, "Yellow": 0, "Blue": 0, "Green": 0}
        principle_count = 0

        for frame, data in markers.items():
            color = data.get("color", "")
            marker_name = data.get("name", "")

            if color in color_counts:
                color_counts[color] += 1

            if marker_name in expected_names:
                principle_count += 1

        principle_timelines.append(
            {
                "name": name,
                "total": total,
                "colors": color_counts,
                "principle_count": principle_count,
            }
        )

        # Status indicator
        status = "✅" if principle_count >= 4 else "⚠️" if principle_count > 0 else "❌"

        # Truncate name if too long
        display_name = name[:47] + "..." if len(name) > 50 else name

        print(
            f"{status} {display_name:<50} | {total:5} | "
            f"{color_counts['Purple']:6} | {color_counts['Pink']:4} | "
            f"{color_counts['Yellow']:6} | {color_counts['Blue']:4} | {color_counts['Green']:5}"
        )

    print("=" * 100)
    print(f"\n📈 Summary:")
    print(f"  Principle timelines found: {len(principle_timelines)}")

    with_markers = sum(1 for tl in principle_timelines if tl["total"] > 0)
    with_principles = sum(1 for tl in principle_timelines if tl["principle_count"] >= 4)

    print(f"  With markers: {with_markers}/{len(principle_timelines)}")
    print(f"  With principle markers: {with_principles}/{len(principle_timelines)}")

    if with_principles == len(principle_timelines):
        print("\n🎉 All principle timelines have markers!")
    else:
        missing = len(principle_timelines) - with_principles
        print(f"\n⚠️  {missing} timeline(s) missing principle markers")


if __name__ == "__main__":
    audit_principle_markers()
