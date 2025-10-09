# Cut-Note Enrichment Quick Reference

## Overview
Every marker in DEGA v4.6+ includes appended edit pacing guidance based on:
1. **Role** (HOOK, DRAW, COMMIT/PAYOFF, etc.)
2. **Lane** (money, mv, fashion, talking, dil, cook)
3. **Tier/Context** (12s, 22s, 30s, principle, selects)

---

## Default Role Guidance

| Role | Guidance |
|------|----------|
| **HOOK** | Average shot 0.6–1.0s; avoid holds >1.3s unless a reveal lands |
| **DRAW** | 0.8–1.5s per beat; each cut must add new info/contrast |
| **INTERRUPT** | ≤0.5–0.7s micro-jolt (whip/insert/flip) |
| **COMMIT / PAYOFF** | Let clarity breathe 1.2–2.2s; cut earlier if energy dips |
| **COMMIT / PAYOFF #1** | 1.0–1.8s; extend only for readability/proof |
| **SECOND HOOK** | 0.7–1.2s beats; sharper than first to recapture |
| **DEVELOP** | 1.0–1.8s/beat; 2–3 support beats max before moving on |
| **DEVELOP A** | ~1.3–1.9s/beat; escalate motion/variation every 2–3 cuts |
| **DEVELOP B** | ~1.0–1.6s/beat; quicker than A to build into close |
| **FINAL PAYOFF / LOOP** | 0.8–1.5s; favor clean loop seam or unmistakable CTA |
| **LOOP / CTA** | 0.5–1.2s; quick, readable, loop-friendly |

---

## Lane-Specific Nuances

### 💰 Money
- **HOOK:** Keep copy plain; 0.6–0.9s 'receipt' cut is ideal
- **COMMIT / PAYOFF:** Up to ~2.4s if proof needs a clean read

### 🎵 MV (Music-Video)
- **HOOK:** Front-load signature visual; 0.5–0.9s with rhythm accents
- **DRAW:** Lean on lyric/beat sync; stay <1.3s unless choreography sells
- **COMMIT / PAYOFF:** Musical phrase can justify 1.5–2.2s; add camera energy if longer

### 👗 Fashion
- **HOOK:** Silhouette read > flash; 0.8–1.4s pose can hold if clean
- **DRAW:** Detail inserts ~0.7–1.1s; avoid back-to-back similar textures
- **COMMIT / PAYOFF:** Full-body/transition may hold 1.6–2.4s if attitude carries

### 🗣️ Talking Head
- **HOOK:** Punch line then move; 0.7–1.2s with breath trims
- **DRAW:** B-roll overlays 0.8–1.3s; hide jump cuts
- **COMMIT / PAYOFF:** Let takeaway land ~1.4–2.2s if comprehension benefits
- **DEVELOP:** One tight example 1.0–1.6s; don't spiral

### 📸 DIL (Day in the Life)
- **HOOK:** Mid-action entry; 0.6–1.0s, keep momentum
- **DRAW:** Mini-arc beats 0.9–1.5s; vary textures (hands/ambient/motion)
- **COMMIT / PAYOFF:** Micro-resolution can hold 1.2–2.0s if it 'arrives'

### 🎹 Cook-Ups
- **HOOK:** Show identity sound first; 0.6–1.0s with visible action
- **DRAW:** Layer/constraint ~0.8–1.2s; keep UI readable
- **COMMIT / PAYOFF:** Let the 'lock' groove sit 1.5–2.4s if it slaps
- **DEVELOP:** Fills/mutes/knob rides 0.6–1.0s; align to beat grid
- **FINAL PAYOFF / LOOP:** Land on bar boundary; 1.0–1.6s if needed for loop

---

## Tier/Context Nudges

### Master Timelines

| Tier | Nudge |
|------|-------|
| **12s** | Bias toward SHORT end (snappier overall) |
| **22s** | Stay mid-range; one 1.6–2.0s hold is fine if it 'earns' it |
| **30s** | Include one longer 2.0–2.4s payoff; avoid back-to-back long holds |

### Principle Timelines
- Use ranges but favor **clarity over speed** if technique needs readability

### Selects/Stringouts
- Favor **faster trims** (0.5–1.0s) while reviewing
- Tag candidates then refine

---

## Usage Examples

### Example 1: Money Master 12s HOOK
```
Base Note: "Range 0–3s. Lead with clearest value..."
Enriched:
  "Range 0–3s. Lead with clearest value...
   — Edit pacing: average shot 0.6–1.0s; avoid holds >1.3s
   — Money nuance: keep copy plain; 0.6–0.9s 'receipt' cut
   — Tier nudge: bias toward SHORT end (snappier overall)"
```

