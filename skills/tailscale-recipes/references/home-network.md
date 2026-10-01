# Reach your home printer or network drive from anywhere

## When you'd want this

You're away and want to print on the printer at home, open files on a network drive, or get to your router's settings page. Those devices can't run Tailscale, but your home Mac can pass your traffic along to them.

A few words first:

- **Tailnet**: your private network. Every device signed in to your Tailscale account is on it.
- **Subnet router**: a device on your tailnet that lets your other devices reach things on its home network that don't run Tailscale. Here, that's the home Mac.
- **Home network range**: the block of addresses your home router hands out, written like `192.168.1.0/24`. Every device at home has an address inside it.
- **Bonjour**: how Macs find printers and drives nearby without you typing an address. It only works on the local network, so it doesn't reach you over Tailscale.

## One-time setup on the home Mac

1. Find the home network range. Run freely, on the home Mac:

   ```sh
   iface=$(route -n get default | awk '/interface:/{print $2}')
   python3 -c 'import ipaddress,sys; print(ipaddress.ip_interface(sys.argv[1]+"/"+sys.argv[2]).network)' "$(ipconfig getifaddr "$iface")" "$(ipconfig getoption "$iface" subnet_mask)"
   ```

   It prints something like `192.168.1.0/24`. Run it while the home Mac isn't using an exit node.

2. Offer that range to your tailnet. Ask first:

   ```sh
   tailscale set --advertise-routes=192.168.1.0/24
   ```

   Use the range from step 1. macOS switches on the forwarding this needs by itself.

   Undo: `tailscale set --advertise-routes=`

3. Approve it. The user does this in the admin console: on the Machines page, find the home Mac (it shows a **Subnets** badge), open its menu, choose **Edit route settings**, turn on the range, and save.

4. Keep the home Mac awake. See [travel-wifi.md](travel-wifi.md), "One-time setup at home".

Check what the home Mac is offering (run freely): `tailscale get advertise-routes`. An empty line means nothing.

## Find the printer's address

Your laptop won't find the printer by itself when you're away, because Bonjour stays at home. You add the printer once, by address.

On the home Mac, run freely:

```sh
ippfind -T 5
```

It looks for printers for 5 seconds and lists them, like `ipp://Office-Printer.local.:631/ipp/print`. Then get that printer's address (run freely):

```sh
ping -c 1 Office-Printer.local
```

The first line shows it in parentheses: `PING Office-Printer.local (192.168.1.50)`.

A printer can get a new address when the router restarts. To keep it fixed, the user reserves the address for the printer in the router's app or settings page. Every router does this differently.

## Add the printer on your laptop

The user's way: System Settings, Printers & Scanners, **Add Printer, Scanner, or Fax**. Click the **IP** tab (the globe), type the address, set **Protocol** to **AirPrint**, and click **Add**.

The agent's way. Ask first:

```sh
lpadmin -p Home_Printer -E -v ipp://192.168.1.50/ipp/print -m everywhere
```

Use the path `ippfind` showed. `/ipp/print` is common. Check it (run freely): `lpstat -p Home_Printer`. Undo (ask first): `lpadmin -x Home_Printer`. If `lpadmin` says `Forbidden`, use the System Settings way.

With the subnet router on, the same printer works whether you're at home or away.

## Network drives and the router page

- **Network drive**: Finder, Go, **Connect to Server**, then `smb://` and the drive's address, like `smb://192.168.1.60`. Bonjour doesn't reach you here either, so type the address.
- **Router settings**: open the router's address in a browser, like `http://192.168.1.1`. On the home Mac, `route -n get default` shows it on the `gateway:` line (run freely).

## What success looks like

Away from home, on your laptop, run freely:

```sh
route -n get 192.168.1.50
```

The `interface:` line shows `utun` and a number, which means the traffic goes through Tailscale. At home it shows your normal connection, like `en0`, because the laptop reaches the printer directly. Both are right. `ping -c 3 192.168.1.50` gets replies, and a test page comes out of the printer at home.

## Undo

- To stop offering the range, ask first: `tailscale set --advertise-routes=`
- To remove the printer, ask first: `lpadmin -x Home_Printer`. Or select it in Printers & Scanners and click the minus button.
- The user can also turn the route off in the admin console, in the same **Edit route settings** screen.

## When it goes wrong

- **Nothing at home answers**: the route isn't approved yet, or the home Mac is asleep or offline. Run `tailscale ping home-mac`.
- **The printer doesn't appear in the printer list**: expected. Add it by address.
- **The printer worked before and now doesn't**: it got a new address. Find it again with `ippfind` and `ping`, and reserve the address in the router.
- **Odd behavior on someone else's network**: if the network you're on uses the same range as your home (`192.168.1.x` and `192.168.0.x` are very common), the addresses clash. Moving your home router to a less common range avoids it. That's a router setting, so the user does it.
- **A Linux machine can't reach home devices**: Macs, iPhones, and Windows pick up the route by themselves. Linux needs `tailscale set --accept-routes` (ask first).
