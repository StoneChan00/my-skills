#!/usr/bin/env bash
# ============================================================
#  sync-pages.sh
#  Sync travel-plans/ + map-collections/ from master to gh-pages branch
#  Usage:  run from repo root as ./scripts/sync-pages.sh
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

# --- Step 1: Verify we're on master ---
CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null)"

if [[ "$CURRENT_BRANCH" == "gh-pages" ]]; then
    echo "[WARN] Already on gh-pages. Staying here."
    exit 0
fi

if [[ "$CURRENT_BRANCH" != "master" ]]; then
    echo "[ERR] You're on branch '$CURRENT_BRANCH'. Switch to master first." >&2
    exit 1
fi

# --- Step 2: Check for uncommitted output changes ---
if ! git diff --quiet travel-plans/ map-collections/ 2>/dev/null; then
    echo "[ERR] You have uncommitted changes in travel-plans/ or map-collections/. Commit them to master first." >&2
    exit 1
fi

# --- Step 3: Checkout gh-pages ---
echo "[1/4] Switching to gh-pages..."
if ! git checkout gh-pages --quiet 2>/dev/null; then
    echo "[ERR] gh-pages branch not found. Did you push it already?" >&2
    exit 1
fi

# --- Step 4: Pull output dirs from master ---
echo "[2/4] Pulling travel-plans/ + map-collections/ from master..."
git checkout master -- travel-plans/ map-collections/ 2>/dev/null || true

# --- Step 5: Check if anything actually changed ---
if git diff --cached --quiet travel-plans/ map-collections/ 2>/dev/null; then
    echo "[INFO] No changes to sync. gh-pages is already up to date."
    git checkout master --quiet
    exit 0
fi

# --- Step 6: Commit + push ---
echo "[3/4] Committing and pushing..."
MASTER_MSG="$(git log master -1 --format='%s' 2>/dev/null)"
git add travel-plans/ map-collections/
git commit -m "sync: $MASTER_MSG" --quiet
if ! git push --quiet; then
    echo "[ERR] Push failed. You're still on gh-pages - fix and switch back manually." >&2
    exit 1
fi

# --- Step 7: Back to master ---
echo "[4/4] Returning to master..."
git checkout master --quiet

echo ""
echo "Done. gh-pages updated."
echo "Pages URL will refresh in 1-2 minutes."
