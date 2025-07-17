#!/bin/bash
# this_file: scripts/setup.sh
# Setup script for twat-llm development environment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_status "Setting up twat-llm development environment..."

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    print_error "pyproject.toml not found. Please run this script from the project root."
    exit 1
fi

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    print_warning "uv is not installed. Installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source ~/.bashrc || true
    export PATH="$HOME/.local/bin:$PATH"
fi

# Check uv installation
if ! command -v uv &> /dev/null; then
    print_error "Failed to install uv. Please install manually:"
    echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

print_success "UV is available"

# Install the package in development mode
print_status "Installing package in development mode..."
uv pip install --upgrade pip
uv pip install -e ".[dev,test,all]"

# Install pre-commit hooks
print_status "Setting up pre-commit hooks..."
if ! command -v pre-commit &> /dev/null; then
    print_status "Installing pre-commit..."
    uv pip install pre-commit
fi

pre-commit install
print_success "Pre-commit hooks installed"

# Make scripts executable
print_status "Making scripts executable..."
chmod +x scripts/*.sh

# Run initial code quality checks
print_status "Running initial code quality checks..."

# Check if ruff is working
if uv run ruff check --version &> /dev/null; then
    print_success "Ruff is working"
else
    print_error "Ruff is not working correctly"
    exit 1
fi

# Check if mypy is working
if uv run mypy --version &> /dev/null; then
    print_success "MyPy is working"
else
    print_error "MyPy is not working correctly"
    exit 1
fi

# Check if pytest is working
if uv run pytest --version &> /dev/null; then
    print_success "Pytest is working"
else
    print_error "Pytest is not working correctly"
    exit 1
fi

# Run a quick test to ensure everything is working
print_status "Running quick validation tests..."
if uv run python -c "import twat_llm; print(f'Package version: {twat_llm.__version__}')"; then
    print_success "Package import successful"
else
    print_error "Package import failed"
    exit 1
fi

# Test the build process
print_status "Testing build process..."
if uv run python -c "import build; print('Build module available')"; then
    print_success "Build tools available"
else
    print_warning "Build tools not available, installing..."
    uv pip install build hatchling hatch-vcs
fi

# Show available commands
print_status "Available development commands:"
echo ""
echo "  make help        - Show all available commands"
echo "  make test        - Run test suite"
echo "  make build       - Build package"
echo "  make lint        - Run linting"
echo "  make format      - Format code"
echo ""
echo "  ./scripts/test.sh --help      - Test script options"
echo "  ./scripts/build.sh            - Build with all checks"
echo "  ./scripts/release.sh --help   - Release script options"
echo ""

# Check git status
if git rev-parse --git-dir > /dev/null 2>&1; then
    print_success "Git repository detected"
    
    # Check if there are any unstaged changes
    if [ -n "$(git status --porcelain)" ]; then
        print_warning "There are unstaged changes in the repository"
        print_status "Run 'git status' to see the changes"
    else
        print_success "Working directory is clean"
    fi
    
    # Show current branch
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
    print_status "Current branch: $CURRENT_BRANCH"
    
    # Show latest tag
    LATEST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "No tags found")
    print_status "Latest tag: $LATEST_TAG"
else
    print_warning "Not a git repository"
fi

# Final setup verification
print_status "Running final setup verification..."
verification_failed=false

# Check if we can run tests
if ! uv run pytest --collect-only tests/ > /dev/null 2>&1; then
    print_error "Test collection failed"
    verification_failed=true
fi

# Check if we can run linting
if ! uv run ruff check src/ > /dev/null 2>&1; then
    print_error "Linting check failed"
    verification_failed=true
fi

# Check if we can run type checking
if ! uv run mypy src/twat_llm > /dev/null 2>&1; then
    print_error "Type checking failed"
    verification_failed=true
fi

if [ "$verification_failed" = true ]; then
    print_error "Setup verification failed. Please check the errors above."
    exit 1
fi

print_success "Development environment setup completed successfully!"
print_status "Next steps:"
print_status "1. Run 'make test' to run the test suite"
print_status "2. Run 'make build' to build the package"
print_status "3. Check 'DEVELOPMENT.md' for detailed development guide"
print_status "4. Start developing!"

# Optional: Show some useful information
print_status "Development environment info:"
print_status "- Python version: $(python --version)"
print_status "- UV version: $(uv --version)"
print_status "- Working directory: $(pwd)"
print_status "- Package installed in development mode"
print_status "- Pre-commit hooks installed"
print_status "- All development tools configured"