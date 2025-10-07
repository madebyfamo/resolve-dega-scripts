#!/usr/bin/env python3
"""
COMPREHENSIVE TEST SUMMARY
Run this to verify all aspects of the principle markers fix
"""

import sys
import os

# Add parent dir to path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

print("=" * 80)
print("🧪 COMPREHENSIVE PRINCIPLE MARKERS TEST")
print("=" * 80)
print()

# Test 1: Verify imports and connections
print("1️⃣  Testing DaVinci Resolve connection...")
try:
    import DaVinciResolveScript as dvr

    resolve = dvr.scriptapp("Resolve")
    if not resolve:
        print("   ❌ Cannot connect to DaVinci Resolve")
        sys.exit(1)
    pm = resolve.GetProjectManager()
    proj = pm.GetCurrentProject()
    if not proj:
        print("   ❌ No project open")
        sys.exit(1)
    print(f"   ✅ Connected to project: {proj.GetName()}")
except Exception as e:
    print(f"   ❌ Connection failed: {e}")
    sys.exit(1)

# Test 2: Verify ensure_min_duration guard exists
print("\n2️⃣  Checking ensure_min_duration() guard...")
content = None
has_guard = False
guard_called = False
try:
    with open("dega_formula_builder_enhanced.py", "r", encoding="utf-8") as f:
        content = f.read()
        if "def ensure_min_duration(dur_frames):" in content:
            print("   ✅ ensure_min_duration() function found")
            has_guard = True
            if "dur_frames = ensure_min_duration(dur_frames)" in content:
                print("   ✅ Guard is called in _add_marker_safe()")
                guard_called = True
            else:
                print("   ⚠️  Guard not called in _add_marker_safe()")
        else:
            print("   ❌ ensure_min_duration() function NOT FOUND")
except Exception as e:
    print(f"   ❌ File check failed: {e}")

# Test 3: Check title matcher flexibility
print("\n3️⃣  Checking title matcher flexibility...")
has_flexible_match = False
try:
    if content and 'if ("shotfx" in t) or ("shot fx" in t):' in content:
        print("   ✅ Flexible 'contains' matching implemented")
        has_flexible_match = True
    elif content and 'if t.startswith("shotfx -"):' in content:
        print("   ⚠️  Still using strict 'startswith' matching")
    else:
        print("   ⚠️  Matching pattern unclear")
except:
    print("   ⚠️  Could not verify")

# Test 4: Count principle timelines
print("\n4️⃣  Counting principle timelines...")
cnt = int(proj.GetTimelineCount() or 0)
principle_count = 0
master_count = 0

for i in range(1, cnt + 1):
    tl = proj.GetTimelineByIndex(i)
    if not tl:
        continue
    title = (tl.GetName() or "").lower()

    if " money master" in title or title.startswith("money master"):
        master_count += 1
    elif any(
        x in title
        for x in ["segment", "shotfx", "shot fx", "interview", "look", "chapter", "section"]
    ):
        principle_count += 1

print(f"   ✅ Found {principle_count} principle timelines")
print(f"   ✅ Found {master_count} master timelines")

# Test 5: Verify marker counts
print("\n5️⃣  Verifying marker counts...")
principle_with_markers = 0
principle_without_markers = 0

for i in range(1, cnt + 1):
    tl = proj.GetTimelineByIndex(i)
    if not tl:
        continue
    title = (tl.GetName() or "").lower()

    if " money master" in title or title.startswith("money master"):
        continue

    if any(
        x in title
        for x in ["segment", "shotfx", "shot fx", "interview", "look", "chapter", "section"]
    ):
        markers = tl.GetMarkers() or {}
        if len(markers) >= 4:
            principle_with_markers += 1
        else:
            principle_without_markers += 1

print(f"   ✅ {principle_with_markers} principle timelines have markers (4+)")
if principle_without_markers > 0:
    print(f"   ⚠️  {principle_without_markers} principle timelines missing markers")
else:
    print(f"   ✅ All principle timelines have markers")

# Test 6: Verify marker spacing
print("\n6️⃣  Checking marker spacing on sample timeline...")
found_sample = False
for i in range(1, min(cnt + 1, 10)):
    tl = proj.GetTimelineByIndex(i)
    if not tl:
        continue
    title = tl.GetName() or ""
    title_lower = title.lower()

    if "segment" in title_lower and "money master" not in title_lower:
        markers = tl.GetMarkers() or {}
        fps_obj = tl.GetSetting("timelineFrameRate")
        fps = float(fps_obj or 29.97)

        # Check for markers at 0s, 1s, 2s
        expected_frames = [0, int(fps), int(fps * 2)]
        found_frames = [int(f) for f in markers.keys()]

        found_at_start = any(f <= 1 for f in found_frames)
        found_at_1s = any(abs(f - fps) <= 2 for f in found_frames)
        found_at_2s = any(abs(f - fps * 2) <= 2 for f in found_frames)

        if found_at_start and found_at_1s and found_at_2s:
            print(f"   ✅ Sample timeline '{title[:40]}...' has proper spacing")
            found_sample = True
            break

if not found_sample:
    print("   ⚠️  Could not verify spacing on sample timeline")

# Test 7: Check for anchor marker (299s)
print("\n7️⃣  Checking for 299s anchor markers...")
found_anchor = False
for i in range(1, min(cnt + 1, 10)):
    tl = proj.GetTimelineByIndex(i)
    if not tl:
        continue
    title = tl.GetName() or ""
    title_lower = title.lower()

    if (
        any(x in title_lower for x in ["segment", "shotfx", "chapter"])
        and "money master" not in title_lower
    ):
        markers = tl.GetMarkers() or {}
        fps_obj = tl.GetSetting("timelineFrameRate")
        fps = float(fps_obj or 29.97)

        # Check for marker near 299s
        anchor_frame = int(fps * 299)
        found_frames = [int(f) for f in markers.keys()]

        if any(abs(f - anchor_frame) <= 10 for f in found_frames):
            print(f"   ✅ Found 299s anchor marker in '{title[:40]}...'")
            found_anchor = True
            break

if not found_anchor:
    print("   ⚠️  Could not find 299s anchor marker in sample timelines")

# Final Summary
print("\n" + "=" * 80)
print("📊 FINAL TEST SUMMARY")
print("=" * 80)

total_tests = 7
passed_tests = 0

if resolve and proj:
    passed_tests += 1
if has_guard:
    passed_tests += 1
if has_flexible_match:
    passed_tests += 1
if principle_count > 0:
    passed_tests += 1
if principle_without_markers == 0:
    passed_tests += 1
if found_sample:
    passed_tests += 1
if found_anchor:
    passed_tests += 1

print(f"\n✅ Tests Passed: {passed_tests}/{total_tests}")
print(f"📈 Success Rate: {passed_tests/total_tests*100:.0f}%")

if passed_tests == total_tests:
    print("\n🎉 ALL TESTS PASSED! System is fully operational.")
elif passed_tests >= 5:
    print("\n✅ Core functionality verified. Minor issues may exist.")
else:
    print("\n⚠️  Some critical tests failed. Review needed.")

print("\n" + "=" * 80)
