# Principle Markers - Debugging Changes

## Date: October 6, 2025

## Issues Found & Fixed

### Issue 1: Script Was Opening Wrong Project ✅ FIXED
**Problem:** Script was loading "DEGA_VERT_2025_10_06" instead of using the currently open project.

**Solution:** Modified `main()` function to **use the currently open project** instead of creating/loading a specific project name.

**Before:**
```python
proj = pm.GetCurrentProject()
if proj and proj.GetName() in {PROJECT_NAME, PROJECT_NAME_FALLBACK}:
    log.info(f"✅ Using current project: {proj.GetName()}")
else:
    # Complex logic to load/create specific project
```

**After:**
```python
proj = pm.GetCurrentProject()
if not proj:
    log.error("❌ No project is currently open. Please open a project first.")
    return False

project_name = proj.GetName()
log.info(f"🎯 Project: {project_name}")
```

---

### Issue 2: Markers Detected but Not Added (0 added) 🔍 INVESTIGATING
**Problem:** Logs show "🏷️  Adding 3 principle markers" but "✅ Markers added: 0"

**Evidence from logs:**
```
🏷️  Adding 3 principle markers to: Segment — Hook Performance — ⏱ 29.97p • 📐 2160×3840
✅ Markers added: 0
```

**Diagnosis:** `_add_marker_safe()` is **silently failing** to add markers via `tl.AddMarker()`.

**Solution:** Added comprehensive debug logging to `_add_marker_safe()` to trace:
- 6-argument AddMarker attempts
- 5-argument AddMarker fallback attempts
- Color fallback attempts
- Exception details
- Exact failure points

**New Debug Output:** You should now see detailed logs like:
```
⚠️  AddMarker failed (6-arg): frame=0, color=Purple, name=PRINCIPLES — Scenes/Segments
✓ AddMarker succeeded with fallback color: Red
```
OR
```
❌ ALL AddMarker attempts failed for: PRINCIPLES — Scenes/Segments @ frame 0
```

---

## Next Steps

### Run the script again and look for these new log messages:

1. **Project handling:**
   - ✅ Should say "🎯 Project: [YOUR_PROJECT_NAME]" (not DEGA_VERT_2025_10_06)
   - ✅ Should work on whatever project you have open

2. **Marker addition failures:**
   - Look for "⚠️  AddMarker failed" messages
   - Look for "❌ ALL AddMarker attempts failed" warnings
   - These will tell us WHY the markers can't be added

### Possible Causes for Marker Failure:

1. **Timeline has zero duration** - Can't add markers to empty timelines
2. **Frame number out of range** - Frame 0 might not be valid on some timelines
3. **Color names not supported** - Purple, Pink, Yellow, Cyan might not work
4. **API signature changed** - Resolve 20.2 might need different parameters
5. **Permissions issue** - Timeline might be locked or in a weird state

---

## Test Results

### Detection Logic: ✅ WORKS PERFECTLY
```bash
$ python3 test_principle_markers.py
✅ Segment — Hook Performance → 3 markers
✅ ShotFX — Clone in Hallway → 3 markers
✅ Interview — Radio Cut + B-Roll → 3 markers
✅ LOOK — (Generic) → 3 markers
✅ Chapter — (Generic) → 4 markers
✅ Section — (Generic) → 4 markers
⚪️ MV Master → 0 markers (correctly skipped)
```

### Marker Data Structure: ✅ CORRECT
```python
{'t': 0.0, 'color': 'Purple', 'name': 'PRINCIPLES — Scenes/Segments',
 'dur': 0.0, 'notes': 'Research-backed principles...'}
```

---

## What to Share Next

Run the script in Resolve and share:
1. The full log output (especially the new debug messages)
2. What project you have open
3. Whether the timelines have any clips in them (or are they empty?)
4. The timeline duration (if empty, markers can't be added)

This will help us identify the exact reason `tl.AddMarker()` is returning `False`.
