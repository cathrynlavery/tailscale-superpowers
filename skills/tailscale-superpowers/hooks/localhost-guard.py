#!/usr/bin/env python3
"""Stop hook (Claude Code and Codex): turn localhost links into working tailnet links, with no agent involved.

When the agent's final reply links to http(s)://localhost, 127.0.0.1, 0.0.0.0 or [::1] outside a code block,
this runs tailnet-url for each link itself (share over Tailscale Serve, check it loads) and shows the user the
working links under the reply as a hook message. It never blocks the reply and never asks the agent to do
anything. It does nothing on a computer without Tailscale.
"""

import json
import os
import re
import shutil
import subprocess
import sys

SCRIPT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts", "tailnet-url"))
MAC_CLI = "/Applications/Tailscale.app/Contents/MacOS/Tailscale"
FENCE = re.compile(r"(```|~~~).*?(\1|\Z)", re.S)
LOCAL_URL = re.compile(r"https?://(?:localhost|127\.0\.0\.1|0\.0\.0\.0|\[::1\])(?::(\d{1,5}))?(/[^\s)>\]\"'`]*)?",
                       re.I)


def localhost_links(text):
    """Return (url, port, path) for each localhost link outside fenced code blocks."""
    prose = FENCE.sub(" ", text or "")
    found = []
    for m in LOCAL_URL.finditer(prose):
        port = m.group(1) or ("443" if m.group(0).lower().startswith("https") else "80")
        found.append((m.group(0), port, m.group(2) or "/"))
    return found


def last_message(payload):
    msg = payload.get("last_assistant_message")
    if isinstance(msg, str):
        return msg
    path = payload.get("transcript_path")  # older clients: read the last assistant turn from the transcript
    if not path or not os.path.exists(path):
        return ""
    last = ""
    with open(path, errors="ignore") as f:
        for line in f:
            try:
                row = json.loads(line)
            except ValueError:
                continue
            m = row.get("message") or {}
            if row.get("type") == "assistant" and m.get("role") == "assistant":
                parts = m.get("content")
                text = "".join(p.get("text", "") for p in parts if isinstance(p, dict)) if isinstance(parts, list) else str(parts or "")
                if text.strip():
                    last = text
    return last


def share(port, path):
    """Run tailnet-url; return (link, None) or (None, error)."""
    try:
        r = subprocess.run([sys.executable, SCRIPT, port, path], capture_output=True, text=True, timeout=25)
    except subprocess.TimeoutExpired:
        return None, "timed out"
    if r.returncode == 0 and r.stdout.strip():
        return r.stdout.strip(), None
    return None, (r.stderr.strip() or "failed").replace("tailnet-url: ", "")


def message(links):
    lines, seen = [], set()
    for url, port, path in links:
        if (port, path) in seen:
            continue
        seen.add((port, path))
        link, err = share(port, path)
        lines.append(f"Tailnet link for {url}: {link}" if link else f"No tailnet link for {url} ({err})")
    return "\n".join(lines)


def main():
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return 0
    if not (shutil.which("tailscale") or os.path.exists(MAC_CLI)):
        return 0
    links = localhost_links(last_message(payload))
    if links:
        print(json.dumps({"systemMessage": message(links)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
