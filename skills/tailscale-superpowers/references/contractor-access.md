# Give a contractor access to one Mac

## When you'd want this

You've hired someone to build or fix something on one of your machines, like the Mac mini that runs your agents. They need to get in without seeing your other devices and without your password.

A few words first:

- **Tailnet**: your private network. Every device signed in to your Tailscale account is on it.
- **Sharing a machine**: Tailscale can share one device with someone outside your tailnet. They see that device and nothing else of yours.
- **Quarantine**: a shared device can answer the contractor's connections but can't start connections into their network. Tailscale does this by default.
- **Standard account**: a Mac user account without admin rights.

## Before you start

Everything in this recipe is "ask first and name the risk", because it gives another person a way into your Mac.

- **Pick the Mac.** If you have a choice, share a machine set aside for the job, not the Mac with your email, files, and saved passwords.
- **Decide what they need**: a terminal (SSH), the screen (Screen Sharing), or both.
- **Decide when access ends**, and write the date down.

## Step 1: their own account on that Mac

The user does this on the Mac: System Settings, **Users & Groups**, **Add User**. Make it a **Standard** account with its own password, named something like `contractor`.

Their work stays separate from yours, they never need your password, and deleting the account ends their access on that Mac. If the job needs admin rights, treat that as a bigger decision, because an admin account can change anything on the Mac.

## Step 2: let that account in

The user does this on the same Mac, in System Settings, General, Sharing:

- **For SSH**: switch on **Remote Login**, click the info button, choose **Only these users**, and add the contractor account. Risk: "This lets that account log in to this Mac from anywhere it can reach it."
- **For the screen**: same steps under **Screen Sharing**. Risk: "This lets that account see and control this Mac's screen."

## Step 3: share the Mac on Tailscale

The user does this in the admin console. The agent never does.

1. On the Machines page, open the Mac's menu and choose **Share**.
2. Share by email. The contractor gets a single-use invite. A link works too, but Tailscale says to treat an invite link like a password.
3. The contractor accepts with their own Tailscale account. Tailscale requires the account accepting to be an owner or admin of its tailnet, and a personal account is.

The contractor reaches the Mac only by its full name. To find it, run freely on the shared Mac:

```sh
tailscale dns status
```

Look for the line `Other devices in your tailnet can reach this device at` followed by a name like `agent-mini.your-tailnet.ts.net`.

Send the contractor that name and their account's username. Send the password separately, through a password manager's sharing feature or a phone call, not in the same email as the invite.

## Optional: limit what they can reach

With Tailscale's default rules, the contractor can reach every service on that Mac, including ones you didn't mean to share. Tailscale's access rules can narrow that using `autogroup:shared`. That means editing the policy file, so the user does it, starting from Tailscale's sharing docs or its official skill. With `tailscale-pp-cli` set up, you can check which rules let them reach the Mac (run freely): `tailscale-pp-cli access check --to agent-mini:22 --from <their-login>`.

## While they work

Run freely, on the shared Mac:

```sh
who
```

It lists who's logged in right now. A remote session shows its address in parentheses at the end, like `contractor  ttys003  Oct  1 10:00  (100.64.0.7)`. To see which device and Tailscale account that address belongs to (run freely):

```sh
tailscale whois 100.64.0.7
```

## What success looks like

The contractor connects with `ssh contractor@agent-mini.your-tailnet.ts.net` or opens `vnc://agent-mini.your-tailnet.ts.net`, and `who` on the Mac shows their account.

## Undo: when the job ends

Do all of these on the same day:

1. **Revoke the share.** The user does this in the admin console: on the Machines page, open **Share** for that Mac, then the invite's menu, then **Revoke invite**.

   With `tailscale-pp-cli` set up, list every invite on that Mac and who accepted it (run freely): `tailscale-pp-cli shares audit --device agent-mini`. Invites nobody accepted can go through the CLI: `tailscale-pp-cli shares revoke --device agent-mini --pending` shows what it would delete (run freely), and adding `--yes` deletes them (ask first and name the risk: "Those invite links stop working."). For the invite the contractor accepted, use the admin console as above, then run `shares audit` again to confirm it's gone.
2. **Take their account off** the Remote Login and Screen Sharing lists.
3. **Delete their Mac account** in System Settings, **Users & Groups**. macOS offers to keep their home folder as a disk image, which helps if you want to look over their work later.
4. **Check** with `who` that they're gone (run freely).
5. If their account had admin rights, change any passwords they could have seen.

## When it goes wrong

- **They can't see the Mac**: they haven't accepted the invite yet, or they accepted with an account that isn't an owner or admin of its tailnet.
- **`Could not resolve hostname`**: they used the short name. Shared devices need the full `.ts.net` name.
- **`Connection refused`**: Remote Login, or Screen Sharing, is off on the Mac.
- **`Permission denied`**: their account isn't on the **Only these users** list, or the username or password is wrong.
- **They need a second machine**: sharing covers one device. Share that one too, or rethink the setup.
