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

Undo (ask first): `tailscale serve --https=<port> off`, using the port in the printed link.

## 2. The hook

The hook reads the agent's final reply. If it finds an `http://` or `https://` link to `localhost`, `127.0.0.1`, `0.0.0.0` or `[::1]` outside a code block, it runs `tailnet-url` for each one itself and shows you the result under the reply:

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

Port links are fine for quick previews. For something that's always running, like a dashboard or a review page, a name is easier to remember. Tailscale Services gives a service its own name on your tailnet, with a certificate:

```sh
tailscale serve --service=svc:dashboard --https=443 127.0.0.1:8080
```

After the user approves the service once in the admin console, it's reachable at `https://dashboard.your-tailnet.ts.net` from any device on the tailnet. The app itself stays on `127.0.0.1`. Safety tier: ask first, and the approval is the user's step.

Some people do the same thing with their own domain: split DNS in the tailnet settings sends `*.internal.example` to one machine, and Caddy on that machine routes each name to the right local port. It's more to run (a DNS server, Caddy, and certificates for your domain), so use it when you want your own names; Tailscale Services covers most people.

## When it goes wrong

- **`nothing is loading on local port 3000`**: the app isn't running, or it's on a different port. Start it, or check the port.
- **`Tailscale link did not load`**: the mapping was made but the link didn't answer. Check `tailscale serve status`, and that HTTPS certificates are turned on.
- **`Tailscale CLI not found`**: on a Mac, the app's CLI is at `/Applications/Tailscale.app/Contents/MacOS/Tailscale`. The script finds it there automatically; otherwise add `tailscale` to PATH.
- **The hook keeps stopping a reply that only mentions localhost in passing**: put the address in a code block, or drop the `http://`. The hook only acts on full links.
