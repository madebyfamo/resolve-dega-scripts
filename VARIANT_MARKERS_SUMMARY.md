# Variant-Specific Principle Markers System

## Overview
The DEGA Formula Builder now includes **context-sensitive marker variants** that adapt principle markers based on the specific task, formula type, and workflow stage.

---

## Architecture

### Base + Variant Pattern
```
Timeline Markers = BASE_PACK + VARIANT_PACK (if detected)
```

- **BASE packs**: 4-6 universal markers covering core principles
- **VARIANT packs**: 2-7 additional markers with task-specific techniques
- **Detection**: Automatic based on timeline name keywords
- **Fallback**: Returns base pack if no variant detected

---

## 1. ShotFX Variants (6 variants)

### Coverage
- **7 ShotFX timelines** enhanced
- **Marker counts**: 6-8 markers each (4 base + 2-4 variant)

### Variants
1. **clone** - Clone/Twin/Multiplicity effects
   - Lock-off plates, mask strategy, parallax sanity
   - Seam checking, shadow/occlusion, grain matching

2. **clean_plate** - Beauty/Cleanup patches
   - Source selection, tracking, patch blending
   - Skin texture preservation, edge blending

3. **background_cleanup** - Removing distractions
   - Garbage matte workflow, patch source selection
   - Edge treatment, motion matching

4. **remove_mic_cable** - Object removal
   - Frame-by-frame painting, clone stamp workflow
   - Feathering, temporal coherence

5. **hand_split** - Hand/object splits
   - Rotoscoping workflow, motion blur matching
   - Edge refinement, tracking

6. **screen_insert** - Screen replacement/UI inserts
   - Corner pin tracking, perspective matching
   - Color correction, lighting integration

### Example: Clone in Hallway
```
✅ 8 markers total
   4 base ShotFX principles
   + 7 clone-specific techniques
   + 1 anchor marker @ 299s
```

---

## 2. Selects & Stringouts Variants (12 variants)

### Coverage
- **13 Selects/Stringouts timelines** enhanced
- **Marker counts**: 8-9 markers each (6 base + 2-3 variant)
- **5 formula types** covered: MV, Fashion, TH, DIL, Cook-Ups

### Base Pack (6 markers)
All Selects timelines start with these universal tips:
- **Purple**: 3-pass workflow (reject → keep A's → choose alts)
- **Orange**: Labeling & notes (⭐/color/keywords)
- **Blue**: Cut points (prefer motion/syllables, 6-12f handles)
- **Green**: Sync sanity (claps/peaks, frame-accurate)
- **Yellow**: Stringout pointers (range-mark beats, gaps for pacing)
- **Blue**: 5min anchor @ 299s

### Variants by Formula

#### Music-Video (MV)
- **mv_perf**: Performance Selects
  - Lyric mapping to footage
  - Angle variety & camera energy
  - Micro-ramps & speed ramps

- **broll**: B-Roll Selects
  - Texture diversity (wide/medium/tight)
  - Parallax & depth
  - Cutaway purpose (illustrative vs. atmospheric)

#### Fashion (OOTD)
- **fashion_look**: LOOK Selects
  - Silhouette first (read from thumbnail)
  - Motion beauty (fabric, hair, walk)
  - Color continuity across shots

#### Talking Head (TH)
- **th_aroll**: A-Roll Selects
  - Message spine (setup → payoff)
  - Cut on gesture/inflection
  - Caption sync considerations

- **th_broll**: B-Roll Selects
  - Illustrative matches (show what's said)
  - Readability (clean framing, identifiable subjects)

#### Day in the Life (DIL)
- **dil_generic**: Generic DIL Selects
  - Micro-scenes (beginning/middle/end)
  - Entrances & exits (motion continuity)

- **dil_commute**: Commute Selects
  - Travel rhythm (fast → slow → arrival)
  - Landmarks & geography

- **dil_coffee**: Coffee Shop Selects
  - Hands & steam details
  - Loop beats (sips, stirs, pour)

#### Cook-Ups
- **cook_overhead**: Overhead Selects
  - Clean hits (hands visible, action clear)
  - UI context (show plugin/gear)

- **cook_front**: Front Cam Selects
  - Energy & eye line
  - Reveal moments (light up, smile, head bob)

- **cook_foley**: Foley/Production Selects
  - Transient truth (crisp hits)
  - Variety (different buttons/knobs/pads)

#### Stringouts
- **stringout_generic**: Generic Stringouts
  - Order (best first or story arc)
  - Air for pacing (2-4s gaps)
  - Markers to beats (flag highlights)

### Example: PERF Selects (MV)
```
✅ 9 markers total
   6 base (workflow, labeling, cuts, sync, stringouts, anchor)
   + 3 mv_perf variant (lyric mapping, angle variety, micro-ramps)
```

---

## Detection Logic

### Priority Order
1. **Exclude Masters** - Skip all master timelines
2. **Check Selects/Stringouts** - Match before other keywords
3. **Check ShotFX** - Match "shotfx" or "shot fx"
4. **Check Other Types** - segment, interview, look, chapter, section

### Why Priority Matters
Example: "LOOK Selects" contains both "look" and "selects"
- ❌ Old logic: Matched "look" first → returned Fashion base pack (4 markers)
- ✅ New logic: Matched "selects" first → returned Selects base + fashion_look variant (9 markers)

---

## Verification

### Testing Tools
```bash
# Verify ShotFX variants
python3 verify_shotfx_variants.py

# Verify Selects variants
python3 verify_selects_variants.py

# Audit all principle markers
python3 dega_audit_markers.py
```

### Results
```
ShotFX Variants:     7/7 timelines enhanced (6-8 markers each)
Selects Variants:   13/13 timelines enhanced (8-9 markers each)
Total Enhanced:     20/20 variant timelines (100% coverage)
```

---

## Benefits

### Before Variants
- Generic tips applied to all timelines of same type
- "ShotFX tips" for all VFX work (not specific to cloning vs. cleanup)
- No markers on Selects/Stringouts timelines

### After Variants
- ✅ **Context-aware guidance** - Tips specific to exact task
- ✅ **More markers per timeline** - 6-9 vs 4 before
- ✅ **Better discoverability** - Selects timelines now tagged
- ✅ **Formula-specific workflow** - MV Selects ≠ Cook-Up Selects
- ✅ **Scalable architecture** - Easy to add new variants

---

## Git History
```
1. feat: Fix principle marker detection (duration bug)
2. feat: Add variant-specific ShotFX marker packs
3. feat: Add variant-specific Selects & Stringouts marker packs
```

---

## Future Extensions

### Potential New Variants
- **Multicam Selects** - Angle switching, sync, coverage
- **Color Grade Selects** - Reference frames, skin tones, continuity
- **Audio Selects** - Dialogue clarity, ambience, music
- **Archive Selects** - Metadata, quality, rights

### Pattern for Adding Variants
1. Create `_your_variant_for_title()` detector function
2. Add `YOUR_BASE` list (universal tips)
3. Add `YOUR_SPECIFIC` dict (variant packs)
4. Integrate into `get_principle_markers_for_title()`
5. Add verification script
6. Test and commit

---

## Summary

The variant system transforms principle markers from **generic best practices** into **targeted, workflow-specific guidance** that adapts to exactly what you're doing. Whether you're cloning a twin, selecting MV performance clips, or choosing DIL coffee shop moments, you get **tips that matter for that exact task**.

**Enhancement complete!** 🎉
