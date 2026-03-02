# Git Workflow Strategy

## 🎯 Golden Rule
**NEVER commit directly to `main`**. Always use feature branches.

---

## 📋 Standard Workflow (Follow Every Time)

### 1. Before Starting Any Work

```bash
# Ensure you're on main and it's up to date
git checkout main
git pull origin main

# Create a new feature branch with descriptive name
git checkout -b feature/your-feature-name
```

### 2. Branch Naming Convention

Use descriptive prefixes:

- `feature/` - New features (e.g., `feature/add-weekly-results`)
- `fix/` - Bug fixes (e.g., `fix/u10-score-display`)
- `cleanup/` - Code cleanup/refactoring (e.g., `cleanup/remove-old-files`)
- `docs/` - Documentation only (e.g., `docs/update-readme`)
- `hotfix/` - Urgent production fixes (e.g., `hotfix/broken-deployment`)

**Examples:**
```bash
git checkout -b feature/add-table-sorting
git checkout -b fix/font-loading-issue
git checkout -b cleanup/code-review-2026-03-02
```

### 3. Making Changes

```bash
# Make your code changes...

# Check what changed
git status

# Stage specific files (preferred over 'git add .')
git add file1.py file2.py

# Commit with clear message
git commit -m "Add feature X that does Y"
```

### 4. Commit Message Guidelines

**Format:**
```
<type>: <short description>

<optional longer description>
<optional bullet points>
```

**Good Examples:**
```bash
git commit -m "Fix U10 score display to show X - X instead of 0 - 0"

git commit -m "Add weekly results post generation

- Separate boys and girls fixtures
- Max 6 fixtures per post
- Use correct templates"

git commit -m "Remove obsolete scraper and social_media folders"
```

**Bad Examples:**
```bash
git commit -m "fix"
git commit -m "updates"
git commit -m "wip"
```

### 5. Push Your Branch

```bash
# First time pushing a new branch
git push -u origin feature/your-feature-name

# Subsequent pushes
git push
```

### 6. Create Pull Request

1. Go to GitHub: https://github.com/jd1977/scorps-fulltime-scraper
2. Click "Compare & pull request"
3. Add description of changes
4. Review the diff
5. Create pull request

### 7. Merge to Main

**Option A: Merge via GitHub (Recommended)**
1. Review the PR on GitHub
2. Click "Merge pull request"
3. Delete the branch on GitHub

**Option B: Merge Locally**
```bash
# Switch to main
git checkout main

# Merge your feature branch
git merge feature/your-feature-name

# Push to GitHub
git push origin main

# Delete local branch
git branch -d feature/your-feature-name

# Delete remote branch
git push origin --delete feature/your-feature-name
```

### 8. Clean Up

```bash
# Update main
git checkout main
git pull origin main

# Delete merged branch locally
git branch -d feature/your-feature-name
```

---

## 🚨 Emergency Hotfix Workflow

For urgent production fixes:

```bash
# Create hotfix branch from main
git checkout main
git pull origin main
git checkout -b hotfix/critical-issue

# Make fix
# ... edit files ...

# Commit and push
git add .
git commit -m "Hotfix: Fix critical issue X"
git push -u origin hotfix/critical-issue

# Merge immediately (can skip PR for true emergencies)
git checkout main
git merge hotfix/critical-issue
git push origin main

# Clean up
git branch -d hotfix/critical-issue
git push origin --delete hotfix/critical-issue
```

---

## 📝 Daily Workflow Checklist

Before starting work each day:

- [ ] `git checkout main`
- [ ] `git pull origin main`
- [ ] `git checkout -b feature/descriptive-name`

Before finishing work:

- [ ] `git status` (check what changed)
- [ ] `git add <files>` (stage changes)
- [ ] `git commit -m "Clear message"`
- [ ] `git push origin feature/descriptive-name`

---

## 🔄 Keeping Your Branch Updated

If main has changed while you're working:

```bash
# Save your work first
git add .
git commit -m "WIP: Save current work"

# Update from main
git checkout main
git pull origin main

# Go back to your branch
git checkout feature/your-feature-name

# Merge main into your branch
git merge main

# Or rebase (cleaner history, but more advanced)
git rebase main
```

---

## ⚠️ Common Mistakes to Avoid

1. ❌ **DON'T** commit directly to main
   ```bash
   # BAD
   git checkout main
   git add .
   git commit -m "changes"
   ```

2. ❌ **DON'T** use vague commit messages
   ```bash
   # BAD
   git commit -m "fix"
   git commit -m "update"
   ```

3. ❌ **DON'T** commit everything blindly
   ```bash
   # BAD - might include unwanted files
   git add .
   
   # GOOD - be specific
   git add app.py utils.py
   ```

4. ❌ **DON'T** leave branches unmerged for weeks
   - Merge or delete old branches regularly

5. ❌ **DON'T** force push to shared branches
   ```bash
   # DANGEROUS
   git push --force
   ```

---

## 🎓 Quick Reference

### Check Status
```bash
git status                    # What changed?
git branch                    # What branch am I on?
git log --oneline -5          # Recent commits
```

### Undo Changes
```bash
git restore file.py           # Undo unstaged changes
git restore --staged file.py  # Unstage file
git reset HEAD~1              # Undo last commit (keep changes)
```

### View Changes
```bash
git diff                      # Unstaged changes
git diff --staged             # Staged changes
git diff main                 # Compare to main
```

### Branch Management
```bash
git branch                    # List local branches
git branch -a                 # List all branches (including remote)
git branch -d feature/name    # Delete local branch
git push origin --delete feature/name  # Delete remote branch
```

---

## 📊 Workflow Diagram

```
main (protected)
  │
  ├─── feature/add-feature-x
  │    │
  │    ├─ commit: Add feature X
  │    ├─ commit: Fix bug in feature X
  │    └─ commit: Update tests
  │    │
  │    └─── [Pull Request] ──> merge to main
  │
  ├─── fix/score-display
  │    │
  │    ├─ commit: Fix U10 score display
  │    └─ commit: Update tests
  │    │
  │    └─── [Pull Request] ──> merge to main
  │
  └─── cleanup/code-review
       │
       ├─ commit: Remove old files
       ├─ commit: Update docs
       └─ commit: Fix formatting
       │
       └─── [Pull Request] ──> merge to main
```

---

## 🎯 Summary: The 3 Golden Rules

1. **Always branch** - Never commit to main directly
2. **Clear commits** - Write descriptive commit messages
3. **Pull before push** - Keep your branch updated

---

## 🆘 Help! I Made a Mistake

### I committed to main by accident
```bash
# Create a branch with your changes
git branch feature/my-changes

# Reset main to match origin
git reset --hard origin/main

# Switch to your new branch
git checkout feature/my-changes
```

### I need to undo my last commit
```bash
# Keep the changes, undo the commit
git reset HEAD~1

# Discard everything (CAREFUL!)
git reset --hard HEAD~1
```

### I have merge conflicts
```bash
# See which files have conflicts
git status

# Edit the files to resolve conflicts
# Look for <<<<<<< and >>>>>>>

# After fixing
git add resolved-file.py
git commit -m "Resolve merge conflicts"
```

---

**Remember:** When in doubt, create a branch! It's easy to merge, hard to undo commits to main.
