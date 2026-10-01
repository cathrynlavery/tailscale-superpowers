# Let your agents on different machines ask each other for help

## When you'd want this

You have an agent on your laptop, another on a Mac mini at home, maybe one in the cloud, and you're tired of copying messages between them. You want one agent to hand another a job and get the answer back.

This skill doesn't do that itself. Agent Tincan does: https://github.com/mvanhorn/agent-tincan

Its one-line description: "Let your AI agents ask each other for help, over Tailscale. Wherever they run."

## How it works, briefly

It runs a small relay on your tailnet (your private network of devices signed in to Tailscale). Every agent connects out to the relay, so no machine needs an open port. The relay queues requests, wakes the agent that should answer, and carries the reply back. There are no API keys between agents, because Tailscale tells the relay which machine each request came from.

You can see that idea yourself. Run freely: `tailscale whois 100.64.0.2` shows which device and account own an address.

## Before you set it up

- Its README says agents you join "trust each other like teammates: a request from a teammate is handled as if you asked." Only join agents you'd trust with each other's access.
- Its README names the main risk: "an agent that reads untrusted content being tricked into asking a powerful teammate to do something harmful." It has an owner approval gate you can turn on for chosen agents.
- Its setup sends you a Tailscale link to approve. The user clicks it, not the agent. The safety tiers in [SKILL.md](../SKILL.md) still apply: this skill never creates auth keys or edits the policy file for it.
- Installing it on each machine is ask first. Follow its own guide: https://agenttincan.com/agents.txt

## Undo

`tincan remove <name>` cuts one agent off right away, per its README. Ask first before running it. For anything beyond that, follow Agent Tincan's own docs.
