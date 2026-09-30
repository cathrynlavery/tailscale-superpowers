# Is my other Mac online? Why is it slow?

## When you'd want this

Your agent on the laptop can't reach the home Mac, a file won't send, or an SSH session feels laggy. Three commands tell you whether the other machine is on, how it's connected, and whether your own network is the problem.

Every command here only looks. The agent can run all of them without asking.

A few words first:

- **Tailnet**: your private network. Every device signed in to your Tailscale account is on it.
- **Direct connection**: your two devices talk straight to each other. This is the fast path.
- **Relay**: when a direct path isn't possible, traffic bounces through one of Tailscale's relay servers. It still works, just slower. Tailscale calls these relays DERP servers, and the output uses that name.

## 1. Is it online?

Run freely:

```sh
tailscale status
```

Each line is one device: its Tailscale address, its name, the account that owns it, its operating system, and a status. The status column is the part to read:

| Status | What it means |
| --- | --- |
| `-` | Online. Nothing has been sent to it yet. |
| `active; direct 192.0.2.10:41641` | Connected directly. Good. |
| `active; relay "nyc"` | Connected through the relay in New York. Works, but slower. |
| `idle` | Online and has talked to you before, but quiet right now. |
| `offline, last seen 15d ago` | Asleep, switched off, or Tailscale isn't running on it. |
| `...offers exit node` | You could route your internet traffic through it. See [travel-wifi.md](travel-wifi.md). |
| `active; exit node; ...` | Your internet traffic is going through it right now. |
| `..., tx 1955376 rx 3061500` | Bytes sent and received since Tailscale started. |

Add `--active` to show only devices you're talking to right now. Add `--header` for column names.

## 2. How is it connected?

Run freely:

```sh
tailscale ping home-mac
```

This sends up to 10 pings and stops early once it finds a direct path. Typical output:

```text
pong from home-mac (100.64.0.2) via DERP(nyc) in 38ms
pong from home-mac (100.64.0.2) via 192.0.2.10:41641 in 4ms
```

How to read it:

- `via DERP(nyc)` means that reply came through a relay. The first reply or two often does while Tailscale looks for a direct path. That's normal.
- `via 192.0.2.10:41641` (an address and port) means direct.
- `ping "100.64.0.2" timed out`, repeated, then `no reply`: the device can't be reached. It's asleep, offline, or Tailscale is off on it.
- `direct connection not established`: replies came back, but only through the relay. It works but will feel slower. A strict firewall on one side usually causes this (hotel, office, some home routers).
- `no such host`: the name is wrong. Copy the name exactly as `tailscale status` shows it.

`tailscale ping` tests Tailscale itself, not the other computer's firewall. If it works but your app still can't connect, the app or the other Mac's firewall is the problem.

## 3. Is my network the problem?

Run freely:

```sh
tailscale netcheck
```

The report is a short list. What each line means:

- **UDP**: `true` is good. `false` means this network blocks the traffic Tailscale prefers, so expect relays. Hotel, airplane, and office wifi do this a lot.
- **IPv4**: `yes`, followed by the public address the internet sees for you.
- **IPv6**: either answer is fine.
- **MappingVariesByDestIP**: `true` means your router makes direct connections harder, so expect more relays.
- **PortMapping**: blank is common. If it lists UPnP, NAT-PMP, or PCP, your router is helping Tailscale open direct paths.
- **CaptivePortal**: only appears when the wifi wants you to log in on a web page first.
- **Nearest DERP** and **DERP latency**: the closest relay and how far away each relay is, in milliseconds.

## Putting it together

When something feels slow:

1. `tailscale status`. If the other device is offline, wake it up or check that Tailscale is running on it.
2. `tailscale ping <name>`. Direct or relay?
3. If it's relayed, run `tailscale netcheck` on both ends. `UDP: false` or `MappingVariesByDestIP: true` means the network is forcing the relay. Try a phone hotspot to compare.
4. If it's direct and still slow, the internet connection at one end is the limit. Tailscale can't make a slow home upload faster.

## Two more lookups

This device's own Tailscale address (run freely):

```sh
tailscale ip -4
```

Which device and account own an address (run freely). It needs an address, not a name:

```sh
tailscale whois 100.64.0.2
```

## Undo

Nothing to undo. These commands only look.

## When it goes wrong

- **`command not found`**: the CLI isn't on your PATH. Go back to the "Find the CLI" step in [SKILL.md](../SKILL.md).
- **`no reply` for a device that should be on**: check that it's awake and that Tailscale is running and signed in on it. Macs that sleep drop off the tailnet.
- **`400 Bad Request: invalid 'addr' parameter` from `whois`**: you gave it a name. Give it the 100.x address from `tailscale status`.
- **Everything shows offline, including devices you know are on**: Tailscale on this machine is disconnected. Open the Tailscale app and check that it's connected.
