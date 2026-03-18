#!/usr/bin/env bash
# do_commit.sh — safely stage and commit
# Usage: do_commit.sh "<commit-message>" [--push]

set -euo pipefail

MSG="${1:-}"
PUSH="${2:-}"

if [ -z "$MSG" ]; then
  echo "Error: commit message required as first argument"
  exit 1
fi

# Stage all tracked modified files (never secrets)
echo "Staging tracked files..."
git add -u

# Check if there's anything to commit
if git diff --cached --quiet; then
  echo "Nothing staged to commit."
  exit 0
fi

# Commit
git commit -m "$MSG"
echo "✅ Committed: $MSG"

# Show the commit
git log --oneline -1

# Optionally push
if [ "$PUSH" = "--push" ]; then
  BRANCH=$(git rev-parse --abbrev-ref HEAD)
  echo "Pushing to origin/$BRANCH..."
  git push origin "$BRANCH"
  echo "✅ Pushed to origin/$BRANCH"
fi
