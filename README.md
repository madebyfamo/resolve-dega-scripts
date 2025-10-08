Editor & Workflow Conventions — DaVinci Resolve Scripting Workspace
================================================================

This workspace implements **Context7-aligned best practices** for professional DaVinci Resolve / Fusion Python scripting. Zero‑drama editing, consistent formatting across editors, and predictable behavior inside Resolve.

## 🚀 Quick Start

```bash
# Clone/setup workspace
cd "/Users/[username]/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility"

# Install dependencies (if needed)
pip install black ruff

# Run full workflow
make all

# Test Resolve environment
make test
```

## 📋 TL;DR

- **On save:** Ruff fixes + import sort → then Black formats
- **UTF‑8 + LF**, 4‑space indents, 100‑col ruler
- **Scripts run from Resolve ▸ Workspace ▸ Scripts** (not Terminal)
- **Modern Python 3.11+** with Context7-aligned linting rules

## ⚙️ Configuration Stack

### Core Standards (Context7-aligned)
- **Encoding:** UTF‑8 (no explicit declarations needed in Python 3.11+)
- **Line endings:** LF
- **Indentation:** 4 spaces
- **Line length:** 100 characters
- **Quote style:** Double quotes (Black-compatible)
- **Import organization:** Automatic with isort integration

### Tooling Pipeline
1. **Ruff** (fast Rust-based linter) - primary linting and auto-fixing
2. **Black** (formatter) - consistent code formatting
3. **VS Code integration** - real-time feedback and formatting

## 🔧 Development Commands

```bash
make help        # Show all available commands
make format      # Format code with Black
make lint        # Lint code with Ruff (report only)
make fix         # Auto-fix linting issues
make check       # Full check (lint + format verification)
make test        # Test Resolve environment probe
make clean       # Clean cache files
make all         # Complete workflow: clean, fix, format, check
```

## 📦 Recommended VS Code Extensions

- **ms-python.python** (Python language support)
- **ms-python.black-formatter** (Black formatting)
- **charliermarsh.ruff** (Ruff native server)
- **material-icon-theme** (visual clarity)
- **errorlens** (inline diagnostics)

## 🎯 Running Scripts in Resolve

### From Resolve Menu (Recommended)
Scripts appear in **Resolve ▸ Workspace ▸ Scripts ▸ Utility** and any subfolders you create.

### From External Terminal (macOS)
```zsh
export RESOLVE_SCRIPT_API="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting"
export PYTHONPATH="$PYTHONPATH:$RESOLVE_SCRIPT_API/Modules/"

python3 resolve_env_probe.py
```

Add these exports to `~/.zshrc` for convenience.

## 🤖 AI Coding Guidelines (Context7-Informed)

### API Usage Patterns
```python
# Preferred: Modern import pattern
import DaVinciResolveScript as dvr

# Robust connection with fallbacks
def get_resolve():
    # Try injected bmd module first (when inside Resolve)
    if 'bmd' in globals():
        try:
            return bmd.scriptapp("Resolve")
        except Exception:
            pass

    # Fallback to DaVinciResolveScript
    return dvr.scriptapp("Resolve")
```

### Error Handling Best Practices
```python
# Use contextlib.suppress for cleaner exception handling
import contextlib

with contextlib.suppress(Exception):
    mp.SetCurrentFolder(folder)

# Comprehensive error logging
def safe_api_call(operation_name):
    try:
        result = resolve_api_call()
        log.info(f"✅ {operation_name}: Success")
        return result
    except Exception as e:
        log.error(f"❌ {operation_name}: {e}")
        return None
```

### Code Organization
- **Single responsibility** - Each function has one clear purpose
- **Idempotent operations** - Safe to run multiple times
- **Comprehensive logging** - Track all operations and errors
- **Type hints** - Improve code clarity and catch errors early
- **Docstrings** - Document complex logic and API interactions

## 🔍 Linting Rules (Context7-Aligned)

Our Ruff configuration includes:
- **E, F** - Core pycodestyle and Pyflakes errors
- **I** - Import organization (isort)
- **UP** - Modern Python syntax (pyupgrade)
- **B** - Likely bugs and design problems (bugbear)
- **SIM** - Code simplification suggestions
- **C4** - List/dict comprehension improvements

## 📁 Project Structure

```
/Utility/
├── .vscode/settings.json       # VS Code workspace configuration
├── .editorconfig              # Cross-editor consistency
├── .gitignore                 # Version control exclusions
├── ruff.toml                  # Linting configuration
├── Makefile                   # Development commands
├── README.md                  # This file
├── templates/                 # Script templates
│   ├── python_resolve_template.py
│   └── lua_resolve_template.lua
├── the_dega_template_full.py          # Main production script
├── resolve_env_probe.py       # Environment testing
└── logs/                      # Generated log files (gitignored)
```

## 🚨 Troubleshooting

