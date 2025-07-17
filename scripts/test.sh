#!/bin/bash
# this_file: scripts/test.sh
# Test script for twat-llm package

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

# Parse command line arguments
RUN_BENCHMARKS=false
RUN_COVERAGE=false
RUN_SLOW_TESTS=false
PARALLEL_TESTS=true
VERBOSE=false
SPECIFIC_TEST=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --benchmarks)
            RUN_BENCHMARKS=true
            shift
            ;;
        --coverage)
            RUN_COVERAGE=true
            shift
            ;;
        --slow)
            RUN_SLOW_TESTS=true
            shift
            ;;
        --no-parallel)
            PARALLEL_TESTS=false
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --test=*)
            SPECIFIC_TEST="${1#*=}"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --benchmarks    Run benchmark tests"
            echo "  --coverage      Run with coverage reporting"
            echo "  --slow          Run slow integration tests"
            echo "  --no-parallel   Disable parallel test execution"
            echo "  --verbose, -v   Verbose output"
            echo "  --test=NAME     Run specific test or test file"
            echo "  --help, -h      Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

print_status "Starting test suite for twat-llm..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    print_error "uv is not installed. Please install it first:"
    echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Install test dependencies
print_status "Installing test dependencies..."
uv pip install --upgrade pip
uv pip install -e ".[dev,test]"

# Build pytest command
PYTEST_ARGS=()

# Add specific test if provided
if [ -n "$SPECIFIC_TEST" ]; then
    PYTEST_ARGS+=("$SPECIFIC_TEST")
else
    PYTEST_ARGS+=("tests/")
fi

# Add parallel execution if enabled
if [ "$PARALLEL_TESTS" = true ]; then
    PYTEST_ARGS+=("-n" "auto")
fi

# Add verbose output if requested
if [ "$VERBOSE" = true ]; then
    PYTEST_ARGS+=("-v")
fi

# Add coverage if requested
if [ "$RUN_COVERAGE" = true ]; then
    PYTEST_ARGS+=("--cov=src/twat_llm" "--cov=tests" "--cov-report=term-missing" "--cov-report=html:htmlcov")
fi

# Add benchmark marker if requested
if [ "$RUN_BENCHMARKS" = true ]; then
    PYTEST_ARGS+=("-m" "benchmark")
    print_status "Running benchmark tests..."
else
    PYTEST_ARGS+=("-m" "not benchmark")
fi

# Add slow tests if requested
if [ "$RUN_SLOW_TESTS" = true ]; then
    print_status "Including slow integration tests..."
    # Add any slow test markers here
else
    print_status "Skipping slow tests (use --slow to include)"
fi

# Add other useful pytest options
PYTEST_ARGS+=("--tb=short")  # Shorter traceback format
PYTEST_ARGS+=("--strict-markers")  # Fail on unknown markers
PYTEST_ARGS+=("--disable-warnings")  # Disable warnings for cleaner output

# Run the tests
print_status "Running test command: uv run pytest ${PYTEST_ARGS[*]}"
if uv run pytest "${PYTEST_ARGS[@]}"; then
    print_success "Test suite passed!"
else
    print_error "Test suite failed!"
    exit 1
fi

# Show coverage report if generated
if [ "$RUN_COVERAGE" = true ]; then
    print_status "Coverage report generated in htmlcov/index.html"
    if command -v open &> /dev/null; then
        print_status "Opening coverage report in browser..."
        open htmlcov/index.html
    elif command -v xdg-open &> /dev/null; then
        print_status "Opening coverage report in browser..."
        xdg-open htmlcov/index.html
    fi
fi

# Show benchmark results if run
if [ "$RUN_BENCHMARKS" = true ]; then
    print_status "Benchmark results saved in benchmark/ directory"
fi

print_success "All tests completed successfully!"

# Optional: Run additional checks
if [ "$SPECIFIC_TEST" = "" ]; then
    print_status "Running additional code quality checks..."
    
    # Quick linting check
    if uv run ruff check src/ tests/ --quiet; then
        print_success "Code quality checks passed"
    else
        print_warning "Code quality issues found. Run 'uv run ruff check src/ tests/' for details."
    fi
    
    # Quick type check
    if uv run mypy src/twat_llm tests/ --quiet; then
        print_success "Type checking passed"
    else
        print_warning "Type checking issues found. Run 'uv run mypy src/twat_llm tests/' for details."
    fi
fi

print_status "Test summary:"
print_status "- Use --coverage to generate coverage reports"
print_status "- Use --benchmarks to run performance benchmarks"
print_status "- Use --slow to include slow integration tests"
print_status "- Use --test=<name> to run specific tests"