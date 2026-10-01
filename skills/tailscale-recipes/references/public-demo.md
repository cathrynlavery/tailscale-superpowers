# Share a local site publicly for a demo, then turn it off

## When you'd want this

You want to show a client or a friend something running on your laptop, and they aren't on your tailnet. Funnel puts that site on the public internet at an `https://...ts.net` address for as long as you leave it on. Then you turn it off.

A few words first:

- **Tailnet**: your private network. Every device signed in to your Tailscale account is on it.
- **Funnel**: the Tailscale feature that makes a site on this computer reachable by anyone on the internet who has the link. For private sharing, use [open-site-on-phone.md](open-site-on-phone.md) instead.

Every Funnel change is ask first and name the risk. The risk sentence: "Anyone on the internet who has this link can open the site until you turn it off."

## Before you start

- Funnel is a beta feature. It needs MagicDNS (Tailscale's naming), HTTPS certificates, and permission in your tailnet's policy file. If any of these are missing, the first `funnel` command prints a link to approve. The user opens it. The agent never edits the policy file or the admin console.
- Turning on HTTPS publishes your device names and tailnet name in a public certificate log. If a device name is private, rename the device first.
- Check the site has nothing private in it: no admin pages, no real customer data, no keys or passwords in the page.
- Funnel only works on ports 443, 8443, and 10000. Tailscale 1.102 accepts other ports without an error and even lists them as `(Funnel on)`, but nobody outside can reach them.

## Steps

1. See what this Mac already shares. Run freely:

   ```sh
   tailscale funnel status
   ```

   Each address ends in `(tailnet only)` or `(Funnel on)`. `No serve config` means nothing is shared.

   Funnel switches on per port, not per page. If something else is already shared on the port you pick, it goes public too. Pick a port with nothing on it. This recipe uses 8443.

2. Go public. Ask first and name the risk, and show the undo (`tailscale funnel --https=8443 off`) at the same time:

   ```sh
   tailscale funnel --bg --https=8443 3000
   ```

   `3000` is your site's port on this computer. `--bg` keeps it running after the command returns.

## What success looks like

The command prints something like:

```text
Available on the internet:

https://laptop.your-tailnet.ts.net:8443/
|-- proxy http://127.0.0.1:3000

Funnel started and running in the background.
To disable the proxy, run: tailscale funnel --https=8443 off
```

Test it from your phone with wifi turned off, so you know it works from outside your network. A brand-new Funnel address can take up to 10 minutes to work for everyone, because public DNS records take time to appear.

If the user runs it themselves in Terminal and nothing else is shared, `tailscale funnel 3000` is simpler. It stays public until they press Ctrl+C.

## Undo

Turn it off as soon as the demo ends. Ask first:

```sh
tailscale funnel --https=8443 off
```

Check it worked (run freely): `tailscale funnel status` no longer shows `:8443`.

Don't use `tailscale funnel reset` unless the user wants everything this Mac shares turned off. It clears every Serve and Funnel setting at once, private ones included.

## On a Mac

The Mac App Store and Standalone apps can put a site running on this computer on Funnel. They can't share a file or a folder.

## When it goes wrong

- **Status says `(Funnel on)` but nobody outside can open it**: check the port. Only 443, 8443, and 10000 work, even though the CLI accepts others. Turn that port off (`tailscale funnel --https=<port> off`) and use 8443.
- **It printed a link and is waiting**: Funnel or HTTPS isn't turned on for your tailnet yet. The user opens the link and approves it.
- **It works for you but not for them**: give it up to 10 minutes after the first time. If they opened the link before it was live, their network may remember "not found" for a while longer, so have them try on a phone with wifi off. Then check they have the exact address, including `:8443`.
- **`Warning: funnel=on for ..., but no serve config`**: Funnel is on for a port with nothing behind it. Run the undo for that port.
- **Something you didn't mean to share is public**: it was on the same port. Run the undo now, then share the demo again on a port with nothing else on it.
