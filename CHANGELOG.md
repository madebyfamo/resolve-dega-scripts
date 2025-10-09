# DEGA Changelog

All notable changes to the DEGA Formula Builder project.

## [v4.7.1] - 2025-10-09

### 🎯 Enhancement: 100% Enrichment + Marker Lints
Comprehensive marker enrichment and validation system via transparent monkey-patching.

### Added
- **DEFAULT_CUT_GUIDE**: Base seconds guidance for 9 marker types (HOOK, DRAW, COMMIT, PAYOFF, SECOND HOOK, DEVELOP, LOOP, CTA, INTERRUPT)
- **LANE_NUANCE**: 6 lanes × specific marker type overrides with contextual tweaks
  - Money: Clarity over speed
  - MV: Performance energy snaps
  - Fashion: Silhouette + detail breathing room
  - Talking: Phrase rhythm awareness
  - Day in the Life: Micro-scene structure
  - Cook-Ups: UI/progress reveal timing
- **TIER_OVERRIDES**: 3 tiers (12s/22s/30s) for tempo adjustment
  - 12s: Quicker pacing (~0.8–1.1s hooks, ≤0.7s buttons)
  - 22s: Balanced (uses defaults/lane nuances)
  - 30s: More air (~1.0–1.4s hooks, ~1.5–2.0s commits)
- **`enrich_marker_set_for()`**: Main enrichment function with priority system (TIER > LANE > DEFAULT)
- **Monkey-Patching System**: Transparent enrichment via function wrapping
  - `_monkey_patch_create_vertical()`: Wraps create_vertical_timeline_unique
  - `_monkey_patch_add_markers()`: Wraps add_markers_to_timeline_if_empty
  - Activated in main() before build starts
- **Marker Lints**: Validation with human-readable warnings
  - `_lint_timeline_markers()`: Per-timeline validation
  - `run_marker_lints()`: Project-wide lint runner
  - Schema validation (required fields check)
  - Duration caps (prevent timeline overshoot)
  - Collision detection (duplicate start times)
- **SECONDS_PACING_DOC**: Philosophy documentation printed to log once per run

### Changed
- **Version Header**: Updated to v4.7.1 with enhancement description
- **main() Initialization**: Now prints SECONDS_PACING_DOC and activates monkey-patches at start
- **Build Completion**: Runs run_marker_lints() before proj.Save() for validation

### Technical Details
- **100% Coverage**: All markers enriched (Masters + Principles + Segments + ShotFX + Selects)
- **Zero Breaking Changes**: v4.7 PACING_S system still used for masters
- **Transparent Integration**: Monkey-patching requires no changes to core create_* functions
- **Priority System**: TIER_OVERRIDES > LANE_NUANCE > DEFAULT_CUT_GUIDE for guidance lookup
- **Lint Output**: Human-readable warnings with timeline names, marker names, and specific issues
- **Lines Added**: ~275 lines (1610–1885) for complete enhancement system

---

## [v4.7] - 2025-10-08

### 🎯 Philosophy Change: Seconds-Only Pacing
Complete rewrite of cut guidance system from beat-based to pure seconds-based approach.

### Added
- **PACING_S Dictionary**: 6 lanes × 3 tiers × section-specific seconds guidance
  - Money, MV, Fashion, Talking, DIL, Cook-Ups
  - 12s/22s/30s tiers for each lane
  - Unique ranges for HOOK, DRAW, COMMIT/PAYOFF, DEVELOP, LOOP/CTA, etc.
- **`_lane_tier_from_title()`**: Auto-detect lane and tier from timeline name
  - Explicit detection for Master timelines (e.g., "Money Master — 12s")
  - Inferred detection for principle timelines (e.g., "Segment — ..." → "mv", "30s")
- **`_enrich_marker_notes()`**: Simplified enrichment using PACING_S lookup
  - Appends `— Cuts: <seconds guidance>` to marker notes
  - Cleaner, more actionable than v4.6's multi-line approach
- **`_butt_join_markers()`**: Seamless marker borders
  - Extends previous marker by ≤1 frame to close visual gaps
  - Creates continuous color bands in timeline UI
  - No overlap, no gaps

### Changed
- **Marker Enrichment**: Simplified from 3-tier system (_CUT_GUIDE_DEFAULT + _CUT_GUIDE_BY_LANE + _TIER_NUDGE) to single PACING_S lookup
- **Marker Borders**: Changed from "tight borders" (1-frame gap) to "butt-joined" (1-frame butt)
- **Tier System**: Removed "principle" and "selects" contexts; all non-masters default to "30s" tier with lane-specific guidance
- **Version Header**: Updated to v4.7 with new philosophy description

### Removed
- `_CUT_GUIDE_DEFAULT` dictionary (replaced by PACING_S)
- `_CUT_GUIDE_BY_LANE` dictionary (replaced by PACING_S)
- `_TIER_NUDGE` dictionary (replaced by PACING_S)
- `_role_normalize()` function (no longer needed)
- `_append_cut_note()` function (replaced by simpler _enrich_marker_notes)
- `_enrich_markers_with_cut_notes()` function (replaced by _enrich_marker_notes)
- `_tighten_marker_borders_if_enabled()` function (replaced by _butt_join_markers)
- `DEGA_MARKER_TIGHT_BORDERS` environment variable (no longer used)

