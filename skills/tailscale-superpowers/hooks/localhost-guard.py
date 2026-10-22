#!/usr/bin/env python3
"""Stop hook (Claude Code and Codex): don't let an agent hand the user a localhost link.

When the agent's final reply links to http(s)://localhost, 127.0.0.1, 0.0.0.0 or [::1] outside a code block,
this exits 2 with instructions, which both tools treat as "keep going": the agent runs tailnet-url for each
port and swaps in the Tailscale link. It blocks once per reply (stop_hook_active), and does nothing on a machine
without Tailscale, where the script couldn't work anyway.
"""

import json
import os
import re
import shutil
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


def reason(links):
    lines = ["Your reply links to localhost, which only opens on this computer. The user works across several "
             "devices, so replace each link below with the Tailscale link this prints, then send the reply again:"]
    seen = set()
    for url, port, path in links:
        if (port, path) in seen:
            continue
        seen.add((port, path))
        lines.append(f"- {url}  ->  run: {SCRIPT} {port} {path}")
    lines.append("If tailnet-url fails, say the link couldn't be verified instead of giving a localhost one.")
    return "\n".join(lines)


def main():
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return 0
    if payload.get("stop_hook_active"):
        return 0
    if not (shutil.which("tailscale") or os.path.exists(MAC_CLI)):
        return 0
    links = localhost_links(last_message(payload))
    if not links:
        return 0
    print(reason(links), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
