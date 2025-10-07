# Makefile for DaVinci Resolve scripting workspace
PYTHON ?= python3

.PHONY: help format lint fix check test clean all

help: ## Show this help message
	@echo "DaVinci Resolve Scripting Workspace"
	@echo "===================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

format: ## Format code with Black
	$(PYTHON) -m black . --line-length 100

lint: ## Lint code with Ruff (report only)
	ruff check . --config ruff.toml

fix: ## Fix linting issues with Ruff (auto-fix enabled)
	ruff check . --config ruff.toml --fix

check: ## Run full check (lint + format)
	ruff check . --config ruff.toml
	$(PYTHON) -m black . --line-length 100 --check

test: ## Test Resolve environment probe
	@echo "Testing Resolve scripting environment..."
	$(PYTHON) resolve_env_probe.py

clean: ## Clean cache files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

all: clean fix format check ## Run complete workflow: clean, fix, format, check
