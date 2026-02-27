# Git Branching Strategy

## Overview
This project uses a simplified Git Flow branching strategy to maintain code quality and enable safe development.

## Branch Structure

### Main Branches

#### `main`
- **Purpose**: Production-ready code
- **Protection**: Should always be stable and deployable
- **Updates**: Only via Pull Requests from `develop` or `hotfix/*` branches
- **Never**: Commit directly to main

#### `develop` (optional for future)
- **Purpose**: Integration branch for testing features before production
- **Updates**: Merge feature branches here first for testing
- **Then**: Merge to `main` when stable

### Supporting Branches

#### `feature/*`
- **Purpose**: New features or refactoring work
- **Naming**: `feature/description-of-work`
- **Examples**: 
  - `feature/refactor-phase1-utils-config`
  - `feature/add-weekly-results-post`
  - `feature/optimize-scraping`
- **Lifecycle**: 
  1. Branch from `main` (or `develop` if using)
  2. Develop and test
  3. Create Pull Request to merge back
  4. Delete after merge

#### `hotfix/*`
- **Purpose**: Urgent fixes for production issues
- **Naming**: `hotfix/description-of-fix`
- **Examples**: 
  - `hotfix/fix-scraping-timeout`
  - `hotfix/correct-team-name-display`
- **Lifecycle**:
  1. Branch from `main`
  2. Fix and test quickly
  3. Merge directly to `main` (and `develop` if exists)
  4. Delete after merge

## Workflow

### Creating a New Feature

```bash
# 1. Make sure you're on main and up to date
git checkout main
git pull origin main

# 2. Create feature branch
git checkout -b feature/your-feature-name

# 3. Make changes and commit
git add .
git commit -m "Descriptive commit message"

# 4. Push to remote
git push -u origin feature/your-feature-name

# 5. Create Pull Request on GitHub
# Review, test, then merge via GitHub UI

# 6. After merge, clean up
git checkout main
git pull origin main
git branch -d feature/your-feature-name
```

### Creating a Hotfix

```bash
# 1. Branch from main
git checkout main
git pull origin main
git checkout -b hotfix/fix-description

# 2. Make fix and commit
git add .
git commit -m "Fix: description of fix"

# 3. Push and create PR
git push -u origin hotfix/fix-description

# 4. Merge quickly after review
```

## Commit Message Guidelines

### Format
```
Type: Brief description (50 chars or less)

Detailed explanation if needed (wrap at 72 chars)
- Bullet points for multiple changes
- What changed and why
```

### Types
- **Feature**: New feature or enhancement
- **Fix**: Bug fix
- **Refactor**: Code restructuring without changing behavior
- **Docs**: Documentation changes
- **Test**: Adding or updating tests
- **Chore**: Maintenance tasks (dependencies, config, etc.)

### Examples
```
Feature: Add weekly results post with 2-column layout

Refactor: Extract shared utilities to utils.py
- Centralize team name formatting
- Remove duplicate code across modules
- Add type hints for better IDE support

Fix: Correct form guide display on table posts
```

## Pull Request Process

1. **Create PR** on GitHub with descriptive title and description
2. **Self-review** your changes before requesting review
3. **Test** the changes work as expected
4. **Request review** (if working with team)
5. **Address feedback** if any
6. **Merge** using "Squash and merge" for clean history
7. **Delete branch** after merge

## Current Active Branches

- `main` - Production code
- `feature/refactor-phase1-utils-config` - Phase 1 refactoring (utils & config modules)

## Benefits of This Strategy

✅ **Safety**: Main branch always stable
✅ **Clarity**: Clear purpose for each branch
✅ **Collaboration**: Easy to review changes via PRs
✅ **History**: Clean, understandable git history
✅ **Rollback**: Easy to revert if needed
✅ **Parallel Work**: Multiple features can be developed simultaneously

## Tips

- Keep feature branches short-lived (days, not weeks)
- Commit often with clear messages
- Pull from main regularly to avoid conflicts
- Delete branches after merging to keep repo clean
- Use descriptive branch names that explain the work
