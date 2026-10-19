"""Site check: fails CI when a page would break or lose its hardening.

For every HTML page it verifies that:
  - every local link, script, stylesheet, image and video points at a file
    that exists (query strings such as ?v= cache busters are ignored)
  - the page carries the site's Content Security Policy, identical on
    every page, with no inline-script or inline-style allowances
  - there are no inline scripts, inline styles or inline event handlers
    (the CSP would block them, so they would silently not work)
  - every link that opens a new tab has rel="noopener"
  - the contact address never appears as plain text (site.js assembles it)

It also checks .well-known/security.txt (RFC 9116): it has a contact that is
a web address (never an email address or phone number), one Expires date,
and is neither expired nor within 30 days of expiring, so renewal is a
nudge while there is still time.

Standard library only, so it runs with no install step.
Usage: python3 .github/scripts/check_site.py [site-root]
"""

import datetime
import pathlib
import re
import sys
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit

ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
SKIP_DIRS = {".git", ".github", "node_modules"}
URL_ATTRS = {("a", "href"), ("link", "href"), ("script", "src"), ("img", "src"),
             ("source", "src"), ("video", "src"), ("video", "poster"), ("audio", "src")}
BANNED_CSP = ("'unsafe-inline'", "'unsafe-eval'", "'unsafe-hashes'")
SECURITY_TXT = pathlib.Path(".well-known") / "security.txt"
RENEW_WITHIN_DAYS = 30


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.urls, self.problems, self.csp = [], [], None
        self._in_inline_script = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        for name, value in attrs:
            if name.startswith("on"):
                self.problems.append(f"inline event handler {name}= on <{tag}>")
            if name == "style":
                self.problems.append(f"inline style attribute on <{tag}>")
            if (tag, name) in URL_ATTRS and value:
                self.urls.append((tag, value))
        if tag == "meta" and (a.get("http-equiv") or "").lower() == "content-security-policy":
            self.csp = a.get("content", "")
        if tag == "script" and "src" not in a and a.get("type") != "application/ld+json":
            self.problems.append("inline <script>")
        if tag == "style":
            self.problems.append("inline <style> block")
        if tag == "a" and a.get("target") == "_blank" and "noopener" not in (a.get("rel") or ""):
            self.problems.append(f'target="_blank" without rel="noopener": {a.get("href")}')


def check_security_txt(root, now=None):
    """Problems with .well-known/security.txt, as a list of messages."""
    path = root / SECURITY_TXT
    if not path.is_file():
        return [f"{SECURITY_TXT}: missing"]
    now = now or datetime.datetime.now(datetime.timezone.utc)
    problems, fields = [], {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        name, sep, value = line.partition(":")
        if not sep:
            problems.append(f"{SECURITY_TXT}: line is not 'Field: value': {line[:60]}")
            continue
        fields.setdefault(name.strip().lower(), []).append(value.strip())

    contacts = fields.get("contact", [])
    if not contacts:
        problems.append(f"{SECURITY_TXT}: no Contact field")
    for contact in contacts:
        if urlsplit(contact).scheme != "https":
            problems.append(f"{SECURITY_TXT}: Contact must be an https address, not {contact.split(':')[0]}: "
                            "keep email addresses and phone numbers out of public files")
    expires = fields.get("expires", [])
    if len(expires) != 1:
        problems.append(f"{SECURITY_TXT}: needs exactly one Expires field")
    else:
        try:
            when = datetime.datetime.fromisoformat(expires[0].replace("Z", "+00:00"))
            if when.tzinfo is None:
                raise ValueError("no time zone")
        except ValueError:
            problems.append(f"{SECURITY_TXT}: Expires is not an RFC 3339 date-time: {expires[0]}")
        else:
            left = (when - now).days
            if when <= now:
                problems.append(f"{SECURITY_TXT}: expired on {expires[0]}. Set a new Expires date (about six months out)")
            elif left < RENEW_WITHIN_DAYS:
                problems.append(f"{SECURITY_TXT}: expires in {left} days ({expires[0]}). Renew it: set Expires about six months out")
            elif left > 366:
                problems.append(f"{SECURITY_TXT}: Expires is more than a year away; RFC 9116 recommends less")
    text = path.read_text(encoding="utf-8")
    if re.search(r"mailto:|tel:|[\w.+-]+@[\w-]+\.[\w.]+", text, re.I):
        problems.append(f"{SECURITY_TXT}: contains an email address or phone number")
    return problems


def main():
    pages = sorted(p for p in ROOT.rglob("*.html") if not SKIP_DIRS & set(p.relative_to(ROOT).parts))
    failures, policies = [], {}
    for page in pages:
        rel = page.relative_to(ROOT)
        text = page.read_text(encoding="utf-8")
        parser = Page()
        parser.feed(text)
        failures += [f"{rel}: {p}" for p in parser.problems]
        if re.search(r"mhoward14@|mailto:m", text, re.I):
            failures.append(f"{rel}: contact address in plain text")
        if not parser.csp:
            failures.append(f"{rel}: no Content-Security-Policy meta tag")
        else:
            policies[str(rel)] = parser.csp
            failures += [f"{rel}: CSP allows {b}" for b in BANNED_CSP if b in parser.csp]
        for tag, url in parser.urls:
            parts = urlsplit(url)
            if parts.scheme or parts.netloc or url.startswith("#"):
                continue  # external, mailto:, or in-page anchor
            target = (page.parent / unquote(parts.path)).resolve()
            if target.is_dir():
                target = target / "index.html"
            if not target.is_file():
                failures.append(f"{rel}: <{tag}> points at missing file {url}")
    for page in ("site.js", "style.css"):
        text = (ROOT / page).read_text(encoding="utf-8")
        if re.search(r"mhoward14@", text, re.I):
            failures.append(f"{page}: contact address in plain text")
    if len(set(policies.values())) > 1:
        failures.append("pages carry different Content Security Policies: " + ", ".join(policies))
    failures += check_security_txt(ROOT)

    if failures:
        print(f"Site check failed ({len(failures)}):")
        for f in failures:
            print(f"  x {f}")
        sys.exit(1)
    print(f"Site check passed: {len(pages)} pages, links resolve, one strict CSP, no inline code, address not exposed, security.txt current.")


if __name__ == "__main__":
    main()
