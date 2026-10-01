# Share a folder between your Macs (Taildrive)

## When you'd want this

You want to open a folder on your home Mac from your laptop without copying it anywhere: video footage, an archive, a folder your agents write into. Tailscale's Taildrive feature shares it over your tailnet.

A few words first:

- **Tailnet**: your private network. Every device signed in to your Tailscale account is on it.
- **Taildrive**: Tailscale's folder sharing. Tailscale labels it alpha, so expect rough edges and changes.
- **Policy file**: the rules for your tailnet, kept in the Tailscale admin console. It says which devices can do what.

## Taildrive or Dropbox?

They do different jobs.

**Taildrive** keeps one copy of each file, on the Mac that shares it. Other devices open the files over your tailnet. Nothing goes to a cloud company's servers and there's no storage plan to pay for. Two machines can't drift out of sync, because there's only one copy. The sharing Mac has to be awake and online, though. There are no offline copies, and no version history beyond whatever backups that Mac has.

**Dropbox** (or iCloud Drive) keeps a copy on every device. Files work offline, there's version history, and you can send a link to someone outside your tailnet. The files also live on the company's servers and count against your plan. When two machines change the same file before it syncs, you get "conflicted copy" files.

Keep working files you need everywhere in Dropbox, and use Taildrive for big or private files that live on one Mac.

## Is Taildrive allowed on your tailnet?

Run freely, on each Mac that will share or open folders:

```sh
tailscale status --json | python3 -c 'import json,sys; c=json.load(sys.stdin)["Self"].get("CapMap") or {}; print("share:", "drive:share" in c, "access:", "drive:access" in c)'
```

`share: True access: True` means the policy file allows it for this device. `False` means the next step comes first.

## One-time: allow it in the policy file

The user does this in the admin console. The agent never edits the policy file. It's ask first and name the risk: "These rules let devices on your tailnet read and write each other's shared folders."

On the **Access controls** page, the user adds these two blocks from Tailscale's Taildrive docs. If the file already has a `nodeAttrs` or `grants` section, the entries go inside the existing one:

```json
"nodeAttrs": [
  {
    "target": ["autogroup:member"],
    "attr": [
      "drive:share",
      "drive:access",
    ],
  }
]
```

```json
"grants": [
  {
    "src": ["*"],
    "dst": ["*"],
    "app": {
      "tailscale.com/cap/drive": [{
        "shares": ["*"],
        "access": "rw"
      }]
    }
  }
]
```

As written, every device on the tailnet can read and write every share. That's fine when the tailnet is only you. If other people are on it, ask Tailscale's official skill or docs for a narrower rule first.

Undo: the user removes those entries.

## One-time: show the hidden setting on the sharing Mac

On a Mac, sharing is done in the Tailscale app, and the setting is hidden until you switch it on. Check whether it's already showing (run freely):

```sh
defaults read io.tailscale.ipn.macos FileSharingConfiguration
```

It prints `show` if it's on. An error saying it `Could not find key` means it's off.

To switch it on, ask first. For the App Store app:

```sh
defaults write io.tailscale.ipn.macos FileSharingConfiguration -string show
```

For the Standalone app from tailscale.com:

```sh
defaults write ~/Library/Preferences/io.tailscale.ipn.macsys.plist FileSharingConfiguration show
```

Step one of [SKILL.md](../SKILL.md) explains how to tell which app is installed. Then the user quits and reopens Tailscale.

Undo (ask first): `defaults delete io.tailscale.ipn.macos FileSharingConfiguration` for the App Store app, or `defaults delete ~/Library/Preferences/io.tailscale.ipn.macsys.plist FileSharingConfiguration` for Standalone. Then reopen Tailscale.

## Share a folder

The user does this in the app. A Mac has no CLI command for it.

1. Open Tailscale's **Settings**, then **File Sharing**.
2. Click the plus button and pick the folder. The share is named after the folder. Double-click a name to rename it.

Share only the folder you need, not your whole home folder.

On Linux and Windows the CLI does it: `tailscale drive share footage /path/to/footage` (ask first), `tailscale drive list` (run freely), `tailscale drive unshare footage` (ask first).

## Open it from another Mac

The user does this in Finder:

1. Choose Go, then **Connect to Server** (or press Command-K).
2. Enter `http://100.100.100.100:8080` and connect. Finder warns that the connection isn't secure. Choose **Continue**. The traffic is still encrypted by Tailscale.
3. Connect as **Guest**.

Folders are arranged by tailnet, then device, then share, like `your-tailnet/home-mac/footage`.

Tailscale says phones can open shares too. Its Taildrive docs have the details.

## What success looks like

A Finder window with the shared folder's files. Open a file, change it, save it, and the change is on the home Mac.

## Undo

- To disconnect, eject the share in Finder's sidebar.
- To stop sharing a folder, the user selects it in Tailscale's **Settings**, **File Sharing**, and clicks the minus button.
- To hide the setting again, see the undo under "Show the hidden setting".
- To turn Taildrive off for the tailnet, the user removes the policy file entries.

## When it goes wrong

- **The check prints `False`**: the policy file entries are missing or don't cover this device.
- **No File Sharing in Settings**: the hidden setting isn't on, or Tailscale wasn't reopened after switching it on.
- **Finder can't connect to `100.100.100.100:8080`**: Tailscale is off on this Mac, or this device doesn't have `access: True`.
- **The share is missing or slow**: the sharing Mac is asleep or on a relay. See [is-it-online.md](is-it-online.md).
