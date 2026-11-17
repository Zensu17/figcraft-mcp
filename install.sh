#!/usr/bin/env bash
set -e

echo "=================================================="
echo "      FigCraft Universal MCP Setup"
echo "=================================================="
echo ""

if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
else
    echo "[ERROR] Python 3 is not installed or not in PATH!"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$PYTHON_CMD" "$SCRIPT_DIR/install.py"
