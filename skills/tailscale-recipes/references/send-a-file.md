# Send a file to your phone or another Mac

## When you'd want this

You want a PDF from your laptop on your phone, or a log file from one Mac on another, and the devices aren't on the same wifi. Taildrop is Tailscale's way of sending files between your own devices over your tailnet (the private network of devices signed in to your Tailscale account).

## Before you start

The user handles these:

- Taildrop is an alpha feature, so it's off until the tailnet owner turns on **Send Files** in the admin console's General settings. The agent doesn't do this.
- It only sends between devices signed in as you. You can't send to someone else's device, even on the same tailnet.

## Steps

1. See which devices can receive. Run freely:

   ```sh
   tailscale file cp --targets
   ```

   Each line is an address and a device name. Offline devices say so, with when they were last seen. Use the name from the second column.

2. Send it. Ask first:

   ```sh
   tailscale file cp ~/Downloads/report.pdf phone:
   ```

   The colon after the device name is required. To send several files, list them all before the device name. Folders don't work, so zip the folder first (ask first, since it creates a new file): `zip -r ~/Downloads/project.zip ~/Projects/project`.

**On the Mac App Store version**, the CLI runs inside Apple's sandbox, which can read your Downloads folder. If you see `the GUI version of Tailscale on macOS runs in a macOS sandbox that can't read files`, copy the file into Downloads and send it from there.

From Finder you can also right-click a file and use **Share**, then Tailscale. The first time, turn Tailscale on in System Settings, under General, Login Items & Extensions, Sharing.

## What success looks like

The command finishes without an error. In a Terminal you'll see a progress line. Add `--verbose` and it prints `sent "report.pdf"` at the end.

Where the file shows up:

- **iPhone or iPad**: a notification. Opening it shows the file in the Files app.
- **Android**: the Downloads section of the Files app.
- **Mac**: your Downloads folder.
- **Windows**: your Downloads folder.
- **Linux**: it waits in an inbox until you collect it. See below.

## Receiving on Linux or a headless machine

Run freely, into a folder the user named:

```sh
tailscale file get ~/Downloads
```

It moves waiting files into that folder and exits. With nothing waiting, it does nothing. `--verbose` prints `moved 0/0 files` so you can tell. Useful options:

- `--wait` waits for a file to arrive if none are there yet.
- `--conflict=rename` keeps both copies when a file with the same name already exists. The default, `skip`, leaves the new one in the inbox and prints an error.

On Linux, files may belong to root. If you get a permission error, the command needs `sudo`, so ask first.

Never run `tailscale file get /dev/null`. That deletes every waiting file without saving any of them.

## Undo

You can't unsend a file. Delete it on the receiving device. That's why sending is ask first.

## When it goes wrong

- **`final argument to 'tailscale file cp' must end in colon`**: add `:` after the device name.
- **`cannot send files: peer is owned by a different user`**: it's someone else's device. Taildrop only works between your own.
- **`cannot send files: missing required Taildrop capability`**: Send Files isn't turned on for your tailnet. The user turns it on in the admin console.
- **`warning: phone is reportedly offline; trying anyway`**, or the same warning ending in `is not replying; trying anyway`: wake the phone, open the Tailscale app, and check it's connected.
- **`directories not supported`**: zip the folder and send the zip.
- **`unknown target; not in your Tailnet`**: the name is wrong. Copy it from `tailscale file cp --targets`.
