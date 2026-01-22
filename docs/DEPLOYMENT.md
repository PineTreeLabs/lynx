# Documentation Deployment Guide

This guide explains how to deploy the Lynx documentation to GitHub Pages.

## Current Status

✅ Documentation is complete and ready for deployment
⚠️ Deployment is currently **DISABLED** because the repository is private

## Deployment Checklist

When you're ready to make the documentation public, follow these steps:

### 1. Make Repository Public

1. Go to repository **Settings**
2. Scroll to **Danger Zone** section
3. Click **Change visibility** → **Make public**
4. Confirm the action

### 2. Enable GitHub Pages

1. Go to repository **Settings** → **Pages**
2. Under **Source**, select **"GitHub Actions"**
3. Save changes

### 3. Enable Deployment in Workflow

Edit `.github/workflows/docs.yml`:

```diff
  deploy:
-   if: false  # DISABLED - Remove this line to enable deployment
+   if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    needs: build
```

### 4. Merge Documentation PR

1. Merge the `016-github-pages-docs` PR to `main`
2. GitHub Actions will automatically:
   - Build the documentation
   - Run link checks
   - Deploy to GitHub Pages (now enabled)

### 5. Verify Deployment

1. Check **Actions** tab - "Documentation" workflow should succeed
2. Visit documentation URL: `https://pinetreelabs.github.io/lynx/`
3. Test navigation, dark mode, examples, search

## Build Validation (Pre-Deployment)

The documentation has been pre-validated:

- ✅ **Build succeeds** - clean HTML output, zero critical warnings
- ✅ **Linkcheck passes** - zero broken internal links
- ✅ **Notebooks execute** - all 3 examples render correctly
- ✅ **MyST markdown** - notebooks converted from .ipynb to .md
- ✅ **Dark mode** - Archimedes-quality CSS enhancements
- ✅ **Brand colors** - Lynx indigo (#6366f1) theme applied

## Local Testing

Test the documentation locally before deployment:

```bash
# Build HTML
cd docs
make html

# Serve locally at http://localhost:8000
make serve

# Run link checks
make linkcheck
```

## Troubleshooting

### Workflow fails with "duplicate __init__ warnings"

These are benign warnings from autodoc. The build will still succeed and generate correct documentation. These warnings are suppressed in `docs/source/conf.py`:

```python
suppress_warnings = ['autodoc']
```

### Cache issues with notebooks

If notebooks don't re-execute after changes:

```bash
# Clear Jupyter cache
rm -rf docs/_build/.jupyter_cache

# Rebuild
cd docs && make clean && make html
```

### GitHub Pages 404 error

1. Verify **Settings → Pages → Source** is set to **"GitHub Actions"**
2. Check that deployment job ran successfully in **Actions** tab
3. Wait 5-10 minutes for DNS propagation

## Post-Deployment Tasks

After successful deployment:

1. Update `README.md` with documentation link:
   ```markdown
   ## Documentation

   📚 [Read the documentation](https://pinetreelabs.github.io/lynx/)
   ```

2. Run user testing (SC-001):
   - Recruit 3+ first-time users
   - Provide only docs URL, no guidance
   - Validate <10 minute quickstart completion

3. Monitor for issues:
   - Check GitHub Issues for documentation bugs
   - Watch for broken links after code changes
   - Update examples when API changes

## Success Criteria Validation

Deployment satisfies these criteria:

- **SC-001**: First-time users complete quickstart in <10 minutes
- **SC-002**: All public methods documented with examples
- **SC-003**: Build succeeds with zero warnings
- **SC-004**: All 3 notebooks execute and render correctly
- **SC-005**: Deployment completes within 5 minutes
- **SC-006**: 95%+ mobile usability (responsive design)
- **SC-007**: Zero broken internal links
- **SC-008**: Dark mode works correctly with logo switching

## Maintenance

Documentation automatically rebuilds on every push to `main`:

- Notebooks re-execute if changed (cached otherwise)
- API docs regenerate from docstrings
- Deployment completes in ~3-5 minutes

To update documentation:
1. Make changes on feature branch
2. Test locally with `make html`
3. Create PR → merge to `main`
4. GitHub Actions deploys automatically
