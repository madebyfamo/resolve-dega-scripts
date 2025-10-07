# DEGA Principle Markers - Quick Reference

## ✅ STATUS: FULLY OPERATIONAL

All 27 principle timelines have correct markers as of 2025-10-06.

## 🔑 The Golden Key

**DaVinci Resolve 20.2+ requires marker duration ≥ 1 frame.**  
Duration=0 causes `AddMarker()` to silently return `False`.

## 🚀 Quick Commands

### Run Main Builder
```bash
cd "$HOME/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility"
python3 dega_formula_builder_enhanced.py
```

### Force Re-seed Markers (override existing)
```bash
DEGA_PRINCIPLE_FORCE_RESEED=1 python3 dega_formula_builder_enhanced.py
```

### Audit Markers (3-second sanity check)
```bash
python3 dega_audit_markers.py
```

### Fix Individual Timeline
```bash
python3 dega_fix_segment_markers.py
```

### Verify Specific Timelines
```bash
python3 verify_markers.py
```

## 📊 Expected Marker Counts

| Timeline Type | Marker Count | Spacing |
|--------------|-------------|---------|
| Segment      | 4           | 0s, 1s, 2s, 299s |
| ShotFX       | 4           | 0s, 1s, 2s, 299s |
| Interview    | 4           | 0s, 1s, 2s, 299s |
| LOOK         | 4           | 0s, 1s, 2s, 299s |
| Chapter      | 5           | 0s, 1s, 2s, 3s, 299s |
| Section      | 5           | 0s, 1s, 2s, 3s, 299s |

## 🎨 Color Scheme

- **Purple**: Primary PRINCIPLES marker (0s)
- **Pink**: Secondary principle (1s)
- **Yellow**: Tertiary principle (2s)
- **Blue**: Anchors and utility markers
- **Green**: Closure/completion markers (3s when present)

## 🛡️ Core Safeguards

```python
def ensure_min_duration(dur_frames):
    """Guard for Resolve 20.2+ which requires duration >= 1 frame."""
    return max(1, int(dur_frames or 1))
```

This function is now called in `_add_marker_safe()` to prevent duration=0 bugs.

## 🧪 Regression Test (30 seconds)

1. Run audit: `python3 dega_audit_markers.py`
2. Verify: All principle timelines show 4-5 markers
3. Test idempotency: `DEGA_PRINCIPLE_FORCE_RESEED=1 python3 dega_formula_builder_enhanced.py`
4. Re-audit: Counts should remain identical ✅

## 📁 Project Structure

```
Utility/
├── dega_formula_builder_enhanced.py  # Main builder
├── dega_audit_markers.py             # Fast audit tool
├── dega_fix_segment_markers.py       # Individual timeline fixer
├── verify_markers.py                 # Detailed verification
├── PRINCIPLE_MARKERS_FIX.md          # Complete analysis
└── PRINCIPLE_MARKERS_QUICK_REF.md    # This file
```

## 🎯 Anchors (Fixed/Adjustable/Flexible)

### FIXED 🔒
- All markers MUST have `dur_frames >= 1`
- Canonical marker names per content type
- 299s anchor as standard duration marker
- Color scheme remains consistent

### ADJUSTABLE 🎚️
- Anchor timing (299s default, parameterizable)
- Timeline regex filters (which timelines get seeded)
- Force re-seed behavior (env var toggle)

### FLEXIBLE 🌊
- Additional "guide" markers for experiments
- Silent clip fallback (optional, not needed after duration fix)
- Custom marker notes and metadata

## 🔍 Troubleshooting

### Markers not appearing?
1. Check duration: `dur_frames >= 1` ✅
2. Verify timeline name matches pattern (use audit tool)
3. Check force re-seed flag if markers should exist
4. Review logs in `logs/` directory

### Wrong marker names?
1. Run fix script: `python3 dega_fix_segment_markers.py`
2. Or force re-seed: `DEGA_PRINCIPLE_FORCE_RESEED=1 python3 dega_formula_builder_enhanced.py`

### Need to verify quickly?
```bash
python3 dega_audit_markers.py | grep "🎉\|⚠️\|❌"
```

## 📝 Version History

- **v4.5** (2025-10-06): Fixed duration bug, added audit tools, 27/27 timelines ✅
- **v4.3**: Added principle marker framework
- **v4.0**: Initial vertical timeline builder

## 🎉 Success Criteria

- ✅ All 27 principle timelines have markers
- ✅ Master timelines unchanged (4-7 markers each)
- ✅ Audit shows 100% compliance
- ✅ Idempotent: re-running doesn't duplicate
- ✅ Future-proof: `ensure_min_duration()` prevents regression

---

**Last Updated**: 2025-10-06  
**Status**: Production Ready 🚀  
**Confidence**: 100% 🔥
