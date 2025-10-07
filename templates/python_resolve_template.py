#!/usr/bin/env python
"""
DaVinci Resolve Python Script Template

Best practices:
- Always use the bundled DaVinciResolveScript module (import as shown below)
- Avoid using unsupported Python features (no async, subprocess, or non-bundled modules)
- Use resolve = scriptapp('Resolve') as entry point
- Check for None on all API calls (Resolve API can return None on failure)
- Add comments for version-specific quirks
"""

import DaVinciResolveScript as dvr_script

resolve = dvr_script.scriptapp("Resolve")
if not resolve:
    raise RuntimeError("Could not connect to DaVinci Resolve scripting API.")

fusion = resolve.Fusion()
project_manager = resolve.GetProjectManager()
project = project_manager.GetCurrentProject()

# Example: Create a new project
# new_project = project_manager.CreateProject("My Project")

# Example: Access media storage
# media_storage = resolve.GetMediaStorage()

# Add your script logic below
