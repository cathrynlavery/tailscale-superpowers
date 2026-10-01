# Check on all your Macs at once

## When you'd want this

You want a quick morning answer to "are all my machines up?" Or an agent can't reach one Mac and you want the whole picture before digging in. Or you want to know which device is about to fall off your tailnet because its sign-in is running out.

A few words first:

- **Tailnet**: your private network. Every device signed in to your Tailscale account is on it.
- **Key expiry**: each device's Tailscale sign-in lasts a set time, 180 days by default on new tailnets. When it runs out, the device drops off the tailnet until someone signs in on it again.
- **Relay**: when two devices can't connect directly, traffic goes through one of Tailscale's relay servers. It works, just slower.

## The check

Run freely. It reads `tailscale status --json` and changes nothing:

```sh
python3 scripts/check-all-macs.py
```

Run it from the skill's folder, the one with SKILL.md in it. It finds the Tailscale CLI by itself, the same way step one of SKILL.md does. To be warned earlier than 30 days ahead, add `--days 60`.

## What success looks like

One row per device, this device first, then a short summary:

```text
DEVICE      OS     STATUS   LAST SEEN  CONNECTION   KEY EXPIRES
laptop      macOS  online   -          this device  2027-02-12 (134d)
home-mac    macOS  online   -          direct       off
office-mac  macOS  online   -          relay (nyc)  2027-03-10 (160d)
phone       iOS    online   -          idle         2027-01-03 (94d)
agent-mini  macOS  offline  3d ago     -            2026-10-20 (19d)  <- expiring soon

5 devices: 4 online, 1 offline.
Sign-in expires within 30 days: agent-mini
```

How to read it:

- **LAST SEEN**: for offline devices, how long since Tailscale last heard from them.
- **CONNECTION**: `direct` is the fast path. `relay (nyc)` means traffic goes through the New York relay. `idle` means online, with nothing sent to it lately. To find out how an idle device would connect, run `tailscale ping` on it (see [is-it-online.md](is-it-online.md)).
- **KEY EXPIRES**: the date the sign-in runs out and the days left. `off` means key expiry is turned off for that device. `EXPIRED` means it's already off the tailnet.
- Devices shared with you from someone else's tailnet show their full name, ending in `.ts.net`, marked `(shared)`.

## Is Tailscale up to date?

Run freely:

```sh
tailscale version --upstream
```

The first line is this device's version. The `upstream:` line is the newest release. If they differ, update Tailscale the way it was installed: the App Store, the Standalone app's own updater, or Homebrew.

To check another Mac, run the same command over SSH (ask first, it's SSH into your own machine), using that Mac's CLI path. For the App Store app: `ssh home-mac '/Applications/Tailscale.app/Contents/MacOS/Tailscale version'`.

## When a sign-in is about to expire

The agent's job is the warning. Either fix belongs to the user:

- **Sign in again before the date.** On that device, the user signs in again in the Tailscale app. With the CLI it's `tailscale up --force-reauth`, which is ask first and name the risk: "This disconnects the device until you finish signing in, so don't run it over SSH or Tailscale."
- **Turn key expiry off for that device.** Admin console, Machines page, the menu at the far right of the device's row, **Disable Key Expiry**. The agent never does this. Before the user does, say the risk: a device with expiry off stays on the tailnet until someone removes it, even if it's lost or stolen.

A device that already shows `EXPIRED` needs someone to sign in on it.

## Undo

Nothing to undo. The check only reads.

## When it goes wrong

- **`python3: command not found`, or a popup asking to install developer tools**: on a fresh Mac, `python3` comes with Apple's command line tools. The user can install them from that popup. Until then, `tailscale status` shows who's online, without expiry dates.
- **`Couldn't find the tailscale command`**: see step one of [SKILL.md](../SKILL.md).
- **`Tailscale isn't connected on this machine`**: open the Tailscale app and connect.
- **A device you expected is missing**: it's signed in to a different account, or it was removed from the tailnet.
