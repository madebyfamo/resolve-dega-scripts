#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚚 DaVinci Resolve 20.2 - Multi-Deliver Export System
Version: 2.0
Automatically queues YouTube masters and Instagram/TikTok vertical exports
"""

import os
import sys
import datetime
from pathlib import Path
import time

# ═══════════════════════════════════════════════════════════════
# 🔧 RESOLVE API INITIALIZATION
# ═══════════════════════════════════════════════════════════════

def get_resolve():
    """Get Resolve instance with proper error handling"""
    try:
        import DaVinciResolveScript as dvr
        return dvr.scriptapp("Resolve")
    except ImportError:
        pass
    
    try:
        from python_get_resolve import GetResolve
        return GetResolve()
    except ImportError:
        pass
    
    # Try direct import from system paths
    resolve_script_paths = [
        "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules",
        os.path.expanduser("~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility")
    ]
    
    for path in resolve_script_paths:
        if os.path.exists(path):
            sys.path.insert(0, path)
            try:
                import DaVinciResolveScript as dvr
                return dvr.scriptapp("Resolve")
            except:
                pass
    
    print("❌ Could not connect to DaVinci Resolve!")
    print("📋 Make sure:")
    print("   • DaVinci Resolve is running")
    print("   • Scripting is enabled in Preferences > System > General")
    sys.exit(1)

# ═══════════════════════════════════════════════════════════════
# 📊 EXPORT CONFIGURATION
# ═══════════════════════════════════════════════════════════════

EXPORT_CONFIG = {
    # 📁 Base export directory
    "base_dir": os.path.expanduser("~/Movies/Exports"),
    
    # 🎬 Timeline patterns to scan
    "patterns": {
        "horizontal": ["01_Master_*"],
        "vertical": ["02_Vertical_*", "02_Social_*"]
    },
    
    # 🎥 YouTube Master Settings
    "youtube": {
        "format": "mp4",
        "codec": "H.264",
        "audio_codec": "aac",
        "quality": "Automatic",
        "suffix": "__YOUTUBE_UHD"
    },
    
    # 📱 Instagram/TikTok Settings
    "social": {
        "format": "mp4", 
        "codec": "H.264",
        "audio_codec": "aac",
        "quality": "Automatic",
        "resolution": {
            "width": 1080,
            "height": 1920
        }
    },
    
    # 🎯 FPS Buckets
    "fps_buckets": {
        23.976: "23.976p",
        23.98: "23.976p",
        24.0: "24p",
        29.97: "29.97p",
        30.0: "30p",
        59.94: "59.94p",
        60.0: "60p"
    },
    
    # ⚙️ Render Settings
    "render_settings": {
        "SelectAllFrames": 1,  # Render full timeline
        "UniqueFilenameStyle": 0,  # Prefix
        "ExportVideo": 1,
        "ExportAudio": 1,
        "ColorSpaceTag": "Same as Project",
        "GammaTag": "Same as Project",
        "NetworkOptimization": 1,
        "AudioBitDepth": 24,
        "AudioSampleRate": 48000
    }
}

# ═══════════════════════════════════════════════════════════════
# 🛠️ HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def print_header(text):
    """Print formatted header"""
    print("\n" + "═" * 60)
    print(f"  {text}")
    print("═" * 60)

def print_status(emoji, text):
    """Print status with emoji"""
    print(f"  {emoji} {text}")

def ensure_dir(path):
    """Create directory if it doesn't exist"""
    Path(path).mkdir(parents=True, exist_ok=True)

def get_fps_bucket(fps):
    """Map FPS to standard bucket"""
    # Find the closest bucket
    for bucket_fps, label in EXPORT_CONFIG["fps_buckets"].items():
        if abs(fps - bucket_fps) < 0.01:  # Tolerance for floating point
            return label
    
    # Default to the exact FPS if no bucket matches
    return f"{fps}p"

def matches_pattern(name, patterns):
    """Check if name matches any pattern"""
    for pattern in patterns:
        # Simple wildcard matching
        pattern_base = pattern.replace("*", "")
        if pattern_base in name:
            return True
    return False

# ═══════════════════════════════════════════════════════════════
# 🔍 TIMELINE SCANNER
# ═══════════════════════════════════════════════════════════════

