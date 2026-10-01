# Help fix a family member's Mac

## When you'd want this

A family member's Mac is full, slow, or stuck on an update, and they live in another city. With their permission, your agent can connect to their Mac from yours and help, with every step approved.

A few words first:

- **SSH**: a way to type commands on another computer from your own.
- **Remote Login**: the Mac setting that allows SSH connections.
- **Tailnet**: a private network of devices signed in to a Tailscale account.

## Rules before anything else

Everything on their Mac is in the "ask first and name the risk" tier, including commands that only look.

1. They say yes, out loud or in writing, for this session. A yes today doesn't cover next month.
2. They can watch. Share your screen on a call, or read each command to them.
3. For every command on their Mac: show it, say in one sentence what it does, and wait for a yes. Anything that changes their Mac needs their yes, not only yours.
4. Look before you change anything. Make changes only after you both agree on the problem.
5. Keep a list of every command run on their Mac and give it to them at the end.
6. If a fix needs their admin password (`sudo`), don't ask for the password. Read them the command and have them run it on their own Mac.

## Part 1: on their Mac

They do these, with you guiding them on the phone.

1. Install Tailscale and sign in with their own account.
2. Share their Mac with you. In their Tailscale admin console, on the Machines page, they open their Mac's menu, choose **Share**, then **Share by email**, and enter your email. You accept the invite. Accepting is safe for you: Tailscale quarantines shared machines, so their Mac can receive your connection but can't start one into your network.
3. Turn on Remote Login: System Settings, General, Sharing, then switch on **Remote Login**. Click the info button next to it, set **Allow access for** to **Only these users**, and make sure only their account is listed. Leave **Allow full disk access for remote users** off.
4. Tell you their Mac username. It's the name of their home folder in Finder, the one with the house icon.

## Part 2: a key just for this

A key lets you connect without them sharing their password. You'll delete it afterward.

1. Make the key on your Mac. Ask first. You run this in your own Terminal and press Enter at both passphrase prompts:

   ```sh
   ssh-keygen -t ed25519 -C family-helper -f ~/.ssh/family_helper
   ```

   Undo: `rm ~/.ssh/family_helper ~/.ssh/family_helper.pub`

2. Show the public half. Run freely. It's safe to send to anyone:

   ```sh
   cat ~/.ssh/family_helper.pub
   ```

   It's one line that starts with `ssh-ed25519` and ends with `family-helper`.

3. Text or email them that line. They open Terminal on their Mac and run this, with your line pasted between the quotes:

   ```sh
   mkdir -p ~/.ssh && echo 'PASTE-THE-LINE-HERE' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys
   ```

## Part 3: connect

1. Find their Mac. Run freely:

   ```sh
   tailscale status
   ```

   A shared Mac shows up under its full name, something like `family-mac.their-tailnet.ts.net`. Shared devices need that full name. The short name won't work.

2. Check you can reach it. Run freely:

   ```sh
   tailscale ping family-mac.their-tailnet.ts.net
   ```

3. Connect. Ask first and name the risk: "This opens a session on their Mac, so anything run there changes their computer, not yours."

   ```sh
   ssh -i ~/.ssh/family_helper their-username@family-mac.their-tailnet.ts.net
   ```

   The first time, SSH asks `Are you sure you want to continue connecting`. Type `yes`. That saves their Mac's identity so SSH can warn you if it ever changes. An agent can't answer that prompt, so make the first connection yourself in Terminal. After that, an agent can run one command at a time by adding it in quotes at the end, like `ssh -i ~/.ssh/family_helper their-username@family-mac.their-tailnet.ts.net 'df -h /'`.

4. Look first. Still ask first and name the risk, because it's their Mac:

   - `sw_vers`: which macOS version.
   - `df -h /`: how full the disk is.
   - `uptime`: how long since the last restart.
   - `top -l 1 -o cpu -n 10`: the 10 programs using the most CPU right now.
   - `softwareupdate --list`: updates waiting to install.

5. For each fix, say what it changes and how to undo it, then wait for their yes.

## Tailscale SSH instead?

Tailscale has its own SSH (`tailscale ssh`) that handles login without keys. It needs the Mac you connect to to run the open-source version of Tailscale, not the App Store or Standalone app, and the tailnet owner has to add SSH rules to the policy file. This skill never edits the policy file. For most family Macs, regular `ssh` as above is the way.

## Undo: clean up when you're done

1. Remove your key from their Mac. Ask first and name the risk: "This edits a file on their Mac, and only removes the line you added."

   ```sh
   ssh -i ~/.ssh/family_helper their-username@family-mac.their-tailnet.ts.net "sed -i '' '/family-helper/d' ~/.ssh/authorized_keys"
   ```

2. They turn off Remote Login in System Settings, General, Sharing. This blocks all SSH, so it works even if step 1 was skipped.
3. They stop sharing their Mac: on their admin console's Machines page, they revoke the share.
4. Delete the helper key on your Mac. Ask first: `rm ~/.ssh/family_helper ~/.ssh/family_helper.pub`
5. Give them the list of every command you ran.

## When it goes wrong

- **Their Mac isn't in `tailscale status`**: you haven't accepted the share yet, or their Mac is asleep, or Tailscale isn't running on it.
- **`Could not resolve hostname`**: use the full `.ts.net` name. Shared devices don't answer to short names.
- **`Connection refused`**: Remote Login is off on their Mac.
- **`Permission denied (publickey,...)`**: the username is wrong, or the key line didn't get added. Have them run `tail -1 ~/.ssh/authorized_keys` and check the last line ends with `family-helper`.
- **`Operation not permitted` when reading their Documents or Desktop**: macOS privacy protection blocks remote sessions from those folders by default. Leave that protection on and work around it, or have them open the folder themselves.
