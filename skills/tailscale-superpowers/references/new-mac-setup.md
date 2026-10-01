# New Mac setup: install Tailscale, then let an agent finish

## When you'd want this

You've got a new Mac, maybe a Mac mini that will run agents all day. A few steps need your hands on it. After that, an agent on your laptop can connect and do the rest while you watch.

A few words first:

- **Tailnet**: your private network. Every device signed in to your Tailscale account is on it.
- **SSH**: a way to type commands on another computer from your own.
- **Remote Login**: the Mac setting that allows SSH connections.

## Part 1: at the new Mac

The user does these.

1. **Name it.** In System Settings, General, About, give the Mac a clear name like `agent-mini`. Tailscale names the device after the computer's name when it first signs in.
2. **Install Tailscale.** Any of these works:
   - The Mac App Store.
   - The Standalone app from tailscale.com, or `brew install --cask tailscale-app`, which installs the same Standalone app. It can put the `tailscale` command on your PATH from its settings, which makes agent work simpler. See "Find the CLI" in [SKILL.md](../SKILL.md).
3. **Sign in** with the same account as your other devices.
4. **Turn on Remote Login.** System Settings, General, Sharing, then switch on **Remote Login**. Click the info button next to it and set **Allow access for** to **Only these users**, with just your account.
5. **If it will run agents all day, keep it awake.** In System Settings, Energy, turn on the option that prevents automatic sleeping when the display is off. Desktop Macs also have an option to start up automatically after a power failure.
6. **Make sure Tailscale opens at login**, so the Mac rejoins your tailnet after a restart. The setting is in the Tailscale app's settings.

## Part 2: connect from your laptop

1. Find the new Mac. Run freely:

   ```sh
   tailscale status
   ```

   It should appear as `agent-mini`, or whatever you named it.

2. Check you can reach it. Run freely:

   ```sh
   tailscale ping agent-mini
   ```

3. Copy your SSH key to it, so nobody has to type a password each time. Ask first. It asks for the new Mac's password once, so the user runs it in their own Terminal:

   ```sh
   ssh-copy-id your-username@agent-mini
   ```

   Your username is the name of your home folder on the new Mac. If this says you have no key, make one first (ask first): `ssh-keygen -t ed25519`. Undo: on the new Mac, delete the matching line from `~/.ssh/authorized_keys`.

4. Test it. Ask first, since it's the first command on the new machine:

   ```sh
   ssh your-username@agent-mini 'sw_vers'
   ```

   It prints the macOS version. The agent can now run commands on the new Mac.

## Part 3: the checklist the agent runs

It's your own machine, so looking is run freely once the SSH connection is approved. Changes are ask first, with the undo shown.

| Job | Command on the new Mac | Tier | Undo |
| --- | --- | --- | --- |
| macOS version | `sw_vers` | Run freely | None needed |
| Updates waiting | `softwareupdate --list` | Run freely | None needed |
| Free disk space | `df -h /` | Run freely | None needed |
| Sleep is off | `pmset -g` (look for `sleep 0`) | Run freely | None needed |
| Tailscale works | `tailscale version`, then `tailscale status` | Run freely | None needed |
| Install Homebrew | The command from brew.sh. It asks for a password, so the user runs it | Ask first | Homebrew's uninstall script |
| Install your tools | `brew install git gh` and so on | Ask first | `brew uninstall <name>` |
| Set your git name | `git config --global user.name "Your Name"` | Ask first | `git config --global --unset user.name` |
| Install your agent | Follow that agent's install guide | Ask first | Its uninstall steps |

Use the CLI path you found in step one of [SKILL.md](../SKILL.md). On a new Mac with the App Store app, that's the full path inside the app.

## Key expiry

A device's Tailscale sign-in expires after a while (180 days by default), and it drops off your tailnet until you sign in again. You can turn off key expiry for this Mac in the admin console. That's the user's call. The agent never does it.

## Undo

- Turn off Remote Login in System Settings, General, Sharing.
- Remove your key from `~/.ssh/authorized_keys` on the new Mac.
- To take the Mac off your tailnet, the user signs out in the Tailscale app. It's ask first and name the risk if an agent runs `tailscale logout`, because it cuts off any connection coming in over Tailscale, including the agent's own.

## When it goes wrong

- **The new Mac isn't in `tailscale status`**: it isn't signed in, it's signed in to a different account, or it's asleep.
- **`Connection refused`**: Remote Login is off.
- **`Permission denied`**: wrong username. Use the short name (the home folder name), not your full name.
- **`Could not resolve hostname`**: use the exact name from `tailscale status`, or its 100.x address.
- **A command hangs waiting for a password**: agents can't type passwords. The user runs that step in their own Terminal.
- **`WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!`**: expected if you erased and reinstalled a Mac with the same name. If you didn't, stop and find out why. Once you're sure, clear the old entry (ask first and name the risk, because it removes a safety check): `ssh-keygen -R agent-mini`.
