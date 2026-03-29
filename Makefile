# =============================================================================
# imdbapi-client — Docker-only developer contract
#
# Usage:
#   make help
#   make <target>
#
# All supported developer commands execute through Docker Compose so local
# linting, testing, formatting, coverage, and pre-commit do not depend on a
# host-managed uv environment.
# =============================================================================

.PHONY: help build editor-up editor-down ci-down shell lint format typecheck test \
	coverage test-coverage pre-commit detect-secrets check init up down logs \
	run run-dev setup

.DEFAULT_GOAL := help

COMPOSE ?= docker compose
SERVICE ?= imdbapi
GIT_DIR_HOST := $(shell git rev-parse --git-dir)
SOURCE_PATHS := src tests
COVERAGE_XML ?= coverage.xml
COVERAGE_HTML ?= htmlcov
JUNIT_XML ?= test-results.xml

help:
	@echo ""
	@echo "imdbapi-client — available targets"
	@echo "=================================="
	@echo ""
	@echo "  Editor"
	@echo "    editor-up      Start only the editor container for VS Code attach"
	@echo "    editor-down    Stop the editor container and remove compose resources"
	@echo "    shell          Open a shell in the editor container"
	@echo ""
	@echo "  Lifecycle"
	@echo "    init           Build the dev image used by Docker Compose"
	@echo "    up             Start the container in the background (alias for editor-up)"
	@echo "    down           Stop the container and remove compose resources (alias for editor-down)"
	@echo "    logs           Follow the container logs"
	@echo "    ci-down        Full cleanup for CI: stop containers and remove volumes + local images"
	@echo ""
	@echo "  Quality"
	@echo "    lint           Run ruff check inside Docker"
	@echo "    format         Run ruff format inside Docker"
	@echo "    typecheck      Run mypy --strict inside Docker"
	@echo "    test           Run pytest inside Docker"
	@echo "    test-coverage  Run pytest with coverage + JUnit output inside Docker"
	@echo "    detect-secrets Run detect-secrets inside Docker"
	@echo "    pre-commit     Run pre-commit hooks inside Docker"
	@echo "    check          Convenience alias: lint + typecheck + test"
	@echo ""
	@echo "  Compatibility aliases"
	@echo "    build          Alias for init"
	@echo "    run            Alias for up"
	@echo "    run-dev        Alias for up"
	@echo "    setup          Alias for init"
	@echo ""

build:
	IMDBAPI_GIT_DIR="$(GIT_DIR_HOST)" $(COMPOSE) build $(SERVICE)

init: build

up: editor-up

down: editor-down

editor-up:
	IMDBAPI_GIT_DIR="$(GIT_DIR_HOST)" $(COMPOSE) up -d $(SERVICE)

editor-down:
	IMDBAPI_GIT_DIR="$(GIT_DIR_HOST)" $(COMPOSE) down --remove-orphans

ci-down:
	IMDBAPI_GIT_DIR="$(GIT_DIR_HOST)" $(COMPOSE) down -v --rmi local --remove-orphans

logs:
	IMDBAPI_GIT_DIR="$(GIT_DIR_HOST)" $(COMPOSE) logs -f $(SERVICE)

shell:
	@if IMDBAPI_GIT_DIR="$(GIT_DIR_HOST)" $(COMPOSE) ps --services --status running | grep -qx "$(SERVICE)"; then \
		IMDBAPI_GIT_DIR="$(GIT_DIR_HOST)" $(COMPOSE) exec $(SERVICE) sh; \
	else \
		IMDBAPI_GIT_DIR="$(GIT_DIR_HOST)" $(COMPOSE) run --rm --build $(SERVICE) sh; \
	fi

lint:
	IMDBAPI_GIT_DIR="$(GIT_DIR_HOST)" $(COMPOSE) run --rm --build --no-deps $(SERVICE) ruff check $(SOURCE_PATHS)

format:
	IMDBAPI_GIT_DIR="$(GIT_DIR_HOST)" $(COMPOSE) run --rm --build --no-deps $(SERVICE) ruff format $(SOURCE_PATHS)

typecheck:
	IMDBAPI_GIT_DIR="$(GIT_DIR_HOST)" $(COMPOSE) run --rm --build --no-deps $(SERVICE) mypy $(SOURCE_PATHS)

test:
	IMDBAPI_GIT_DIR="$(GIT_DIR_HOST)" $(COMPOSE) run --rm --build --no-deps $(SERVICE) \
		pytest tests/ --asyncio-mode=auto -v --tb=short

coverage:
	IMDBAPI_GIT_DIR="$(GIT_DIR_HOST)" $(COMPOSE) run --rm --build --no-deps $(SERVICE) \
		pytest tests/ --asyncio-mode=auto -v --tb=short \
		--cov=src \
		--cov-report=term-missing \
		--cov-report=xml:$(COVERAGE_XML) \
		--cov-report=html:$(COVERAGE_HTML) \
		--junitxml=$(JUNIT_XML)

test-coverage: coverage

detect-secrets:
	IMDBAPI_GIT_DIR="$(GIT_DIR_HOST)" $(COMPOSE) run --rm --build --no-deps $(SERVICE) \
		detect-secrets scan --baseline .secrets.baseline

pre-commit:
	IMDBAPI_GIT_DIR="$(GIT_DIR_HOST)" $(COMPOSE) run --rm --build --no-deps $(SERVICE) pre-commit run --all-files

check: lint typecheck test

run: up
run-dev: up
setup: init
