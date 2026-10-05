# Checklist: DNS and Hosting Changes

Use this before, during, and after pointing a client's domain at a new website. It comes from setting up Camplese Media client sites on [Reclaim Hosting](https://reclaimhosting.com), which runs cPanel. Client names, domains, and credentials are removed. Most steps apply to any host.

---

## Before the Change

> **Shortcut:** `./tools/dns-precheck.sh example.com --save` runs the lookups below in one step and saves the result as your rollback record. Run it again after the change and compare the two files.

- [ ] **Get registrar access the right way.** The client adds you as a delegate or user on their registrar account. Do not ask for their password. If the domain is registered through Reclaim Hosting, it is managed in the Reclaim client area instead.
- [ ] **Find out where DNS is actually hosted.** It may not be the registrar. Check the nameservers:
  ```bash
  dig NS example.com +short
  ```
- [ ] **Export or screenshot every existing DNS record** before changing anything. This is the rollback plan.
- [ ] **Identify email records and do not touch them:** `MX`, and the `TXT` records for SPF (`v=spf1 ...`), DKIM, and DMARC (`_dmarc`). Breaking these stops the client's email, which is worse than a website outage.
  ```bash
  dig MX example.com +short
  dig TXT example.com +short
  dig TXT _dmarc.example.com +short
  ```
- [ ] **Lower the TTL** on the records you will change (for example to 300 seconds) at least 24 hours ahead, so the change spreads quickly and a rollback is fast.
- [ ] **Agree on a time** with the client when a short outage is acceptable, and tell them what they might see.

## The Change

There are two ways to point a domain at a cPanel host like Reclaim. Pick one.

**Option A: keep DNS where it is, change only the website records.** Safest when the client's email works and you don't want to touch it.

- [ ] **Root domain** (`example.com`): set the `A` record to the server's IP address. In cPanel it is shown as **Shared IP Address** in the General Information panel.
- [ ] **www** (`www.example.com`): set a `CNAME` to the root domain, `example.com`.
- [ ] **Remove old conflicting records** for the same names (an old `A` record left in place sends some visitors to the old site).
- [ ] **Add any verification record** the host asks for (usually a `TXT` record).
- [ ] **Leave every email record exactly as it was.**

**Option B: move all DNS to the host by changing nameservers.** Simpler to manage afterward, but every record moves with it.

- [ ] **Recreate every non-website record in cPanel's Zone Editor first,** especially `MX` and the SPF, DKIM, and DMARC `TXT` records from your export.
- [ ] **If email is hosted elsewhere** (for example Google Workspace or Microsoft 365), set cPanel's **Email Routing** to **Remote Mail Exchanger**. Otherwise the server may try to deliver the domain's mail locally.
- [ ] **Change the nameservers at the registrar** to the ones the host lists for your account.
- [ ] **Expect a longer wait.** Nameserver changes can take up to 24 to 48 hours to spread, and lowering a record's TTL does not speed them up.

## After the Change

- [ ] **Check the new records from outside your own network:**
  ```bash
  dig A example.com +short
  dig CNAME www.example.com +short
  dig @1.1.1.1 A example.com +short    # ask a public resolver directly
  ```
- [ ] **Confirm HTTPS works** with no certificate warning on both `https://example.com` and `https://www.example.com`. On cPanel, **AutoSSL** issues the certificate automatically once DNS points to the server. If it hasn't appeared, open **SSL/TLS Status** in cPanel and run AutoSSL.
- [ ] **Confirm one version redirects to the other** (for example `example.com` to `www.example.com`), so search engines see one site.
- [ ] **Send a test email to and from the client's address** to prove email still works.
- [ ] **Raise the TTL back** (for example to 3600) once everything is stable.
- [ ] **Write down what changed** (record, old value, new value, date) and send the client a short summary.

## If Something Breaks

| Symptom | Likely cause | First thing to check |
|---|---|---|
| Site shows the old website | Old record still cached, or old `A` record not removed | `dig A example.com +short` from two resolvers; wait out the old TTL |
| "Server not found" | Record missing, or typo in the name or target | Compare against the host's instructions character by character |
| Certificate warning | Certificate not issued yet, or `www` not covered | cPanel **SSL/TLS Status**; run AutoSSL, then re-check |
| Email stopped arriving | `MX` or SPF record changed or deleted, or cPanel Email Routing set to local | Compare with the export from "Before the change" and restore; check Email Routing |

**Rollback:** restore the exported records. For Option A with the TTL lowered to 300 seconds, most visitors see the old site again within about 5 minutes. For Option B, change the nameservers back; that can take as long as the original change.