def scan_timelines(project):
    """Scan and categorize timelines"""
    horizontal = []
    vertical = []
    
    timeline_count = project.GetTimelineCount()
    
    print_status("🔍", f"Scanning {timeline_count} timelines...")
    
    for i in range(1, timeline_count + 1):
        timeline = project.GetTimelineByIndex(i)
        name = timeline.GetName()
        
        # Get timeline properties
        width = float(timeline.GetSetting("timelineResolutionWidth"))
        height = float(timeline.GetSetting("timelineResolutionHeight"))
        fps = float(timeline.GetSetting("timelineFrameRate"))
        
        # Categorize
        if matches_pattern(name, EXPORT_CONFIG["patterns"]["horizontal"]):
            horizontal.append({
                "timeline": timeline,
                "name": name,
                "width": width,
                "height": height,
                "fps": fps
            })
            print_status("🎬", f"Found horizontal: {name}")
            
        elif matches_pattern(name, EXPORT_CONFIG["patterns"]["vertical"]):
            vertical.append({
                "timeline": timeline,
                "name": name,
                "width": width,
                "height": height,
                "fps": fps
            })
            print_status("📱", f"Found vertical: {name}")
    
    return horizontal, vertical

# ═══════════════════════════════════════════════════════════════
# 🎥 YOUTUBE EXPORT
# ═══════════════════════════════════════════════════════════════

def queue_youtube_export(project, timeline_info):
    """Queue YouTube master export"""
    timeline = timeline_info["timeline"]
    name = timeline_info["name"]
    
    # Set current timeline
    project.SetCurrentTimeline(timeline)
    
    # Generate export path
    date_folder = datetime.datetime.now().strftime("%Y-%m-%d")
    export_dir = os.path.join(
        EXPORT_CONFIG["base_dir"],
        date_folder,
        name
    )
    ensure_dir(export_dir)
    
    # Configure filename
    filename = f"{name}{EXPORT_CONFIG['youtube']['suffix']}"
    
    # Set render format and codec
    config = EXPORT_CONFIG["youtube"]
    if not project.SetCurrentRenderFormatAndCodec(config["format"], config["codec"]):
        print_status("❌", f"Failed to set format/codec for {name}")
        return None
    
    # Set render settings
    settings = EXPORT_CONFIG["render_settings"].copy()
    settings["TargetDir"] = export_dir
    settings["CustomName"] = filename
    settings["FormatWidth"] = int(timeline_info["width"])
    settings["FormatHeight"] = int(timeline_info["height"])
    settings["FrameRate"] = timeline_info["fps"]
    settings["AudioCodec"] = config["audio_codec"]
    settings["VideoQuality"] = config["quality"]
    
    project.SetRenderSettings(settings)
    
    # Add render job
    job_id = project.AddRenderJob()
    if job_id:
        print_status("✅", f"Queued YouTube: {filename}")
        print_status("📂", f"Output: {export_dir}")
        return job_id
    else:
        print_status("❌", f"Failed to queue {filename}")
        return None

# ═══════════════════════════════════════════════════════════════
# 📱 INSTAGRAM/TIKTOK EXPORT
# ═══════════════════════════════════════════════════════════════

def queue_social_export(project, timeline_info):
    """Queue Instagram/TikTok vertical export at 1080x1920"""
    timeline = timeline_info["timeline"]
    name = timeline_info["name"]
    fps = timeline_info["fps"]
    
    # Store original settings
    original_width = timeline.GetSetting("timelineResolutionWidth")
    original_height = timeline.GetSetting("timelineResolutionHeight")
    
    # Set current timeline
    project.SetCurrentTimeline(timeline)
    
    # Temporarily change timeline resolution to 1080x1920
    print_status("🔄", f"Temporarily setting {name} to 1080x1920...")
    timeline.SetSetting("timelineResolutionWidth", "1080")
    timeline.SetSetting("timelineResolutionHeight", "1920")
    
    # Generate export path
    date_folder = datetime.datetime.now().strftime("%Y-%m-%d")
    export_dir = os.path.join(
        EXPORT_CONFIG["base_dir"],
        date_folder,
        name
    )
    ensure_dir(export_dir)
    
    # Configure filename with FPS bucket
    fps_label = get_fps_bucket(fps)
    filename = f"{name}__IG_1080x1920__{fps_label}"
    
    # Set render format and codec
    config = EXPORT_CONFIG["social"]
    if not project.SetCurrentRenderFormatAndCodec(config["format"], config["codec"]):
        print_status("❌", f"Failed to set format/codec for {name}")
        # Restore original resolution
        timeline.SetSetting("timelineResolutionWidth", original_width)
        timeline.SetSetting("timelineResolutionHeight", original_height)
        return None
    
    # Set render settings
    settings = EXPORT_CONFIG["render_settings"].copy()
    settings["TargetDir"] = export_dir
    settings["CustomName"] = filename
    settings["FormatWidth"] = config["resolution"]["width"]
    settings["FormatHeight"] = config["resolution"]["height"]
    settings["FrameRate"] = fps
    settings["AudioCodec"] = config["audio_codec"]
    settings["VideoQuality"] = config["quality"]
    
    project.SetRenderSettings(settings)
    
    # Add render job
    job_id = project.AddRenderJob()
    
    # Restore original timeline resolution
    print_status("🔄", f"Restoring {name} to {original_width}x{original_height}...")
    timeline.SetSetting("timelineResolutionWidth", original_width)
    timeline.SetSetting("timelineResolutionHeight", original_height)
    
    if job_id:
        print_status("✅", f"Queued Social: {filename}")
        print_status("📂", f"Output: {export_dir}")
        return job_id
    else:
        print_status("❌", f"Failed to queue {filename}")
        return None

