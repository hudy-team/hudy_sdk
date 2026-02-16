#!/bin/bash
set -e

# Bump version script for Hudy SDK
# Usage: ./scripts/bump-version.sh [typescript|python] [major|minor|patch]

PACKAGE=$1
VERSION_TYPE=$2

if [ -z "$PACKAGE" ] || [ -z "$VERSION_TYPE" ]; then
  echo "Usage: ./scripts/bump-version.sh [typescript|python] [major|minor|patch]"
  exit 1
fi

if [ "$PACKAGE" == "typescript" ]; then
  cd packages/typescript
  npm version $VERSION_TYPE --no-git-tag-version
  NEW_VERSION=$(node -p "require('./package.json').version")
  echo "TypeScript SDK version bumped to $NEW_VERSION"
  echo "Run: git tag typescript-v$NEW_VERSION"

elif [ "$PACKAGE" == "python" ]; then
  cd packages/python
  CURRENT_VERSION=$(python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])")

  # Simple version bumping (you may want to use a tool like bump2version)
  IFS='.' read -ra PARTS <<< "$CURRENT_VERSION"
  MAJOR=${PARTS[0]}
  MINOR=${PARTS[1]}
  PATCH=${PARTS[2]}

  if [ "$VERSION_TYPE" == "major" ]; then
    MAJOR=$((MAJOR + 1))
    MINOR=0
    PATCH=0
  elif [ "$VERSION_TYPE" == "minor" ]; then
    MINOR=$((MINOR + 1))
    PATCH=0
  elif [ "$VERSION_TYPE" == "patch" ]; then
    PATCH=$((PATCH + 1))
  fi

  NEW_VERSION="$MAJOR.$MINOR.$PATCH"

  # Update pyproject.toml (basic sed, consider using toml tools)
  sed -i.bak "s/version = \"$CURRENT_VERSION\"/version = \"$NEW_VERSION\"/" pyproject.toml
  rm pyproject.toml.bak

  # Update __init__.py
  sed -i.bak "s/__version__ = \"$CURRENT_VERSION\"/__version__ = \"$NEW_VERSION\"/" hudy/__init__.py
  rm hudy/__init__.py.bak

  echo "Python SDK version bumped to $NEW_VERSION"
  echo "Run: git tag python-v$NEW_VERSION"

else
  echo "Unknown package: $PACKAGE"
  exit 1
fi
