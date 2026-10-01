# Open a site running on your laptop from your phone

## When you'd want this

You're building a site on your laptop at `http://localhost:3000` and want to see it on your phone, or show it to someone else on your tailnet. Serve gives that site a private web address that only devices on your tailnet can open.

A few words first:

- **Tailnet**: your private network. Every device signed in to your Tailscale account is on it.
- **localhost**: "this computer". A site at localhost only works on the machine running it until you share it.
- **Serve**: the Tailscale feature that shares a site from this computer with your tailnet. It stays private. For public sharing, see [public-demo.md](public-demo.md).

## Before you start

- The site is running on the laptop, for example at `http://localhost:3000`.
- Tailscale is on and connected on your phone.
- HTTPS certificates are turned on for your tailnet. If they aren't, the first `serve` command prints a link to turn them on. The user opens it, not the agent. Tell them this first: turning on HTTPS publishes your device names and tailnet name in a public certificate log. If a device name is private, such as a client's name, rename the device first.

## Steps

1. See what this Mac already shares. Run freely:

   ```sh
   tailscale serve status
   ```

   `No serve config` means nothing is shared. If it lists anything, leave those alone. They're other things this Mac is already serving.

2. Share the site. Ask first, and show the undo (`tailscale serve --https=8443 off`) at the same time:

   ```sh
   tailscale serve --bg --https=8443 3000
   ```

   `3000` is the site's port. `--bg` keeps it running after the command returns. `--https=8443` gives it its own port. Without it, Serve uses the default port (443), which may already hold something else on this Mac, and turning off a shared port turns off everything on it. With its own port, the undo can't touch anything else.

## What success looks like

The command prints something like:

```text
Available within your tailnet:

https://laptop.your-tailnet.ts.net:8443/
|-- proxy http://127.0.0.1:3000

Serve started and running in the background.
To disable the proxy, run: tailscale serve --https=8443 off
```

Open that `https://` address on your phone. You'll see the same site as on your laptop.

If the user is running this themselves in Terminal and `tailscale serve status` showed nothing, `tailscale serve 3000` is simpler. It runs until they press Ctrl+C, and stopping it is the undo.

## Undo

Ask first:

```sh
tailscale serve --https=8443 off
```

Check it worked (run freely): `tailscale serve status` no longer lists `:8443`.

Don't use `tailscale serve reset` unless the user wants everything this Mac shares turned off. It clears every Serve and Funnel setting at once.

## On a Mac

The Mac App Store and Standalone apps can share a site running on this computer. They can't share a file or a folder, and they can't point at another computer's address.

## When it goes wrong

- **The phone can't open the address**: check the Tailscale app on the phone is on and connected.
- **The page loads with an error**: the site isn't running at `localhost:3000`. Start it, then reload.
- **`Path serving is not supported on macOS due to sandbox restrictions`**: you pointed Serve at a folder. Start a small local web server in that folder instead (ask first), then serve its port: `cd ~/Sites/demo && python3 -m http.server 3000 --bind 127.0.0.1`. The `--bind` part keeps that server visible only to this computer, so the local wifi can't see it.
- **It printed a link and is waiting**: HTTPS isn't turned on for your tailnet yet. The user opens the link and approves it.
- **`Are you sure you want to delete 3 handlers under port 443?`**: you're turning off a port that has several things on it. Answer no, and turn off only the port you added.
- **`handler does not exist`**: nothing is on that port. Run `tailscale serve status` to see what's there.
- **`Another client is changing the serve config; please try again.`**: run the same command again.
