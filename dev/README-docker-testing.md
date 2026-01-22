<!--
SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Docker Testing Environment

This directory contains tools for running frontend tests in a Docker container that exactly mirrors the GitHub Actions CI environment.

## Why?

Tests may pass locally on macOS but fail in CI (Linux/Ubuntu). This Docker setup lets you reproduce and debug CI failures locally.

## Quick Start

### 1. Run all tests in Docker

```bash
./dev/test-in-docker.sh "npm test -- --run"
```

### 2. Run specific test file

```bash
./dev/test-in-docker.sh "npm test -- src/palette/BlockPalette.test.tsx --run"
```

### 3. Interactive shell for debugging

```bash
./dev/test-in-docker.sh
```

Then inside the container:
```bash
npm test -- --run                                    # Run all tests
npm test -- src/palette/BlockPalette.test.tsx --run  # Specific file
npm test -- --reporter=verbose --run                 # Verbose output
```

## Environment Details

The Docker container matches CI exactly:
- **OS**: Ubuntu (latest)
- **Node.js**: v20.x
- **Package manager**: npm
- **Install method**: `npm ci` (clean install from lock file)

## Files

- `Dockerfile.test` - Container definition
- `docker-compose.test.yml` - Service configuration
- `test-in-docker.sh` - Helper script

## Troubleshooting

### "Unable to find an element" errors

These often indicate timing issues where the component hasn't rendered yet. Check:
- Are you using `await waitFor()` for async assertions?
- Are timers set consistently (all real or all fake, not switching mid-test)?

### "Test timed out" errors

Usually caused by:
- `waitFor()` called with fake timers active (use real timers or `act()` + `advanceTimers`)
- Waiting for an element that will never appear

### Cleanup between tests

If tests fail only when run together (pass individually):
- Check `afterEach()` cleanup hooks
- Look for fake timers not being restored with `vi.useRealTimers()`
