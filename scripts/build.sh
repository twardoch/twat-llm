#!/bin/bash
# this_file: scripts/build.sh
# Build script for twat-llm package

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

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    print_error "pyproject.toml not found. Please run this script from the project root."
    exit 1
fi

print_status "Starting build process for twat-llm..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    print_error "uv is not installed. Please install it first:"
    echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Clean previous builds
print_status "Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info/
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Install build dependencies
print_status "Installing build dependencies..."
uv pip install --upgrade pip
uv pip install build hatchling hatch-vcs

# Install package dependencies
print_status "Installing package dependencies..."
uv pip install -e ".[dev,test]"

# Run code quality checks
print_status "Running code quality checks..."

# Lint with ruff
print_status "Running ruff linter..."
if uv run ruff check src/ tests/; then
    print_success "Ruff linting passed"
else
    print_error "Ruff linting failed"
    exit 1
fi

# Format check with ruff
print_status "Running ruff format check..."
if uv run ruff format --check src/ tests/; then
    print_success "Ruff format check passed"
else
    print_error "Ruff format check failed. Run 'uv run ruff format src/ tests/' to fix."
    exit 1
fi

# Type checking with mypy
print_status "Running mypy type checking..."
if uv run mypy src/twat_llm tests/; then
    print_success "MyPy type checking passed"
else
    print_error "MyPy type checking failed"
    exit 1
fi

# Run tests
print_status "Running test suite..."
if uv run pytest tests/ -v --cov=src/twat_llm --cov-report=term-missing; then
    print_success "Test suite passed"
else
    print_error "Test suite failed"
    exit 1
fi

# Build the package
print_status "Building package distributions..."
if uv run python -m build --outdir dist/; then
    print_success "Package built successfully"
else
    print_error "Package build failed"
    exit 1
fi

# Verify built distributions
print_status "Verifying built distributions..."
if [ -n "$(find dist -name '*.whl')" ] && [ -n "$(find dist -name '*.tar.gz')" ]; then
    print_success "Both wheel and source distributions created"
    ls -la dist/
else
    print_error "Missing distribution files"
    exit 1
fi

# Optional: Test installation from built wheel
print_status "Testing installation from built wheel..."
WHEEL_FILE=$(find dist -name "*.whl" | head -1)
if [ -n "$WHEEL_FILE" ]; then
    # Create a temporary environment to test installation
    TEMP_ENV=$(mktemp -d)
    python -m venv "$TEMP_ENV"
    source "$TEMP_ENV/bin/activate"
    
    if pip install "$WHEEL_FILE"; then
        print_success "Wheel installation test passed"
        # Test basic import
        if python -c "import twat_llm; print(f'Version: {twat_llm.__version__}')"; then
            print_success "Package import test passed"
        else
            print_error "Package import test failed"
        fi
    else
        print_error "Wheel installation test failed"
    fi
    
    deactivate
    rm -rf "$TEMP_ENV"
fi

print_success "Build completed successfully!"
print_status "Distribution files available in dist/"
print_status "To install locally: pip install dist/$(basename $(find dist -name '*.whl' | head -1))"
print_status "To publish to PyPI: python -m twine upload dist/*"