# Put text on another Mac's clipboard

## When you'd want this

You've got a link, an address, or a code on your laptop and want it ready to paste on another Mac: your Mac mini, or a family member's Mac with their OK. Tailscale has no clipboard sync, but it makes the other Mac reachable, and every Mac has a built-in clipboard command you can run over SSH.

A few words first:

- **SSH**: a way to type commands on another computer.
- **Remote Login**: the Mac setting that allows SSH.
- **pbcopy**: the Mac's built-in "put this on the clipboard" command. Whatever you send it lands on that Mac's clipboard.
- **pbpaste**: the opposite. It prints what's on the clipboard.

## Before you start

- The other Mac has Remote Login on and your SSH key. See steps 1 and 2 of [one-word-shortcuts.md](one-word-shortcuts.md).
- SSH in as the person who uses that Mac. The clipboard you set belongs to that account.
- Someone else's Mac needs their yes first, and the rules in [help-family-mac.md](help-family-mac.md) apply.

## Send text

On your own Mac this is ask first. On someone else's Mac it's ask first and name the risk: "This replaces whatever is on their clipboard right now."

Send a piece of text:

```sh
echo "text here" | ssh home-mac 'pbcopy'
```

Send whatever is on your own clipboard:

```sh
pbpaste | ssh home-mac 'pbcopy'
```

Send the contents of a text file:

```sh
ssh home-mac 'pbcopy' < notes.txt
```

Or type it in: run `ssh home-mac 'pbcopy'`, type the text, then press Control-D.

## Bring their clipboard to yours

Your own Macs only. Never read someone else's clipboard; it's private. Ask first, since this replaces what's on your clipboard:

```sh
ssh home-mac 'pbpaste' | pbcopy
```

## One word for it

If you set up a short SSH name in [one-word-shortcuts.md](one-word-shortcuts.md), add an alias so copying something and typing one word sends it over. Ask first, since it edits `~/.zshrc`:

```sh
echo "alias tomini=\"pbpaste | ssh mini 'pbcopy'\"" >> ~/.zshrc
```

Open a new Terminal window, copy something, and type `tomini`. Undo: delete that line from `~/.zshrc`.

## What success looks like

On the other Mac, Command-V pastes your text. To check from your laptop, ask first (it's SSH into your own machine):

```sh
ssh home-mac 'pbpaste'
```

It prints what's on that Mac's clipboard.

## Undo

A clipboard has no undo: the new text replaces what was there. If the old contents matter on your own Mac, save them first (ask first):

```sh
ssh home-mac 'pbpaste' > ~/clipboard-before.txt
```

Put them back with `ssh home-mac 'pbcopy' < ~/clipboard-before.txt`. This only works for text.

## When it goes wrong

- **`Connection refused`**: Remote Login is off on the other Mac.
- **It asks for a password, or says `Permission denied`**: your SSH key isn't on that Mac yet. See [one-word-shortcuts.md](one-word-shortcuts.md).
- **`Host key verification failed`** when an agent runs it: nobody has accepted that Mac's identity under this name yet. The user runs the command once in their own Terminal and types `yes`.
- **Accents or emoji come out garbled**: the other Mac isn't getting a UTF-8 language setting over SSH. Use `LANG=en_US.UTF-8 pbcopy` in place of `pbcopy`.
- **You want to send an image or a file**: `pbcopy` is for text. Use Taildrop instead. See [send-a-file.md](send-a-file.md).
