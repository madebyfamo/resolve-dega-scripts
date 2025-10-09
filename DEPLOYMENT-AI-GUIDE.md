# DEPLOYMENT GUIDE FOR AI ASSISTANTS

## 🎯 CRITICAL UNDERSTANDING

**THIS IS ESSENTIAL:** DaVinci Resolve does NOT execute Python scripts from this development directory. Scripts MUST be deployed to a specific location for Resolve to find and run them.

### Directory Structure

```
Development Directory (where AI works):
/Users/rodneywright/Developer/FAMO Show Labs/resolve-dega-scripts/
├── the_dega_template_full.py    ← AI edits this file
├── deploy.sh                     ← Run this to deploy
└── [other dev files]

Execution Directory (where Resolve looks):
/Users/rodneywright/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility/
└── the_dega_template_full.py    ← Resolve runs this file
```

---

## 📋 MANDATORY DEPLOYMENT WORKFLOW

### When AI Makes Changes

**EVERY TIME** you modify `the_dega_template_full.py`, you MUST run the deployment script. The file will NOT work in Resolve until deployed.

### Step-by-Step Process

1. **Make your changes** to `the_dega_template_full.py` in the dev directory
2. **Save the file** (AI should confirm edits are complete)
3. **Run deployment** using the terminal command below
4. **Verify success** by checking the output

---

## 🚀 DEPLOYMENT COMMAND

### First Time Only (Make Script Executable)

```bash
cd /Users/rodneywright/Developer/FAMO\ Show\ Labs/resolve-dega-scripts
chmod +x deploy.sh
```

### Every Deployment (After Changes)

```bash
cd /Users/rodneywright/Developer/FAMO\ Show\ Labs/resolve-dega-scripts
./deploy.sh
```

### Alternative: Full Path Deployment

```bash
/Users/rodneywright/Developer/FAMO\ Show\ Labs/resolve-dega-scripts/deploy.sh
```

---

## ✅ VERIFICATION CHECKLIST

After running `deploy.sh`, verify:

- [ ] Script output shows "✅ DEPLOYMENT COMPLETE"
- [ ] No error messages in red
- [ ] File size displayed matches expectations
- [ ] Version number extracted correctly
- [ ] Target path shown: `/Users/rodneywright/Library/Application Support/.../Utility/the_dega_template_full.py`

---

## 🔄 TYPICAL AI WORKFLOW

### Scenario 1: Bug Fix

```
1. User reports bug in the_dega_template_full.py
2. AI analyzes code and identifies fix
3. AI makes edit using replace_string_in_file tool
4. AI runs: ./deploy.sh
5. AI confirms: "Deployment complete. Ready to test in Resolve."
6. User tests in Resolve
```

### Scenario 2: New Feature

```
1. User requests new feature
2. AI implements feature in the_dega_template_full.py
3. AI updates version number (e.g., v4.6 → v4.7)
4. AI updates docstring with "What's new in vX.X"
5. AI runs: ./deploy.sh
6. AI creates release notes
7. AI confirms: "v4.7 deployed and ready to test."
```

### Scenario 3: Multiple Changes

```
1. AI makes multiple edits to the_dega_template_full.py
2. After ALL edits are complete (not between edits)
3. AI runs: ./deploy.sh ONCE
4. AI confirms deployment
```

---

## ⚠️ COMMON MISTAKES TO AVOID

### ❌ WRONG: Forgetting to Deploy

```
AI: "I've updated the code."
User: "It's not working in Resolve."
Problem: AI didn't run deploy.sh
```

### ❌ WRONG: Deploying Too Early

```
AI runs deploy.sh after first edit
AI makes second edit
AI forgets to deploy again
Problem: Second change not deployed
```

### ❌ WRONG: Wrong Directory

```
AI runs: ./deploy.sh
Error: "deploy.sh: No such file or directory"
Problem: Not in resolve-dega-scripts directory
```

### ✅ CORRECT: Complete Workflow

```
AI: "I'm making 3 changes to the code..."
AI: [makes all 3 changes]
AI: "All changes complete. Deploying now..."
AI: [runs deploy.sh]
AI: "✅ Deployment successful. Ready to test in Resolve."
```

---

## 🔍 TROUBLESHOOTING

### Error: "Source file not found"

**Cause:** Wrong directory or filename typo

**Solution:**
```bash
cd /Users/rodneywright/Developer/FAMO\ Show\ Labs/resolve-dega-scripts
ls -la the_dega_template_full.py  # Verify file exists
./deploy.sh
```

### Error: "Permission denied"

**Cause:** Script not executable

**Solution:**
```bash
chmod +x deploy.sh
./deploy.sh
```

### Error: "Directory creation failed"

**Cause:** macOS permissions issue

**Solution:**
```bash
# User may need to grant permissions in System Preferences
# Or manually create directory:
mkdir -p "$HOME/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility"
./deploy.sh
```

### Script Not Appearing in Resolve

