#!/usr/bin/env python3
"""
Force Re-apply v4.6 Marker Enhancements
- Re-seeds principle markers with cut-note enrichment
- Applies tight borders (1-frame gaps)
- Only updates principle timelines (not masters)
"""

import sys
import os


def get_resolve():
    """Connect to Resolve API"""
    bmd = globals().get("bmd")
    if bmd:
        try:
            r = bmd.scriptapp("Resolve")
            if r:
                return r
        except Exception:
            pass

    try:
        import DaVinciResolveScript as dvr

        r = dvr.scriptapp("Resolve")
        if r:
            return r
    except Exception:
        pass

    print("❌ Could not acquire Resolve API.")
    sys.exit(1)


def main():
    print("=" * 80)
    print("🔄 FORCE RE-APPLY v4.6 MARKER ENHANCEMENTS")
    print("=" * 80)
    print()

    # Check if deployed script exists
    deployed_script = os.path.expanduser(
        "~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility/the_dega_template_full.py"
    )

    if not os.path.exists(deployed_script):
        print("❌ Deployed script not found at:")
        print(f"   {deployed_script}")
        print()
        print("💡 Run: ./deploy.sh")
        sys.exit(1)

    print("✅ Found deployed script")

    # Check version
    with open(deployed_script, "r", encoding="utf-8") as f:
        first_lines = [f.readline() for _ in range(10)]
        version_line = [l for l in first_lines if "v4." in l and "DEGA" in l]
        if version_line:
            print(f"   Version: {version_line[0].strip()}")

    print()
    print("⚠️  IMPORTANT:")
    print("   This will re-seed principle markers with v4.6 enrichment.")
    print("   Existing markers on principle timelines will be updated.")
    print()
    print("🚀 To apply v4.6 features:")
    print()
    print("   1. In DaVinci Resolve, go to:")
    print("      Workspace ▸ Scripts ▸ Utility ▸ the_dega_template_full")
    print()
    print("   2. Before running, set this environment variable:")
    print("      export DEGA_PRINCIPLE_FORCE_RESEED=1")
    print()
    print("   3. Or run from terminal with:")
    print()
    print('      DEGA_PRINCIPLE_FORCE_RESEED=1 open -a "DaVinci Resolve"')
    print()
    print("   4. Then run the script from Resolve's menu")
    print()
    print("=" * 80)
    print()
    print("💡 After running, use test_v4_6_markers.py to verify enrichment")
    print()


if __name__ == "__main__":
    main()
