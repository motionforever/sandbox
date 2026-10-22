# quantlab sandbox

A Python research sandbox set up for a hybrid workflow:

- **Cloud** (Claude Code on the web): code, refactors, tests, small backtests. Isolated VM, can't touch your disks.
- **Local Mac**: private data, heavy compute, interactive work. Runs inside Claude Code's sandbox.

Both use the same `pyproject.toml` + `uv.lock`, so the environment is defined in code, not per machine.

## Layout

```
pyproject.toml / uv.lock          dependencies (numpy, pandas, scipy, statsmodels, matplotlib; dev: pytest, ruff, ipykernel)
.python-version                   Python 3.13
src/quantlab/                     your code (example: metrics.py)
tests/                            pytest tests
.claude/settings.json             project settings: hooks + permission rules
.claude/hooks/session-start.sh    cloud only: runs `uv sync` and puts .venv on PATH
.claude/hooks/block-writes-outside-project.py  local only: Claude's file tools can't write outside this repo
scripts/setup-mac.sh              one-time local setup on macOS
docs/claude-user-settings.mac.json  suggested ~/.claude/settings.json for your Mac
```

## Cloud

Nothing to do. When a cloud session starts on this repo, the hook runs `uv sync --all-groups`,
so `python`, `pytest` and `ruff` are ready. Packages Claude installs mid-session do not carry
over; add them to `pyproject.toml` (`uv add <pkg>`) and commit instead.

Docs: https://code.claude.com/docs/en/cloud-environments

## Local Mac

1. Install uv: `brew install uv` (or see https://docs.astral.sh/uv/getting-started/installation/).
2. Clone into a folder that is **not** synced to a cloud drive, e.g.:
   ```bash
   mkdir -p ~/Developer && cd ~/Developer
   git clone https://github.com/motionforever/sandbox.git && cd sandbox
   ```
3. Run `./scripts/setup-mac.sh`. It refuses to run inside iCloud/Dropbox/OneDrive/Google Drive
   folders, installs Python 3.13 via uv (never touching the macOS system Python), syncs the venv
   and runs the tests.
4. Merge `docs/claude-user-settings.mac.json` into `~/.claude/settings.json`. It turns on the
   Bash sandbox in strict mode (no unsandboxed retries, fail if the sandbox can't start),
   disables `bypassPermissions`, asks before `rm` / `git push`, lets sandboxed commands write
   only to the repo plus uv's cache, and allows network only to PyPI and GitHub.
   Then start `claude` in the repo and run `/sandbox` to confirm it is active.

### Write boundary

Two paths can write files, and each has its own guard:

| Path | Guard |
| --- | --- |
| Shell commands (`rm`, `mv`, `python script.py`, ...) | Bash sandbox (OS-enforced): repo, temp dir, `~/.cache/uv` only |
| Claude's Edit/Write/NotebookEdit tools (run outside the sandbox) | `block-writes-outside-project.py` PreToolUse hook: repo and temp dir only |
| Same file tools, second layer | Built-in `deny` rules in `.claude/settings.json` for cloud-synced folders (`~/Dropbox`, `~/Library/CloudStorage`, iCloud Drive), in case the hook ever fails |

### Network

`.claude/settings.json` adds Yahoo Finance hosts to the sandbox allowlist for this project only
(they merge with the PyPI/GitHub entries in your user settings), so Claude can run `yfinance`.
Hosts are the ones the yfinance package itself calls: `finance.yahoo.com`, `query1`/`query2`/`streamer`
under `*.finance.yahoo.com`, plus `fc`, `guce` and `consent.yahoo.com` for the cookie/consent flow.
Cloud sessions don't use these: add the same hosts under the cloud environment's **Custom** network access.

Always start `claude` from inside the repo (`cds && claude`), never from `~/Developer`:
the boundary is the directory you launch from.

Docs: https://code.claude.com/docs/en/sandboxing ·
https://code.claude.com/docs/en/permission-modes

## Day to day

```bash
uv add <package>      # add a dependency (updates pyproject.toml + uv.lock)
uv run pytest         # tests
uv run ruff check .   # lint
```

Keep private data under `data/private/` (git-ignored, and Claude's Read tool is denied there).
