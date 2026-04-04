# =============================================================================
# imdbapi-client — Docker-only developer contract
#
# Usage:
#   make help
#   make <target>
#
# All developer commands execute through Docker Compose so linting, testing,
# formatting, and pre-commit do not depend on a host-managed Python environment.
#
# Typical first-time flow:
#   make init        # build image + create .env + install git hook
#   make editor-up   # start container for VS Code attach
#   make check       # lint + typecheck + tests with coverage
#
# When the editor container is already running, quality commands (lint, test,
# etc.) use `docker compose exec` instead of creating a new container — faster
# than `docker compose run` for interactive development.
# =============================================================================

.PHONY: help init build setup clean \
	editor-up editor-down ci-down shell logs up down  run run-dev \
	lint format fix typecheck test test-coverage pre-commit detect-secrets check \
	agent clean-docker

.DEFAULT_GOAL := help

COMPOSE ?= docker compose
SERVICE ?= imdbapi
GIT_DIR_HOST := $(shell git rev-parse --git-dir)
GIT_HOOKS_DIR := $(GIT_DIR_HOST)/hooks

# Export so docker compose picks it up automatically (avoids per-command prefix).
export IMDBAPI_GIT_DIR := $(GIT_DIR_HOST)

SOURCE_PATHS := .
COVERAGE_XML ?= coverage.xml
COVERAGE_HTML ?= htmlcov
JUNIT_XML ?= test-results.xml

# ---------------------------------------------------------------------------
# exec when running, run --rm otherwise — avoids container startup overhead
# for interactive development while remaining correct for CI.
# ---------------------------------------------------------------------------
define exec_or_run
	@if $(COMPOSE) ps --services --status running 2>/dev/null | grep -qx "$(SERVICE)"; then \
		$(COMPOSE) exec $(SERVICE) $(1); \
	else \
		$(COMPOSE) run --rm --no-deps $(SERVICE) $(1); \
	fi
endef

help:
	@echo ""
	@echo "imdbapi-client — available targets"
	@echo "=================================="
	@echo ""
	@echo "  Setup"
	@echo "    init           Build image, create .env from template, install git hook"
	@echo ""
	@echo "  Editor"
	@echo "    editor-up      Start the attached-container workspace in the background"
	@echo "    editor-down    Stop the local workspace container"
	@echo "    shell          Open a bash shell in the workspace container"
	@echo ""
	@echo "  Lifecycle"
	@echo "    up             Alias for editor-up"
	@echo "    down           Alias for editor-down"
	@echo "    logs           Follow workspace container logs"
	@echo "    ci-down        Full cleanup for CI: stop containers, remove volumes + local images"
	@echo ""
	@echo "  Quality"
	@echo "    lint           Run ruff check (report only)"
	@echo "    format         Run ruff format (apply)"
	@echo "    fix            Run ruff check --fix + ruff format (apply all auto-fixes)"
	@echo "    typecheck      Run mypy --strict"
	@echo "    test           Run pytest"
	@echo "    test-coverage  Run pytest with coverage + JUnit output"
	@echo "    detect-secrets Run detect-secrets scan"
	@echo "    pre-commit     Run all pre-commit hooks"
	@echo "    check          lint + typecheck + test-coverage"
	@echo ""
	@echo "  Maintenance"
	@echo "    clean          Remove __pycache__, .pytest_cache, .mypy_cache, reports (via Docker)"
	@echo "    clean-docker   Stop containers, remove volumes + local images"
	@echo ""
	@echo "  Compatibility aliases"
	@echo "    build          Alias for init"
	@echo "    run / run-dev  Alias for editor-up"
	@echo "    setup          Alias for init"
	@echo ""
	@echo "  Apps"
	@echo "    agent          Runs LangChain Agent Example"
	@echo ""

init:
	@if [ ! -f .env ]; then cp .env.example .env && echo ">>> .env created from .env.example"; fi
	$(COMPOSE) build $(SERVICE)
	@printf '#!/bin/sh\nexec make pre-commit\n' > $(GIT_HOOKS_DIR)/pre-commit
	@chmod +x $(GIT_HOOKS_DIR)/pre-commit
	@echo ">>> git pre-commit hook installed (calls 'make pre-commit' on every commit)"

build: init
setup: init

editor-up:
	$(COMPOSE) up -d $(SERVICE)

up: editor-up
run: editor-up
run-dev: editor-up

editor-down:
	$(COMPOSE) down --remove-orphans

down: editor-down

ci-down:
	$(COMPOSE) down -v --remove-orphans

logs:
	$(COMPOSE) logs -f $(SERVICE)

shell:
	@if $(COMPOSE) ps --services --status running 2>/dev/null | grep -qx "$(SERVICE)"; then \
		$(COMPOSE) exec $(SERVICE) bash; \
	else \
		$(COMPOSE) run --rm --no-deps $(SERVICE) bash; \
	fi

lint:
	$(call exec_or_run,ruff check $(SOURCE_PATHS))

format:
	$(call exec_or_run,ruff format $(SOURCE_PATHS))

fix:
	$(call exec_or_run,ruff check --fix $(SOURCE_PATHS))
	$(call exec_or_run,ruff format $(SOURCE_PATHS))

typecheck:
	$(call exec_or_run,mypy $(SOURCE_PATHS))

test:
	$(call exec_or_run,pytest tests/ --asyncio-mode=auto -v --tb=short)

test-coverage:
	$(call exec_or_run,pytest tests/ --asyncio-mode=auto -v --tb=short \
		--junitxml=$(JUNIT_XML) \
		--cov=imdbapi \
		--cov-report=term-missing \
		--cov-report=xml:$(COVERAGE_XML) \
		--cov-report=html:$(COVERAGE_HTML))

detect-secrets:
	$(call exec_or_run,detect-secrets scan --baseline .secrets.baseline)

pre-commit:
	$(call exec_or_run,pre-commit run --all-files)

check: lint typecheck test-coverage

clean:
	@echo ">>> Removing Python cache files (via Docker)..."
	$(call exec_or_run,find . -type d -name "__pycache__" -not -path "./.git/*" -exec rm -rf {} + 2>/dev/null || true)
	$(call exec_or_run,find . -type d -name ".pytest_cache" -not -path "./.git/*" -exec rm -rf {} + 2>/dev/null || true)
	$(call exec_or_run,find . -type d -name ".mypy_cache" -not -path "./.git/*" -exec rm -rf {} + 2>/dev/null || true)
	$(call exec_or_run,find . -type d -name ".ruff_cache" -not -path "./.git/*" -exec rm -rf {} + 2>/dev/null || true)
	$(call exec_or_run,find . -name "*.egg-info" -not -path "./.git/*" -exec rm -rf {} + 2>/dev/null || true)
	$(call exec_or_run,find . -name "$(COVERAGE_XML)" -not -path "./.git/*" -delete 2>/dev/null || true)
	$(call exec_or_run,find . -name "$(JUNIT_XML)" -not -path "./.git/*" -delete 2>/dev/null || true)
	$(call exec_or_run,find . -type d -name "$(COVERAGE_HTML)" -not -path "./.git/*" -exec rm -rf {} + 2>/dev/null || true)
	@echo "Clean complete."

clean-docker: ci-down

agent:
	$(call exec_or_run,python examples/langchain_agent_example.py)
