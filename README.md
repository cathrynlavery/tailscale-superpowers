# Tailscale Recipes

A community skill for Tailscale. It gives your AI agent plain-English recipes for the everyday things you'd use Tailscale for, with a safety tier on every command.

This is an independent project. It isn't made by, affiliated with, or endorsed by Tailscale Inc.

## Why this exists

I run AI agents on a few Macs, and Tailscale is what ties them together. The official Tailscale tools are written for engineers configuring networks. I wanted recipes for the everyday stuff, written so my agent can explain each step to me, with clear limits on what it's allowed to touch.

The one I use most:

> Hotel/airplane wifi sketchy or slow? I route all my traffic through my house in Austin with one tap.

## What's inside

| Recipe | What it does |
| --- | --- |
| [Travel wifi](skills/tailscale-recipes/references/travel-wifi.md) | Send all your traffic through your home Mac when the wifi is sketchy |
| [Send a file](skills/tailscale-recipes/references/send-a-file.md) | Send a file to your phone or another Mac with Taildrop |
| [Help a family member's Mac](skills/tailscale-recipes/references/help-family-mac.md) | Fix their Mac over SSH, with their consent and every change approved |
| [New Mac setup](skills/tailscale-recipes/references/new-mac-setup.md) | Install Tailscale on a new Mac, then let an agent finish the setup |
| [Open a laptop site on your phone](skills/tailscale-recipes/references/open-site-on-phone.md) | Share a local site with your own devices only |
| [Public demo](skills/tailscale-recipes/references/public-demo.md) | Put a local site on the internet for a demo, then turn it off |
| [Is it online? Why is it slow?](skills/tailscale-recipes/references/is-it-online.md) | Check status, direct vs relayed connections, and your network |
| [Agents talking to agents](skills/tailscale-recipes/references/agents-talk.md) | A pointer to Agent Tincan |
| [Check on all your Macs](skills/tailscale-recipes/references/check-all-macs.md) | A read-only script lists every device, how it's connected, and when its sign-in expires |
| [See the screen](skills/tailscale-recipes/references/see-the-screen.md) | Use your home Mac's screen from your laptop with Screen Sharing |
| [Agents from your phone](skills/tailscale-recipes/references/agents-from-phone.md) | Check on an agent running on your home Mac from your phone |
| [Shared folders](skills/tailscale-recipes/references/shared-folders.md) | Share a folder between your Macs with Taildrive, and when Dropbox is the better fit |
| [Home printer and network drive](skills/tailscale-recipes/references/home-network.md) | Reach devices at home that can't run Tailscale, from anywhere |
| [Contractor access](skills/tailscale-recipes/references/contractor-access.md) | Give someone access to one Mac, then take it away |
| [One-word shortcuts](skills/tailscale-recipes/references/one-word-shortcuts.md) | Type one word to get into another Mac |

Each recipe covers when you'd want it, the exact commands, what success looks like, how to undo it, and what the common errors mean.

## Safety tiers

Every command in every recipe has one of four tiers:

- **Run freely**: read-only commands like `tailscale status` and `tailscale ping`.
- **Ask first**: the agent shows you the exact command and waits for a yes. Setting an exit node, sending a file, sharing a site on your tailnet, SSH into your own Mac.
- **Ask first and name the risk**: the agent also tells you the risk in one sentence. Making a site public, disconnecting, turning on Remote Login or Screen Sharing, giving someone else a way into your Mac, anything on someone else's device, anything that could cut the agent's own connection.
- **Never**: auth keys, access rules, the policy file, users, the admin console, key expiry. When a recipe needs one of these, such as approving a route or sharing a Mac with a contractor, the agent tells you what to click and you do it.

Every change comes with its undo, shown before the change runs. The full rules are at the top of [SKILL.md](skills/tailscale-recipes/SKILL.md).

## "tailscale: command not found"

On a Mac, the `tailscale` command lives inside the Tailscale app and isn't on your PATH. That's true of the App Store version, and of the version from tailscale.com until you install its command line tool from the app's settings. The skill's first step finds it and explains the fix, so you don't need to sort this out before installing.

## Install

The skill is the `skills/tailscale-recipes` folder. It follows the [Agent Skills](https://agentskills.io/specification) format, so it works in any agent that reads `SKILL.md` files. Copy that folder into your agent's skills folder:

| Agent | Personal skills folder |
| --- | --- |
| Claude Code | `~/.claude/skills/` |
| Codex | `~/.agents/skills/` |
| Cursor | `~/.agents/skills/` or `~/.cursor/skills/` |
| Pi | `~/.agents/skills/` |
| Hermes | `~/.hermes/skills/` |

<!-- TODO(Cathryn): once this is on GitHub, add the one-line install: npx skills add <owner>/tailscale-recipes -->

Then ask your agent something like "the hotel wifi here is sketchy, can you route me through my home Mac?"

## Sharing a clipboard between machines

Tailscale has no built-in clipboard sync, so there's no recipe for it.

<!-- TODO(Cathryn): add the tool you use to share a clipboard between your Macs. -->

## Going deeper

This skill sticks to everyday use. For configuration, access rules, and admin work:

- [tailscale/tailscale-skill](https://github.com/tailscale/tailscale-skill): Tailscale's official agent skill, a public alpha. Start here for deeper configuration questions.
- [Tailscale docs MCP server](https://tailscale.com/docs/develop-with-ai): lets your agent search Tailscale's documentation.
- [Aperture by Tailscale](https://tailscale.com/docs/aperture/what-is-aperture): Tailscale's AI agent for the machines in your tailnet.
- [YawLabs/tailscale-mcp](https://github.com/YawLabs/tailscale-mcp): a third-party MCP server with 97 admin API tools.
- [Tailscale documentation](https://tailscale.com/docs)

The commands here were last checked against Tailscale 1.102.4 on macOS.

## License

MIT. See [LICENSE](LICENSE).

## Trademark

Tailscale is a registered trademark of Tailscale Inc. This project uses the name only to say what the skill works with. It doesn't use the Tailscale logo and isn't affiliated with, sponsored by, or endorsed by Tailscale Inc.
