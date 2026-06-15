#!/usr/bin/env bash
# Set up .opencode/skills symlinks (the directory is git-ignored)
# Run from repo root: bash init.sh

set -e

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
SKILLS_DIR="$REPO_ROOT/.opencode/skills"

mkdir -p "$SKILLS_DIR"

# skills-creator
if [ ! -e "$SKILLS_DIR/skills-creator" ]; then
  ln -s ../../skills-creator "$SKILLS_DIR/skills-creator"
  echo "Created symlink: $SKILLS_DIR/skills-creator -> ../../skills-creator"
else
  echo "Already exists: $SKILLS_DIR/skills-creator"
fi

# travel-planner
if [ ! -e "$SKILLS_DIR/travel-planner" ]; then
  ln -s ../../travel-planner "$SKILLS_DIR/travel-planner"
  echo "Created symlink: $SKILLS_DIR/travel-planner -> ../../travel-planner"
else
  echo "Already exists: $SKILLS_DIR/travel-planner"
fi

echo "Done."
