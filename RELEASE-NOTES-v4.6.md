# DEGA Formula Builder v4.6 — Release Notes

**Date:** October 8, 2025
**Focus:** Cut-Note Enrichment & Tight Marker Borders

---

## 🎯 Overview

Version 4.6 adds **lane-specific edit pacing guidance** and **tight marker borders** to every timeline marker across the entire DEGA system. This enhancement provides editors with actionable shot duration ranges and cutting strategies directly in marker notes, while creating gapless color bands for better visual organization.

---

## ✨ What's New

### 1. **Cut-Note Enrichment** 🏷️

Every marker now includes automatically appended edit pacing notes with:

- **Role-specific guidance** (HOOK, DRAW, COMMIT/PAYOFF, etc.)
  - Average shot durations (e.g., "0.6–1.0s")
  - Cutting strategies and timing ranges

- **Lane-specific nuances** layered on top:
  - **Money:** Plain copy, receipt cuts (0.6–0.9s)
  - **MV:** Front-load visuals, rhythm sync
  - **Fashion:** Silhouette reads, pose holds
  - **Talking Head:** Punch lines, B-roll overlays
  - **DIL:** Mid-action entries, micro-arcs
  - **Cook-Ups:** Identity sound first, beat grid alignment

- **Tier/context nudges:**
  - **12s:** Bias toward SHORT end (snappier)
  - **22s:** Mid-range, one earned hold OK
  - **30s:** Include longer payoff (2.0–2.4s)
  - **principle:** Favor clarity over speed if technique needs readability
  - **selects:** Faster trims (0.5–1.0s) for auditioning

### 2. **Tight Marker Borders** 📐

Markers now end **1 frame before the next marker** by default:
- Creates gapless color bands on the timeline ruler
- Provides clearer visual separation between sections
- **Default:** ON (enabled)
- **Disable:** Set environment variable `DEGA_MARKER_TIGHT_BORDERS=0`

### 3. **Universal Application** 🌐

Both features are applied to **ALL timeline types:**
- ✅ Money Masters (12s, 22s, 30s)
- ✅ All pillar Master Builds (MV, Fashion, TH, DIL, Cook-Ups)
- ✅ Principle timelines (Scenes/Segments, ShotFX, Interview, LOOK, Chapter, Section)
- ✅ Selects & Stringouts (with context-specific guidance)
- ✅ Project-wide reseed function

---

## 🔧 Implementation Details

### New Functions

```python
# Edit pacing guidance structures
_CUT_GUIDE_DEFAULT        # Role-specific default timing ranges
_CUT_GUIDE_BY_LANE        # Lane-specific nuances (money, mv, fashion, etc.)
_TIER_NUDGE               # Tier/context-specific guidance

# Helper functions
_role_normalize()         # Normalize marker role names to canonical forms
_append_cut_note()        # Append lane/tier pacing notes to marker
_enrich_markers_with_cut_notes()  # Enrich all markers in a list
_infer_lane_from_pillar_or_title()  # Detect lane from pillar/timeline name

# Border tightening
_tighten_marker_borders_if_enabled()  # Apply 1-frame gaps (default ON)
```

### Updated Workflows

1. **Money Masters:** Loop enriches & tightens before applying
2. **Pillar loop:** Standard timelines get enriched with lane-aware guidance
3. **Master Build:** Tiered masters enriched per-lane with tier nudges
4. **Project reseed:** Infers lane, enriches, and tightens automatically

---

## 📝 Example: Before & After

### Before (v4.5)
```
Marker: "HOOK"
Note: "Range 0–3s. Lead with the clearest value: a visual or line..."
```

### After (v4.6)
```
Marker: "HOOK"
Note: "Range 0–3s. Lead with the clearest value: a visual or line...
— Edit pacing: average shot 0.6–1.0s; avoid holds >1.3s unless a reveal lands.
— Money nuance: keep copy plain; 0.6–0.9s 'receipt' cut is ideal.
— Tier nudge: bias toward the SHORT end (snappier overall)."
```

**Result:** Editor now has precise guidance for shot timing within that marker range.

---

## 🎨 Visual Benefits

### Tight Borders
```
Before: [HOOK      ][DRAW      ][INTERRUPT]
After:  [HOOK][DRAW][INTERRUPT]  ← Gapless color bands
```

Provides clearer visual separation and professional timeline appearance.

---

## 🛠️ Configuration

### Environment Variables

```bash
# Disable tight borders (keep default Resolve spacing)
export DEGA_MARKER_TIGHT_BORDERS=0

# Force re-seed markers on existing timelines
export DEGA_PRINCIPLE_FORCE_RESEED=1
```

### Defaults
- Tight borders: **ON**
- Cut-note enrichment: **Always ON** (no toggle)
- Force reseed: **OFF** (set env var to enable)

---

## 🚀 Usage

No changes to workflow—all features are automatic:

```bash
# Standard usage (enrichment + tight borders applied automatically)
python3 the_dega_template_full.py

# Disable tight borders
DEGA_MARKER_TIGHT_BORDERS=0 python3 the_dega_template_full.py

# Force reseed existing markers with new enriched versions
DEGA_PRINCIPLE_FORCE_RESEED=1 python3 the_dega_template_full.py
```

---

## 🎓 Benefits for Editors

1. **Faster Decision Making**
   - Shot duration guidance right in marker notes
   - No need to reference external docs

2. **Lane-Aware Strategies**
   - Tailored advice per content type
   - Tier-specific pacing recommendations

3. **Better Visual Organization**
   - Gapless color bands for clearer section boundaries
   - Professional timeline appearance

4. **Consistent Standards**
   - Research-informed edit pacing across all timelines
   - Universal application ensures consistency

---

## 🔄 Backward Compatibility

- Existing timelines remain unchanged (markers only added if empty)
- Previous marker notes remain intact (new notes appended)
- All v4.5 features still included
- No breaking changes

---

## 📚 Technical Notes

### Marker Duration Calculation
```python
# Tight border: current marker ends 1 frame before next
cur_start = _sec_to_frames(cur["t"], fps)
nxt_start = _sec_to_frames(nxt["t"], fps)
tight = max(0, (nxt_start - cur_start) - 1)  # 1-frame visual seam
cur["dur"] = tight / fps
```

### Lane Inference Priority
```python
1. Pillar name check (e.g., "Music-Video" → "mv")
2. Title prefix check (e.g., "Segment —" → "mv")
3. Master title check (e.g., "MV Master" → "mv")
4. Default fallback: "money"
```

---

## 🐛 Known Issues

None at this time. Please report any issues via GitHub Issues.

---

## 🙏 Acknowledgments

- Enhanced cut-note guidance based on ChatGPT recommendations
- Tight border implementation inspired by professional editing workflows
- Context7 API documentation used for DaVinci Resolve marker validation

---

## 📦 Version History

- **v4.6** (Oct 2025): Cut-note enrichment + tight marker borders
- **v4.5** (Previous): Tiered marker templates (12s/22s/30s) across all lanes
- **v4.0** (Previous): Initial principle markers implementation

---

## 🔮 Future Enhancements

Potential additions for future versions:
- Timeline-specific marker sets for Selects/Stringouts (rate, alt take, B-roll candidate)
- Dynamic shot duration analysis based on timeline content
- Custom lane profiles for specialized workflows
- Integration with external editing analysis tools

---

**Questions?** Check the main README.md or open a GitHub Issue.
