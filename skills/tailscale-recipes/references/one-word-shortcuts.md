# One word to get into another Mac

## When you'd want this

You hop between Macs all day. You'd rather type `mini` than `ssh your-username@agent-mini`, and maybe land straight in the session where your agents are running. A short name helps agents too: they can run `ssh mini 'uptime'` without knowing your username.

A few words first:

- **SSH**: a way to type commands on another computer.
- **SSH key**: a pair of files that proves who you are, so you don't type a password every time.
- **Alias**: a nickname in your Terminal that stands for a longer command.

There are three pieces: a key, a short name in your SSH settings, and an alias.

## 1. Check the other Mac accepts SSH

Run freely:

```sh
nc -z -G 3 agent-mini 22
```

`Connection to agent-mini port 22 [tcp/ssh] succeeded!` means yes. No output means Remote Login is off on that Mac. See [new-mac-setup.md](new-mac-setup.md), Part 1.

## 2. A key, so there's no password

If you already did Part 2 of [new-mac-setup.md](new-mac-setup.md) for this Mac, skip ahead.

Check for a key (run freely):

```sh
ls ~/.ssh/id_ed25519.pub
```

If it says `No such file or directory`, make one. Ask first. The user presses Enter at the prompts, or sets a passphrase:

```sh
ssh-keygen -t ed25519
```

Then copy it to the other Mac. Ask first. It asks for that Mac's password once, so the user runs it in their own Terminal:

```sh
ssh-copy-id your-username@agent-mini
```

Undo: on the other Mac, delete the matching line from `~/.ssh/authorized_keys`. Delete a key you just made with `rm ~/.ssh/id_ed25519 ~/.ssh/id_ed25519.pub` only if nothing else uses it, such as GitHub.

## 3. A short name in your SSH settings

See which names you already have (run freely):

```sh
grep -n '^Host ' ~/.ssh/config
```

Add the new one. Ask first, and show the user these three lines before adding them:

```sh
mkdir -p ~/.ssh && printf '\nHost mini\n  HostName agent-mini\n  User your-username\n' >> ~/.ssh/config
```

Check it, without connecting (run freely):

```sh
ssh -G mini | grep -E '^(hostname|user) '
```

It prints `user your-username` and `hostname agent-mini`. Now `ssh mini` works, for you and for agents.

Undo: delete those three lines from `~/.ssh/config`.

## 4. The one word

Check the word isn't already a command (run freely):

```sh
type mini
```

`mini not found` means it's free. If it prints anything else, pick another word.

Add the alias. Ask first:

```sh
echo "alias mini='ssh mini'" >> ~/.zshrc
```

Open a new Terminal window and type `mini`.

Undo: delete that line from `~/.zshrc`.

## Variations

- **Land in your agents' session.** If you use tmux (see [agents-from-phone.md](agents-from-phone.md)), use this alias instead:

  ```sh
  alias mini='ssh -t mini "/opt/homebrew/bin/tmux new -A -s agents"'
  ```

  It joins the `agents` session, or starts one if there isn't one. `-t` gives tmux a full screen. The full path is there because commands sent over SSH may not load your usual PATH. A session this alias starts is started over SSH, so macOS blocks it from Documents and Desktop by default. A session you start at the Mac doesn't have that problem.

- **One word for the screen**: `alias mini-screen='open vnc://agent-mini'`. See [see-the-screen.md](see-the-screen.md).
- **More Macs**: repeat steps 3 and 4 with a different name for each.

Agents usually don't load your aliases, but they do read `~/.ssh/config`. That's why step 3 matters even if you only care about the one word.

## What success looks like

In a new Terminal window, `mini` puts you at the other Mac's prompt with no password. `exit` brings you back.

## Undo

- Delete the alias line from `~/.zshrc`.
- Delete the `Host mini` block from `~/.ssh/config`.
- On the other Mac, delete your key's line from `~/.ssh/authorized_keys`.

## When it goes wrong

- **`zsh: command not found: mini`**: that Terminal window was open before you added the alias. Open a new one.
- **It still asks for a password**: the key didn't get copied. Run `ssh-copy-id` again.
- **`Could not resolve hostname agent-mini`**: use the name exactly as `tailscale status` shows it.
- **`Bad configuration option`**: a typo in `~/.ssh/config`. The error names the line.
- **`open terminal failed: not a terminal`**: the alias is missing `-t`.
- **`/opt/homebrew/bin/tmux: No such file or directory`**: tmux isn't installed on that Mac, or it's an Intel Mac, where the path is `/usr/local/bin/tmux`.
