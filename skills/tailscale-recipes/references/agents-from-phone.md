# Check on your agents from your phone

## When you'd want this

You left an agent working on your home Mac and now you're out. You want to see what it's doing, answer its question, or tell it to stop, from your phone.

A few words first:

- **SSH**: a way to type commands on another computer.
- **Remote Login**: the Mac setting that allows SSH.
- **tmux**: a free program that keeps a Terminal session running on the Mac after you disconnect. You can reattach to the same session later from anywhere, including your phone.

## One-time setup on the home Mac

1. **Turn on Remote Login.** The user does it: System Settings, General, Sharing, then switch on **Remote Login**. Click the info button, set **Allow access for** to **Only these users**, and keep the list to your own account. It's ask first and name the risk: "Anyone who can reach this Mac and has a key or password for your account can log in to it remotely."
2. **Install tmux if it isn't there.** Check (run freely):

   ```sh
   command -v tmux
   ```

   If nothing prints, install it. Ask first:

   ```sh
   brew install tmux
   ```

   Undo: `brew uninstall tmux`

## One-time setup on your phone

1. Install Tailscale and sign in with the same account as your Macs.
2. Install an SSH app. Termius and Blink Shell are two that run on iPhone.
3. In the app, create a key and copy its public half. It's one line that starts with `ssh-`. It's safe to send anywhere: AirDrop, Notes, or Taildrop (see [send-a-file.md](send-a-file.md)).
4. Add that line to the home Mac. Ask first. On the home Mac, with the line pasted between the quotes:

   ```sh
   mkdir -p ~/.ssh && echo 'PASTE-THE-LINE-HERE' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys
   ```

   Undo: open `~/.ssh/authorized_keys` on the home Mac and delete the line that matches your phone's key.

## Start your agent inside tmux

On the home Mac itself, in Terminal:

```sh
tmux new -s agents
```

Start your agent in that window as usual. To walk away and leave it running, press Control-b, then d. That's called detaching.

Start the session at the Mac, not over SSH. macOS guards folders like Documents and Desktop, and programs started over SSH are blocked from them by default. Programs started inside a tmux session you opened in Terminal get Terminal's access, and they keep it when you reattach from your phone.

## From your phone

1. In the SSH app, add the home Mac: address `home-mac` (the name in `tailscale status`), your Mac username (the name of your home folder), and the key you made.
2. Connect. The first time, the app asks whether to trust the Mac. Say yes.
3. Reattach:

   ```sh
   tmux attach -t agents
   ```

4. When you're done, press Control-b, then d, and close the app. The agent keeps working.

## What success looks like

After step 3 you see the agent's screen exactly as you left it, and what you type goes to the agent.

To list sessions (run freely, on the home Mac or over SSH):

```sh
tmux ls
```

You'll see a line like `agents: 1 windows (created ...)`. While your phone is attached, it ends with `(attached)`.

## Agents can look too

An agent on your laptop can read what's on the home agent's screen without attaching. Ask first, since it's SSH into your own machine:

```sh
ssh home-mac '/opt/homebrew/bin/tmux capture-pane -p -t agents'
```

It prints the visible text of the session. The full path is there because commands sent this way may not load your usual PATH. On an Intel Mac, Homebrew puts tmux in `/usr/local/bin` instead.

## Undo

- To leave a session running, detach: Control-b, then d.
- To stop a session and whatever is running in it, ask first: `tmux kill-session -t agents`
- To remove your phone's access, delete its line from `~/.ssh/authorized_keys` on the home Mac (ask first).
- To block all SSH, the user turns off Remote Login in System Settings, General, Sharing.

## When it goes wrong

- **The app times out**: Tailscale is off on your phone, or the home Mac is asleep. Open the Tailscale app on the phone and check it's connected.
- **`Connection refused`**: Remote Login is off on the home Mac.
- **`Permission denied (publickey,...)`**: the key line didn't get added, or the username is wrong.
- **`can't find session: agents`** or **`no server running`**: the session isn't running. tmux sessions don't survive a restart, so start it again at the Mac.
- **`Operation not permitted` when the agent reads Documents or Desktop**: the agent was started over SSH. Start it again inside tmux at the Mac.
- **`tmux: command not found` from the phone**: use the full path, `/opt/homebrew/bin/tmux attach -t agents`.
