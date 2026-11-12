#!/usr/bin/env python3
"""Add every Mac on the tailnet that answers on port 5900 to macOS Screen Sharing's
"All Connections" list, by its full tailnet name. Prints a plan; --yes writes it.

Usage: screen-sharing-list.py [--yes] [--user NAME=LOGIN ...] [--skip NAME ...]
Quit Screen Sharing before --yes; it rewrites its list from memory when it quits.
"""
import json, os, plistlib, shutil, socket, subprocess, sys, tempfile, time, uuid

PREFS = os.path.expanduser("~/Library/Containers/com.apple.ScreenSharing/Data/Library/"
                           "Preferences/com.apple.ScreenSharing.plist")
DOMAIN = PREFS[:-len(".plist")]


def tailscale():
    for c in ("tailscale", "/Applications/Tailscale.app/Contents/MacOS/Tailscale"):
        if shutil.which(c) or os.path.exists(c):
            return c
    sys.exit("tailscale CLI not found")


def port_open(host, port=5900, timeout=3):
    try:
        with socket.create_connection((host, port), timeout):
            return True
    except OSError:
        return False


def entry(name, address, user):
    i = str(uuid.uuid4()).upper()
    na = {"displayName": name, "address": address,
          "displayConfiguration": {"displayType": {"compatibilityMode": {}}}}
    if user:
        na["username"] = user
    return i, {"id": i, "isManaged": False, "createdFromMigration": False,
               "connectionParameters": {"networkAddress": {"_0": na}}}


def plan(store, peers, users, skip):
    """Return [(name, address, user)] for Macs not already saved by address or IP."""
    have = {d["connectionParameters"]["networkAddress"]["_0"]["address"].rstrip(".").lower()
            for d in store.get("connectionDetails", {}).values()}
    out = []
    for p in peers:
        dns = p["DNSName"].rstrip(".").lower()
        short = dns.split(".")[0]
        if p.get("OS") != "macOS" or short in skip:
            continue
        if dns in have or short in have or any(ip in have for ip in p["TailscaleIPs"]):
            continue
        out.append((p.get("HostName") or short, dns, users.get(short)))
    return out


def main(argv):
    yes = "--yes" in argv
    users, skip = {}, set()
    for flag, val in zip(argv, argv[1:]):
        if flag == "--user":
            k, _, v = val.partition("=")
            users[k.lower()] = v
        elif flag == "--skip":
            skip.add(val.lower())
    st = json.loads(subprocess.run([tailscale(), "status", "--json"], capture_output=True,
                                   text=True, check=True).stdout)
    peers = [p for p in st.get("Peer", {}).values() if p.get("Online")]
    d = plistlib.load(open(PREFS, "rb")) if os.path.exists(PREFS) else {}
    if "connectionsStore" not in d:
        sys.exit("No saved connections yet. Connect to one Mac in Screen Sharing once, then rerun.")
    # Edit the blob with plutil: it can hold dates (like distantPast) that Python's plistlib rejects.
    tmp = os.path.join(tempfile.mkdtemp(), "store.plist")
    open(tmp, "wb").write(d["connectionsStore"])
    details = plistlib.loads(subprocess.run(["plutil", "-extract", "connectionDetails", "xml1", "-o", "-", tmp],
                                            capture_output=True, check=True).stdout)
    todo = [t for t in plan({"connectionDetails": details}, peers, users, skip) if port_open(t[1])]
    if not todo:
        print("Nothing to add: every online Mac with Screen Sharing on is already listed.")
        return 0
    for name, addr, user in todo:
        print(f"add  {name}  vnc://{(user + '@') if user else ''}{addr}")
    if not yes:
        print("\nPlan only. Quit Screen Sharing, then run again with --yes.")
        return 0
    if subprocess.run(["pgrep", "-x", "Screen Sharing"], capture_output=True).returncode == 0:
        sys.exit("Screen Sharing is open. Quit it first, or it will overwrite this change.")
    if os.path.exists(PREFS):
        bak = f"{PREFS}.bak-{time.strftime('%Y%m%d-%H%M%S')}"
        shutil.copy2(PREFS, bak)
        print(f"backup: {bak}")
    for name, addr, user in todo:
        i, e = entry(name, addr, user)
        subprocess.run(["plutil", "-insert", f"connectionDetails.{i}", "-json", json.dumps(e), tmp], check=True)
    subprocess.run(["plutil", "-convert", "binary1", tmp], check=True)
    hexdata = open(tmp, "rb").read().hex()
    # defaults goes through cfprefsd, so the app sees the change; a direct file write may not stick.
    subprocess.run(["defaults", "write", DOMAIN, "connectionsStore", "-data", hexdata], check=True)
    print(f"added {len(todo)}. Open Screen Sharing to see them.")
    return 0


def _selftest():
    store = {"connectionDetails": dict([entry("a", "a.example.ts.net", None)])}
    peers = [{"DNSName": "a.example.ts.net.", "HostName": "a", "OS": "macOS", "TailscaleIPs": ["100.1.1.1"]},
             {"DNSName": "b.example.ts.net.", "HostName": "b", "OS": "macOS", "TailscaleIPs": ["100.1.1.2"]},
             {"DNSName": "c.example.ts.net.", "HostName": "c", "OS": "iOS", "TailscaleIPs": ["100.1.1.3"]},
             {"DNSName": "d.example.ts.net.", "HostName": "d", "OS": "macOS", "TailscaleIPs": ["100.1.1.4"]}]
    got = plan(store, peers, {"b": "me"}, {"d"})
    assert got == [("b", "b.example.ts.net", "me")], got
    print("selftest ok")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        _selftest()
    else:
        sys.exit(main(sys.argv[1:]))
