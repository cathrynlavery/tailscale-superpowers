# Give tailnet links, never localhost, without relying on a rule

## When you'd want this

You work across a few computers and your phone. An agent finishes something and says "open http://localhost:3000". That link only works on the machine running the app, so from your laptop or phone it's a dead end.

You could add a line to AGENTS.md asking for Tailscale links. That works until an agent forgets. This recipe doesn't depend on the agent at all:

1. **`tailnet-url`**, a script that turns a local port into a working tailnet link in one step.
2. **`localhost-guard`**, a hook that runs when an agent finishes a reply. If the reply has a localhost link, the hook makes the tailnet link itself and shows it to you under the reply.
3. Optional: **a stable name** like `https://preview.your-tailnet.ts.net` for apps that are always running.

A few words first:

- **Tailnet**: your private network. Every device signed in to your Tailscale account is on it.
- **Serve**: the Tailscale feature that shares something running on this computer with your tailnet only. See [open-site-on-phone.md](open-site-on-phone.md).
- **Hook**: a small program your agent tool runs at set moments. This one runs when the agent is about to finish its reply.

## Before you start

- Tailscale is on and HTTPS certificates are turned on for your tailnet. If they aren't, the first `serve` prints a link to turn them on. The user opens it, not the agent.
- `python3` is installed. It comes with macOS's command line tools.

## 1. The script

Run it with the app's port, and optionally a path:

```sh
scripts/tailnet-url 3000
scripts/tailnet-url 3000 /dashboard
```