### Example 2: MV Master 30s COMMIT/PAYOFF
```
Base Note: "Range 3–5s. Tight performance moment..."
Enriched:
  "Range 3–5s. Tight performance moment...
   — Edit pacing: let clarity breathe 1.2–2.2s
   — MV nuance: musical phrase can justify 1.5–2.2s; add camera energy
   — Tier nudge: include one longer 2.0–2.4s payoff"
```

### Example 3: Selects — B-Roll (Principle Timeline)
```
Base Note: "Collect movement textures..."
Enriched:
  "Collect movement textures...
   — Context: selects—favor faster trims (0.5–1.0s) while reviewing"
```

---

## Tight Borders

### Behavior
- Each marker ends **1 frame before the next marker starts**
- Creates gapless color bands on timeline ruler
- **Default:** ON

### Disable
```bash
export DEGA_MARKER_TIGHT_BORDERS=0
python3 the_dega_template_full.py
```

### Visual Comparison
```
Without Tight Borders:
[HOOK        ][DRAW        ][INTERRUPT   ]

With Tight Borders:
[HOOK][DRAW][INTERRUPT]
```

---

## Marker Note Structure

```
┌─────────────────────────────────────────┐
│ Original Base Note                      │
│ (from marker template)                  │
├─────────────────────────────────────────┤
│ — Default Role Guidance                 │
│   (if role matches _CUT_GUIDE_DEFAULT)  │
├─────────────────────────────────────────┤
│ — Lane-Specific Nuance                  │
│   (if lane + role match)                │
├─────────────────────────────────────────┤
│ — Tier/Context Nudge                    │
│   (if tier/context applies)             │
└─────────────────────────────────────────┘
```

---

## Integration Points

### 1. Money Masters
- Loop applies enrichment for 12s/22s/30s
- Lane: `"money"`
- Tier: `"12s"`, `"22s"`, or `"30s"`

### 2. Pillar Standard Timelines
- Infers lane from pillar name or title
- Context: `"principle"` (default) or `"selects"`
- Applied to all principle packs

### 3. Master Build (Per Lane)
- MV, Fashion, TH, DIL, Cook-Up masters
- Lane: Detected from pillar name
- Tier: `"12s"`, `"22s"`, or `"30s"`

### 4. Project Reseed
- Scans all timelines
- Infers lane from title
- Context: `"principle"` or `"selects"`

---

## Customization Notes

All guidance is **hardcoded** in the following dictionaries:

```python
_CUT_GUIDE_DEFAULT    # Role-based guidance
_CUT_GUIDE_BY_LANE    # Lane-specific overrides
_TIER_NUDGE           # Tier/context nudges
```

To customize:
1. Edit the dictionaries in `the_dega_template_full.py`
2. Add new roles/lanes as needed
3. Re-run script to apply changes

---

## Best Practices

### For Editors
1. Read marker notes BEFORE cutting
2. Use ranges as starting points, not hard rules
3. Adjust based on content rhythm and energy
4. Check tight borders for visual section clarity

### For Customization
1. Keep role names consistent with marker templates
2. Use ranges (e.g., "0.6–1.0s") not absolutes
3. Layer general → specific guidance
4. Test on sample timeline before full deployment

---

## Troubleshooting

### Markers Not Enriched
- Check timeline isn't a master (masters use LANE_MARKERS directly)
- Verify principle pack is returned by `get_principle_markers_for_title()`
- Check lane inference with debug logs

### Borders Not Tight
- Confirm `DEGA_MARKER_TIGHT_BORDERS` not set to `0`
- Check markers are sorted by time
- Verify last marker in list (no next marker to tighten against)

### Wrong Lane Detected
- Review `_infer_lane_from_pillar_or_title()` logic
- Add explicit title patterns if needed
- Check pillar name matching

---

## Reference: Lane Detection

```python
def _infer_lane_from_pillar_or_title(pillar_name, title):
    Priority:
    1. Music-Video / segment / mv master → "mv"
    2. Fashion / look / fashion master → "fashion"
    3. Talking Head / interview / th master → "talking"
    4. Day in Life / chapter / dil master → "dil"
    5. Cook-Ups / section / cook-up master → "cook"
    6. Money / money master → "money"
    7. Default → "money"
```

---

**Updated:** October 8, 2025
**Version:** DEGA v4.6
