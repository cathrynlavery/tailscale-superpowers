---
name: tailscale-superpowers
description: Plain-English recipes for everyday Tailscale tasks on a few personal Macs, with a safety tier on every command. Use when someone wants to route their traffic through a home computer on hotel or plane wifi, send a file to their phone or another Mac, help fix a family member's Mac over SSH, finish setting up a new Mac remotely, open a site running on their laptop from their phone, share a local site publicly for a demo, check whether another machine is online or why it's slow, let agents on different machines ask each other for help, check every machine at once, see another Mac's screen, check on agents from a phone, share a folder between Macs, reach a home printer or network drive while away, give a contractor access to one Mac, or set up one-word shortcuts into another Mac. A community skill for Tailscale, not made by or affiliated with Tailscale Inc.
license: MIT
---

# Tailscale Superpowers

For your agents.

A community skill for Tailscale. It isn't made by, affiliated with, or endorsed by Tailscale Inc.

These recipes cover everyday jobs for people who run AI agents on a few Macs. For admin work such as access rules, the policy file, users, or auth keys, point the user to Tailscale's official skill: https://github.com/tailscale/tailscale-skill

Talk to the user in plain English. Define tailnet, exit node, SSH, and relay the first time you use them. Use example names like home-mac, laptop, and phone, never real device names in anything you write down.

## Safety tiers

Every command in the recipes is labeled with one of these. Follow the tier even when the user sounds sure.

**Run freely.** Read-only: `tailscale status` (including `--json`), `ping`, `netcheck`, `ip`, `whois`, `whoami`, `version` (including `--upstream`), `get`, `dns status`, `exit-node list`, `exit-node suggest`, `serve status`, `funnel status`, `file cp --targets`, `file get` into a folder the user named, and `scripts/check-all-macs.py`. Also the look-only helpers the recipes use: `nc -z` port checks, `ssh -G`, `ippfind`, `lpstat`, `who`, `tmux ls`, and `defaults read`.

**Ask first.** Show the exact command and wait for a yes: set or clear an exit node, send a file, `serve`, SSH into the user's own machine, offer or stop offering a home network range (`--advertise-routes`), add or remove a printer, add an SSH key, edit `~/.ssh/config` or `~/.zshrc`, and switch Taildrive's hidden setting on or off.

**Ask first and name the risk.** Show the command, say the risk in one sentence, then wait for a yes: `funnel` (public internet), `down` or `logout`, turning on Remote Login or Screen Sharing, giving anyone else a way into the user's Mac, anything on another person's device, and anything that could cut the connection you're using. If you reach this machine over SSH or Tailscale, changing its exit node or running `down` can lock you out.

**Never.** Create or delete auth keys, edit access rules or the policy file, add or remove users, touch the admin console, or turn off key expiry. When a recipe needs one of these, such as approving a route, sharing a machine, adding Taildrive rules, or turning off key expiry, tell the user what to click and let them do it.

Show the undo next to every change, before you run it.

## Step one: find the CLI

`tailscale` in the recipes means the command-line tool. Find it before anything else. Check PATH, then the Mac app, then Homebrew:

```sh
command -v tailscale \
  || ls /Applications/Tailscale.app/Contents/MacOS/Tailscale \
  || ls /opt/homebrew/bin/tailscale /usr/local/bin/tailscale
```

Then confirm it runs (run freely): `<path> version`.

What to tell the user, depending on what you found:

- **On PATH.** Nothing to fix.
- **Inside the app.** The Mac app keeps the tool inside itself and doesn't add it to PATH, so typing `tailscale` in Terminal says "command not found". Run it by full path: `/Applications/Tailscale.app/Contents/MacOS/Tailscale status`. Use that path wherever a recipe says `tailscale`. If a script opens the app window instead of printing output, Tailscale's docs say to set `TAILSCALE_BE_CLI=1`.
- **Want plain `tailscale` in their own Terminal?** Ask first, since it edits their shell settings. Add `alias tailscale="/Applications/Tailscale.app/Contents/MacOS/Tailscale"` to `~/.zshrc`. Undo: delete that line. Agent shells often skip aliases, so keep using the full path yourself.
- **Standalone app** (downloaded from tailscale.com, or `brew install --cask tailscale-app`): the user can open the app's Settings, find the CLI integration section, choose Show me how, then Install Now. That puts `tailscale` at `/usr/local/bin/tailscale` and asks for their Mac password, so they do it.
- **Homebrew formula** (`brew install tailscale`): the open-source version, at `/opt/homebrew/bin/tailscale` on Apple silicon or `/usr/local/bin/tailscale` on Intel.
- **Linux:** usually already on PATH after install. **Windows:** `C:\Program Files\Tailscale\tailscale.exe`.
- **Nowhere.** Tailscale isn't installed. See [new-mac-setup.md](references/new-mac-setup.md).

Which Mac app it is matters. If `/Applications/Tailscale.app/Contents/_MASReceipt` exists, it's the Mac App Store version. That version can't run `tailscale ssh`, and Apple's sandbox limits which files it can send.

## Recipes

- [travel-wifi.md](references/travel-wifi.md): hotel or plane wifi you don't trust. Send your traffic through your home Mac.
- [send-a-file.md](references/send-a-file.md): send a file to your phone or another Mac with Taildrop.
- [help-family-mac.md](references/help-family-mac.md): help fix a family member's Mac over SSH, with their consent.
- [new-mac-setup.md](references/new-mac-setup.md): install Tailscale on a new Mac, then let an agent finish the setup.
- [open-site-on-phone.md](references/open-site-on-phone.md): open a site running on your laptop from your phone.
- [public-demo.md](references/public-demo.md): share a local site publicly for a demo, then turn it off.
- [is-it-online.md](references/is-it-online.md): is my other Mac online, and why is it slow?
- [agents-talk.md](references/agents-talk.md): let agents on different machines ask each other for help.
- [check-all-macs.md](references/check-all-macs.md): check every device at once, with how it's connected and when its sign-in expires.
- [see-the-screen.md](references/see-the-screen.md): see and control your home Mac's screen with Screen Sharing.
- [agents-from-phone.md](references/agents-from-phone.md): check on an agent running on your home Mac from your phone.
- [shared-folders.md](references/shared-folders.md): share a folder between your Macs with Taildrive, and when Dropbox is the better fit.
- [home-network.md](references/home-network.md): reach your home printer, network drive, or router page from anywhere.
- [contractor-access.md](references/contractor-access.md): give a contractor access to one Mac, then take it away.
- [one-word-shortcuts.md](references/one-word-shortcuts.md): type one word to get into another Mac.