**Causes & Solutions:**

1. **Not deployed:** Run `./deploy.sh`
2. **Wrong location:** Check deploy.sh output for target path
3. **Resolve cache:** Restart DaVinci Resolve
4. **Menu location:** Check Workspace ▸ Scripts ▸ Utility (not root Scripts menu)

---

## 📝 AI RESPONSE TEMPLATES

### After Successful Deployment

```
✅ Changes implemented and deployed successfully!

📝 Changes made:
- [List changes]

📦 Deployment:
- Deployed to: /Users/.../Utility/the_dega_template_full.py
- Version: vX.X
- Size: XX KB

🎬 Next steps:
1. Open DaVinci Resolve
2. Go to: Workspace ▸ Scripts ▸ Utility
3. Run: the_dega_template_full
4. Test the changes

Ready for testing!
```

### After Failed Deployment

```
⚠️ Deployment encountered an error.

❌ Error message:
[paste error]

🔍 Diagnosis:
[explain what went wrong]

🔧 Solution:
[provide fix]

Shall I attempt to fix this?
```

---

## 🎓 FOR AI: KEY PRINCIPLES

### 1. **Always Deploy After Changes**

Never tell the user "changes are complete" without deploying. The correct flow is:
1. Make all code changes
2. Deploy
3. Confirm to user

### 2. **Use Terminal Tools**

Always use `run_in_terminal` tool with:
```python
command="cd /Users/rodneywright/Developer/FAMO\ Show\ Labs/resolve-dega-scripts && ./deploy.sh"
explanation="Deploying updated script to DaVinci Resolve"
isBackground=False
```

### 3. **Verify Success**

Check the terminal output for:
- "✅ DEPLOYMENT COMPLETE" message
- No red error messages
- Correct target path shown

### 4. **Communicate Clearly**

Tell user:
- What changed
- That deployment happened
- Where to find script in Resolve
- That it's ready to test

### 5. **Handle Errors Gracefully**

If deployment fails:
- Show the error message
- Explain what it means
- Provide solution steps
- Offer to fix it

---

## 📚 RELATED FILES

- `deploy.sh` - The deployment script itself
- `the_dega_template_full.py` - The main script that gets deployed
- `DEPLOYMENT-AI-GUIDE.md` - This file (comprehensive AI instructions)
- `README.md` - User-facing documentation

---

## 🆘 EMERGENCY RECOVERY

### If Deployed Script is Broken

1. **Restore from backup:**
   ```bash
   cd "$HOME/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility"
   ls -la the_dega_template_full.py.backup_*  # Find latest backup
   cp the_dega_template_full.py.backup_YYYYMMDD_HHMMSS the_dega_template_full.py
   ```

2. **Or redeploy from dev:**
   ```bash
   cd /Users/rodneywright/Developer/FAMO\ Show\ Labs/resolve-dega-scripts
   git checkout the_dega_template_full.py  # Revert to last commit
   ./deploy.sh
   ```

### If Dev File is Corrupted

```bash
cd /Users/rodneywright/Developer/FAMO\ Show\ Labs/resolve-dega-scripts
git status  # Check what changed
git diff the_dega_template_full.py  # Review changes
git checkout the_dega_template_full.py  # Revert if needed
```

---

## 🔐 PERMISSIONS & SECURITY

### File Permissions

The script should be readable and writable:
```bash
chmod 644 the_dega_template_full.py  # In dev directory
```

The deploy script should be executable:
```bash
chmod +x deploy.sh
```

### Directory Permissions

Resolve's Scripts directory should be accessible:
```bash
ls -la "$HOME/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility"
```

If permission denied, user may need to grant access in macOS System Preferences.

---

## 📞 QUICK REFERENCE

### Essential Commands

```bash
# Navigate to dev directory
cd /Users/rodneywright/Developer/FAMO\ Show\ Labs/resolve-dega-scripts

# Deploy script
./deploy.sh

# Check deployed version
grep "DEGA.*Builder.*v" "$HOME/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility/the_dega_template_full.py" | head -1

# List backups
ls -lht "$HOME/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility"/*.backup_*

# View deploy script
cat deploy.sh

# Make deploy script executable
chmod +x deploy.sh
```

### File Paths (Copy-Paste Ready)

```
Dev Directory:
/Users/rodneywright/Developer/FAMO Show Labs/resolve-dega-scripts

Main Script (Dev):
/Users/rodneywright/Developer/FAMO Show Labs/resolve-dega-scripts/the_dega_template_full.py

Deploy Script:
/Users/rodneywright/Developer/FAMO Show Labs/resolve-dega-scripts/deploy.sh

Target Directory:
/Users/rodneywright/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility

Main Script (Deployed):
/Users/rodneywright/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility/the_dega_template_full.py
```

---

**Last Updated:** October 8, 2025  
**Version:** 1.0  
**For:** DaVinci Resolve DEGA Script Deployment
