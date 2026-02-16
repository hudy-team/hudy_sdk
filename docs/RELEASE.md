# Release Process

## Prerequisites

1. All tests passing on main branch
2. CHANGELOG.md updated
3. Version numbers decided
4. NPM_TOKEN secret configured in GitHub (for npm)
5. PyPI trusted publishing configured (for PyPI)

## TypeScript SDK Release

1. Update version:
```bash
./scripts/bump-version.sh typescript [major|minor|patch]
```

2. Commit changes:
```bash
git add packages/typescript/package.json
git commit -m "chore(typescript): bump version to X.Y.Z"
git push
```

3. Create and push tag:
```bash
git tag typescript-vX.Y.Z
git push origin typescript-vX.Y.Z
```

4. GitHub Actions will automatically:
   - Run tests
   - Build package
   - Publish to npm
   - Create GitHub release

## Python SDK Release

1. Update version:
```bash
./scripts/bump-version.sh python [major|minor|patch]
```

2. Commit changes:
```bash
git add packages/python/pyproject.toml packages/python/hudy/__init__.py
git commit -m "chore(python): bump version to X.Y.Z"
git push
```

3. Create and push tag:
```bash
git tag python-vX.Y.Z
git push origin python-vX.Y.Z
```

4. GitHub Actions will automatically:
   - Run tests
   - Build package
   - Publish to PyPI
   - Create GitHub release

## Manual Release (if needed)

### TypeScript
```bash
cd packages/typescript
npm run build
npm publish
```

### Python
```bash
cd packages/python
python -m build
twine upload dist/*
```

## Post-Release

1. Update CHANGELOG.md with release date
2. Announce on relevant channels
3. Update documentation if needed
