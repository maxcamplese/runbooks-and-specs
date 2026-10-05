# IT Runbooks and Specs

[![CI](https://github.com/maxcamplese/runbooks-and-specs/actions/workflows/ci.yml/badge.svg)](https://github.com/maxcamplese/runbooks-and-specs/actions/workflows/ci.yml)

Plain-language IT runbooks for non-technical users, a sample technical spec with a RACI matrix and UAT test plan, and a DNS and hosting checklist, plus two small tools that make the docs runnable.

| Document | Audience | What it shows |
|---|---|---|
| [Runbook: Wi-Fi Not Working](runbooks/wifi-not-working.md) | Any employee | Step-by-step fixes, and what to tell IT if they fail |
| [Runbook: Website or Domain Down](runbooks/website-or-domain-down.md) | Any employee | Is it me or the site, plus an error-message decoder table |
| [Runbook: Can't Sign In](runbooks/cannot-sign-in.md) | Any employee | Lockouts, password resets, two-factor clock problems |
| [Spec: Account Region Field](specs/account-region-field-spec.md) | IT, Sales Ops, approvers | Requirements, field and flow design, backfill, RACI, UAT, rollout, rollback |
| [Checklist: DNS and Hosting Changes](checklists/dns-and-hosting-checklist.md) | Whoever moves a domain | Pre-change, change, verification, and rollback steps |

## Tools

| Tool | What it does |
|---|---|
| [`tools/dns-precheck.sh`](tools/dns-precheck.sh) | Snapshots a domain's nameservers, website records, email records (MX, SPF, DMARC), HTTPS certificate, and redirects, then flags problems in plain language. It automates the checklist's before and after steps. |
| [`tools/check_docs.py`](tools/check_docs.py) | Checks every Markdown file for broken internal links and leftover `[placeholders]`. It runs in CI on every push. |

Requirements: macOS or Linux with `dig`, `curl`, and `openssl` (built into macOS), and Python 3.9 or newer. No third-party packages.

```bash
./tools/dns-precheck.sh example.com          # report
./tools/dns-precheck.sh example.com --save   # also save a snapshot file as a rollback record
python3 tools/check_docs.py                  # broken links fail; placeholders are listed
python3 tools/check_docs.py --strict         # placeholders fail too (run before publishing)
python3 -m unittest discover tests           # tests for check_docs.py
```

Sample `dns-precheck.sh` output for `example.com`: [`samples/dns-precheck-example.com.txt`](samples/dns-precheck-example.com.txt).

## How to Use the Documents

These are Markdown files. Read them on GitHub, or copy one into your own wiki or help desk and change the names, links, and channels to fit.

The runbooks follow one pattern: start with "is it just you," move from the easiest fix to the hardest, and end with exactly what to send IT so the ticket does not bounce back with questions.

## Known Limitations

- **The spec is a sample.** It describes a fictional company and a change that was not built in a real Salesforce org. Field, rule, and flow names follow Salesforce conventions, but the design has not been tested in an org.
- **Runbook menu paths change.** Steps for macOS, Windows, iPhone, and Android were written for macOS 26, Windows 11, and current iOS and Android, and have not been checked on older versions. Settings menus move between releases, and Android menus differ by phone maker.
- **`dns-precheck.sh` does not check DKIM.** DKIM records live under a selector name (for example `selector1._domainkey`) that differs by email provider, so you have to know the selector to look it up.
- **`check_docs.py` does not check external links,** so it can run with no network connection. A dead outside link will not be caught.
- **The runbooks assume a typical office setup** (a help desk, a password reset page, an authenticator app). Edit them to match a specific company's tools.

## License

- **Documents** (runbooks, spec, checklist): [CC BY 4.0](LICENSE). You may reuse and adapt them with credit.
- **Code** (`tools/` and `tests/`): [MIT](LICENSE-CODE).
