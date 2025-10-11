#!/usr/bin/env python3
"""
Verify a previously exported Resolve markers manifest against the live project state.
Must be run from Resolve (Workspace ▸ Scripts) or a Resolve-launched terminal so
that the scripting API is available.
"""

import argparse
import collections
import json
import pathlib
import sys
from collections import defaultdict
from datetime import UTC, datetime
from fractions import Fraction

BASE_TIERS = {"12s", "22s", "30s"}
_TERMINAL_TIER_SECONDS = {12.0: 12.0, 22.0: 22.0, 30.0: 30.0}


def _tier_spec_from_title(title: str) -> float | None:
    text = (title or "").lower()
    if "— 12s" in text or " 12s " in text or text.endswith(" 12s") or " 12s —" in text:
        return 12.0
    if "— 22s" in text or " 22s " in text or text.endswith(" 22s") or " 22s —" in text:
        return 22.0
    if "— 30s" in text or " 30s " in text or text.endswith(" 30s") or " 30s —" in text:
        return 30.0
    return None


def _is_master_title(title: str) -> bool:
    lowered = (title or "").lower()
    return (
        lowered.startswith("money master")
        or lowered.startswith("mv master")
        or lowered.startswith("th master")
        or lowered.startswith("fashion master")
        or lowered.startswith("dil master")
        or lowered.startswith("cook-up master")
        or (" master —" in lowered)
    )


def _tier_seconds_from_title(title: str) -> float | None:
    tier = _tier_spec_from_title(title)
    if tier in _TERMINAL_TIER_SECONDS:
        return tier
    text = (title or "").lower()
    if "12s" in text and "29.97" in text:
        return 12.0
    if "22s" in text and "29.97" in text:
        return 22.0
    if "30s" in text and "29.97" in text:
        return 30.0
    if "(ig short" in text:
        return 12.0
    if "(ig mid" in text:
        return 22.0
    if "(ig upper" in text:
        return 30.0
    return None


def _sec_to_frame_exact(sec: float, fps: float) -> int:
    try:
        return int(round(float(Fraction(str(sec)) * Fraction(str(fps)))))
    except Exception:
        return int(round(sec * fps))


def _remarkers_dict(timeline) -> dict[int, dict]:
    try:
        raw = timeline.GetMarkers()
    except Exception:
        return {}
    if isinstance(raw, dict):
        result: dict[int, dict] = {}
        for key, value in raw.items():
            try:
                result[int(key)] = value or {}
            except Exception:
                continue
        return result
    if isinstance(raw, list):
        result = {}
        for entry in raw:
            try:
                fr = int(entry.get("frame", 0))
            except Exception:
                continue
            result[fr] = entry or {}
        return result
    return {}


def _marker_span_covers(marker: dict, start_frame: int, target_frame: int) -> bool:
    dur_raw = marker.get("duration") or marker.get("durationFrames") or 0
    try:
        dur = int(dur_raw)
    except Exception:
        try:
            dur = int(float(dur_raw))
        except Exception:
            dur = 0
    if dur <= 0:
        return start_frame == target_frame
    return start_frame <= target_frame < start_frame + dur


def _find_covering_marker(markers: dict[int, dict], target_frame: int):
    for frame, marker in markers.items():
        if _marker_span_covers(marker, frame, target_frame):
            return frame, marker
    return None


def _frame_is_covered(markers: dict[int, dict], target_frame: int) -> bool:
    marker = markers.get(target_frame)
    if marker and _marker_span_covers(marker, target_frame, target_frame):
        return True
    return _find_covering_marker(markers, target_frame) is not None


def _inspect_terminal_loop_lock(project, fallback_fps: float | None):
    unlocked: list[str] = []
    try:
        timeline_total = int(project.GetTimelineCount() or 0)
    except Exception:
        timeline_total = 0

    for index in range(1, timeline_total + 1):
        timeline = project.GetTimelineByIndex(index)
        if not timeline:
            continue
        try:
            title = timeline.GetName() or ""
        except Exception:
            title = ""
        if not title or not _is_master_title(title):
            continue
        tier_seconds = _tier_seconds_from_title(title)
        if tier_seconds is None:
            continue
        fps_value = timeline.GetSetting("timelineFrameRate")
        fps = _as_float(fps_value) or fallback_fps
        if not fps or fps <= 0:
            continue
        markers = _remarkers_dict(timeline)
        if not markers:
            unlocked.append(title)
            continue
        end_frame = _sec_to_frame_exact(tier_seconds, fps)
        if not _frame_is_covered(markers, end_frame):
            unlocked.append(title)

    return {
        "locked": not unlocked,
        "unlocked_timelines": unlocked,
    }


