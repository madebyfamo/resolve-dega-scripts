# Makefile for DaVinci Resolve scripting workspace
PY ?= ../.venv/bin/python

.PHONY: help format lint fix check test clean all

help: ## Show this help message
	@echo "DaVinci Resolve Scripting Workspace"
	@echo "===================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

format: ## Format code with Black
	$(PY) -m black . --line-length 100

lint: ## Lint code with Ruff (report only)
	ruff check . --config ruff.toml

fix: ## Fix linting issues with Ruff (auto-fix enabled)
	ruff check . --config ruff.toml --fix

check: ## Run full check (lint + format)
	ruff check . --config ruff.toml
	$(PY) -m black . --line-length 100 --check

test: ## Test Resolve environment probe
	@echo "Testing Resolve scripting environment..."
	$(PY) resolve_env_probe.py

build: ## Run the template build end-to-end inside Resolve
	$(PY) the_dega_template_full.py

export: ## Export the current project's markers manifest to JSON
	$(PY) export_markers_manifest.py -o markers_manifest.json

verify: export ## Export and verify markers manifest against the open project
	$(PY) verify_markers_manifest.py -i markers_manifest.json --frame-tolerance 1 --out-report markers_verify_report.json
	@echo "Report: markers_verify_report.json"

export-manifest: ## Export markers manifest quietly for automation
	$(PY) export_markers_manifest.py --quiet -o markers_manifest.json

verify-manifest: ## Verify markers manifest quietly for automation
	$(PY) verify_markers_manifest.py --quiet -i markers_manifest.json --frame-tolerance 1 --out-report markers_verify_report.json

ci: export-manifest verify-manifest ## Run automation-friendly export/verify and fail on errors
	@$(PY) -c 'import json, sys; from pathlib import Path; report=json.loads(Path("markers_verify_report.json").read_text(encoding="utf-8")); summary=report.get("summary", {}); warnings=summary.get("warnings", 0); errors=summary.get("errors", 0); print(f"[verify] timelines={summary.get("timelines_checked", 0)} warnings={warnings} errors={errors}"); sys.exit(1 if errors else 0)'

clean: ## Clean cache files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

all: clean fix format check ## Run complete workflow: clean, fix, format, check
