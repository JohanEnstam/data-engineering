#!/bin/bash

# Data Engineering Git Hygiene Validation Script
# This script checks for violations in Git hygiene and prevents build artifacts from being committed

set -e

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
TIMESTAMP=$(date +%Y-%m-%d_%H:%M:%S)
LOGS_DIR="$PROJECT_ROOT/scripts/operations/maintenance/logs"
REPORT_FILE="$LOGS_DIR/git-hygiene-report-$TIMESTAMP.txt"

# Create logs directory if it doesn't exist
mkdir -p "$LOGS_DIR"

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Parse command line arguments
SCAN_MODE="full"  # Default to full scan
CHECK_TYPE="all"  # Default to all checks
while [[ $# -gt 0 ]]; do
    case $1 in
        --incremental|-i)
            SCAN_MODE="incremental"
            shift
            ;;
        --full|-f)
            SCAN_MODE="full"
            shift
            ;;
        --check|-c)
            CHECK_TYPE="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --incremental, -i              Only check staged files (FAST)"
            echo "  --full, -f                     Check all files in project (SLOW, default)"
            echo "  --check, -c CHECK_TYPE         Check specific type (build|deps|env|all)"
            echo "  --help, -h                     Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 --incremental               # Fast check of staged files only"
            echo "  $0 --full                      # Complete check of all files"
            echo "  $0 --check build               # Check build artifacts only"
            echo "  $0 --check deps                # Check dependencies only"
            echo "  $0 --check env                 # Check environment files only"
            echo "  $0                             # Default: full check"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

echo "🔍 Data Engineering Git Hygiene Validation"
echo "=========================================="
echo -e "Scan Mode: ${BLUE}$SCAN_MODE${NC}"
echo -e "Check Type: ${PURPLE}$CHECK_TYPE${NC}"
echo ""

# Function to get files to check based on scan mode
get_files_to_check() {
    local files_to_check=()
    
    if [[ "$SCAN_MODE" == "incremental" ]]; then
        echo -e "${BLUE}📊 Incremental Mode: Checking only staged files...${NC}"
        
        # Check if we're in a git repository
        if ! git rev-parse --git-dir > /dev/null 2>&1; then
            echo -e "${RED}❌ Not a git repository! Falling back to full scan.${NC}"
            SCAN_MODE="full"
            # Fall through to full scan
        else
            # Get staged files
            local staged_files
            staged_files=$(git diff --cached --name-only 2>/dev/null || echo "")
            
            if [[ -z "$staged_files" ]]; then
                echo -e "${GREEN}✅ No staged files detected - nothing to check!${NC}"
                return 0
            fi
            
            # Convert to array
            while IFS= read -r file; do
                if [[ -n "$file" ]]; then
                    files_to_check+=("$file")
                fi
            done <<< "$staged_files"
        fi
    fi
    
    if [[ "$SCAN_MODE" == "full" ]]; then
        echo -e "${BLUE}📊 Full Mode: Checking all files in project...${NC}"
        
        # Get all tracked files
        if git rev-parse --git-dir > /dev/null 2>&1; then
            while IFS= read -r file; do
                if [[ -n "$file" ]]; then
                    files_to_check+=("$file")
                fi
            done < <(git ls-files)
        else
            # Fallback: find all files
            while IFS= read -r file; do
                if [[ -n "$file" ]]; then
                    files_to_check+=("$file")
                fi
            done < <(find . -type f -not -path "./.git/*" -not -path "./node_modules/*" -not -path "./venv/*" -not -path "./.next/*")
        fi
    fi
    
    echo -e "${GREEN}📋 Found ${#files_to_check[@]} files to check${NC}"
    echo ""
    
    # Return array
    echo "${files_to_check[@]}"
}

# Function to check for build artifacts
check_build_artifacts() {
    local violations=0
    local files_to_check=($1)
    
    echo -e "${PURPLE}🔨 Checking for build artifacts...${NC}"
    
    for file in "${files_to_check[@]}"; do
        # Check for Next.js build artifacts
        if [[ "$file" =~ \.next/ ]]; then
            echo -e "${RED}❌ Build artifact detected: $file${NC}"
            echo "   → This should be in .gitignore"
            violations=$((violations + 1))
        fi
        
        # Check for TypeScript build info
        if [[ "$file" =~ \.tsbuildinfo$ ]]; then
            echo -e "${RED}❌ TypeScript build info: $file${NC}"
            echo "   → This should be in .gitignore"
            violations=$((violations + 1))
        fi
        
        # Check for build directories
        if [[ "$file" =~ /(build|dist|out)/ ]]; then
            echo -e "${RED}❌ Build directory detected: $file${NC}"
            echo "   → This should be in .gitignore"
            violations=$((violations + 1))
        fi
    done
    
    return $violations
}

