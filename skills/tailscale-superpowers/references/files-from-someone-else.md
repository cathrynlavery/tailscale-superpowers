# Get files from someone else over Tailscale

## When you'd want this

A friend or coworker says "I'm sharing the files with you over Tailscale." Whether you can open them, and from which device, depends on how your Tailscale accounts connect. This recipe works out which case you're in and what works in each.

A few words first:

- **Tailnet**: a private network of devices. Each Tailscale account belongs to one tailnet, and one person can be a user on more than one, such as a personal tailnet and a work one.
- **Taildrop**: sends files between your own devices.
- **Taildrive**: Tailscale's folder sharing. You open the folder in Finder while the files stay on the other person's Mac. Tailscale labels it alpha.
- **Policy file**: the rules for a tailnet, kept in its admin console. Whoever runs the tailnet writes it.
- **Sharing a machine**: one tailnet lends a single device to a user on another tailnet. The receiver sees that device and nothing else.
- **Account switching**: a device can be signed in to several Tailscale accounts, but it connects to one tailnet at a time.

## Taildrop won't do this

From Tailscale's Taildrop docs: "Taildrop is currently limited to sending files between your own personal devices. You cannot send files to devices owned by other users (even users on the same Tailscale network)." If they tried and got `cannot send files: peer is owned by a different user`, that's why. Use one of the cases below.

## Which case are you in?

Ask them two things: which tailnet the files are on, and which login they gave access to. Then check this device. Run freely:

```sh
tailscale status --json | python3 -c 'import json,sys; s=json.load(sys.stdin); print("tailnet:", s["CurrentTailnet"]["Name"], "| signed in as:", s["User"][str(s["Self"]["UserID"])]["LoginName"])'
tailscale switch --list
```

The first prints the tailnet this device is connected to and the login it uses. The second lists every account this device is signed in to, with `*` next to the one in use.

- **Case 1: you're both users on the same tailnet, and this device is connected to it.** Taildrive works.
- **Case 2: you're a user on their tailnet, but this device is on your own.** The share exists, but only a device connected to their tailnet as you can see it.
- **Case 3: you aren't a user on their tailnet.** Taildrive can't cross between tailnets. They share a machine with you and serve the files from it, or they send a cloud link.

Case 2 is common. Someone adds you to a work or business tailnet, and your own Macs stay on your personal one.

## Case 1: the same tailnet

1. **Allow Taildrive for both of you.** Whoever runs the tailnet adds these to its policy file. If the file already has a `nodeAttrs` or `grants` section, the entries go inside the existing one. They let the friend's devices share, let yours open shares, and give you read-only access to one share called `for-you`:

   ```json
   "nodeAttrs": [
     {"target": ["friend@example.com"], "attr": ["drive:share", "drive:access"]},
     {"target": ["you@example.com"], "attr": ["drive:access"]}
   ],
   "grants": [
     {
       "src": ["you@example.com"],
       "dst": ["friend@example.com"],
       "app": {"tailscale.com/cap/drive": [{"shares": ["for-you"], "access": "ro"}]}
     }
   ]
   ```

   If it's their tailnet, they make the change. If it's yours, it's the same job as in [shared-folders.md](shared-folders.md), with these entries in place of the catch-all ones: the user adds them in the admin console, or the agent plans each one with `tailscale-pp-cli policy add-entry` and runs it with `--yes` after asking first and naming the risk. The agent never edits the file by hand. Undo: remove the entries.

2. **Share the folder on their Mac.** They switch on the hidden File Sharing setting and add the folder in Tailscale's Settings, as in [shared-folders.md](shared-folders.md). The share's name has to match the grant, `for-you` here.

3. **Check this device can open shares.** Run freely:

   ```sh
   tailscale status --json | python3 -c 'import json,sys; c=json.load(sys.stdin)["Self"].get("CapMap") or {}; print("access:", "drive:access" in c)'
   ```

   `access: True` means their policy covers this device.

4. **Open it.** See "Open a Taildrive share in Finder" below.

## Case 2: you're on their tailnet, your Macs aren't

Their share is set up for your login, but Finder only shows shares from the tailnet a device is connected to. Your everyday Macs are on your own tailnet, so the share is invisible from them. You need a device connected to their tailnet as you.

Pick the device with the least to lose:

- **A phone or a spare laptop** that runs nothing you depend on. This is the best choice.
- **A Mac you're sitting at** that serves nothing to your other devices.
- **Never the Mac that runs your always-on services, and never the Mac you reach over SSH or Tailscale.** Switching takes it off your tailnet, and you'd lose the connection you need to switch it back.

On that device:

1. **Add the account, first time only.** The user does this: the Tailscale menu bar icon, **Settings**, **Accounts**, **Add Account**, then sign in as themselves with the login their tailnet knows. On an iPhone, in the Tailscale app: tap the profile picture at the top right, tap the account details at the top, then **Add another account**. Switching happens in that same list.

