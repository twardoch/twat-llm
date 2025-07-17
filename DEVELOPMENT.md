# Development Guide

This document provides comprehensive information about developing, testing, and releasing the `twat-llm` package.

## Quick Start

```bash
# Clone the repository
git clone https://github.com/twardoch/twat-llm.git
cd twat-llm

# Set up development environment
make install

# Run tests
make test

# Build the package
make build
```

## Development Environment Setup

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) (recommended package manager)
- Git

### Installation

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install the package in development mode
uv pip install -e ".[dev,test,all]"

# Or use the convenience script
make install
```

### Pre-commit Hooks

Set up pre-commit hooks to ensure code quality:

```bash
uv pip install pre-commit
pre-commit install
```

## Development Workflow

### Code Quality

The project uses several tools to maintain code quality:

- **Ruff**: Linting and code formatting
- **MyPy**: Static type checking
- **Bandit**: Security vulnerability scanning
- **Pre-commit**: Automated code quality checks

```bash
# Format code
make format

# Run linting
make lint

# Run type checking
make type-check

# Run security checks
make security
```

### Testing

The project has a comprehensive test suite including:

- Unit tests
- Integration tests
- Performance benchmarks
- Cross-platform compatibility tests

```bash
# Run all tests
make test

# Run tests with coverage
make test-cov

# Run only fast tests
make test-fast

# Run performance benchmarks
make benchmarks

# Run specific test file
./scripts/test.sh --test=tests/test_mallmo.py
```

### Test Configuration

Tests are configured through `pyproject.toml` with the following markers:

- `benchmark`: Performance benchmark tests
- Standard pytest markers for categorization

## Build System

The project uses Hatch as the build system with the following features:

- **hatch-vcs**: Automatic versioning from Git tags
- **Cross-platform builds**: Support for Linux, Windows, and macOS
- **Multiple Python versions**: 3.10, 3.11, 3.12

### Building

```bash
# Build distributions
make build

# Build and run all checks
make build-check

# Clean build artifacts
make clean
```

## Release Process

### Versioning

The project uses semantic versioning (SemVer) with automatic version detection from Git tags:

- **Patch releases**: Bug fixes (`v1.0.1`)
- **Minor releases**: New features (`v1.1.0`)
- **Major releases**: Breaking changes (`v2.0.0`)

### Creating a Release

```bash
# Create a patch release
make release-patch

# Create a minor release
make release-minor

# Create a major release
make release-major

# Preview release (dry run)
make release-dry
```

### Manual Release Process

```bash
# Create and push a tag
git tag v1.0.0
git push origin v1.0.0

