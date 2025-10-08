# DEGA Formula Builder - Principle Markers Fix

## Problem Summary
Principle markers were not appearing on non-master timelines (Segment, ShotFX, Interview, LOOK, Chapter, Section).

## Root Causes Identified

### 1. Title Matching Too Strict (FIXED)
**Issue**: The `get_principle_markers_for_title()` function used `startswith()` which required exact prefix matches and didn't handle dash variations.

**Solution**: Changed to `contains` matching with dash normalization:
```python
def get_principle_markers_for_title(title):
    t = (title or "").lower().replace("—", "-").replace("–", "-")
    # Use "in" instead of "startswith()"
    if "segment" in t:
        return PRINCIPLE_PACKS["scenes_segments"]
    # ... etc
```

### 2. Marker Duration Must Be ≥ 1 Frame (CRITICAL FIX) ⭐
**Issue**: DaVinci Resolve 20.2's `AddMarker()` API **silently fails** when duration=0.

**Discovery**: Through systematic testing, found that:
- `AddMarker(frame, color, name, note, 0)` → Returns `False`, marker not added
- `AddMarker(frame, color, name, note, 1)` → Returns `True`, marker added successfully

**Solution**: Ensure all markers have minimum 1-frame duration:
```python
dur = _sec_to_frames(m.get("dur", 0.0), fps_float)
# CRITICAL: Resolve 20.2 requires duration >= 1, cannot be 0
if dur < 1:
    dur = 1
```

### 3. Silent Clip Fallback (Added but Not Needed)
**Implementation**: Added helper functions to append silent audio clips to empty timelines.

**Result**: This wasn't actually necessary once the duration fix was applied. The issue was never about empty timelines - it was about zero-duration markers.

## Testing Results

### Before Fix
```
❌ ALL AddMarker attempts failed for: PRINCIPLES — Scenes/Segments @ frame 0
❌ ALL AddMarker attempts failed for: Micro-jolt cadence @ frame 30
❌ ALL AddMarker attempts failed for: Loop seam awareness @ frame 60
❌ ALL AddMarker attempts failed for: ⏱ 5min anchor @ frame 8961
```

### After Fix
```
✅ ShotFX timeline: 4 markers (0s, 1s, 2s, 299s)
✅ LOOK timeline: 4 markers (0s, 1s, 2s, 299s)
✅ Interview timeline: 4 markers (0s, 1s, 2s, 299s)
✅ Chapter timeline: 5 markers (0s, 1s, 2s, 3s, 299s)
✅ Section timeline: 5 markers (0s, 1s, 2s, 3s, 299s)
```

## Key Learnings

1. **API Documentation Gap**: The Resolve API doesn't clearly document that duration=0 fails
2. **Silent Failures**: `AddMarker()` returns `False` instead of raising exceptions
3. **Master Timelines**: Existing master timelines had markers because they were created before this issue or had different marker data
4. **Parameter Order**: The `_mp()` helper had a dur/notes swap bug that was also fixed during investigation

## Files Modified

- `the_dega_template_full.py`:
  - Added `import wave, struct` for silent clip generation
  - Fixed `get_principle_markers_for_title()` matcher
  - Added minimum duration check in `add_markers_to_timeline_if_empty()`
  - Added `_ensure_silence_asset()` helper (optional fallback)
  - Added `ensure_timeline_nonempty_with_silence()` helper (optional fallback)
  - Added `seed_principle_markers_across_project()` function
  - Added force parameter to `add_markers_to_timeline_if_empty()`
  - Call `seed_principle_markers_across_project()` at end of main()

## Usage

Run the script normally:
```bash
python3 dega_formula_builder_enhanced.py
```

To force re-seed markers on timelines that already have markers:
```bash
DEGA_PRINCIPLE_FORCE_RESEED=1 python3 the_dega_template_full.py
```

## Verification

Check markers on principle timelines:
```bash
python3 verify_markers.py
```

Expected output:
- Segment timelines: 4 markers
- ShotFX timelines: 4 markers
- Interview timelines: 4 markers
- LOOK timelines: 4 markers
- Chapter timelines: 5 markers
- Section timelines: 5 markers
- Master timelines: Unchanged (4-7 markers depending on tier)

## Status

✅ **FIXED** - All principle markers now successfully added to matching timelines.
