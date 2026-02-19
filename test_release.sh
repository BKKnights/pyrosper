#!/bin/bash

# Test script to simulate the GitHub Actions workflow locally
# Usage: ./test_release.sh [version]

set -e

VERSION=${1:-0.1.1}
echo "Testing release workflow for version: $VERSION"

# Clean up any existing test artifacts
rm -rf dist/ build/ *.egg-info/

# Create a test tag
echo "Creating test tag v$VERSION..."
git tag -d "v$VERSION" 2>/dev/null || true
git tag "v$VERSION"

# Generate version file
echo "Generating version file..."
uv run python -c "
import setuptools_scm
from setuptools_scm import dump_version
version = setuptools_scm.get_version()
dump_version('.', version, 'src/pyrosper/version.py')
"

# Show the generated version
echo "Generated version file:"
cat src/pyrosper/version.py
echo ""

# Build the package
echo "Building package..."
uv build

# Show what was built
echo "Built packages:"
ls -la dist/

# Test package validation
echo "Validating package..."
uv run twine check dist/*

# Show package contents
echo "Package contents:"
tar -tzf dist/*.tar.gz | head -10
echo ""

echo "Wheel contents:"
unzip -l dist/*.whl | head -10

# Clean up test tag
echo "Cleaning up test tag..."
git tag -d "v$VERSION"

echo ""
echo "✅ Test completed successfully!"
echo "To actually publish, run: uv publish" 