#!/usr/bin/env bash
#
# dns-precheck.sh: Snapshot a domain's DNS, email, and HTTPS setup before
# you change anything, and flag common problems in plain language.
#
# This automates the "Before the change" and "After the change" sections of
# checklists/dns-and-hosting-checklist.md. Run it before a change and save the
# output as your rollback record, then run it again afterward and compare.
#
# Usage:
#   ./tools/dns-precheck.sh example.com
#   ./tools/dns-precheck.sh example.com --save   # also writes dns-snapshot-<domain>-<date>.txt
#   ./tools/dns-precheck.sh --help
#
# Exit codes: 0 = report finished, 1 = domain does not resolve at all, 2 = bad usage.
# Needs dig, curl, and openssl (all built into macOS; on Linux install dnsutils).

set -u

usage() { sed -n '3,17p' "$0" | sed 's/^# \{0,1\}//'; }

domain="${1:-}"
save=false
case "$domain" in
  ""|--help|-h) usage; [ -z "$domain" ] && exit 2; exit 0 ;;
esac
case "${2:-}" in
  --save) save=true ;;
  "") ;;
  *) echo "Unknown option: $2" >&2; exit 2 ;;
esac

# Only allow characters that can appear in a domain name. This also keeps
# anything odd from reaching the commands below.
if ! printf '%s' "$domain" | grep -Eq '^[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'; then
  echo "That does not look like a domain name: $domain" >&2
  exit 2
fi

for tool in dig curl openssl; do
  command -v "$tool" >/dev/null 2>&1 || { echo "Missing required tool: $tool" >&2; exit 2; }
done

WARNINGS=()
warn() { WARNINGS+=("$1"); }

# Print records as "name  TTL  type  value", one per line.
records() {
  # dig prints: name TTL class type value. Drop the class (always IN).
  dig +noall +answer +time=3 +tries=1 "$1" "$2" 2>/dev/null \
    | awk '{ printf "%s  %s  %s ", $1, $2, $4; for (i = 5; i <= NF; i++) printf " %s", $i; print "" }'
}

section() { printf '\n%s\n' "$1"; }
show() { if [ -n "$1" ]; then printf '%s\n' "$1" | sed 's/^/  /'; else echo "  (none)"; fi; }

# Days until a certificate's expiry date. The date command differs between macOS and Linux.
days_until() {
  local end_epoch now_epoch
  if [ "$(uname)" = "Darwin" ]; then
    end_epoch=$(date -j -f "%b %e %T %Y %Z" "$1" +%s 2>/dev/null) || return 1
  else
    end_epoch=$(date -d "$1" +%s 2>/dev/null) || return 1
  fi
  now_epoch=$(date +%s)
  echo $(( (end_epoch - now_epoch) / 86400 ))
}

report() {
  echo "DNS pre-check for $domain ($(date '+%Y-%m-%d %H:%M %Z'))"
  echo "Columns: name  TTL (seconds)  type  value"

  section "Nameservers (who hosts the DNS; this may not be the registrar)"
  ns="$(records "$domain" NS)"
  show "$ns"

  section "Website: root domain"
  root_a="$(records "$domain" A)"
  show "$root_a"
  [ -z "$root_a" ] && warn "The root domain has no A record, so $domain will not load without www."

  section "Website: www"
  www="$(records "www.$domain" A)"
  show "$www"
  [ -z "$www" ] && warn "www.$domain does not resolve. Visitors who type www will get an error."

  section "Email: MX (where mail is delivered)"
  mx="$(records "$domain" MX)"
  show "$mx"
  [ -z "$mx" ] && warn "No MX records: this domain cannot receive email. If the client uses email here, stop and find out why."
  # A "null MX" (priority 0, host ".") is a deliberate statement that the domain takes no email.
  if printf '%s\n' "$mx" | grep -Eq 'MX  0 \.$'; then
    echo "  Note: this is a null MX. The domain deliberately accepts no email."
  fi

  section "Email: SPF (which servers may send mail as this domain)"
  spf="$(records "$domain" TXT | grep -i 'v=spf1')"
  show "$spf"
  [ -n "$mx" ] && [ -z "$spf" ] && warn "Email is set up but there is no SPF record. Mail from this domain is more likely to land in spam."
  [ "$(printf '%s\n' "$spf" | grep -c 'v=spf1')" -gt 1 ] && warn "More than one SPF record. Receivers treat that as an error; merge them into one."

  section "Email: DMARC (policy for mail that fails checks)"
  dmarc="$(records "_dmarc.$domain" TXT)"
  show "$dmarc"
  [ -n "$mx" ] && [ -z "$dmarc" ] && warn "No DMARC record. Others can spoof this domain more easily."

  section "HTTPS certificate"
  end_date="$(echo | openssl s_client -servername "$domain" -connect "$domain:443" 2>/dev/null \
    | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)"
  if [ -n "$end_date" ]; then
    days="$(days_until "$end_date")"
    echo "  Expires: $end_date (${days:-?} days)"
    if [ -n "$days" ] && [ "$days" -lt 14 ]; then
      warn "The HTTPS certificate expires in $days days. Check that automatic renewal is working."
    fi
  else
    echo "  (could not read a certificate on port 443)"
    [ -n "$root_a" ] && warn "No HTTPS certificate found on $domain. Visitors will see a security warning."
  fi

  section "Redirects"
  for url in "https://$domain" "https://www.$domain"; do
    result="$(curl -s -o /dev/null -m 8 -w '%{http_code} %{redirect_url}' "$url")"
    echo "  $url -> ${result:-no response}"
  done

  section "TTL note"
  echo "  Lower the TTL on records you will change (for example to 300) at least a day ahead,"
  echo "  so the change spreads quickly and a rollback is fast."

  section "Findings"
  if [ "${#WARNINGS[@]}" -eq 0 ]; then
    echo "  No problems found."
  else
    for w in "${WARNINGS[@]}"; do echo "  [WARN] $w"; done
  fi
}

# Stop early if the domain does not exist at all.
# NXDOMAIN is DNS's answer for "this name does not exist".
if dig +noall +comments +time=3 +tries=1 "$domain" 2>/dev/null | grep -q 'status: NXDOMAIN'; then
  echo "$domain does not resolve at all. Check the spelling, or whether the domain has expired." >&2
  exit 1
fi

if $save; then
  file="dns-snapshot-$domain-$(date +%Y%m%d-%H%M).txt"
  report | tee "$file"
  echo
  echo "Saved to $file. Keep it until the change is confirmed working; it is your rollback record."
else
  report
fi
