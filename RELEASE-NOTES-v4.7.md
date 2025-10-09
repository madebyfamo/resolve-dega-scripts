# DEGA v4.7 Release Notes

## 🎯 Core Philosophy Change: **Seconds-Only Pacing**

v4.7 represents a fundamental shift from beat-based thinking to **pure seconds-based cut guidance**. No beat math, no BPM calculations—just clean, actionable seconds ranges tailored to your content type.

---

## ✨ What's New

### 1. **Seconds-Only Pacing System (`PACING_S`)**
- **6 Lanes × 3 Tiers = 18 Unique Configurations**
  - **Lanes**: Money, MV, Fashion, Talking, DIL, Cook-Ups
  - **Tiers**: 12s, 22s, 30s (short/mid/upper length)
- **Section-Specific Guidance**: Each marker (HOOK, DRAW, COMMIT/PAYOFF, etc.) gets unique seconds ranges
- **Example**: Money Master 12s HOOK = "Cut every ~0.8–1.2s; micro-jolt ≤0.7s ok."

### 2. **Butt-Joined Markers (`_butt_join_markers`)**
- **Seamless Color Bands**: Adjacent markers extend to touch (1-frame butt joint)
- **No Visual Gaps**: Eliminates hairline seams between markers in timeline UI
- **Smart Extension**: Extends previous marker by ≤1 frame to close gaps without overlap

### 3. **Universal Application**
- **Master Timelines**: All 6 lanes × 3 tiers get lane/tier-specific guidance
- **Principle Timelines**: Segments, ShotFX, Selects, Stringouts, etc.
- **Auto-Detection**: `_lane_tier_from_title()` infers lane/tier from timeline names

---

## 🔄 What Changed from v4.6

| **v4.6** | **v4.7** |
|----------|----------|
| Beat-based cut guides (_CUT_GUIDE_DEFAULT, _CUT_GUIDE_BY_LANE, _TIER_NUDGE) | Seconds-only pacing (PACING_S) |
| `_enrich_markers_with_cut_notes()` | `_enrich_marker_notes()` |
| `_tighten_marker_borders_if_enabled()` (1-frame gap) | `_butt_join_markers()` (1-frame butt) |
| Tier contexts: "12s", "22s", "30s", "principle", "selects" | Pure tier system: "12s", "22s", "30s" |
| Generic "principle" guidance for non-masters | Lane-specific 30s guidance (inferred from timeline name) |

---

## 📋 PACING_S Structure

```python
PACING_S = {
    "money": {
        "12s": { "HOOK": "...", "DRAW": "...", "COMMIT / PAYOFF": "...", ... },
        "22s": { ... },
        "30s": { ... },
    },
    "mv": { ... },
    "fashion": { ... },
    "talking": { ... },
    "dil": { ... },
    "cook": { ... },
}
```

**Key Features**:
- **Marker Name Matching**: Uses exact marker name (e.g., "HOOK", "COMMIT / PAYOFF #1") as key
- **Appends to Notes**: Adds `— Cuts: <guidance>` to existing marker notes
- **Backwards Compatible**: If no rule exists, marker notes unchanged

---

## 🎨 Marker Note Format

**Before** (v4.6):
```
[Original marker note]
— Edit pacing: average shot 0.6–1.0s; avoid holds >1.3s unless a reveal lands.
Money nuance: keep copy plain; 0.6–0.9s 'receipt' cut is ideal.
Tier nudge: bias toward the SHORT end (snappier overall).
```

**After** (v4.7):
```
[Original marker note]
— Cuts: Cut every ~0.8–1.2s; micro-jolt ≤0.7s ok.
```

**Why It's Better**:
- **Simpler**: One line instead of three
- **Clearer**: Direct seconds ranges, no abstract "nuances"
- **Actionable**: Editor knows exactly what to do

---

## 🚀 How to Use

### Fresh Project Creation
```bash
cd ~/Developer/FAMO\ Show\ Labs/resolve-dega-scripts
python3 the_dega_template_full.py
```
✅ All markers created with v4.7 seconds-only pacing + butt-joined borders

### Update Existing Project
```bash
DEGA_PRINCIPLE_FORCE_RESEED=1 python3 the_dega_template_full.py
```
✅ Replaces old v4.6 markers with new v4.7 markers on principle timelines

