#!/usr/bin/env python3
"""Read-only report on every device in your tailnet.

Runs `tailscale status --json` and prints one row per device: online or
offline, when it was last seen, how this machine reaches it, and when its
sign-in (node key) expires. It never changes anything.

Usage:
  python3 check-all-macs.py              warn about keys expiring within 30 days
  python3 check-all-macs.py --days 60    warn earlier
  python3 check-all-macs.py --status-json saved.json
                                         read a saved `tailscale status --json`
                                         instead of running the CLI (for testing)
"""

import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys

CLI_CANDIDATES = [
    "/Applications/Tailscale.app/Contents/MacOS/Tailscale",
    "/opt/homebrew/bin/tailscale",
    "/usr/local/bin/tailscale",
    "/usr/bin/tailscale",
    r"C:\Program Files\Tailscale\tailscale.exe",
]


def find_cli():
    found = shutil.which("tailscale")
    if found:
        return found
    for path in CLI_CANDIDATES:
        if os.path.exists(path):
            return path
    return None


def load_status(args):
    if args.status_json:
        with open(args.status_json, encoding="utf-8") as f:
            return json.load(f)
    cli = find_cli()
    if not cli:
        sys.exit("Couldn't find the tailscale command. See step one of SKILL.md.")
    env = dict(os.environ, TAILSCALE_BE_CLI="1")
    result = subprocess.run(
        [cli, "status", "--json"], capture_output=True, text=True, env=env
    )
    if result.returncode != 0:
        sys.exit("tailscale status failed: " + (result.stderr.strip() or "no output"))
    return json.loads(result.stdout)


def parse_time(value):
    """Parse Go's RFC 3339 timestamps. Returns None for empty or zero times."""
    if not value or value.startswith("0001-"):
        return None
    value = value.replace("Z", "+00:00")
    if "." in value:
        head, rest = value.split(".", 1)
        digits = ""
        while rest and rest[0].isdigit():
            digits, rest = digits + rest[0], rest[1:]
        value = head + "." + digits[:6].ljust(6, "0") + rest
    return dt.datetime.fromisoformat(value)


def ago(when, now):
    minutes = int((now - when).total_seconds()) // 60
    if minutes < 2:
        return "just now"
    if minutes < 120:
        return f"{minutes}m ago"
    hours = minutes // 60
    if hours < 48:
        return f"{hours}h ago"
    return f"{hours // 24}d ago"


def device_name(node, suffix):
    dns = (node.get("DNSName") or "").rstrip(".")
    if dns and suffix and dns.endswith("." + suffix):
        return dns[: -len(suffix) - 1], False
    if dns:
        # Shared in from another tailnet: only the full name works.
        return dns, True
    return node.get("HostName") or "?", False


def connection(node, is_self):
    if is_self:
        return "this device"
    if not node.get("Online"):
        return "-"
    if not node.get("Active"):
        return "idle"
    if node.get("CurAddr"):
        return "direct"
    relay = node.get("Relay")
    return f"relay ({relay})" if relay else "relay"


def key_expiry(node, now, warn_days):
    """Returns (label, state) where state is ok, soon, expired, or off."""
    when = parse_time(node.get("KeyExpiry"))
    if when is None:
        return "off", "off"
    if node.get("Expired") or when <= now:
        return "EXPIRED", "expired"
    days = (when - now).days
    label = f"{when:%Y-%m-%d} ({days}d)"
    return label, "soon" if days <= warn_days else "ok"


def main():
    parser = argparse.ArgumentParser(description="Read-only report on every device in your tailnet.")
    parser.add_argument("--days", type=int, default=30, help="warn when a key expires within this many days (default 30)")
    parser.add_argument("--status-json", help="read a saved `tailscale status --json` file instead of running the CLI")
    args = parser.parse_args()

    status = load_status(args)
    state = status.get("BackendState")
    if state != "Running":
        sys.exit(f"Tailscale isn't connected on this machine (state: {state}). Open the Tailscale app and connect.")

    now = dt.datetime.now(dt.timezone.utc)
    suffix = (status.get("MagicDNSSuffix") or "").rstrip(".")
    nodes = [(status.get("Self") or {}, True)]
    nodes += [(p, False) for p in (status.get("Peer") or {}).values()]

    rows, soon, expired, offline, hidden = [], [], [], [], 0
    for node, is_self in nodes:
        if "mullvad.ts.net" in (node.get("DNSName") or ""):
            hidden += 1
            continue
        name, shared = device_name(node, suffix)
        online = is_self or bool(node.get("Online"))
        seen = parse_time(node.get("LastSeen"))
        key_label, key_state = key_expiry(node, now, args.days)
        if key_state == "soon":
            soon.append(name)
            key_label += "  <- expiring soon"
        elif key_state == "expired":
            expired.append(name)
        if not online:
            offline.append(name)
        rows.append([
            name + (" (shared)" if shared else ""),
            node.get("OS") or "?",
            "online" if online else "offline",
            "-" if online or not seen else ago(seen, now),
            connection(node, is_self),
            key_label,
        ])

    # This device first, then online devices, then offline, each by name.
    rows = rows[:1] + sorted(rows[1:], key=lambda r: (r[2] != "online", r[0].lower()))
    header = ["DEVICE", "OS", "STATUS", "LAST SEEN", "CONNECTION", "KEY EXPIRES"]
    widths = [max(len(r[i]) for r in rows + [header]) for i in range(len(header) - 1)]
    for row in [header] + rows:
        print("  ".join(cell.ljust(w) for cell, w in zip(row, widths)) + "  " + row[-1])

    print()
    print(f"{len(rows)} devices: {len(rows) - len(offline)} online, {len(offline)} offline.")
    if expired:
        print("Sign-in expired (off the tailnet until someone signs in on it): " + ", ".join(expired))
    if soon:
        print(f"Sign-in expires within {args.days} days: " + ", ".join(soon))
    if not expired and not soon:
        print(f"No sign-ins expire within {args.days} days.")
    if hidden:
        print(f"Not shown: {hidden} Mullvad exit nodes.")


if __name__ == "__main__":
    main()
