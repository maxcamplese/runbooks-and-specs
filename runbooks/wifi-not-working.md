# Runbook: Wi-Fi Not Working

**Who this is for:** anyone. No technical knowledge needed.
**Time:** about 5 minutes.
**You will need:** your laptop and, if possible, a phone on the same Wi-Fi.

---

## Step 1: Is It Just You?

Check a phone or a coworker's laptop on the same Wi-Fi.

- **Their internet works but yours does not:** the problem is your computer. Go to Step 2.
- **Nobody's internet works:** the problem is the network. Skip to [When to Contact IT](#when-to-contact-it) and say "Wi-Fi is down for everyone in [room or area]."

## Step 2: Turn Wi-Fi Off and On

- **Mac:** click the Wi-Fi icon in the top-right menu bar, switch Wi-Fi off, wait 10 seconds, switch it on.
- **Windows:** click the network icon in the bottom-right corner, click Wi-Fi to turn it off, wait 10 seconds, turn it on.

Wait 30 seconds and try a website. Fixed? You are done.

## Step 3: Check That You Joined the Right Network

Open the Wi-Fi menu and look at which network has the check mark.

- Guest networks often block work tools. Join the main work network if you have access.
- If you see a network name you do not recognize, disconnect from it. Do not sign in to anything on an unknown network.

## Step 4: Forget the Network and Join Again

This clears a saved password that may be out of date.

- **Mac:** System Settings > Wi-Fi > click the "..." or "Details" button next to the network > **Forget This Network**. Then join it again and enter the password.
- **Windows:** Settings > Network & internet > Wi-Fi > Manage known networks > select the network > **Forget**. Then join it again.

## Step 5: Restart the Computer

A full restart (not just closing the lid) fixes most remaining problems.

## Step 6: Move Closer

If Wi-Fi works near the access point but not at your desk, the signal is too weak where you sit. That is a network problem, not your fault. Tell IT where you sit.

---

## When to Contact IT

Contact IT if Step 5 did not fix it, or if Wi-Fi is down for everyone. Include:

1. **What you see:** for example "connected but no internet," "cannot see the network," or "keeps disconnecting."
2. **Where you are:** building, floor, room or desk.
3. **When it started,** and whether it affects anyone else.
4. **What you already tried** from this page (for example "Steps 1 to 5").
5. A screenshot of any error message.

> For IT staff: `scripts/net-check.sh` and `scripts/wifi-summary.sh` in [IT Automation Scripts](https://github.com/maxcamplese/it-automation-scripts) check each layer and report signal quality.
