#!/usr/bin/env python3
"""
Debug script to inspect actual marker content
"""

import sys


def get_resolve():
    bmd = globals().get("bmd")
    if bmd:
        try:
            return bmd.scriptapp("Resolve")
        except:
            pass
    try:
        import DaVinciResolveScript as dvr

        return dvr.scriptapp("Resolve")
    except:
        pass
    print("❌ Could not connect to Resolve")
    sys.exit(1)


def main():
    resolve = get_resolve()
    pm = resolve.GetProjectManager()
    proj = pm.GetCurrentProject()

    print(f"📊 Project: {proj.GetName()}\n")

    # Find a segment timeline
    for i in range(1, int(proj.GetTimelineCount()) + 1):
        tl = proj.GetTimelineByIndex(i)
        if not tl:
            continue

        name = tl.GetName() or ""
        if "Segment —" in name:
            print(f"🎬 Timeline: {name}")
            markers = tl.GetMarkers()

            if not markers:
                print("   ⚠️  No markers found\n")
                continue

            print(f"   📍 Found {len(markers)} markers:\n")

            for frame, data in sorted(markers.items()):
                print(f"   Frame {frame}:")
                print(f"      Name:  {data.get('name', 'N/A')}")
                print(f"      Color: {data.get('color', 'N/A')}")
                print(f"      Duration: {data.get('duration', 'N/A')}")
                note = data.get("note", "") or ""
                if note:
                    print(f"      Note ({len(note)} chars):")
                    # Show first 300 chars
                    preview = note[:300] if len(note) > 300 else note
                    print(f"      {repr(preview)}")
                    if len(note) > 300:
                        print(f"      ... ({len(note)-300} more chars)")
                else:
                    print(f"      Note:  (empty)")
                print()

            # Only check first matching timeline
            break

    print("=" * 80)


if __name__ == "__main__":
    main()
