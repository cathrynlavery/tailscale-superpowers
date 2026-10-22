#!/usr/bin/env python3
"""Checks for localhost-guard.py. Run: python3 hooks/test_localhost_guard.py"""

import importlib.util
import io
import json
import os
import sys
import tempfile

spec = importlib.util.spec_from_file_location("guard", os.path.join(os.path.dirname(__file__), "localhost-guard.py"))
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


def run(payload, tailscale=True):
    old_in, old_err, old_which, old_exists = sys.stdin, sys.stderr, guard.shutil.which, guard.os.path.exists
    sys.stdin, sys.stderr = io.StringIO(json.dumps(payload)), io.StringIO()
    guard.shutil.which = lambda _: "/usr/bin/tailscale" if tailscale else None
    guard.os.path.exists = (lambda p: old_exists(p) if p != guard.MAC_CLI else False) if not tailscale else old_exists
    try:
        return guard.main(), sys.stderr.getvalue()
    finally:
        sys.stdin, sys.stderr, guard.shutil.which, guard.os.path.exists = old_in, old_err, old_which, old_exists


# Detection
assert guard.localhost_links("Open http://localhost:3000/dash to see it.") == [("http://localhost:3000/dash", "3000", "/dash")]
assert [p for _, p, _ in guard.localhost_links("http://127.0.0.1:8787 and https://0.0.0.0:5173")] == ["8787", "5173"]
assert guard.localhost_links("Config:\n```\nproxy: http://localhost:3000\n```\nDone.") == []
assert guard.localhost_links("The server binds to 127.0.0.1 only.") == []
assert guard.localhost_links("See https://cat-studio.tail95fe1c.ts.net:3000/") == []
assert guard.localhost_links("http://localhost/") == [("http://localhost/", "80", "/")]

# Hook behavior
code, err = run({"last_assistant_message": "Preview: http://localhost:3000"})
assert code == 2 and "tailnet-url 3000 /" in err, err
assert run({"last_assistant_message": "Preview: http://localhost:3000", "stop_hook_active": True})[0] == 0
assert run({"last_assistant_message": "All done."})[0] == 0
assert run({"last_assistant_message": "Preview: http://localhost:3000"}, tailscale=False)[0] == 0

# Transcript fallback for clients that don't send last_assistant_message
with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as t:
    t.write(json.dumps({"type": "assistant", "message": {"role": "assistant",
                        "content": [{"type": "text", "text": "Try http://localhost:4000"}]}}) + "\n")
code, err = run({"transcript_path": t.name})
os.unlink(t.name)
assert code == 2 and "4000" in err

print("localhost-guard tests ok")
