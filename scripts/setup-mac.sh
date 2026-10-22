#!/bin/bash
# One-time local setup on macOS: installs the project's Python env with uv.
# Run from the repo root:  ./scripts/setup-mac.sh
set -euo pipefail

cd "$(dirname "$0")/.."
repo_dir="$(pwd -P)"

# A deletion inside a cloud-synced folder propagates to the cloud copy, so refuse to set up there.
case "$repo_dir" in
  *"/Library/CloudStorage/"*|*"/Library/Mobile Documents/"*|*"/Dropbox"*|*"/OneDrive"*|*"/Google Drive"*|*"/iCloud"*)
    echo "This repo is inside a cloud-synced folder: $repo_dir"
    echo "Clone it somewhere unsynced instead, e.g. ~/Developer/sandbox, and run this script there."
    exit 1
    ;;
esac
case "$repo_dir" in
  "$HOME/Desktop"*|"$HOME/Documents"*)
    echo "Warning: $repo_dir is under Desktop/Documents, which iCloud Drive may sync."
    echo "If 'Desktop & Documents Folders' is on in iCloud settings, move the repo to ~/Developer first."
    read -r -p "Continue anyway? [y/N] " answer
    [[ "$answer" =~ ^[Yy]$ ]] || exit 1
    ;;
esac

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is not installed. Install it with one of:"
  echo "  brew install uv"
  echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
  echo "Then open a new terminal and re-run this script."
  exit 1
fi

# uv manages its own Python; this never touches the macOS system Python.
uv python install "$(cat .python-version)"
uv sync --all-groups

uv run python -c "import sys, numpy, pandas; print('Python', sys.version.split()[0], '| numpy', numpy.__version__, '| pandas', pandas.__version__)"
uv run pytest -q

echo
echo "Done. Use 'uv run python ...' / 'uv run pytest', or 'source .venv/bin/activate'."
echo "For Jupyter/VS Code, select the interpreter at $repo_dir/.venv/bin/python"
