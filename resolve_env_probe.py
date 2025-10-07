#!/usr/bin/env python3
"""
DEGA — Resolve Env Probe (safe)
- Verifies Resolve API acquisition
- Probes folder creation API (MediaPool.AddSubFolder vs folder.AddSubFolder)
- Creates a harmless 'ZZZ_PROBE' folder and 'ZZZ_PROBE_TIMELINE' at project defaults
- Adds 1V/1A track and names them
- NO deletes
"""

import sys


def get_resolve():
    # Prefer bmd.scriptapp (works from Resolve’s script menu)
    bmd = globals().get("bmd")
    if bmd:
        try:
            r = bmd.scriptapp("Resolve")
            if r:
                return r
        except Exception:
            pass
    # Fallback: DaVinciResolveScript (works when module is resolvable)
    try:
        import DaVinciResolveScript as dvr

        r = dvr.scriptapp("Resolve")
        if r:
            return r
    except Exception:
        pass
    print("❌ Could not acquire Resolve API. Run from Resolve (Workspace ▸ Scripts).")
    sys.exit(1)


def _iter_subfolders(folder):
    for accessor in ("GetSubFolders", "GetSubFolderList"):
        f = getattr(folder, accessor, None)
        if not f:
            continue
        try:
            res = f()
            if isinstance(res, dict):
                return list(res.values())
            if isinstance(res, list):
                return res
        except Exception:
            pass
    return []


def get_or_create_folder(mp, parent, name):
    # Find existing
    for sub in _iter_subfolders(parent):
        try:
            if sub.GetName() == name:
                print(f"  ↳ Found: {name}")
                return sub
        except Exception:
            pass
    # Create new (preferred)
    folder = None
    try:
        folder = mp.AddSubFolder(parent, name)
        if isinstance(folder, tuple):
            folder = folder[0]
    except Exception:
        folder = None
    # Fallback older API
    if not folder:
        try:
            add = getattr(parent, "AddSubFolder", None)
            if callable(add):
                folder = add(name)
        except Exception:
            folder = None
    if folder:
        print(f"  + Created: {name}")
    else:
        print(f"  ⚠️ Could not create folder: {name}")
    return folder


def main():
    resolve = get_resolve()
    pm = resolve.GetProjectManager()
    proj = pm.GetCurrentProject() or pm.CreateProject("ZZZ_SAFE_PROBE")
    if not proj:
        print("❌ No project available.")
        return
    print("✅ Project:", proj.GetName())

    mp = proj.GetMediaPool()
    root = mp.GetRootFolder()
    if not root:
        print("❌ MediaPool root missing.")
        return

    # Folder probe
    print("📂 Folder probe:")
    probe_folder = get_or_create_folder(mp, root, "ZZZ_PROBE")
    if not probe_folder:
        print("❌ Folder creation failed. Your AddSubFolder signature differs.")
        return

    # Timeline probe (uses project defaults)
    print("🎞️ Timeline probe:")
    import contextlib

    with contextlib.suppress(Exception):
        mp.SetCurrentFolder(probe_folder)
    tl = mp.CreateEmptyTimeline("ZZZ_PROBE_TIMELINE")
    if not tl:
        print("❌ CreateEmptyTimeline failed.")
        return

    # Track probe
    try:
        tl.AddTrack("video")
        tl.AddTrack("audio")
        tl.SetTrackName("video", 1, "V1 | PROBE")
        tl.SetTrackName("audio", 1, "A1 | PROBE")
        print("✅ Tracks added & named (V1/A1).")
    except Exception as e:
        print("⚠️ Track ops warning:", e)

    print("🎯 Probe completed — check Media Pool for ZZZ_PROBE + ZZZ_PROBE_TIMELINE.")
    print("   No deletes were performed.")


if __name__ == "__main__":
    main()
