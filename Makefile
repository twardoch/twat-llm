# this_file: Makefile
# Makefile for twat-llm package development

.PHONY: help install build test clean lint format type-check coverage benchmarks release docs

# Colors
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m

# Default target
help:
	@echo "$(BLUE)twat-llm Development Commands$(NC)"
	@echo ""
	@echo "$(GREEN)Development:$(NC)"
	@echo "  install     Install package and dependencies"
	@echo "  clean       Clean build artifacts and cache"
	@echo "  format      Format code with ruff"
	@echo "  lint        Run linting checks"
	@echo "  type-check  Run type checking with mypy"
	@echo ""
	@echo "$(GREEN)Testing:$(NC)"
	@echo "  test        Run test suite"
	@echo "  test-fast   Run tests without coverage"
	@echo "  test-cov    Run tests with coverage"
	@echo "  test-slow   Run all tests including slow ones"
	@echo "  benchmarks  Run performance benchmarks"
	@echo ""
	@echo "$(GREEN)Building:$(NC)"
	@echo "  build       Build package distributions"
	@echo "  build-check Build and run all checks"
	@echo ""
	@echo "$(GREEN)Release:$(NC)"
	@echo "  release-patch  Create patch release (x.y.z)"
	@echo "  release-minor  Create minor release (x.y.0)"
	@echo "  release-major  Create major release (x.0.0)"
	@echo "  release-dry    Preview release without making changes"
	@echo ""
	@echo "$(GREEN)Utilities:$(NC)"
	@echo "  docs        Generate documentation"
	@echo "  check-deps  Check for outdated dependencies"
	@echo "  security    Run security checks"

# Installation
install:
	@echo "$(BLUE)Installing package and dependencies...$(NC)"
	python -m pip install --upgrade pip
	python -m pip install -e ".[dev,test,all]"
	@echo "$(GREEN)Installation complete\!$(NC)"

# Cleaning
clean:
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	rm -rf build/ dist/ *.egg-info/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache/ .coverage htmlcov/ .mypy_cache/
	@echo "$(GREEN)Cleaning complete\!$(NC)"

# Code formatting
format:
	@echo "$(BLUE)Formatting code...$(NC)"
	python -m ruff format src/ tests/
	python -m ruff check --fix src/ tests/
	@echo "$(GREEN)Code formatting complete\!$(NC)"

# Linting
lint:
	@echo "$(BLUE)Running linting checks...$(NC)"
	python -m ruff check src/ tests/
	@echo "$(GREEN)Linting complete\!$(NC)"

# Type checking
type-check:
	@echo "$(BLUE)Running type checking...$(NC)"
	python -m mypy src/twat_llm tests/
	@echo "$(GREEN)Type checking complete\!$(NC)"

# Testing
test:
	@echo "$(BLUE)Running test suite...$(NC)"
	./scripts/test.sh
	@echo "$(GREEN)Tests complete\!$(NC)"

test-fast:
	@echo "$(BLUE)Running fast tests...$(NC)"
	python -m pytest tests/ -x --tb=short
	@echo "$(GREEN)Fast tests complete\!$(NC)"

test-cov:
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	./scripts/test.sh --coverage
	@echo "$(GREEN)Tests with coverage complete\!$(NC)"

test-slow:
	@echo "$(BLUE)Running all tests including slow ones...$(NC)"
	./scripts/test.sh --slow --coverage
	@echo "$(GREEN)All tests complete\!$(NC)"

benchmarks:
	@echo "$(BLUE)Running performance benchmarks...$(NC)"
	./scripts/test.sh --benchmarks
	@echo "$(GREEN)Benchmarks complete\!$(NC)"

# Building
build:
	@echo "$(BLUE)Building package...$(NC)"
	./scripts/build.sh
	@echo "$(GREEN)Build complete\!$(NC)"

build-check: clean lint type-check test build
	@echo "$(GREEN)Full build check complete\!$(NC)"

# Release
release-patch:
	@echo "$(BLUE)Creating patch release...$(NC)"
	./scripts/release.sh --patch

release-minor:
	@echo "$(BLUE)Creating minor release...$(NC)"
	./scripts/release.sh --minor

release-major:
	@echo "$(BLUE)Creating major release...$(NC)"
	./scripts/release.sh --major

release-dry:
	@echo "$(BLUE)Preview release (dry run)...$(NC)"
	./scripts/release.sh --patch --dry-run

# Documentation
docs:
	@echo "$(BLUE)Generating documentation...$(NC)"
	@echo "$(YELLOW)Documentation generation not yet implemented$(NC)"
	@echo "$(YELLOW)Consider adding sphinx or mkdocs setup$(NC)"

# Utilities
check-deps:
	@echo "$(BLUE)Checking for outdated dependencies...$(NC)"
	pip list --outdated || echo "$(YELLOW)No outdated packages$(NC)"

security:
	@echo "$(BLUE)Running security checks...$(NC)"
	@if command -v bandit >/dev/null 2>&1; then \
		bandit -r src/; \
	else \
		echo "$(YELLOW)bandit not installed. Installing...$(NC)"; \
		pip install bandit; \
		bandit -r src/; \
	fi

# Quick development workflow
dev-setup: clean install
	@echo "$(GREEN)Development environment setup complete\!$(NC)"

quick-check: lint type-check test-fast
	@echo "$(GREEN)Quick development check complete\!$(NC)"

full-check: clean lint type-check test-cov build
	@echo "$(GREEN)Full development check complete\!$(NC)"

# CI/CD simulation
ci-test:
	@echo "$(BLUE)Running CI-like test suite...$(NC)"
	make clean
	make install
	make lint
	make type-check
	make test-cov
	make build
	@echo "$(GREEN)CI test simulation complete\!$(NC)"

# Version info
version:
	@echo "$(BLUE)Package version information:$(NC)"
	@python -c "import twat_llm; print(f'Version: {twat_llm.__version__}')" 2>/dev/null || echo "Package not installed"
	@git describe --tags --abbrev=0 2>/dev/null  < /dev/null |  sed 's/^/Git tag: /' || echo "No git tags found"
	@git rev-parse --short HEAD 2>/dev/null | sed 's/^/Git commit: /' || echo "Not a git repository"

# Environment info
env-info:
	@echo "$(BLUE)Environment information:$(NC)"
	@echo "Python version: $$(python --version)"
	@echo "UV version: $$(uv --version 2>/dev/null || echo 'not installed')"
	@echo "Git version: $$(git --version 2>/dev/null || echo 'not installed')"
	@echo "Working directory: $$(pwd)"
	@echo "Virtual environment: $${VIRTUAL_ENV:-not activated}"

# Watch mode for development
watch:
	@echo "$(BLUE)Watching for changes...$(NC)"
	@echo "$(YELLOW)This requires 'watchdog' package$(NC)"
	@if command -v watchmedo >/dev/null 2>&1; then \
		watchmedo shell-command --patterns="*.py" --recursive --command="make quick-check" src/ tests/; \
	else \
		echo "$(RED)watchdog not installed. Install with: pip install watchdog$(NC)"; \
	fi
