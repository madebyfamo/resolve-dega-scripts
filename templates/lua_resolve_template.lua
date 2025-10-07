--[[
DaVinci Resolve Lua Script Template

Best practices:
- Use the resolve = bmd.scriptapp('Resolve') entry point
- Avoid using unsupported Lua features (no OS calls, no external modules)
- Always check for nil on API calls
- Add comments for version-specific quirks
]]

resolve = bmd.scriptapp('Resolve')
if not resolve then
    error('Could not connect to DaVinci Resolve scripting API.')
end

fusion = resolve:Fusion()
projectManager = resolve:GetProjectManager()
project = projectManager:GetCurrentProject()

-- Example: Create a new project
-- local newProject = projectManager:CreateProject('My Project')

-- Example: Access media storage
-- local mediaStorage = resolve:GetMediaStorage()

-- Add your script logic below
