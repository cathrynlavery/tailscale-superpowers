# Sketchy hotel or plane wifi: go out through your home Mac

## When you'd want this

You're on hotel, airport, or plane wifi you don't trust, or it's slow or blocking things. You can send all your internet traffic through your Mac at home instead. The hotel network sees only encrypted traffic, and websites see your home internet connection.

A few words first:

- **Tailnet**: your private network. Every device signed in to your Tailscale account is on it.
- **Exit node**: a device on your tailnet that your internet traffic goes out through. Here, that's your home Mac.

## One-time setup at home

The user does these steps. The agent never touches the admin console, though step 2 can go through `tailscale-pp-cli` when it's set up.

1. On the home Mac, open the Tailscale menu and choose **Exit Node**, then **Run Exit Node**.
2. Approve it in the Tailscale admin console: on the Machines page, open the home Mac's menu, choose **Edit route settings**, and turn on **Use as exit node**.

   With `tailscale-pp-cli` set up (see [SKILL.md](../SKILL.md)), the agent can approve it instead. `tailscale-pp-cli routes approve home-mac --exit-node` shows the plan (run freely). Then ask first and name the risk: "Devices on your tailnet will be able to send their internet traffic through your home Mac." Run it again with `--yes`. Undo (ask first and name the risk: "Any device using the home Mac as its exit node loses its internet until it switches off."): `tailscale-pp-cli routes unapprove home-mac --exit-node --yes`
3. Keep the home Mac awake. Tailscale's docs say a Mac exit node has to be kept from sleeping. In System Settings, open Energy (Battery on a laptop) and turn on the option that prevents automatic sleeping when the display is off.

An agent on the home Mac can do step 1 instead (ask first): `tailscale set --advertise-exit-node`. Undo: `tailscale set --advertise-exit-node=false`. Step 2 still belongs to the user.

## On the road, from your laptop

1. See which exit nodes you have. Run freely:

   ```sh
   tailscale exit-node list
   ```

   You get a table with IP, HOSTNAME, COUNTRY, CITY, and STATUS columns. Your home Mac should be in it. Country and city show `-` for your own devices.

2. Check the home Mac is awake. Run freely:

   ```sh
   tailscale ping home-mac
   ```

   A `pong from home-mac` line means it's reachable. If you get `no reply`, stop here: the home Mac is asleep or offline, and turning it on as your exit node would cut your internet.

3. If the wifi has a login page, log in now, before the next step.

   Also check whether local network access is on. Run freely: `tailscale get exit-node-allow-lan-access`. It can already be `true`, which means traffic to devices on this wifi skips the exit node. On wifi you don't trust, turn it off. Ask first: `tailscale set --exit-node-allow-lan-access=false`. Undo: the same command with `=true`.

4. Turn it on. Ask first, and show the undo (`tailscale set --exit-node=`) at the same time:

   ```sh
   tailscale set --exit-node=home-mac
   ```

   If you reach this laptop over SSH or Tailscale from somewhere else, this can drop your connection. Say so before running it.

## What success looks like

Run freely:

```sh
tailscale exit-node list
```

The home Mac's STATUS now says `selected`. In `tailscale status`, its line starts with `active; exit node;`. A "what is my IP" website should show your home city.

## On your phone

In the Tailscale app, tap **Exit Node** at the top of the screen and pick your home Mac. To stop, choose **None**.

## Undo

Ask first:

```sh
tailscale set --exit-node=
```

Check it worked (run freely): `tailscale get exit-node` prints an empty line when no exit node is set.

## When it goes wrong

- **`no exit nodes found`**: the home setup isn't done, or the exit node isn't approved in the admin console yet. The user finishes the one-time setup. With `tailscale-pp-cli`, `tailscale-pp-cli routes overview --exit-nodes` (run freely) shows whether the home Mac is advertising and approved.
- **The internet stops working right after you turn it on**: the home Mac fell asleep, lost power, or the home internet is down. Run the undo, then `tailscale ping home-mac` to see if it's back.
- **The wifi login page won't load**: turn the exit node off, log in to the wifi, then turn it back on.
- **Everything is slow**: your traffic now goes home and back, so your home upload speed sets the limit. `tailscale ping home-mac` showing `via DERP(...)` on every reply means you're on a relay, which is slower still. See [is-it-online.md](is-it-online.md).
- **You can't reach a printer or TV on the local network**: that's the exit node sending everything home, with local network access off. Ask first, then run `tailscale set --exit-node-allow-lan-access=true` to let this device reach the local network directly. On wifi you don't trust, leave it off. Undo: `tailscale set --exit-node-allow-lan-access=false`. Check the current value (run freely) with `tailscale get exit-node-allow-lan-access`.
