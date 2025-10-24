#!/usr/bin/env bash
# Helper to activate the project's virtualenv (.venv)
# IMPORTANT: source this file so activation persists in your current shell:
#
#   source ./scripts/activate-venv.sh
#
VENV_PATH=".venv/bin/activate"
if [ ! -f "$VENV_PATH" ]; then
  echo "Virtual environment not found at .venv. Create it with:"
  echo "  python -m venv .venv"
  return 1 2>/dev/null || exit 1
fi

# shellcheck disable=SC1091
. "$VENV_PATH"

echo "Activated virtualenv at .venv"
