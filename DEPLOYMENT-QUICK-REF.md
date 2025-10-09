# 🚀 QUICK DEPLOYMENT REFERENCE

## For AI Assistants Working on DEGA Scripts

---

### ⚡ CRITICAL RULE

**ALWAYS DEPLOY AFTER CODE CHANGES**

DaVinci Resolve does NOT run scripts from the dev directory.  
Changes are invisible until deployed.

---

### 📍 Two Locations to Know

| Location | Purpose | Path |
|----------|---------|------|
| **Dev Directory** | Where AI edits code | `/Users/rodneywright/Developer/FAMO Show Labs/resolve-dega-scripts/` |
| **Resolve Directory** | Where Resolve runs code | `/Users/rodneywright/Library/Application Support/.../Scripts/Utility/` |

---

### 🔄 Standard Workflow

```bash
# 1. Navigate to dev directory
cd /Users/rodneywright/Developer/FAMO\ Show\ Labs/resolve-dega-scripts

# 2. Make code changes to the_dega_template_full.py
# (AI uses replace_string_in_file or multi_replace_string_in_file)

# 3. Deploy changes
./deploy.sh

# 4. Verify success message appears
```

---

### 📋 AI Task Checklist

When modifying `the_dega_template_full.py`:

- [ ] Complete ALL code changes
- [ ] Run `./deploy.sh`
- [ ] Check for "✅ DEPLOYMENT COMPLETE" message
- [ ] Confirm no red error messages
- [ ] Tell user "Deployed and ready to test in Resolve"

---

### 🎯 One-Command Deploy

```bash
cd /Users/rodneywright/Developer/FAMO\ Show\ Labs/resolve-dega-scripts && ./deploy.sh
```

Copy-paste this into `run_in_terminal` tool.

---

### ✅ Success Indicators

After running deploy.sh, you should see:

```
✅ Source file found
✅ Target directory exists
✅ Copy successful
✅ Verification: File exists at target location
✅ DEPLOYMENT COMPLETE
```

---

### ❌ Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Source file not found` | Wrong directory | `cd` to correct directory |
| `Permission denied` | Script not executable | `chmod +x deploy.sh` |
| `No such file` | Typo in path | Check file exists with `ls` |

---

### 📢 AI Communication Template

After successful deployment, say:

```
✅ Changes deployed successfully!

Changes made:
- [list what you changed]

Deployment confirmed:
- Location: ~/Library/.../Scripts/Utility/the_dega_template_full.py
- Version: vX.X
- Status: Ready to test

To run in Resolve:
Workspace ▸ Scripts ▸ Utility ▸ the_dega_template_full
```

---

### 🆘 Emergency Commands

```bash
# List recent backups
ls -lht "$HOME/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility"/*.backup_* | head -5

# Restore from backup
cp "$HOME/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility/the_dega_template_full.py.backup_TIMESTAMP" "$HOME/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility/the_dega_template_full.py"

# Revert dev file from git
cd /Users/rodneywright/Developer/FAMO\ Show\ Labs/resolve-dega-scripts
git checkout the_dega_template_full.py
```

---

### 🔗 Full Documentation

- **Detailed Guide:** `DEPLOYMENT-AI-GUIDE.md`
- **Deploy Script:** `deploy.sh`
- **Release Notes:** `RELEASE-NOTES-v4.6.md`

---

**Remember:** NO deployment = NO changes in Resolve!

---

*Last Updated: October 8, 2025*
