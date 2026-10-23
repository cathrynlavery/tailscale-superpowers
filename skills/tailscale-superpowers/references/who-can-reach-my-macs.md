# Who can reach my Macs?

## When you'd want this

Someone says "I already have your Tailscale account," or you joined a friend's tailnet, or you shared a Mac with a contractor months ago. You want to know whether that person can open a connection to any of your Macs.

A few words first:

- **Tailnet**: a private network of devices. Each Tailscale account belongs to one, and one person can be a user on several.
- **Peer list**: the devices a Mac can talk to over Tailscale. Tailscale sends each device this list based on the tailnet's rules, and a Mac only accepts Tailscale connections from devices on it.
- **Policy file**: the rules for a tailnet, kept in its admin console. Whoever runs a tailnet writes its policy file.
- **Sharing a machine**: lending one device to a user on another tailnet.

The peer lists are the proof, so start there. The later steps explain what you find and how to close each gap. Steps 2, 3, 5 and 6 use `tailscale-pp-cli` (see "Optional: the admin CLI" in [SKILL.md](../SKILL.md)); without it, the user reads the same pages in the admin console.

## Step 1: the peer list on each of your Macs

Run freely, on each Mac. Running it on another Mac over SSH is ask first.

```sh
tailscale status --json | python3 -c '
import json, sys
s = json.load(sys.stdin)
users = s.get("User") or {}
def login(n): return users.get(str(n.get("UserID")), {}).get("LoginName", "?")
me, suffix = login(s["Self"]), s.get("MagicDNSSuffix", "")
print("this device:", s["Self"]["HostName"], "| you:", me)
rows = []
for p in (s.get("Peer") or {}).values():
    if p.get("Tags"): kind = "tagged"
    elif not p.get("DNSName", "").rstrip(".").endswith(suffix): kind = "shared in"
    elif login(p) == me: kind = "yours"
    else: kind = "OTHER USER"
    rows.append((kind, login(p), p.get("HostName", "?")))
for kind, who, host in sorted(rows):
    print(kind.ljust(11), who.ljust(32), host)
'
```

It looks like this:

```text
this device: home-mac | you: you@example.com
OTHER USER  friend@example.com               friend-laptop
shared in   friend@example.com               friend-mac
tagged      tagged-devices                   build-box
yours       you@example.com                  laptop
```

How to read it:

- **yours**: your own devices.
- **tagged**: devices set up as servers with a tag instead of an owner.
- **shared in**: a device someone shared with you. From Tailscale's sharing docs: "A shared machine can receive incoming connections (from the other user's tailnet) but cannot start connections." It can't open a connection to this Mac.
- **OTHER USER**: another person's device that this Mac can talk to. Tailscale lists it because the rules allow traffic in at least one direction. Step 5's `access check` shows which ports.

If the person's login and devices aren't on any of your Macs' lists, they can't open a Tailscale connection to those Macs. Check two more things before you call it done:

- **A device of yours that offers your home network to the tailnet** (a subnet router, see [home-network.md](home-network.md)). Anyone on its peer list may reach your Macs by their home network addresses without being on the Macs' own lists. Run the same check on that device.
- **Funnel**, which puts a site on the public internet. Run freely on each Mac: `tailscale funnel status`. Anything listed there is open to anyone with the link, with or without Tailscale. To turn it off, see [public-demo.md](public-demo.md).

## Step 2: who is a user on your tailnet

Run freely:

```sh
tailscale-pp-cli tailnet users list --type all
```

Each entry has a `loginName`, a `role`, and a `type`:

- **`member`**: a user of your tailnet whose devices sign in to it. With Tailscale's default rules, every member can reach every device.
- **`shared`**: someone who accepted a machine you shared. They reach that machine and nothing else of yours.

Without the CLI, the admin console's **Users** page shows the same list.

## Step 3: machines you've shared

Run freely:

```sh
tailscale-pp-cli shares audit
```

It checks every device you own and lists each share invite, with who accepted it. An invite marked `redeemable` can still be accepted by anyone holding its link: one nobody accepted yet, or a reusable link even after someone used it. `redeemable_count` says how many there are. Tailscale lets unused links expire after 30 days, but revoke any you don't need now (see "Close the gaps").

## Step 4: your devices on other people's tailnets

This is the other direction. Run freely, on each of your devices:

```sh
tailscale switch --list
```

It lists the accounts this device is signed in to, with `*` next to the one in use. An account on any tailnet other than your own means this device can join someone else's tailnet. On an iPhone, the Tailscale app shows the same list: tap the profile picture at the top right, then the account details at the top.

While a device is connected to their tailnet, its owner and admins write the rules for it, and they can give themselves access whenever they like. Treat any device you put on their tailnet as reachable by them. Being a user on their tailnet with no devices there gives them nothing on yours.

Reaching a Mac still isn't logging in to it. They'd also need a password or key for that Mac. The exception is Tailscale SSH, where the tailnet's rules decide who can log in. It only runs on the open-source variant of Tailscale, so a Mac with the App Store or Standalone app is fine. On other devices, `tailscale get ssh` (run freely) prints `true` when it's on.

## Step 5: red flags in your policy file

