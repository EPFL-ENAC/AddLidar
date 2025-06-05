## Git Subtree Explained

Git Subtree allows you to merge external repositories into subdirectories of your main repo while maintaining the ability to sync bidirectionally.

### Key Concepts:

1. **One-way merge**: Initially pulls code from external repo
2. **Bidirectional sync**: Can pull updates from original repos AND push changes back
3. **History preservation**: Maintains commit history from original repos
4. **No external dependencies**: Unlike submodules, everything is in your main repo

## Implications & Workflows

### Syncing FROM original repos (pulling updates):

```bash
git subtree pull --prefix=backend https://github.com/your-org/backend-repo.git main --squash
```

### Contributing BACK to original repos (pushing changes):

```bash
git subtree push --prefix=backend https://github.com/your-org/backend-repo.git feature-branch
```

### Important Notes:

- **Commit granularity**: Changes in monorepo affect the specific subtree
- **Branch management**: You'll typically push to feature branches in original repos, then PR
- **Squashing**: `--squash` creates cleaner history but loses individual commits
- **Without squash**: Preserves all commits but creates more complex history

## Step-by-Step Migration Process

1. **First, update the repository URLs in the Makefile**
2. **Run the initial setup**:

   ```bash
   make subtree-add
   ```

3. **Test the structure and make any adjustments**

4. **When ready to deprecate, run**:

   ```bash
   make deprecate-repos
   ```

5. **Manually complete the deprecation**:
   - Add the generated `DEPRECATED.md` to each original repo
   - Update README files in original repos
   - Archive repositories on GitHub
   - Update any external references

## Best Practices Going Forward

- **Regular syncing**: Run `make subtree-pull` periodically if original repos are still active
- **Careful pushing**: Only push back to original repos if you plan to maintain them temporarily
- **Branch strategy**: When pushing back, always use feature branches, never push directly to main
- **Communication**: Inform your team about the new workflow

This approach gives you maximum flexibility during the transition period while working toward your goal of centralizing everything in the AddLidar monorepo.
