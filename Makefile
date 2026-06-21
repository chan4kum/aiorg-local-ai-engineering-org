# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  OpenClaw AI Engineering Organization — Makefile                            ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

.DEFAULT_GOAL := help
SHELL := /bin/bash
.PHONY: help install dev test lint format docker-up docker-down migrate seed clean

# ── Variables ────────────────────────────────────────────────────────────────
PYTHON := python3
POETRY := poetry
DOCKER_COMPOSE := docker compose
APP_NAME := openclaw
SRC_DIR := src/openclaw
TEST_DIR := tests
MIGRATIONS_DIR := migrations

# Colors for terminal output
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

# ═══════════════════════════════════════════════════════════════════════════════
# HELP
# ═══════════════════════════════════════════════════════════════════════════════

help: ## Show this help message
	@echo ""
	@echo "$(BLUE)OpenClaw AI Engineering Organization$(RESET)"
	@echo "$(BLUE)════════════════════════════════════$(RESET)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""

# ═══════════════════════════════════════════════════════════════════════════════
# SETUP & INSTALLATION
# ═══════════════════════════════════════════════════════════════════════════════

install: ## Install all dependencies via Poetry
	$(POETRY) install --with dev,docs
	$(POETRY) run pre-commit install

install-prod: ## Install production dependencies only
	$(POETRY) install --only main --no-interaction

setup: ## First-time project setup (install + env + hooks)
	@echo "$(BLUE)🔧 Running first-time setup...$(RESET)"
	cp -n .env.example .env 2>/dev/null || true
	$(MAKE) install
	$(MAKE) docker-up-deps
	@sleep 5
	$(MAKE) migrate
	@echo "$(GREEN)✅ Setup complete! Run 'make dev' to start developing.$(RESET)"

# ═══════════════════════════════════════════════════════════════════════════════
# DEVELOPMENT
# ═══════════════════════════════════════════════════════════════════════════════

dev: ## Start FastAPI dev server with hot-reload
	$(POETRY) run uvicorn openclaw.main:app \
		--host 0.0.0.0 \
		--port 8000 \
		--reload \
		--reload-dir $(SRC_DIR) \
		--log-level debug

dev-worker: ## Start Celery worker for background tasks
	$(POETRY) run celery -A openclaw.worker worker \
		--loglevel=info \
		--concurrency=4 \
		--queues=default,agents,code_execution

dev-beat: ## Start Celery beat scheduler
	$(POETRY) run celery -A openclaw.worker beat \
		--loglevel=info \
		--scheduler=celery.beat:PersistentScheduler

dev-all: ## Start all development services (API + worker + frontend deps)
	@echo "$(BLUE)🚀 Starting all development services...$(RESET)"
	$(MAKE) docker-up-deps
	@sleep 3
	$(MAKE) -j3 dev dev-worker dev-beat

shell: ## Open an interactive Python shell with app context
	$(POETRY) run ipython -i -c "from openclaw.main import app; print('App context loaded')"

# ═══════════════════════════════════════════════════════════════════════════════
# TESTING
# ═══════════════════════════════════════════════════════════════════════════════

test: ## Run all tests
	$(POETRY) run pytest $(TEST_DIR) -v

test-unit: ## Run unit tests only
	$(POETRY) run pytest $(TEST_DIR) -v -m unit

test-integration: ## Run integration tests (requires Docker services)
	$(POETRY) run pytest $(TEST_DIR) -v -m integration

test-e2e: ## Run end-to-end tests
	$(POETRY) run pytest $(TEST_DIR) -v -m e2e

test-cov: ## Run tests with coverage report
	$(POETRY) run pytest $(TEST_DIR) \
		--cov=$(SRC_DIR) \
		--cov-report=term-missing \
		--cov-report=html:reports/coverage \
		--cov-report=xml:reports/coverage.xml \
		-v

test-watch: ## Run tests in watch mode
	$(POETRY) run ptw -- -v --tb=short

test-parallel: ## Run tests in parallel
	$(POETRY) run pytest $(TEST_DIR) -v -n auto

# ═══════════════════════════════════════════════════════════════════════════════
# LINTING & FORMATTING
# ═══════════════════════════════════════════════════════════════════════════════

lint: ## Run all linters
	@echo "$(BLUE)🔍 Running linters...$(RESET)"
	$(POETRY) run ruff check $(SRC_DIR) $(TEST_DIR)
	$(POETRY) run mypy $(SRC_DIR)
	@echo "$(GREEN)✅ All lint checks passed.$(RESET)"

lint-fix: ## Auto-fix linting issues
	$(POETRY) run ruff check --fix $(SRC_DIR) $(TEST_DIR)

format: ## Format code with Black and isort
	$(POETRY) run black $(SRC_DIR) $(TEST_DIR)
	$(POETRY) run isort $(SRC_DIR) $(TEST_DIR)
	$(POETRY) run ruff format $(SRC_DIR) $(TEST_DIR)

format-check: ## Check formatting without making changes
	$(POETRY) run black --check $(SRC_DIR) $(TEST_DIR)
	$(POETRY) run isort --check-only $(SRC_DIR) $(TEST_DIR)

type-check: ## Run mypy type checking
	$(POETRY) run mypy $(SRC_DIR) --show-error-codes

security-check: ## Run security audit on dependencies
	$(POETRY) run pip-audit
	$(POETRY) run bandit -r $(SRC_DIR) -c pyproject.toml

# ═══════════════════════════════════════════════════════════════════════════════
# DATABASE & MIGRATIONS
# ═══════════════════════════════════════════════════════════════════════════════

