#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "$REPO_ROOT"

VERSION=$1
if [ -z "$VERSION" ]; then
  echo "Usage: ./scripts/release.sh <version>  (e.g. ./scripts/release.sh 0.8.0)"
  exit 1
fi

# Abort if working tree is dirty
if [ -n "$(git status --porcelain)" ]; then
  echo "ERROR: You have uncommitted changes. Please commit or stash them before releasing."
  git status --short
  exit 1
fi

MAJOR_MINOR=$(echo "$VERSION" | cut -d. -f1,2)

# Update version in pyproject.toml
sed -i "s/^version = .*/version = \"$VERSION\"/" pyproject.toml

# Commit, tag, branch, push
git add -A
git commit -m "release: v$VERSION"
git tag "v$VERSION"
git checkout -b "release/$MAJOR_MINOR"
git push origin main "release/$MAJOR_MINOR" "v$VERSION"
git checkout main

echo "Released v$VERSION (branch: release/$MAJOR_MINOR)"