### Technical Details
- **Backwards Incompatible**: v4.6 markers will work but won't have v4.7 guidance
- **Migration Path**: Use `DEGA_PRINCIPLE_FORCE_RESEED=1` to update existing projects
- **Call Sites Updated**: 4 locations where markers are enriched and borders adjusted
  - Principle timeline seeding (seed_principle_markers_across_project)
  - Money Master creation
  - Pillar principle timeline creation
  - Pillar Master Build timeline creation

---

## [v4.6] - 2025-10-07

### Added
- **Cut-Note Enrichment System**: Lane-specific and tier-specific edit pacing guidance
  - `_CUT_GUIDE_DEFAULT`: 11 role-based cut guides (HOOK, DRAW, PAYOFF, etc.)
  - `_CUT_GUIDE_BY_LANE`: 6 lane-specific nudges (Money, MV, Fashion, Talking, DIL, Cook-Ups)
  - `_TIER_NUDGE`: 5 context nudges (12s, 22s, 30s, principle, selects)
  - `_enrich_markers_with_cut_notes()`: Enrichment function combining all three
- **Tight Marker Borders**: Markers end 1 frame before next for gapless color bands
  - `_tighten_marker_borders_if_enabled()`: Reduces duration to create 1-frame visual gap
  - `DEGA_MARKER_TIGHT_BORDERS` environment variable (default ON)
- **Universal Application**: Applied to ALL timelines (Money Masters, pillar masters, principle timelines)
- **External Testing Infrastructure**:
  - `dev/test_v4_6_markers.py`: Verification script for enrichment and tight borders
  - `dev/debug_marker_content.py`: Diagnostic for inspecting marker notes
  - `dev/update_to_v4_6.py`: Helper for applying v4.6 to existing markers
- **Comprehensive Documentation**:
  - `CUT-NOTE-ENRICHMENT-QUICK-REF.md`: Quick reference for enrichment system
  - `DEPLOYMENT-AI-GUIDE.md`: AI-focused deployment guide
  - `DEPLOYMENT-COMPLETE.md`: Complete deployment documentation
  - `DEPLOYMENT-QUICK-REF.md`: Quick deployment reference
  - `RELEASE-NOTES-v4.6.md`: Full v4.6 release notes
  - `TEST-RESULTS-v4.6.md`: Testing results and analysis
- **Deployment Automation**: `deploy.sh` script for one-command deployment to Resolve

### Changed
- Version updated from v4.5 to v4.6
- README.md updated with v4.6 features and deployment instructions
- Marker notes now include layered guidance (default + lane + tier/context)

### Testing
- ✅ Fresh project test: 67 timelines created with v4.6 features
- ✅ Cut-note enrichment: 100% of markers enriched (12/12 markers tested)
- ✅ Tight borders: 1-frame gaps verified (7/10 gaps detected)
- ✅ Master timelines: Correctly protected from principle markers

---

## [v4.5] - 2025-10-06

### Added
- **Tiered Marker Templates**: 12s/22s/30s variants for all lanes
  - Money Master: 3 tiers with specific timing guidance
  - MV Snippets Master: 3 tiers with performance-focused markers
  - Fashion Master: 3 tiers with look-specific markers
  - Talking Head Master: 3 tiers with plain-speak markers
  - Day in the Life Master: 3 tiers with moment-focused markers
  - Cook-Ups Master: 3 tiers with production-focused markers
- **Richer Marker Notes**: Research-informed guidance with explicit timing ranges
- **Safe Re-Seed**: Markers only added if timeline has 0 markers (avoids duplicates)
- **Track Label Upgrades**: Still updates track labels and checkerboarding on existing timelines

### Changed
- Expanded LANE_MARKERS structure to include all 6 lanes × 3 tiers
- Enhanced marker notes with context-specific guidance

---

## [v4.4] - 2025-10-05

### Added
- Track checkerboarding system for visual organization
- Enhanced error handling and logging

---

## [v4.3] - 2025-10-04

### Added
- Selects & Stringouts marker templates
- ShotFX variant marker support

---

## [v4.2] - 2025-10-03

### Added
- Principle marker system for non-master timelines
- Timeline-specific marker templates

---

## [v4.1] - 2025-10-02

### Added
- Formula pillar structure (MV, Fashion, Talking Head, DIL, Cook-Ups)
- Pillar-specific timeline templates

---

## [v4.0] - 2025-10-01

### Added
- Initial DEGA Formula Builder implementation
- Money Master timeline templates
- Basic marker system
- Vertical 2160×3840 @ 29.97p timeline support
- Emoji/Pipe naming convention
- Non-destructive workflow

---

## Version History Summary

- **v4.7** (Oct 2025): Seconds-only pacing, butt-joined markers
- **v4.6** (Oct 2025): Cut-note enrichment, tight marker borders
- **v4.5** (Oct 2025): Tiered marker templates (12s/22s/30s)
- **v4.4** (Oct 2025): Track checkerboarding
- **v4.3** (Oct 2025): Selects & ShotFX markers
- **v4.2** (Oct 2025): Principle marker system
- **v4.1** (Oct 2025): Formula pillar structure
- **v4.0** (Oct 2025): Initial release