2. **Switch to it.** Ask first and name the risk: "While switched, this device is off your own tailnet. Your other devices can't reach it, and their tailnet's rules decide who can." Show the undo at the same time.

   ```sh
   tailscale switch you@work.example
   ```

   Use the account name exactly as `tailscale switch --list` shows it. In the app, it's the menu bar icon, the current account, then the other one.

   Undo (ask first): `tailscale switch you@example.com`, your own account, or pick it in the same menu.

3. **Open the share** (see below), copy what you need onto this device, then switch back.

4. **Check you're back.** Run freely: `tailscale switch --list` shows `*` next to your own account.

## Case 3: separate tailnets

From Tailscale's Taildrive docs: "A device shared into your tailnet cannot access any Taildrive folders in your tailnet." And: "a device you share to another tailnet cannot access any Taildrive folders in the other tailnet". So Taildrive between two people needs both of them on one tailnet. Two other ways work.

**A cloud link.** For a one-off, this is the easier answer. They put the files in Dropbox, iCloud Drive, or Google Drive and send you a link. Nothing to set up on either tailnet.

**They share one machine with you and serve the files from it.** Worth it when the files are big or private, or they'll send more later. Everything here happens on their Mac. If your agent helps them, every step is ask first and name the risk, because it's another person's device.

1. **They share their Mac with you.** In their admin console: Machines, the Mac's menu, **Share**, then share by email. You accept with your own account, which has to be an owner or admin of its tailnet (a personal account is). Accepting is safe for you. From Tailscale's sharing docs: "A shared machine can receive incoming connections (from the other user's tailnet) but cannot start connections."

2. **They serve the folder.** `tailscale serve` can serve a folder as a page of links, but Tailscale's docs say: "If you've installed Tailscale on macOS through the Mac App Store or as a Standalone variant system extension, you can use Serve to share ports but not files or directories." Most Macs run one of those. So they put the files in a folder, ideally as one zip, start a small web server in that folder, and serve its port:

   ```sh
   python3 -m http.server 8000 --bind 127.0.0.1 --directory ~/for-you
   tailscale serve --bg --https=8443 8000
   ```

   The first command keeps running in its Terminal window, so they run the second in another. `--bind 127.0.0.1` keeps the web server visible only to their Mac; Tailscale passes your connection to it. With the open-source variant of Tailscale, or on Linux, `tailscale serve --bg --https=8443 /full/path/to/for-you` serves the folder without the extra server. If serve prints a link to turn on HTTPS, see [open-site-on-phone.md](open-site-on-phone.md) for what that publishes.

   The risk to tell them: "Until you turn it off, this folder is open to anyone your tailnet's rules let reach this Mac, plus the person you shared it with."

3. **You open it.** In a browser, go to `https://friend-mac.their-tailnet.ts.net:8443` and download the files. Shared devices need that full name.

Undo, on their Mac (ask first): `tailscale serve --https=8443 off`, then Control-C in the web server's window. They revoke the share in the admin console, on the Machines page, from the Mac's **Share** menu.

## Open a Taildrive share in Finder

The user does this:

1. In Finder, choose Go, then **Connect to Server** (or press Command-K).
2. Enter `http://100.100.100.100:8080` and connect. Finder warns that the connection isn't secure. Choose **Continue**. Tailscale still encrypts the traffic.
3. Connect as **Guest**.

Folders are arranged by tailnet, then device, then share, like `their-tailnet/friend-mac/for-you`. Only the tailnet this device is connected to appears. With `"access": "ro"` you can open and copy the files but not change them.

On an iPhone or iPad, with Tailscale connected to the right tailnet, open the Files app and turn on Tailscale there.

## What success looks like

Finder shows their tailnet, `friend-mac`, and the share, and a file you double-click opens. In Case 3, the browser shows a list of files on their Mac and the download starts.

## Undo

- Eject the share in Finder's sidebar.
- Case 2: switch back to your own account and check `tailscale switch --list`. If you won't need their tailnet again on this device, log out of that account: switch to it, then **Settings**, **Accounts**, **Log Out** in the Tailscale app, then switch back to yours. That's ask first and name the risk, for the same reason as switching. To undo it, add the account again.
- Case 3: they turn off serve and revoke the share.

## When it goes wrong

- **Finder shows only your own tailnet**: this device is connected to your tailnet, not theirs. That's Case 2.
- **Their tailnet shows, but not their Mac or the share**: their Mac is asleep, the folder isn't added in their Tailscale settings, or the grant names a different login or share name.
- **The check prints `access: False`**: their policy's `drive:access` entry doesn't cover your login.
- **Can't save changes to their files**: the grant says `"access": "ro"`. Copy the files to your own disk.
- **`cannot send files: peer is owned by a different user`**: Taildrop between two people doesn't work. Pick a case above.
- **Their shared Mac isn't in `tailscale status`**: you haven't accepted the invite, or you accepted with an account that isn't an owner or admin of its tailnet.
- **`Could not resolve hostname`, or the page won't load**: use the full `.ts.net` name and the `:8443` on the end.
- **`Path serving is not supported on macOS due to sandbox restrictions`**: they pointed serve at a folder on the App Store or Standalone app. Use the web server step instead.