# GitHub Actions will automatically:
# 1. Run the full test suite
# 2. Build the package
# 3. Publish to PyPI
# 4. Create GitHub release with artifacts
```

## Scripts

The project includes several convenience scripts in the `scripts/` directory:

### `scripts/build.sh`

Comprehensive build script that:
- Installs dependencies
- Runs code quality checks
- Executes test suite
- Builds distributions
- Verifies build artifacts

### `scripts/test.sh`

Flexible test runner with options:
- `--coverage`: Generate coverage reports
- `--benchmarks`: Run performance benchmarks
- `--slow`: Include slow integration tests
- `--verbose`: Verbose output
- `--test=NAME`: Run specific test

### `scripts/release.sh`

Release automation script:
- `--patch/--minor/--major`: Release type
- `--dry-run`: Preview without changes
- `--skip-tests`: Skip test execution
- `--force`: Override safety checks

## Makefile Commands

The project includes a comprehensive Makefile:

### Development Commands

```bash
make install      # Install dependencies
make clean        # Clean build artifacts
make format       # Format code
make lint         # Run linting
make type-check   # Run type checking
```

### Testing Commands

```bash
make test         # Run full test suite
make test-fast    # Run fast tests only
make test-cov     # Run tests with coverage
make benchmarks   # Run performance benchmarks
```

### Build Commands

```bash
make build        # Build distributions
make build-check  # Build with all checks
```

### Release Commands

```bash
make release-patch   # Create patch release
make release-minor   # Create minor release
make release-major   # Create major release
make release-dry     # Preview release
```

### Utility Commands

```bash
make help         # Show all available commands
make version      # Show version information
make env-info     # Show environment information
make security     # Run security checks
```

## GitHub Actions

The project uses GitHub Actions for CI/CD:

### Push Workflow (`.github/workflows/push.yml`)

Runs on every push and pull request:
- **Code Quality**: Ruff linting and formatting
- **Type Checking**: MyPy static analysis
- **Testing**: Multi-platform, multi-Python version testing
- **Build**: Create distributions for all platforms
- **Benchmarks**: Performance regression detection

### Release Workflow (`.github/workflows/release.yml`)

Runs on Git tag creation:
- **Testing**: Full test suite on all platforms
- **Building**: Multi-platform distribution creation
- **Publishing**: Automatic PyPI publication
- **Release**: GitHub release with artifacts

## Configuration Files

### `pyproject.toml`

Main configuration file containing:
- Project metadata
- Dependencies
- Build system configuration
- Tool configurations (Ruff, MyPy, Pytest, etc.)
- Security settings

### `.pre-commit-config.yaml`

Pre-commit hooks configuration:
- Ruff linting and formatting
- MyPy type checking
- Standard Python checks
- Security scanning with Bandit
- Documentation formatting

## Testing Strategy

### Unit Tests

Located in `tests/test_mallmo.py` and `tests/test_twat_llm.py`:
- Test individual functions and classes
- Mock external dependencies
- Verify error handling

### Integration Tests

Located in `tests/test_integration.py`:
- Test complete workflows
- CLI integration
- End-to-end functionality
- Cross-platform compatibility

### Performance Tests

Located in `tests/test_benchmark.py`:
- Performance benchmarking
- Memory usage testing
- Scalability verification
- Throughput measurement

## Security Considerations

### Security Scanning

The project includes security scanning with:
- **Bandit**: Static security analysis
- **Pre-commit hooks**: Automated security checks
- **Dependency scanning**: Vulnerability detection

### Security Best Practices

- No secrets in code or configuration
- Input validation and sanitization
- Secure API key handling
- Regular dependency updates

## Contribution Guidelines

### Code Style

- Follow PEP 8 guidelines
- Use type hints for all functions
- Write comprehensive docstrings
- Maintain test coverage above 80%

### Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Submit pull request with clear description

### Code Review

- All changes require review
- Automated checks must pass
- Tests must maintain coverage
- Documentation must be updated

## Troubleshooting

### Common Issues

1. **UV not installed**: Install with `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. **Test failures**: Check dependencies with `make install`
3. **Build issues**: Clean artifacts with `make clean`
4. **Type errors**: Run `make type-check` for details

### Debug Mode

Enable debug mode for detailed output:
```bash
DEBUG=1 make test
VERBOSE=1 ./scripts/test.sh
```

### Getting Help

- Check the README.md for basic usage
- Review this development guide
- Open an issue on GitHub
- Contact the maintainers

## Performance Optimization

### Profiling

Use the benchmark tests to identify performance bottlenecks:
```bash
make benchmarks
```

### Memory Usage

Monitor memory usage with:
```bash
python -m memory_profiler your_script.py
```

### Optimization Tips

- Use batch processing for multiple requests
- Implement caching for repeated operations
- Profile code before optimization
- Monitor resource usage in production

## Deployment

### Local Installation

```bash
# Install from PyPI
pip install twat-llm

# Install from source
pip install -e .

# Install with all dependencies
pip install "twat-llm[all]"
```

### Docker Usage

```bash
# Build Docker image
docker build -t twat-llm .

# Run container
docker run -it twat-llm python -m twat_llm.mallmo --help
```

### Production Considerations

- Set appropriate API keys
- Configure logging levels
- Monitor resource usage
- Implement error handling
- Use connection pooling

## Future Enhancements

### Planned Features

- Additional LLM provider support
- Enhanced error handling
- Performance optimizations
- Extended documentation
- Plugin system

### Contributing Ideas

- New data source integrations
- Performance improvements
- Documentation enhancements
- Test coverage expansion
- Security improvements

## References

- [Hatch Documentation](https://hatch.pypa.io/)
- [UV Documentation](https://github.com/astral-sh/uv)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [MyPy Documentation](http://mypy-lang.org/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Pre-commit Documentation](https://pre-commit.com/)