def _resolve_timecode(timeline, frame_id: int) -> str:
    getter = getattr(timeline, "GetTimecodeFromFrame", None)
    if callable(getter):
        try:
            value = getter(frame_id)
            if value:
                return value
        except Exception:
            pass
    fps = timeline.GetSetting("timelineFrameRate")
    try:
        fps_value = float(fps)
    except (TypeError, ValueError):
        fps_value = 0.0
    if fps_value <= 0:
        return str(frame_id)
    total_seconds = frame_id / fps_value
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    frames = int(round((total_seconds - int(total_seconds)) * fps_value))
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}:{frames:02d}"


def get_resolve():
    """Acquire the Resolve scripting API handle."""
    bmd = globals().get("bmd")
    if bmd:
        try:
            resolve = bmd.scriptapp("Resolve")
            if resolve:
                return resolve
        except Exception:
            pass
    try:
        import DaVinciResolveScript as dvr  # type: ignore

        resolve = dvr.scriptapp("Resolve")
        if resolve:
            return resolve
    except Exception:
        pass
    print("❌ Could not acquire Resolve API. Run from Resolve (Workspace ▸ Scripts).")
    sys.exit(1)


def _infer_tier(name: str) -> str | None:
    lowered = name.lower()
    for label in BASE_TIERS:
        if label in lowered:
            return label
    return None


def _as_float(value) -> float | None:
    try:
        coerced = float(value)
    except (TypeError, ValueError):
        return None
    return coerced


def _interpret_bool(value) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "on"}:
        return True
    if text in {"0", "false", "no", "off"}:
        return False
    return None


def _detect_drop_frame(project, manifest_timelines: list[dict]) -> bool:
    setting_value = _interpret_bool(project.GetSetting("timelineDropFrameTimecode"))
    if setting_value is not None:
        return setting_value
    for entry in manifest_timelines:
        start = entry.get("start_timecode")
        if isinstance(start, str) and ";" in start:
            return True
    return False


def _get_project_uuid(project) -> str | None:
    for attr_name in ("GetProjectID", "GetUniqueID", "GetProjectUniqueID"):
        getter = getattr(project, attr_name, None)
        if callable(getter):
            try:
                value = getter()
            except Exception:
                continue
            if value:
                return str(value)
    return None


def _load_manifest(path: pathlib.Path) -> dict:
    if not path.is_file():
        print(f"❌ Manifest not found: {path}")
        sys.exit(1)
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _prepare_actual_markers(timeline) -> dict[int, list[dict]]:
    marker_map = timeline.GetMarkers() or {}
    prepared: dict[int, list[dict]] = defaultdict(list)
    for frame_id, payload in marker_map.items():
        prepared[int(frame_id)].append(
            {
                "frame_id": int(frame_id),
                "timecode": _resolve_timecode(timeline, int(frame_id)),
                "name": payload.get("name"),
                "note": payload.get("note"),
                "color": payload.get("color"),
                "duration": payload.get("duration"),
                "custom_data": payload.get("customData"),
                "flags": payload.get("flags"),
            }
        )
    for markers in prepared.values():
        markers.sort(key=lambda item: item["frame_id"])
    return prepared


def _pop_match(
    actual_index: dict[int, list[dict]], expected_frame: int, tolerance: int
):
    candidates = []
    for delta in range(tolerance + 1):
        if delta == 0:
            candidates.append(expected_frame)
        else:
            candidates.extend([expected_frame - delta, expected_frame + delta])
    for frame in candidates:
        if frame in actual_index and actual_index[frame]:
            return actual_index[frame].pop(0)
    return None


def _compare_markers(
    timeline_name: str,
    expected_markers: list[dict],
    actual_index: dict[int, list[dict]],
    tolerance: int,
):
    warnings: list[str] = []
    errors: list[str] = []
    for marker in expected_markers:
        expected_frame = int(marker.get("frame_id", 0))
        match = _pop_match(actual_index, expected_frame, tolerance)
        if not match:
            errors.append(
                f"Missing marker at frame {expected_frame} ({marker.get('name')!r})."
            )
            continue
        offset = abs(int(match["frame_id"]) - expected_frame)
        if offset > 0:
            warnings.append(
                f"Frame drift {offset} >0 within tolerance for marker {marker.get('name')!r} (expected {expected_frame}, got {match['frame_id']})."
            )
        for field in ("name", "note", "color", "duration", "custom_data", "flags"):
            expected_value = marker.get(field)
            actual_value = match.get(field)
            if expected_value != actual_value:
                warnings.append(
                    f"Value mismatch for marker {marker.get('name')!r} field '{field}': expected {expected_value!r}, actual {actual_value!r}."
                )
    remaining_extra = sum(len(markers) for markers in actual_index.values())
    if remaining_extra:
        warnings.append(
            f"Found {remaining_extra} additional markers not present in manifest."
        )
    status = "ok"
    if errors:
        status = "error"
    elif warnings:
        status = "warning"
    return {
        "timeline": timeline_name,
        "status": status,
        "warnings": warnings,
        "errors": errors,
    }


