# Runbook: Website or Domain Down

**Who this is for:** anyone who cannot reach a website, including your own company's site.
**Time:** about 5 minutes.

---

## Step 1: Is Your Internet Working?

Open a well-known site such as `https://www.google.com`.

- **It does not load either:** your internet is the problem, not the website. Follow [Runbook: Wi-Fi Not Working](wifi-not-working.md).
- **It loads:** your internet is fine. Go to Step 2.

## Step 2: Is the Site Down for Everyone?

Try the site on your phone **with Wi-Fi turned off** (using cell data).

- **It fails on your phone too:** the site is probably down for everyone. Go to Step 4.
- **It works on your phone:** the problem is your computer or your network. Go to Step 3.

## Step 3: Fix It on Your Computer

Try these in order. Test the site after each one.

1. **Check the address.** One wrong letter goes to a different site or nowhere. Retype it instead of using an old bookmark.
2. **Open it in a private window.** Chrome: `Ctrl+Shift+N` (Windows) or `Cmd+Shift+N` (Mac). Safari: `Cmd+Shift+N`. If it works there, clear your browser's cache and cookies for that site.
3. **Try another browser** (Chrome, Safari, Edge, or Firefox).
4. **Turn off VPN** if you use one, then try again. Turn it back on afterward if your work requires it.
5. **Restart the computer.**

## Step 4: Read the Error Message

The message on the screen tells IT a lot. Write it down or take a screenshot.

| What you see | What it usually means |
|---|---|
| "This site can't be reached" / "Server not found" / `DNS_PROBE_FINISHED_NXDOMAIN` | The name of the site cannot be looked up. Either the address is wrong or the domain's DNS settings are broken. |
| "Your connection is not private" / "Certificate error" | The site's security certificate is expired or wrong. **Do not click "proceed anyway"** on a site where you sign in or pay. |
| "502 Bad Gateway" / "503 Service Unavailable" | The site's server is down or overloaded. Usually the site owner has to fix it. |
| "404 Not Found" | The site works, but that specific page does not exist. Try the home page. |
| "403 Forbidden" / "Access denied" | You may not have permission, or the site is blocking your network. |
| The page loads forever | Network, VPN, or a firewall blocking the site. |

## Step 5: If It Is a Well-Known Service, Check Its Status Page

Most large services publish their status. Search for "[service name] status" (for example `status.slack.com` or `githubstatus.com`). If they report an outage, there is nothing to fix on your end. Wait and check back.

---

## When to Contact IT

Contact IT if Step 3 did not fix it, or if it is your company's own website. Include:

1. **The exact address** you tried (copy it from the address bar).
2. **The error message** or a screenshot.
3. **Whether it works on your phone with Wi-Fi off** (from Step 2).
4. **When it started** and whether coworkers see the same thing.

> For IT staff: if it is your own domain, see [Checklist: DNS and Hosting Changes](../checklists/dns-and-hosting-checklist.md).