### Script Menu Issues
- Confirm script is under a **Scripts/** category (Utility/Edit/Color/Fairlight/Comp)
- Check file permissions and naming conventions

### Import Errors in VS Code
- Normal outside Resolve - add `# type: ignore` to silence linters
- Use environment variables for external terminal testing

### API Quirks
- Always check for `None` returns from Resolve API calls
- Use `MediaPool.AddSubFolder(parent, name)` over `parent.AddSubFolder(name)`
- Normalize `GetSubFolders()` vs `GetSubFolderList()` results

## 📚 References

- **Resolve Scripting Reference:** [Community Documentation](https://extremraym.com/cloud/resolve-scripting-doc/index)
- **Context7 Best Practices:** Applied throughout this workspace
- **Google Python Style Guide:** Integrated via Ruff configuration
- **PEP 8:** Modern interpretation with 100-character line length

---

*Workspace optimized for professional DaVinci Resolve scripting with Context7-aligned development practices.*
==============================================

This folder holds small DaVinci Resolve / Fusion Python utilities. The goal: zero‑drama editing, consistent formatting across editors, and predictable behavior inside Resolve.

TL;DR
-----
- **On save:** Ruff fixes + import sort → then Black formats.
- **UTF‑8 + LF**, 4‑space indents, 100‑col ruler.
- Scripts run from **Resolve ▸ Workspace ▸ Scripts** (not Terminal).

Editor Settings (baseline)
--------------------------
- Encoding: **UTF‑8**
- End of line: **LF**
- Indent: **spaces, 4**
- Trim trailing whitespace: **true**
- Insert final newline: **true**
- Editor ruler: **100**
- Format on save: **enabled (Black)**

Recommended VS Code Extensions
------------------------------
- **ms-python.python**
- **ms-python.black-formatter** (Black as the formatter)
- **charliermarsh.ruff** (Ruff native server)
- **material-icon-theme** (optional)
- **errorlens** (optional, inline diagnostics)

VS Code Settings (drop-in)
--------------------------
Place this in `.vscode/settings.json` at the Utility (or subfolder) root:

```json
{
  "files.encoding": "utf8",
  "files.eol": "\n",
  "editor.tabSize": 4,
  "editor.insertSpaces": true,
  "files.trimTrailingWhitespace": true,
  "files.insertFinalNewline": true,
  "editor.wordWrap": "on",

  // Formatting: Black (modern extension)
  "editor.formatOnSave": true,
  "[python]": { "editor.defaultFormatter": "ms-python.black-formatter" },
  "black-formatter.args": ["--line-length", "100"],

  // Ruff: native server + prefer project config
  "ruff.nativeServer": "on",
  "ruff.configurationPreference": "filesystemFirst",
  "ruff.configuration": "./ruff.toml",

  // Auto-fix + import sort on save (Ruff)
  "editor.codeActionsOnSave": {
    "source.fixAll.ruff": true,
    "source.organizeImports.ruff": true
  },

  // If not using ruff.toml, you can keep these here:
  "ruff.lint.select": ["E", "F", "I", "UP", "ISC"],
  "ruff.lint.ignore": ["E501"],

  "editor.fontFamily": "JetBrains Mono, Menlo, Monaco, 'Apple Color Emoji', monospace",
  "editor.rulers": [100]
}
```

Ruff Config (ruff.toml)
-----------------------
Prefer keeping rules in the repository for portability:

```toml
# ruff.toml
line-length = 100
target-version = "py311"

[lint]
select = ["E", "F", "I", "UP", "ISC"]
ignore = ["E501"]  # let Black handle line wrapping

[lint.isort]
combine-as-imports = true
```

Makefile Shortcuts
------------------
```makefile
PY ?= python3

.PHONY: fmt lint fix check

fmt:
	$(PY) -m black . --line-length 100

lint:
	ruff check . --select E,F,I,UP,ISC --ignore E501

fix:
	ruff check . --select E,F,I,UP,ISC --ignore E501 --fix
	$(PY) -m black . --line-length 100

check: lint
```

Running Scripts in Resolve
--------------------------
- Put scripts under:
  - **macOS:** `~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility/`
  - **Windows:** `%AppData%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Utility\`
- They appear in **Resolve ▸ Workspace ▸ Scripts ▸ Utility** (and any subfolders you create).
- Emoji in **strings** is fine; avoid emoji in **file names** to keep shells happy.

## Running Resolve Scripts from an External Terminal (macOS)

To run Resolve Python scripts outside of DaVinci Resolve:

1. Set up the environment variables so Python can find the Resolve scripting API:

    ```zsh
    export RESOLVE_SCRIPT_API="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting"
    export PYTHONPATH="$PYTHONPATH:$RESOLVE_SCRIPT_API/Modules/"
    ```

2. (Optional) If you need the Fusion library for advanced scripts:

    ```zsh
    export RESOLVE_SCRIPT_LIB="/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so"
    ```

3. Run your script:

    ```zsh
    python3 "/Users/rodneywright/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility/resolve_env_probe.py"
    ```

You can add the export lines to your `~/.zshrc` for convenience.

AI Coding Guidelines for Resolve Scripts
---------------------------------------
- Use official API entry points:
  - **Python:** `import DaVinciResolveScript as dvr` → `resolve = dvr.scriptapp("Resolve")`
  - **Lua:** `resolve = bmd.scriptapp("Resolve")`
- Avoid unsupported features:
  - No `async`, no `subprocess`, no non‑bundled modules
- Check for `None`/`nil` on all API calls (Resolve returns `None`/`nil` on failure)
- Comment version‑specific quirks / limitations
- Keep scripts self‑contained and dependency‑light
- For cross‑language examples, document differences explicitly
- Docs: Resolve Scripting Reference (community mirror): https://extremraym.com/cloud/resolve-scripting-doc/index

Troubleshooting Notes
---------------------
- If a menu item doesn’t appear, confirm the script is under a **Scripts/** category (Utility/Edit/Color/Fairlight/Comp).
- If `DaVinciResolveScript` can’t be imported in VS Code, that’s normal outside Resolve. Add `# type: ignore` to silence linters.
- If folder APIs behave oddly, prefer `MediaPool.AddSubFolder(parent, name)`; fall back to `parent.AddSubFolder(name)` and normalize `GetSubFolders()` vs `GetSubFolderList()` results.