migrate: ## Run all pending database migrations
	$(POETRY) run alembic -c $(MIGRATIONS_DIR)/alembic.ini upgrade head

migrate-down: ## Rollback the last migration
	$(POETRY) run alembic -c $(MIGRATIONS_DIR)/alembic.ini downgrade -1

migrate-new: ## Create a new migration (usage: make migrate-new MSG="add users table")
	$(POETRY) run alembic -c $(MIGRATIONS_DIR)/alembic.ini revision --autogenerate -m "$(MSG)"

migrate-history: ## Show migration history
	$(POETRY) run alembic -c $(MIGRATIONS_DIR)/alembic.ini history --verbose

migrate-current: ## Show current migration version
	$(POETRY) run alembic -c $(MIGRATIONS_DIR)/alembic.ini current

migrate-reset: ## Reset database (drop all, re-migrate, re-seed) ⚠️ DESTRUCTIVE
	@echo "$(RED)⚠️  WARNING: This will destroy all data!$(RESET)"
	@read -p "Are you sure? [y/N] " confirm && [ "$$confirm" = "y" ] || exit 1
	$(POETRY) run alembic -c $(MIGRATIONS_DIR)/alembic.ini downgrade base
	$(POETRY) run alembic -c $(MIGRATIONS_DIR)/alembic.ini upgrade head
	$(MAKE) seed

seed: ## Seed database with sample data
	$(POETRY) run python -m openclaw.db.seed

# ═══════════════════════════════════════════════════════════════════════════════
# DOCKER
# ═══════════════════════════════════════════════════════════════════════════════

docker-up: ## Start all Docker services (full stack)
	$(DOCKER_COMPOSE) up -d --build

docker-up-deps: ## Start only infrastructure dependencies (DB, Redis, Qdrant, etc.)
	$(DOCKER_COMPOSE) up -d postgres redis qdrant litellm otel-collector langfuse

docker-down: ## Stop all Docker services
	$(DOCKER_COMPOSE) down

docker-down-clean: ## Stop all services and remove volumes ⚠️ DESTRUCTIVE
	@echo "$(RED)⚠️  WARNING: This will destroy all Docker volumes!$(RESET)"
	@read -p "Are you sure? [y/N] " confirm && [ "$$confirm" = "y" ] || exit 1
	$(DOCKER_COMPOSE) down -v --remove-orphans

docker-logs: ## Tail logs from all services
	$(DOCKER_COMPOSE) logs -f

docker-logs-api: ## Tail logs from API service only
	$(DOCKER_COMPOSE) logs -f api

docker-ps: ## Show running containers
	$(DOCKER_COMPOSE) ps

docker-build: ## Build all Docker images
	$(DOCKER_COMPOSE) build --no-cache

docker-restart: ## Restart all services
	$(DOCKER_COMPOSE) restart

# ═══════════════════════════════════════════════════════════════════════════════
# DOCUMENTATION
# ═══════════════════════════════════════════════════════════════════════════════

docs: ## Build documentation
	$(POETRY) run mkdocs build

docs-serve: ## Serve documentation locally with hot-reload
	$(POETRY) run mkdocs serve -a localhost:8080

# ═══════════════════════════════════════════════════════════════════════════════
# CLEANUP
# ═══════════════════════════════════════════════════════════════════════════════

clean: ## Remove build artifacts, caches, and temp files
	@echo "$(BLUE)🧹 Cleaning up...$(RESET)"
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .coverage htmlcov/ reports/
	@echo "$(GREEN)✅ Clean complete.$(RESET)"

clean-docker: ## Remove unused Docker resources
	docker system prune -f
	docker volume prune -f

# ═══════════════════════════════════════════════════════════════════════════════
# CI/CD HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

ci-lint: ## CI-specific lint target (strict, no fix)
	$(POETRY) run ruff check $(SRC_DIR) $(TEST_DIR) --output-format=github
	$(POETRY) run mypy $(SRC_DIR) --no-error-summary
	$(POETRY) run black --check $(SRC_DIR) $(TEST_DIR)

ci-test: ## CI-specific test target
	$(POETRY) run pytest $(TEST_DIR) \
		-v \
		--tb=short \
		--junitxml=reports/junit.xml \
		--cov=$(SRC_DIR) \
		--cov-report=xml:reports/coverage.xml \
		-n auto

ci-build: ## Build Docker images for CI
	$(DOCKER_COMPOSE) build --parallel

# ═══════════════════════════════════════════════════════════════════════════════
# UTILITY
# ═══════════════════════════════════════════════════════════════════════════════

check-env: ## Verify all required environment variables are set
	@echo "$(BLUE)🔍 Checking environment variables...$(RESET)"
	@test -f .env || (echo "$(RED)❌ .env file not found. Run: cp .env.example .env$(RESET)" && exit 1)
	@echo "$(GREEN)✅ .env file exists$(RESET)"
	@$(POETRY) run python -c "from openclaw.config import get_settings; s = get_settings(); print('✅ Settings loaded successfully')" 2>/dev/null || \
		echo "$(YELLOW)⚠️  Could not validate settings (app may not be installed yet)$(RESET)"

show-routes: ## Display all registered API routes
	$(POETRY) run python -c "from openclaw.main import app; [print(f'{r.methods} {r.path}') for r in app.routes]"

generate-key: ## Generate a secure random key
	@$(PYTHON) -c "import secrets; print(secrets.token_urlsafe(48))"
