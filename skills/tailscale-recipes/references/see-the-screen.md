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
- **It's laggy**: you're probably on a relay. Run `tailscale ping home-mac` and see [is-it-online.md](is-it-online.md).
