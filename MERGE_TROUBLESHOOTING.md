# Merge Troubleshooting Guide

## Problem Description
You may experience merge troubles when your Git repository is configured with:
1. **Shallow Clone**: Repository cloned with limited history (`--depth=1`)
2. **Limited Fetch Refspec**: Only one branch configured for fetching

## Symptoms
- Unable to merge branches properly
- Error messages about missing commits or objects
- Cannot pull updates from other branches
- `git log` shows "(grafted)" notation indicating incomplete history

## Root Cause
The repository was cloned as a **shallow clone** with a restricted fetch configuration that only includes the current working branch. This causes issues because:
- Git doesn't have the complete history needed to perform merges
- Other branches aren't fetched from the remote repository
- The merge base cannot be properly determined

## Solution Applied

### 1. Unshallow the Repository
```bash
git fetch --unshallow
```
This command fetches the complete history from the remote repository, converting the shallow clone into a full clone.

### 2. Update Fetch Refspec
```bash
git config --unset remote.origin.fetch
git config --add remote.origin.fetch "+refs/heads/*:refs/remotes/origin/*"
```
This updates the Git configuration to fetch all branches from the remote repository, not just the current branch.

### 3. Fetch All Branches
```bash
git fetch origin
```
This fetches all branches from the remote with the new configuration.

## Verification
After applying the fix, you can verify everything works:

```bash
# Check repository is no longer shallow
git rev-parse --is-shallow-repository
# Should output: false

# View all available branches
git branch -a
# Should show all remote branches

# Test merging (dry run)
git merge origin/main --no-commit --no-ff
git merge --abort  # to cancel the test merge

# Test pulling updates
git pull
```

## Prevention
To avoid this issue in the future:
1. **Clone with full history**: Avoid using `--depth` flag when cloning
2. **Use standard fetch refspec**: Ensure `remote.origin.fetch` includes all branches
3. **Regular full clones**: For CI/CD pipelines, prefer full clones over shallow clones when merging is required

## Current Repository Status
✅ Repository is now a **full clone** (not shallow)
✅ Fetch refspec configured to fetch **all branches**
✅ All remote branches are available locally
✅ Merging works correctly in both directions

## Additional Resources
- [Git Shallow Clones Documentation](https://git-scm.com/docs/git-clone#Documentation/git-clone.txt---depthltdepthgt)
- [Git Fetch Refspecs](https://git-scm.com/book/en/v2/Git-Internals-The-Refspec)
