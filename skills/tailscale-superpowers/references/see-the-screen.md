# See and control your home Mac's screen

## When you'd want this

An agent on your home Mac is stuck on something that needs a click: a permission popup, a sign-in window, an app with no command line. SSH gives you a terminal on that Mac. Screen Sharing gives you its screen, mouse, and keyboard, from your laptop.

A few words first:

- **Tailnet**: your private network. Every device signed in to your Tailscale account is on it.
- **Screen Sharing**: built into macOS. It shows another Mac's screen in a window and lets you use it as if you were sitting there.
- **VNC**: the technology Screen Sharing uses. That's why its addresses start with `vnc://`.

## One-time setup on the home Mac

The user does this, at the home Mac. It's ask first and name the risk: "Anyone who can reach this Mac and knows the password for an allowed account can see and control its screen."

1. System Settings, General, Sharing, then switch on **Screen Sharing**.
2. Click the info button next to it. Set **Allow access for** to **Only these users**, and keep the list to your own account.
3. Make sure Tailscale opens at login and the Mac doesn't sleep. See [new-mac-setup.md](new-mac-setup.md), Part 1.

## From your laptop

1. Check the home Mac is on the tailnet. Run freely:

   ```sh
   tailscale ping home-mac
   ```

2. Check Screen Sharing is on, without connecting. Run freely:

   ```sh
   nc -z -G 3 home-mac 5900
   ```

   `Connection to home-mac port 5900 [tcp/rfb] succeeded!` means it's on. No output at all means it's off. `-G 3` makes it give up after 3 seconds.

3. Connect. Ask first:

   ```sh
   open vnc://home-mac
   ```

   The Screen Sharing app opens and asks for a username and password on the home Mac. The user types them. The agent never asks for or handles the password.

## What success looks like

A window showing the home Mac's screen. Your clicks and typing go to the home Mac.

## Put every Mac in the Screen Sharing list

The Screen Sharing app only lists Macs you've connected to before, and often by a home-only name like `home-mac.local`. To list every Mac on the tailnet by its full tailnet name, so each one works from anywhere:

1. Preview. Run freely:

   ```sh
   scripts/screen-sharing-list.py
   ```

   It prints one `add` line for each online Mac that has Screen Sharing on (port 5900 answers) and isn't listed yet. Add `--user home-mac=alex` to fill in the login name, and `--skip home-mac` to leave a machine out, for example a server you never screen-share to.

2. Write. Ask first. Quit Screen Sharing first; it overwrites the list when it quits.

   ```sh
   scripts/screen-sharing-list.py --yes --user home-mac=alex
   ```

   It backs up the settings file first and prints the backup path. Undo: copy that backup over `~/Library/Containers/com.apple.ScreenSharing/Data/Library/Preferences/com.apple.ScreenSharing.plist` while the app is quit.

An entry saved as `home-mac.local` or a raw `100.x` address only works on the home network or until the address changes. Replace it with the tailnet name. Offline Macs aren't added; run it again when they're on.

## Screens 5 (Edovia)

Screens 5's own Tailscale section lists Macs by asking `api.tailscale.com`. Some Wi-Fi networks and DNS filters block that address. Check it. Run freely:

```sh
dig +short api.tailscale.com
```

`0.0.0.0` means it's blocked, and Screens shows "No Registered Computers" under Tailscale. Saved Links don't depend on the API, because the Mac's own Tailscale resolves the tailnet name. To add one, ask first:

```sh
open -a "Screens 5" "vnc://alex@home-mac.your-tailnet.ts.net"
```

Screens saves the address under Links right away and opens a password prompt. The user types the password or cancels; the agent never touches it. Do this once per Mac. Opening a `.screens` archive with `open` did not import anything in testing, so use the links instead.

## From your phone or iPad

Apple doesn't make a Screen Sharing app for iPhone or iPad. A VNC app from the App Store, such as Screens, can connect to `home-mac` while Tailscale is on.

## Someone else's Mac

The same steps work for a family member's Mac, but everything moves to the "ask first and name the risk" tier and their consent comes first. Follow the rules in [help-family-mac.md](help-family-mac.md). A shared Mac needs its full name, like `vnc://family-mac.their-tailnet.ts.net`.

## Undo

- To end the session, close the Screen Sharing window.
- To turn it off, the user goes to System Settings, General, Sharing on the home Mac and switches off **Screen Sharing**.

## When it goes wrong

- **`nc` prints nothing**: Screen Sharing is off on the home Mac, or its firewall blocks it.
- **`tailscale ping` says `no reply`**: the home Mac is asleep, off, or Tailscale isn't running on it. See [is-it-online.md](is-it-online.md).
- **The home Mac restarted and now can't be reached**: the App Store and Standalone Tailscale apps only start after someone logs in at the Mac. Until somebody does, it's off the tailnet.
- **The password is rejected**: use the username and password of an account on the home Mac, one that's on the allowed list.
- **Remote Management rejects a correct admin password**: check its allowed-user list. An empty list can cause `not valid admin`; after the access-change approval required by the skill, grant only the intended account through Remote Management's access settings. The recorded CLI remedy is `kickstart -configure -access -on -users <user> -privs -all -restart -agent` with sudo; preview the access being granted and preserve the prior settings for undo (ERR-20261024-STUDIO36102EAF16).
- **It's laggy**: you're probably on a relay. Run `tailscale ping home-mac` and see [is-it-online.md](is-it-online.md).

If the user wants automatic login after a restart, have them enable it from the
Mac's own System Settings > Users & Groups, in person or over Screen Sharing.
`sysadminctl -autologin set` over SSH can set `autoLoginUser` while failing to save
the password (`SACSetAutoLoginPassword error:22`, missing SessionAgent). Verify
`sysadminctl -autologin status` and that `/etc/kcpassword` exists; never read or print
that file. The `autoLoginUser` key alone does not prove automatic login works
(ERR-20261024-STUDIO36102EAF16; related ERR-20261024-STUDIO0DAAE7BAFE,
ERR-20261024-STUDIO8B6CBB7BE7).
