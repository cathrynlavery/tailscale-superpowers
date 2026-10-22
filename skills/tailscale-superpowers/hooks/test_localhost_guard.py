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
calls = []


def fake_share(port, path):
    calls.append((port, path))
    if port == "9999":
        return None, "nothing is loading on local port 9999/"
    return f"https://laptop.example.ts.net:{port}{path}", None


def run(payload, tailscale=True):
    old = sys.stdin, sys.stdout, guard.shutil.which, guard.os.path.exists, guard.share
    sys.stdin, sys.stdout = io.StringIO(json.dumps(payload)), io.StringIO()
    guard.shutil.which = lambda _: "/usr/bin/tailscale" if tailscale else None
    if not tailscale:
        guard.os.path.exists = lambda p: False if p == guard.MAC_CLI else old[3](p)
    guard.share = fake_share
    try:
        code = guard.main()
        out = sys.stdout.getvalue()
        return code, (json.loads(out)["systemMessage"] if out.strip() else "")
    finally:
        sys.stdin, sys.stdout, guard.shutil.which, guard.os.path.exists, guard.share = old


# Detection
assert guard.localhost_links("Open http://localhost:3000/dash to see it.") == [("http://localhost:3000/dash", "3000", "/dash")]
assert [p for _, p, _ in guard.localhost_links("http://127.0.0.1:8787 and http://0.0.0.0:5173")] == ["8787", "5173"]
assert guard.localhost_links("Docs at http://localhost.example.com/ and https://localhost:5173/") == []  # not loopback / not http
assert guard.localhost_links("Config:\n```\nproxy: http://localhost:3000\n```\nDone.") == []
assert guard.localhost_links("The server binds to 127.0.0.1 only.") == []
assert guard.localhost_links("See https://laptop.your-tailnet.ts.net:3000/") == []
assert guard.localhost_links("http://localhost/") == [("http://localhost/", "80", "/")]

# The hook makes the links itself, shows them to the user, and never blocks
code, msg = run({"last_assistant_message": "Preview: http://localhost:3000/dash and again http://localhost:3000/dash"})
assert code == 0 and ": https://laptop.example.ts.net:3000/dash" in msg, msg
assert calls == [("3000", "/dash")], calls  # same link shared once
code, msg = run({"last_assistant_message": "Try http://localhost:9999/"})
assert code == 0 and "No tailnet link for http://localhost:9999/ (nothing is loading" in msg, msg
assert run({"last_assistant_message": "All done."}) == (0, "")
assert run({"last_assistant_message": "Preview: http://localhost:3000"}, tailscale=False) == (0, "")

# Transcript fallback for clients that don't send last_assistant_message
with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as t:
    t.write(json.dumps({"type": "assistant", "message": {"role": "assistant",
                        "content": [{"type": "text", "text": "Try http://localhost:4000"}]}}) + "\n")
code, msg = run({"transcript_path": t.name})
os.unlink(t.name)
assert code == 0 and ":4000/" in msg

print("localhost-guard tests ok")
