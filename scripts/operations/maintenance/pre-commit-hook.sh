#!/bin/bash

# Pre-commit Hook for Data Engineering Project
# This hook runs before each commit to ensure Git hygiene and prevent build artifacts

set -e

# Get the project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
CHECK_SCRIPT="$PROJECT_ROOT/scripts/operations/maintenance/check-git-hygiene.sh"

echo "🔍 Pre-commit: Checking Data Engineering Git hygiene..."
echo "======================================================"

# Check if the validation script exists
if [[ ! -f "$CHECK_SCRIPT" ]]; then
    echo "❌ Git hygiene validation script not found!"
    echo "Expected: $CHECK_SCRIPT"
    exit 1
fi

# Make sure the script is executable
chmod +x "$CHECK_SCRIPT"

# Run incremental validation (fast mode)
echo "🚀 Running Git hygiene validation..."
if "$CHECK_SCRIPT" --incremental; then
    echo ""
    echo "✅ Git hygiene validation passed!"
    echo "🚀 Proceeding with commit..."
    exit 0
else
    echo ""
    echo "❌ Git hygiene validation failed!"
    echo ""
    echo "🔧 To fix issues:"
    echo "   1. Fix the violations listed above"
    echo "   2. Run: $CHECK_SCRIPT --incremental"
    echo "   3. Try committing again"
    echo ""
    echo "💡 For a full scan: $CHECK_SCRIPT --full"
    echo "💡 For specific checks: $CHECK_SCRIPT --help"
    exit 1
fi
