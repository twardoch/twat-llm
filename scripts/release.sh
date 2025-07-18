#!/bin/bash
# this_file: scripts/release.sh
# Release script for twat-llm package

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
RELEASE_TYPE=""
DRY_RUN=false
SKIP_TESTS=false
FORCE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --major)
            RELEASE_TYPE="major"
            shift
            ;;
        --minor)
            RELEASE_TYPE="minor"
            shift
            ;;
        --patch)
            RELEASE_TYPE="patch"
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [RELEASE_TYPE] [OPTIONS]"
            echo "Release types:"
            echo "  --major     Major version (x.0.0)"
            echo "  --minor     Minor version (x.y.0)"
            echo "  --patch     Patch version (x.y.z)"
            echo "Options:"
            echo "  --dry-run   Show what would be done without making changes"
            echo "  --skip-tests Skip running tests before release"
            echo "  --force     Force release even if working directory is dirty"
            echo "  --help, -h  Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 --patch              # Create a patch release"
            echo "  $0 --minor --dry-run    # Preview a minor release"
            echo "  $0 --major --force      # Force a major release"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Validate release type
if [ -z "$RELEASE_TYPE" ]; then
    print_error "Release type is required. Use --major, --minor, or --patch."
    exit 1
fi

print_status "Starting release process for twat-llm..."
print_status "Release type: $RELEASE_TYPE"

# Check if required tools are installed
for cmd in git uv; do
    if ! command -v "$cmd" &> /dev/null; then
        print_error "$cmd is not installed. Please install it first."
        exit 1
    fi
done

# Check git status
if [ "$FORCE" = false ]; then
    if [ -n "$(git status --porcelain)" ]; then
        print_error "Working directory is dirty. Commit or stash changes first."
        print_status "Use --force to override this check."
        exit 1
    fi
fi

# Check if we're on main branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "main" ]; then
    print_warning "Not on main branch (currently on $CURRENT_BRANCH)"
    if [ "$FORCE" = false ]; then
        print_error "Please switch to main branch or use --force to override."
        exit 1
    fi
fi

# Get current version from git tags
CURRENT_VERSION=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
print_status "Current version: $CURRENT_VERSION"

# Calculate new version
calculate_new_version() {
    local current="$1"
    local type="$2"
    
    # Remove 'v' prefix if present
    current=${current#v}
    
    # Split version into components
    IFS='.' read -r major minor patch <<< "$current"
    
    case "$type" in
        major)
            major=$((major + 1))
            minor=0
            patch=0
            ;;
        minor)
            minor=$((minor + 1))
            patch=0
            ;;
        patch)
            patch=$((patch + 1))
            ;;
    esac
    
    echo "v$major.$minor.$patch"
}

NEW_VERSION=$(calculate_new_version "$CURRENT_VERSION" "$RELEASE_TYPE")
print_status "New version: $NEW_VERSION"

if [ "$DRY_RUN" = true ]; then
    print_status "DRY RUN MODE - No actual changes will be made"
    print_status "Would create tag: $NEW_VERSION"
    print_status "Would push tag to origin"
    print_status "GitHub Actions would handle the rest"
    exit 0
fi

# Run tests unless skipped
if [ "$SKIP_TESTS" = false ]; then
    print_status "Running test suite..."
    if ! ./scripts/test.sh --coverage; then
        print_error "Tests failed. Aborting release."
        exit 1
    fi
    print_success "Tests passed!"
else
    print_warning "Skipping tests as requested"
fi

# Run build to ensure everything is working
print_status "Running build process..."
if ! ./scripts/build.sh; then
    print_error "Build failed. Aborting release."
    exit 1
fi
print_success "Build completed successfully!"

# Update CHANGELOG if it exists
if [ -f "CHANGELOG.md" ]; then
    print_status "Updating CHANGELOG.md..."
    # Create a temporary file with the new entry
    temp_changelog=$(mktemp)
    
    # Add new version entry
    echo "# Changelog" > "$temp_changelog"
    echo "" >> "$temp_changelog"
    echo "## [$NEW_VERSION] - $(date +%Y-%m-%d)" >> "$temp_changelog"
    echo "" >> "$temp_changelog"
    echo "### Added" >> "$temp_changelog"
    echo "- New release $NEW_VERSION" >> "$temp_changelog"
    echo "" >> "$temp_changelog"
    
    # Append existing changelog (skip the first line if it's "# Changelog")
    if grep -q "^# Changelog" CHANGELOG.md; then
        tail -n +2 CHANGELOG.md >> "$temp_changelog"
    else
        cat CHANGELOG.md >> "$temp_changelog"
    fi
    
    mv "$temp_changelog" CHANGELOG.md
    
    print_status "CHANGELOG.md updated"
    
    # Stage the changelog
    git add CHANGELOG.md
fi

# Create and push the tag
print_status "Creating git tag: $NEW_VERSION"
git tag -a "$NEW_VERSION" -m "Release $NEW_VERSION"

print_status "Pushing tag to origin..."
git push origin "$NEW_VERSION"

# If we updated the changelog, commit and push that too
if [ -f "CHANGELOG.md" ] && [ -n "$(git status --porcelain CHANGELOG.md)" ]; then
    print_status "Committing changelog update..."
    git commit -m "Update CHANGELOG for $NEW_VERSION"
    git push origin "$CURRENT_BRANCH"
fi

print_success "Release process completed!"
print_status "Tagged release: $NEW_VERSION"
print_status "GitHub Actions will now:"
print_status "- Run the full test suite"
print_status "- Build the package"
print_status "- Publish to PyPI"
print_status "- Create GitHub release with artifacts"
print_status ""
print_status "Monitor the release at: https://github.com/twardoch/twat-llm/actions"
print_status "PyPI release will be available at: https://pypi.org/project/twat-llm/"

# Show next steps
print_status "Next steps:"
print_status "1. Monitor GitHub Actions workflow"
print_status "2. Verify PyPI publication"
print_status "3. Test installation: pip install twat-llm==$NEW_VERSION"
print_status "4. Update documentation if needed"