# ═══════════════════════════════════════════════════════════════
# 📊 QUEUE SUMMARY
# ═══════════════════════════════════════════════════════════════

def display_queue_summary(project, job_ids):
    """Display summary of queued jobs"""
    print_header("📊 RENDER QUEUE SUMMARY")
    
    jobs = project.GetRenderJobList()
    queued_count = len([j for j in jobs if j["JobId"] in job_ids])
    
    print_status("📦", f"Total jobs queued: {queued_count}")
    
    # Group by type
    youtube_count = 0
    social_count = 0
    
    for job in jobs:
        if job["JobId"] in job_ids:
            if "YOUTUBE" in job.get("RenderJobName", ""):
                youtube_count += 1
            else:
                social_count += 1
    
    print_status("🎬", f"YouTube masters: {youtube_count}")
    print_status("📱", f"Social verticals: {social_count}")
    
    # Calculate estimated size
    total_duration = sum([job.get("FrameCount", 0) for job in jobs if job["JobId"] in job_ids])
    print_status("⏱️", f"Total frames to render: {total_duration}")

# ═══════════════════════════════════════════════════════════════
# 🎮 RENDER CONTROL
# ═══════════════════════════════════════════════════════════════

def start_rendering(resolve, project, job_ids, auto_start=False):
    """Optionally start rendering"""
    if not auto_start:
        print_header("🎮 RENDER CONTROL")
        print_status("🎯", "Jobs are queued but NOT started")
        print_status("💡", "Go to Deliver page to review and start")
        return
    
    print_header("🚀 STARTING RENDER")
    response = input("  Start rendering now? (y/n): ")
    
    if response.lower() == 'y':
        print_status("🏃", "Starting render...")
        
        # Switch to Deliver page
        resolve.OpenPage("deliver")
        
        # Start rendering  
        if project.StartRendering(*job_ids):
            print_status("✅", "Rendering started!")
            
            # Monitor progress
            while project.IsRenderingInProgress():
                time.sleep(2)
                # Could add progress tracking here
            
            print_status("🎉", "Rendering complete!")
        else:
            print_status("❌", "Failed to start rendering")
    else:
        print_status("⏸️", "Rendering not started - jobs remain in queue")

# ═══════════════════════════════════════════════════════════════
# 🚀 MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════

def main():
    """Main execution flow"""
    print_header("🚚 MULTI-DELIVER EXPORT SYSTEM")
    print_status("📊", "Version 2.0 - YouTube & Social Exports")
    
    # Get Resolve and project
    resolve = get_resolve()
    pm = resolve.GetProjectManager()
    project = pm.GetCurrentProject()
    
    if not project:
        print_status("❌", "No project open!")
        sys.exit(1)
    
    print_status("🎬", f"Project: {project.GetName()}")
    
    # Scan timelines
    horizontal, vertical = scan_timelines(project)
    
    if not horizontal and not vertical:
        print_status("⚠️", "No matching timelines found!")
        print_status("📋", "Looking for:")
        print_status("  •", "Horizontal: 01_Master_*")
        print_status("  •", "Vertical: 02_Vertical_* or 02_Social_*")
        sys.exit(1)
    
    # Switch to Deliver page
    resolve.OpenPage("deliver")
    
    # Queue exports
    print_header("📦 QUEUEING EXPORTS")
    job_ids = []
    
    # Queue YouTube masters
    if horizontal:
        print_status("🎬", f"Queueing {len(horizontal)} YouTube masters...")
        for tl_info in horizontal:
            job_id = queue_youtube_export(project, tl_info)
            if job_id:
                job_ids.append(job_id)
    
    # Queue social exports
    if vertical:
        print_status("📱", f"Queueing {len(vertical)} social exports...")
        for tl_info in vertical:
            job_id = queue_social_export(project, tl_info)
            if job_id:
                job_ids.append(job_id)
    
    # Display summary
    if job_ids:
        display_queue_summary(project, job_ids)
        
        # Optional: Start rendering
        start_rendering(resolve, project, job_ids, auto_start=False)
    else:
        print_status("❌", "No jobs were queued successfully")
    
    print_header("✨ COMPLETE!")
    print_status("🎯", f"Total jobs queued: {len(job_ids)}")
    print("═" * 60)

if __name__ == "__main__":
    main()