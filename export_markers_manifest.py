#!/usr/bin/env python3
"""
Export all timeline markers in the current Resolve project to a JSON manifest.
The script must be launched from inside Resolve (Workspace ▸ Scripts) or a
Resolve-provided terminal so the scripting API is available.
"""

import argparse
import collections
import json
import pathlib
import sys

from datetime import UTC, datetime
from math import floor


BASE_TIERS = {"12s", "22s", "30s"}


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


def _normalize_marker_payload(frame_id: int, payload: dict, timecode: str) -> dict:
    return {
        "frame_id": frame_id,
        "timecode": timecode,
        "name": payload.get("name"),
        "note": payload.get("note"),
        "color": payload.get("color"),
        "duration": payload.get("duration"),
        "custom_data": payload.get("customData"),
        "flags": payload.get("flags"),
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
    hours = floor(total_seconds / 3600)
    minutes = floor((total_seconds % 3600) / 60)
    seconds = floor(total_seconds % 60)
    frames = int(round((total_seconds - floor(total_seconds)) * fps_value))
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}:{frames:02d}"


def _infer_tier(timeline_name: str) -> str | None:
    lowered = timeline_name.lower()
    for label in ("12s", "22s", "30s"):
        if label in lowered:
            return label
    return None


def _collect_timeline_data(project) -> tuple[list[dict], int, collections.Counter[str]]:
    timelines: list[dict] = []
    total_markers = 0
    tier_counter: collections.Counter[str] = collections.Counter()
    timeline_count = project.GetTimelineCount() or 0
    for index in range(1, timeline_count + 1):
        timeline = project.GetTimelineByIndex(index)
        if not timeline:
            continue
        timeline_name = timeline.GetName() or f"Timeline {index}"
        marker_map = timeline.GetMarkers() or {}
        marker_items = []
        for frame_id in sorted(marker_map.keys()):
            payload = marker_map.get(frame_id) or {}
            timecode = _resolve_timecode(timeline, frame_id)
            marker_items.append(_normalize_marker_payload(frame_id, payload, timecode))
        total_markers += len(marker_items)
        tier = _infer_tier(timeline_name)
        if tier:
            tier_counter[tier] += len(marker_items)
        timelines.append(
            {
                "name": timeline_name,
                "frame_rate": timeline.GetSetting("timelineFrameRate"),
                "start_timecode": timeline.GetStartTimecode(),
                "marker_count": len(marker_items),
                "markers": marker_items,
            }
        )
    return timelines, total_markers, tier_counter


def _utc_stamp() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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


def _detect_drop_frame(project, timelines: list[dict]) -> bool:
    setting_value = _interpret_bool(project.GetSetting("timelineDropFrameTimecode"))
    if setting_value is not None:
        return setting_value
    for timeline in timelines:
        start = timeline.get("start_timecode")
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


def export_manifest(
    output_path: pathlib.Path, *, quiet: bool = False
) -> tuple[str, int, int]:
    resolve = get_resolve()
    project_manager = resolve.GetProjectManager()
    project = project_manager.GetCurrentProject()
    if not project:
        print("❌ No active project found. Open a project before exporting.")
        sys.exit(1)

    project_name = project.GetName() or "Unnamed Project"
    timelines, marker_total, tier_counts = _collect_timeline_data(project)
    current_timeline = project.GetCurrentTimeline()
    timestamp = _utc_stamp()
    project_fps_value = project.GetSetting("timelineFrameRate")
    project_fps = _as_float(project_fps_value)
    drop_frame = _detect_drop_frame(project, timelines)
    project_uuid = _get_project_uuid(project)
    tier_counts_payload = {
        key: tier_counts.get(key, 0)
        for key in sorted(BASE_TIERS | set(tier_counts.keys()))
    }
    manifest = {
        "schema_version": "1.0",
        "schema": "famo.resolve.markers/v1",
        "generated_at": timestamp,
        "generated_at_utc": timestamp,
        "project_name": project_name,
        "project_uuid": project_uuid,
        "fps": project_fps if project_fps is not None else project_fps_value,
        "drop_frame": drop_frame,
        "tier_counts": tier_counts_payload,
        "markers_total": marker_total,
        "project": {
            "name": project_name,
            "uuid": project_uuid,
            "fps": project.GetSetting("timelineFrameRate"),
            "current_timeline": (
                current_timeline.GetName() if current_timeline else None
            ),
            "timeline_count": len(timelines),
            "drop_frame": drop_frame,
        },
        "timelines": timelines,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2)
        handle.write("\n")

    if not quiet:
        print("📤 Markers manifest export")
        print(f"  Project: {project_name}")
        print(f"  Timelines exported: {len(timelines)}")
        print(f"  Total markers: {marker_total}")
        print(f"  Output file: {output_path}")
    return project_name, len(timelines), marker_total


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export Resolve timeline markers to JSON."
    )
    parser.add_argument(
        "-o",
        "--output",
        default="markers_manifest.json",
        help="Destination path for the markers manifest (default: markers_manifest.json).",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress normal stdout chatter (only errors reported).",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    output_path = pathlib.Path(args.output).resolve()
    export_manifest(output_path, quiet=args.quiet)


if __name__ == "__main__":
    main()
