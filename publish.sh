#!/usr/bin/env bash
# publish.sh — Export codelab and update docs/ for GitHub Pages
#
# Prerequisites:
#   claat binary in PATH or current directory
#   curl (for downloading the Cloud Shell button SVG)
#
# Usage:
#   bash publish.sh

set -e

CODELAB_MD="codelab.md"
DOCS_DIR="docs"

# Use local claat.exe if claat is not in PATH
if command -v claat &>/dev/null; then
  CLAAT="claat"
elif [ -f "./claat.exe" ]; then
  CLAAT="./claat.exe"
else
  echo "ERROR: claat not found. Download from https://github.com/googlecodelabs/tools/releases"
  exit 1
fi

# claat panics on external image URLs — download the SVG locally first
echo "==> Downloading Cloud Shell button SVG..."
curl -s -o open-btn.svg "https://gstatic.com/cloudssh/images/open-btn.svg"

echo "==> Exporting codelab..."
$CLAAT export "$CODELAB_MD"

# claat creates a folder named after the codelab id (from frontmatter)
CODELAB_ID=$(grep '^id:' "$CODELAB_MD" | awk '{print $2}' | tr -d '[:space:]')

if [ -z "$CODELAB_ID" ]; then
  echo "ERROR: Could not read codelab id from $CODELAB_MD"
  exit 1
fi

echo "==> Codelab id: $CODELAB_ID"

# Remove old exported folder from docs/ and replace with fresh export
rm -rf "$DOCS_DIR/$CODELAB_ID"
mv "$CODELAB_ID" "$DOCS_DIR/"

# Replace hashed Cloud Shell button img with direct gstatic URL (avoids local path issues)
echo "==> Fixing Cloud Shell button image..."
sed -i -E 's|src="img[/\\]+[a-f0-9]*\.svg"|src="https://gstatic.com/cloudssh/images/open-btn.svg"|g' "$DOCS_DIR/$CODELAB_ID/index.html"

echo "==> Done! Output: $DOCS_DIR/$CODELAB_ID/index.html"
echo ""
echo "Next steps:"
echo "  git add docs/"
echo "  git commit -m 'publish: update codelab'"
echo "  git push"
echo ""
echo "GitHub Pages URL (after push):"
echo "  https://eiyuumiru.github.io/student-study-agent-codelab/$CODELAB_ID/"
