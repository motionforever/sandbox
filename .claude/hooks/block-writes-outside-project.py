#!/usr/bin/env python3
"""PreToolUse hook: refuse Edit/Write/NotebookEdit on any file outside this project.

Covers Claude's built-in file tools, which run outside the Bash sandbox. Shell commands are
already confined by the sandbox (see docs/claude-user-settings.mac.json). Skipped in cloud
sessions, where the VM itself is the boundary.
"""

import json
import os
import sys
import tempfile

if os.environ.get("CLAUDE_CODE_REMOTE") == "true":
    sys.exit(0)

event = json.load(sys.stdin)
tool_input = event.get("tool_input", {})
target = tool_input.get("file_path") or tool_input.get("notebook_path")
if not target:
    sys.exit(0)

cwd = event.get("cwd") or os.getcwd()
project = os.path.realpath(os.environ.get("CLAUDE_PROJECT_DIR") or cwd)
# realpath resolves `..` and symlinks, so a link inside the project can't point the write elsewhere.
resolved = os.path.realpath(os.path.join(cwd, os.path.expanduser(target)))

allowed_roots = [project, os.path.realpath(tempfile.gettempdir())]
if any(os.path.commonpath([resolved, root]) == root for root in allowed_roots):
    sys.exit(0)

print(
    f"Blocked: {resolved} is outside this project ({project}). "
    "Writes are limited to the project directory and the temp directory.",
    file=sys.stderr,
)
sys.exit(2)
