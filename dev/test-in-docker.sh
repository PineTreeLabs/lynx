#!/bin/bash
# SPDX-FileCopyrightText: 2026 Jared Callaham <jared.callaham@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# Helper script to run frontend tests in Docker (mirrors CI environment)

set -e

cd "$(dirname "$0")/.."

echo "Building Docker test environment (Ubuntu + Node 20)..."
docker-compose -f docker-compose.test.yml build

if [ $# -eq 0 ]; then
    echo ""
    echo "Starting interactive shell in test container..."
    echo "Run 'npm test -- --run' to execute all tests"
    echo "Run 'npm test -- src/palette/BlockPalette.test.tsx --run' for specific tests"
    echo ""
    docker-compose -f docker-compose.test.yml run --rm test
else
    echo ""
    echo "Running command: $@"
    echo ""
    docker-compose -f docker-compose.test.yml run --rm test bash -c "$@"
fi
