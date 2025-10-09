#!/bin/bash
################################################################################
# DEGA Script Deployment to DaVinci Resolve
################################################################################
#
# PURPOSE:
#   This script copies the_dega_template_full.py from the development directory
#   to DaVinci Resolve's Scripts/Utility folder where it can be executed.
#
# WHY THIS EXISTS:
#   DaVinci Resolve ONLY looks for scripts in specific locations:
#   - macOS: ~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/
#   - This dev folder is for version control and AI-assisted development
#   - The Resolve folder is where the script must be to actually run
#
# WHEN TO RUN:
#   - After ANY changes to the_dega_template_full.py
#   - Before testing in DaVinci Resolve
#   - After AI makes updates to the code
#   - When deploying a new version (v4.6, v4.7, etc.)
#
# HOW TO RUN:
#   From terminal in this directory:
#     chmod +x deploy.sh    # Only needed once to make executable
#     ./deploy.sh           # Run deployment
#
# WHAT IT DOES:
#   1. Checks if source file exists
#   2. Creates target directory if needed
#   3. Backs up existing script (if any)
#   4. Copies new version to Resolve
#   5. Verifies deployment success
#
################################################################################

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🚀 DEGA Script Deployment to DaVinci Resolve"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ═══════════════════════════════════════════════════════════════════════════
# STEP 1: Define paths
# ═══════════════════════════════════════════════════════════════════════════

# Source: Development folder (where AI makes changes)
SOURCE_FILE="the_dega_template_full.py"
SOURCE_PATH="$(pwd)/${SOURCE_FILE}"

# Target: DaVinci Resolve's Scripts/Utility folder (where Resolve looks)
RESOLVE_SCRIPTS_BASE="$HOME/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts"
RESOLVE_UTILITY="${RESOLVE_SCRIPTS_BASE}/Utility"
TARGET_PATH="${RESOLVE_UTILITY}/${SOURCE_FILE}"

echo "📂 Source (dev):   ${SOURCE_PATH}"
echo "📂 Target (Resolve): ${TARGET_PATH}"
echo ""

# ═══════════════════════════════════════════════════════════════════════════
# STEP 2: Validate source file exists
# ═══════════════════════════════════════════════════════════════════════════

if [ ! -f "${SOURCE_PATH}" ]; then
    echo -e "${RED}❌ ERROR: Source file not found!${NC}"
    echo ""
    echo "Expected location: ${SOURCE_PATH}"
    echo ""
    echo "🔍 Troubleshooting:"
    echo "   1. Verify you're in the correct directory:"
    echo "      pwd should show: /Users/rodneywright/Developer/FAMO Show Labs/resolve-dega-scripts"
    echo "   2. Verify the_dega_template_full.py exists in this directory"
    echo "   3. Check for typos in the filename"
    echo ""
    exit 1
fi

echo -e "${GREEN}✅ Source file found${NC}"

# ═══════════════════════════════════════════════════════════════════════════
# STEP 3: Create target directory if it doesn't exist
# ═══════════════════════════════════════════════════════════════════════════

if [ ! -d "${RESOLVE_UTILITY}" ]; then
    echo ""
    echo -e "${YELLOW}📁 Creating Utility directory...${NC}"
    mkdir -p "${RESOLVE_UTILITY}"

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Directory created: ${RESOLVE_UTILITY}${NC}"
    else
        echo -e "${RED}❌ ERROR: Failed to create directory${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ Target directory exists${NC}"
fi

# ═══════════════════════════════════════════════════════════════════════════
# STEP 4: Backup existing script (if present)
# ═══════════════════════════════════════════════════════════════════════════

if [ -f "${TARGET_PATH}" ]; then
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    BACKUP_PATH="${RESOLVE_UTILITY}/${SOURCE_FILE}.backup_${TIMESTAMP}"

    echo ""
    echo -e "${YELLOW}📦 Backing up existing script...${NC}"
    cp "${TARGET_PATH}" "${BACKUP_PATH}"

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Backup created: ${BACKUP_PATH}${NC}"
    else
        echo -e "${RED}⚠️  Warning: Backup failed (continuing anyway)${NC}"
    fi
fi

# ═══════════════════════════════════════════════════════════════════════════
# STEP 5: Copy new version to Resolve
# ═══════════════════════════════════════════════════════════════════════════

echo ""
echo -e "${BLUE}📋 Copying script to Resolve...${NC}"

# Check if files are identical first
if cmp -s "${SOURCE_PATH}" "${TARGET_PATH}"; then
    echo -e "${YELLOW}ℹ️  Files are identical - no copy needed${NC}"
    echo -e "${GREEN}✅ Already up-to-date${NC}"
else
    cp -f "${SOURCE_PATH}" "${TARGET_PATH}"

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Copy successful${NC}"
    else
        echo -e "${RED}❌ ERROR: Copy failed${NC}"
        exit 1
    fi
fi

# ═══════════════════════════════════════════════════════════════════════════
# STEP 6: Verify deployment
# ═══════════════════════════════════════════════════════════════════════════

if [ -f "${TARGET_PATH}" ]; then
    FILE_SIZE=$(ls -lh "${TARGET_PATH}" | awk '{print $5}')
    echo ""
    echo -e "${GREEN}✅ Verification: File exists at target location${NC}"
    echo "   Size: ${FILE_SIZE}"

    # Extract version from file
    VERSION=$(grep -m 1 "DEGA.*Builder.*v[0-9]" "${TARGET_PATH}" | sed -E 's/.*v([0-9]+\.[0-9]+).*/\1/')
    if [ -n "${VERSION}" ]; then
        echo "   Version: v${VERSION}"
    fi
else
    echo -e "${RED}❌ ERROR: Verification failed - file not found at target${NC}"
    exit 1
fi

# ═══════════════════════════════════════════════════════════════════════════
# STEP 7: Success summary
# ═══════════════════════════════════════════════════════════════════════════

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}  ✅ DEPLOYMENT COMPLETE${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 Script location:"
echo "   ${TARGET_PATH}"
echo ""
echo "🎬 Next steps:"
echo "   1. Open DaVinci Resolve"
echo "   2. Go to: Workspace ▸ Scripts"
echo "   3. Look in the 'Utility' submenu"
echo "   4. Click: the_dega_template_full"
echo ""
echo "📝 Notes:"
echo "   - Script will appear in Resolve's menu immediately"
echo "   - No restart needed"
echo "   - Re-run this deploy.sh after ANY code changes"
echo ""
echo "🔄 To deploy future updates:"
echo "   ./deploy.sh"
echo ""

exit 0