Read it (run freely): `tailscale-pp-cli tailnet acl get`, or the admin console's **Access controls** page. Look for:

- **`autogroup:danger-all`** in any `src`. Tailscale's docs say it "selects all sources including those outside your tailnet."
- **A catch-all rule**, `"src": ["*"]` with `"dst": ["*"]`. It's Tailscale's default and fine while you're the only user. With other members, it lets each of them reach every device. It doesn't reach outside your tailnet by itself: Tailscale's docs define `*` as "All traffic originating from Tailscale devices in your tailnet, any approved subnets and autogroup:shared."
- **An outside login**: any email that isn't yours in `grants`, `acls`, `ssh`, or in a group that a rule uses.
- **An `externalTailnets` block.** That's declarative node sharing, an alpha Tailscale feature that shares devices between trusted tailnets through both policy files instead of invites (https://tailscale.com/docs/features/declarative-node-sharing). In your file, `"allowIncomingConnections": true` means your tailnet accepts traffic from that tailnet, and grants whose `src` starts with `group://<alias>/` or `tag://<alias>/` say what it can reach. `allowExternalReferencesTo` lists your own groups and tags that the other tailnet may give access to its devices. Access needs matching rules on both sides, so your file alone doesn't settle it. Go by the peer lists from step 1. In one real case, `allowIncomingConnections: true` plus a catch-all `*` rule still put none of the other tailnet's devices on any peer list.

To check one person against one Mac and port (run freely):

```sh
tailscale-pp-cli access check --to home-mac:22 --from friend@example.com
```

It lists the rules that let that login reach port 22 (SSH) on home-mac, and `allowed` says whether any matched. Try 5900 (Screen Sharing) and 445 (file sharing) too. If the login isn't a member or shared user of your tailnet, it warns you, because a typo still matches a `*` rule.

## Step 6: recent changes

Run freely, with the dates you want to look back over:

```sh
tailscale-pp-cli tailnet logging list-configuration-audit-logs \
  --start 2026-09-01T00:00:00Z --end 2026-10-01T00:00:00Z --json \
  | python3 -c 'import json,sys
for e in json.load(sys.stdin)["results"]:
    t = e.get("target") or {}
    print(e["eventTime"][:16], (e.get("actor") or {}).get("loginName") or "-", e["action"], t.get("type") or "-", t.get("property") or "-", t.get("name") or "-")'
```

Use `--json`. With `--agent`, every entry comes back stripped to `{"type":"CONFIG"}`.

Each line is the time, who did it, the action, and what it touched. Look for `UPDATE TAILNET ACL` (someone changed the policy file), `CREATE INVITE NODE_SHARE` and `ACCEPT INVITE` (machine shares), and changes to users. Without the CLI, the admin console's **Logs** page has the same record.

## Close the gaps

Each fix, with its tier and its undo:

- **A member who shouldn't be one.** The user removes or suspends them on the admin console's **Users** page. The agent never adds or removes users. Undo: invite them again.
- **A share someone accepted.** The user revokes it on the **Machines** page, from that Mac's **Share** menu, as in [contractor-access.md](contractor-access.md). Undo: share the Mac again, which sends a new invite. Then run `shares audit` again.
- **Invites nobody accepted.** See the plan first (run freely): `tailscale-pp-cli shares revoke --device home-mac --pending`. Then ask first, name the risk ("Those invite links stop working."), and run it again with `--yes`. Undo: share the Mac again for a new link.
- **A device of yours on their tailnet.** Ask their admin to remove it from their **Machines** page, or log out of that account on the device: switch to it, then **Settings**, **Accounts**, **Log Out** in the Tailscale app, then switch back to your own account. Ask first and name the risk: "Switching takes this device off your tailnet until you switch back, so never do it on the Mac that runs your always-on services or the one you're connected through." Check with `tailscale switch --list` (run freely). Undo: add the account again.
- **A policy rule that lets outside people in.** The user edits the policy file on the **Access controls** page. The agent never edits it by hand. Before they change anything, they copy the whole file somewhere safe, and the undo is pasting it back. Afterward, run step 1 and `access check` again.
- **Funnel on something you didn't mean to publish.** Turn it off as in [public-demo.md](public-demo.md).

## What success looks like

On each of your Macs, and on any device that offers your home network, the peer list shows only `yours`, `tagged` devices you set up, and `shared in`. `access check --from <their-login>` finds no rule for the ports you tried. `shares audit` shows a `redeemable_count` of 0. On the devices you care about, `tailscale switch --list` shows only your own account.

## Undo

The audit only reads. Each fix above has its undo next to it.

## When it goes wrong

- **`tailscale-pp-cli doctor` says `FAIL Auth: not configured`**: it needs an API access token in `TAILSCALE_API_KEY`. See [SKILL.md](../SKILL.md).
- **Every audit log entry is `{"type":"CONFIG"}`**: you used `--agent`. Use `--json`.
- **`access check` warns the login isn't on your tailnet**: it's misspelled, or they aren't a user here. Compare it with step 2's list.
- **Someone shows up on one Mac's list but not another's**: rules can differ per device. That's why the check runs on each Mac.
- **An `OTHER USER` login that isn't in step 2's list**: it came through another route, such as an `externalTailnets` rule. Check step 5.