It checks the app answers on `127.0.0.1:3000`, shares it with Serve (or reuses the mapping if it's already shared), checks the tailnet link loads, and prints it:

```text
https://laptop.your-tailnet.ts.net:3000/dashboard
```

If port 3000 on the tailnet side is already taken by something else, it picks a free port between 18000 and 18999 instead, so it never touches what's already shared.

Safety tier: **ask first**, because it runs `tailscale serve`. If the user has said they always want tailnet links (for example, a standing instruction in their agent rules), that counts as the yes.

Undo (ask first): `tailscale serve --https=<port> off`, using the port in the printed link. If the link was already shared before you ran the script, it was reused, so leave it on.

## 2. The hook

The hook reads the agent's final reply. If it finds an `http://` link to `localhost`, `127.0.0.1`, `0.0.0.0` or `[::1]` outside a code block, it runs `tailnet-url` for each one itself and shows you the result under the reply:

```text
Tailnet link for http://localhost:3000/: https://laptop.your-tailnet.ts.net:3000/
```

If nothing is running on that port, the line says so instead. The agent isn't asked to do anything, and the reply isn't held up. The hook does nothing on a computer without Tailscale, and it leaves code blocks alone, because config files and examples legitimately contain `localhost`.

Because the hook shares the port for you, installing it counts as the user's standing yes for `tailnet-url` on that computer.

Install it for Claude Code by adding this to `~/.claude/settings.json`, merged into any `hooks` you already have. Use the path where the skill is installed:

```json
{
  "hooks": {
    "Stop": [
      { "hooks": [ { "type": "command", "command": "python3 \"$HOME/.claude/skills/tailscale-superpowers/hooks/localhost-guard.py\"", "timeout": 30 } ] }
    ]
  }
}
```

For Codex, add the same entry under `hooks.Stop` in `~/.codex/hooks.json`, then approve it once in Codex's `/hooks` review.

Check it works (run freely):

```sh
python3 hooks/test_localhost_guard.py
```

Undo: remove the entry from the settings file.

## 3. Stable names (optional)

Port links are fine for quick previews. For something that's always running, like a dashboard, a name is easier to remember: `https://dashboard.your-tailnet.ts.net`. Tailscale Services gives it that name with a real certificate, and the app stays on `127.0.0.1`.

One catch: a Service has to be hosted by a tagged device, and your own Mac is signed in as you. Rather than tagging it, run a second small Tailscale node next to the app whose only job is hosting Services.

**One-time setup.** Steps 1 and 2 are the user's, in the admin console:

1. **Access controls**: add a tag for the node: `"tagOwners": {"tag:svc": ["autogroup:admin"]},`
2. **Settings, Keys, Generate auth key**: one-off, pre-approved, tag `tag:svc`. Save it to a file only you can read, such as `services.key`.
3. Install open-source Tailscale into its own folder, so it can't clash with the Tailscale app. It needs Go. Ask first:

   ```sh
   GOBIN=~/.local/share/tailscale-services/bin go install tailscale.com/cmd/tailscale@latest tailscale.com/cmd/tailscaled@latest
   ```

4. Keep it running with launchd, with its own state, socket and port. Like the Tailscale app, it runs while you are logged in. Save this as `~/Library/LaunchAgents/tailscale-services.plist`, with your home folder in place of `/Users/you`, then load it. Ask first:

   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
   <plist version="1.0"><dict>
     <key>Label</key><string>tailscale-services</string>
     <key>ProgramArguments</key><array>
       <string>/Users/you/.local/share/tailscale-services/bin/tailscaled</string>
       <string>--tun=userspace-networking</string>
       <string>--statedir=/Users/you/.local/share/tailscale-services/state</string>
       <string>--socket=/Users/you/.local/share/tailscale-services/tailscaled.sock</string>
       <string>--port=41642</string>
     </array>
     <key>RunAtLoad</key><true/>
     <key>KeepAlive</key><true/>
   </dict></plist>
   ```

   ```sh
   launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/tailscale-services.plist
   S=~/.local/share/tailscale-services
   $S/bin/tailscale --socket=$S/tailscaled.sock up --auth-key=file:services.key --hostname=services --advertise-tags=tag:svc && rm services.key
   ```

**Each name.** Ask first. The first and last commands use the [admin CLI](../SKILL.md#optional-the-admin-cli); run each with `--dry-run` first to see the request:

```sh
S=~/.local/share/tailscale-services
tailscale-pp-cli tailnet services update svc:dashboard --name svc:dashboard --ports tcp:443
$S/bin/tailscale --socket=$S/tailscaled.sock serve --bg --service=svc:dashboard --https=443 http://127.0.0.1:8080
tailscale-pp-cli tailnet services update-device-approval svc:dashboard <node-id> --approved
```

`<node-id>` is the services node's `nodeId` from `tailscale-pp-cli tailnet devices list`. After that, `https://dashboard.your-tailnet.ts.net` opens on every device on your tailnet. Tailscale still passes the visitor's identity headers, such as `Tailscale-User-Login`, so apps that check who's visiting keep working. If your access policy isn't the default allow-all, also grant access in it: `{"src": ["autogroup:member"], "dst": ["svc:dashboard"], "ip": ["tcp:443"]}`. Check the name opens from another device. Without the CLI, define and approve the service on the admin console's Services page instead.

Undo (ask first): `$S/bin/tailscale --socket=$S/tailscaled.sock serve clear svc:dashboard`, then `tailscale-pp-cli tailnet services delete svc:dashboard`.

Some people get names with their own domain instead: split DNS sends `*.internal.example` to one machine, and Caddy there routes each name to a local port. That means running a DNS server, Caddy and certificates for your domain, so use it when you want your own domain.

## When it goes wrong

- **`nothing is loading on local port 3000`**: the app isn't running, or it's on a different port. Start it, or check the port.
- **`Tailscale link did not load`**: the mapping was made but the link didn't answer. Check `tailscale serve status`, and that HTTPS certificates are turned on.
- **`Tailscale CLI not found`**: on a Mac, the app's CLI is at `/Applications/Tailscale.app/Contents/MacOS/Tailscale`. The script finds it there automatically; otherwise add `tailscale` to PATH.
- **The hook shows a link for an address that was only mentioned in passing**: put the address in a code block, or drop the `http://`. The hook only acts on full links.