# Function to check for dependencies
check_dependencies() {
    local violations=0
    local files_to_check=($1)
    
    echo -e "${PURPLE}📦 Checking for dependencies...${NC}"
    
    for file in "${files_to_check[@]}"; do
        # Check for node_modules
        if [[ "$file" =~ node_modules/ ]]; then
            echo -e "${RED}❌ Node.js dependencies detected: $file${NC}"
            echo "   → This should be in .gitignore"
            violations=$((violations + 1))
        fi
        
        # Check for Python virtual environments
        if [[ "$file" =~ /(venv|env|ENV)/ ]]; then
            echo -e "${RED}❌ Python virtual environment detected: $file${NC}"
            echo "   → This should be in .gitignore"
            violations=$((violations + 1))
        fi
        
        # Check for Python cache
        if [[ "$file" =~ __pycache__/ ]] || [[ "$file" =~ \.pyc$ ]]; then
            echo -e "${RED}❌ Python cache detected: $file${NC}"
            echo "   → This should be in .gitignore"
            violations=$((violations + 1))
        fi
    done
    
    return $violations
}

# Function to check for environment files
check_environment_files() {
    local violations=0
    local files_to_check=($1)
    
    echo -e "${PURPLE}🔐 Checking for environment files...${NC}"
    
    for file in "${files_to_check[@]}"; do
        # Check for environment files
        if [[ "$file" =~ \.env$ ]] || [[ "$file" =~ \.env\. ]]; then
            # Allow .env.template files
            if [[ "$file" =~ \.env\.template$ ]]; then
                continue
            fi
            echo -e "${RED}❌ Environment file detected: $file${NC}"
            echo "   → This should be in .gitignore"
            violations=$((violations + 1))
        fi
        
        # Check for log files
        if [[ "$file" =~ \.log$ ]]; then
            echo -e "${RED}❌ Log file detected: $file${NC}"
            echo "   → This should be in .gitignore"
            violations=$((violations + 1))
        fi
    done
    
    return $violations
}

# Function to check for data files
check_data_files() {
    local violations=0
    local files_to_check=($1)
    
    echo -e "${PURPLE}📊 Checking for data files...${NC}"
    
    for file in "${files_to_check[@]}"; do
        # Check for large data files
        if [[ "$file" =~ \.(csv|json|pkl)$ ]]; then
            # Skip if it's a small config file
            if [[ "$file" =~ (package\.json|package-lock\.json|tsconfig\.json|tailwind\.config\.js) ]]; then
                continue
            fi
            
            echo -e "${YELLOW}⚠️  Data file detected: $file${NC}"
            echo "   → Consider if this should be in .gitignore"
            violations=$((violations + 1))
        fi
        
        # Check for GTFS data directories
        if [[ "$file" =~ /(gtfs|gtfs_rt)/ ]]; then
            echo -e "${RED}❌ GTFS data detected: $file${NC}"
            echo "   → This should be in .gitignore"
            violations=$((violations + 1))
        fi
    done
    
    return $violations
}

# Main validation logic
main() {
    local total_violations=0
    
    # Get files to check
    local files_to_check
    files_to_check=$(get_files_to_check)
    
    if [[ -z "$files_to_check" ]]; then
        echo -e "${GREEN}✅ No files to check - all good!${NC}"
        return 0
    fi
    
    # Convert to array
    local files_array=($files_to_check)
    
    # Run checks based on type
    if [[ "$CHECK_TYPE" == "all" ]] || [[ "$CHECK_TYPE" == "build" ]]; then
        check_build_artifacts "${files_array[*]}"
        total_violations=$((total_violations + $?))
    fi
    
    if [[ "$CHECK_TYPE" == "all" ]] || [[ "$CHECK_TYPE" == "deps" ]]; then
        check_dependencies "${files_array[*]}"
        total_violations=$((total_violations + $?))
    fi
    
    if [[ "$CHECK_TYPE" == "all" ]] || [[ "$CHECK_TYPE" == "env" ]]; then
        check_environment_files "${files_array[*]}"
        total_violations=$((total_violations + $?))
    fi
    
    if [[ "$CHECK_TYPE" == "all" ]]; then
        check_data_files "${files_array[*]}"
        total_violations=$((total_violations + $?))
    fi
    
    echo ""
    echo "=========================================="
    
    if [[ $total_violations -eq 0 ]]; then
        echo -e "${GREEN}✅ Git hygiene validation passed!${NC}"
        echo -e "${GREEN}   No violations found${NC}"
        return 0
    else
        echo -e "${RED}❌ Git hygiene validation failed!${NC}"
        echo -e "${RED}   Found $total_violations violation(s)${NC}"
        echo ""
        echo -e "${YELLOW}🔧 To fix violations:${NC}"
        echo "   1. Add problematic files to .gitignore"
        echo "   2. Remove files from Git tracking: git rm --cached <file>"
        echo "   3. Run this script again to verify"
        return 1
    fi
}

# Run main function
main