def _utc_stamp() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def verify_manifest(
    manifest_path: pathlib.Path,
    report_path: pathlib.Path,
    frame_tolerance: int,
    *,
    quiet: bool = False,
) -> dict:
    manifest = _load_manifest(manifest_path)
    resolve = get_resolve()
    project_manager = resolve.GetProjectManager()
    project = project_manager.GetCurrentProject()
    if not project:
        print(
            "❌ No active project found. Open the project referenced in the manifest."
        )
        sys.exit(1)

    manifest_timelines = manifest.get("timelines", [])
    manifest_tier_counts = collections.Counter()
    expected_markers_total = 0
    for entry in manifest_timelines:
        tier = _infer_tier(entry.get("name") or "")
        marker_count = len(entry.get("markers", []))
        expected_markers_total += marker_count
        if tier:
            manifest_tier_counts[tier] += marker_count
    details: list[dict] = []
    errors_total = 0
    warnings_total = 0

    lookup = {
        tl.GetName(): tl
        for tl in (
            project.GetTimelineByIndex(i)
            for i in range(1, (project.GetTimelineCount() or 0) + 1)
        )
        if tl
    }

    for timeline_entry in manifest_timelines:
        name = timeline_entry.get("name")
        timeline = lookup.get(name)
        if not timeline:
            detail = {
                "timeline": name or "(missing name)",
                "status": "error",
                "warnings": [],
                "errors": ["Timeline not found in project."],
            }
            details.append(detail)
            errors_total += 1
            continue
        expected_markers = timeline_entry.get("markers", [])
        actual_index = _prepare_actual_markers(timeline)
        detail = _compare_markers(name, expected_markers, actual_index, frame_tolerance)
        details.append(detail)
        errors_total += len(detail["errors"])
        warnings_total += len(detail["warnings"])

    timestamp = _utc_stamp()
    project_uuid = _get_project_uuid(project)
    project_fps_value = project.GetSetting("timelineFrameRate")
    project_fps = _as_float(project_fps_value)
    drop_frame = _detect_drop_frame(project, manifest_timelines)
    declared_tier_counts = manifest.get("tier_counts") or {}
    loop_lock = _inspect_terminal_loop_lock(project, project_fps)

    summary = {
        "project": {
            "name": project.GetName() or "Unnamed Project",
            "manifest_project": manifest.get("project", {}).get("name"),
            "uuid": project_uuid,
            "fps": project_fps if project_fps is not None else project_fps_value,
            "drop_frame": drop_frame,
            "manifest_uuid": manifest.get("project_uuid"),
            "manifest_fps": manifest.get("fps"),
            "manifest_drop_frame": manifest.get("drop_frame"),
        },
        "timelines_checked": len(details),
        "warnings": warnings_total,
        "errors": errors_total,
        "frame_tolerance": frame_tolerance,
        "generated_at": timestamp,
        "generated_at_utc": timestamp,
        "loop_end_locked": loop_lock["locked"],
        "manifest": {
            "schema": manifest.get("schema"),
            "schema_version": manifest.get("schema_version"),
            "markers_total_declared": manifest.get("markers_total"),
            "markers_total_counted": expected_markers_total,
            "tier_counts_declared": {
                key: declared_tier_counts.get(key, 0)
                for key in sorted(BASE_TIERS | set(declared_tier_counts.keys()))
            },
            "tier_counts_counted": {
                key: manifest_tier_counts.get(key, 0)
                for key in sorted(BASE_TIERS | set(manifest_tier_counts.keys()))
            },
        },
    }

    if loop_lock["unlocked_timelines"]:
        summary["loop_end_unlocked"] = loop_lock["unlocked_timelines"]

    report = {
        "summary": summary,
        "details": details,
    }
    report["generated_at_utc"] = timestamp

    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")

    if not quiet:
        print("🧪 Markers manifest verification")
        print(f"  Timelines checked: {summary['timelines_checked']}")
        print(f"  Warnings: {summary['warnings']}")
        print(f"  Errors: {summary['errors']}")
        print(f"  Report file: {report_path}")

    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a Resolve markers manifest against the current project."
    )
    parser.add_argument(
        "-i",
        "--input",
        default="markers_manifest.json",
        help="Path to the markers manifest JSON file (default: markers_manifest.json).",
    )
    parser.add_argument(
        "--frame-tolerance",
        type=int,
        default=1,
        help="Frame tolerance when matching markers (default: 1 frame).",
    )
    parser.add_argument(
        "--out-report",
        default="markers_verify_report.json",
        help="Destination path for the verification report (default: markers_verify_report.json).",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress normal stdout chatter (only errors reported).",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    manifest_path = pathlib.Path(args.input).resolve()
    report_path = pathlib.Path(args.out_report).resolve()
    report = verify_manifest(
        manifest_path,
        report_path,
        args.frame_tolerance,
        quiet=args.quiet,
    )

    errors = report["summary"]["errors"]
    warnings = report["summary"]["warnings"]
    if errors > 0:
        sys.exit(1)
    if warnings > 0:
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