---

## 🔍 Technical Details

### Lane/Tier Detection (`_lane_tier_from_title`)
```python
# Master timelines (explicit tier in name)
"Money Master — 12s (IG short)" → ("money", "12s")
"MV Master — 22s" → ("mv", "22s")
"Fashion Master — 30s" → ("fashion", "30s")

# Non-master timelines (inferred from prefix)
"Segment — Hook Performance" → ("mv", "30s")  # default 30s
"Interview — Tech Review" → ("talking", "30s")
"Look — Streetwear Capsule" → ("fashion", "30s")
"Chapter — Morning Routine" → ("dil", "30s")
"Section — Beat Breakdown" → ("cook", "30s")
```

### Marker Enrichment Flow
1. **Get base markers**: From template (LANE_MARKERS, principle packs, etc.)
2. **Detect lane/tier**: `_lane_tier_from_title(timeline_name)`
3. **Enrich notes**: `_enrich_marker_notes(markers, lane, tier)` adds seconds guidance
4. **Butt-join**: `_butt_join_markers(enriched, FPS)` closes visual gaps
5. **Add to timeline**: `add_markers_to_timeline_if_empty(tl, FPS, markers)`

---

## 📊 Coverage

### Master Timelines (18 total)
- ✅ Money Master × 3 tiers (12s/22s/30s)
- ✅ MV Master × 3 tiers
- ✅ Fashion Master × 3 tiers
- ✅ TH Master × 3 tiers
- ✅ DIL Master × 3 tiers
- ✅ Cook-Up Master × 3 tiers

### Principle Timelines
- ✅ Segments (MV pillar): 30 timelines → "mv" lane, "30s" tier
- ✅ ShotFX (all pillars): → inferred lane, "30s" tier
- ✅ Selects & Stringouts: → inferred lane, "selects" tier (if still using old system)
- ✅ Scenes, Interviews, Looks, Chapters, Sections: → respective lanes, "30s" tier

---

## 🎯 Benefits

1. **Editor-Friendly**: No beat math required—just read the seconds range and cut
2. **Context-Aware**: Different guidance for Money vs MV vs Fashion, 12s vs 30s
3. **Visual Clarity**: Butt-joined markers create seamless color bands (no gaps)
4. **Consistent**: All timelines use same seconds-based system
5. **Backwards Compatible**: Existing marker notes preserved, new guidance appended

---

## 🛠️ Migration from v4.6

### Automatic
- ✅ v4.7 script detects old markers and applies new system
- ✅ Use `DEGA_PRINCIPLE_FORCE_RESEED=1` to update existing timelines

### Manual (if needed)
1. Delete old markers from timeline (right-click → Delete Marker)
2. Run DEGA v4.7 with `DEGA_PRINCIPLE_FORCE_RESEED=1`
3. New markers appear with seconds-only guidance

---

## 📝 Sample Marker Notes (Money 12s)

**HOOK**:
```
— Cuts: Cut every ~0.8–1.2s; micro-jolt ≤0.7s ok.
```

**DRAW**:
```
— Cuts: Quicker trims ~0.6–0.9s; 1 brisk insert per beat of idea.
```

**COMMIT / PAYOFF**:
```
— Cuts: Let proof breathe 1.2–1.8s; single cut-ins ≤0.5s.
```

**LOOP / CTA**:
```
— Cuts: Button ≤0.7s; avoid extra frames after action lands.
```

---

## 🚧 Known Limitations

1. **Marker Name Matching**: Must match exact key in PACING_S (e.g., "COMMIT / PAYOFF" not "PAYOFF")
   - **Solution**: Normalize marker names or add aliases in code
2. **Non-Standard Timelines**: If timeline name doesn't match expected patterns, fallback to None
   - **Solution**: Uses existing `_infer_lane_from_pillar_or_title()` as backup
3. **Selects/Stringouts**: Currently default to "30s" tier (could be made configurable)

---

## 🎉 Bottom Line

v4.7 = **Seconds, not beats. Seamless markers. Universal application.**

Every timeline now has **actionable, lane-specific, tier-appropriate cut guidance** in pure seconds ranges. No guesswork, no beat math—just edit.

**Ready for production.** 🚀
