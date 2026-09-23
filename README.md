# SEO Elements Competitors Watch

Daily snapshots of homepage SEO elements for Studocu and its main competitors, used for competitive SEO/GEO monitoring.

## Tracked domains
- studocu.com
- chegg.com
- quizlet.com
- coursehero.com
- scribd.com
- brainly.com

## Tracked elements (per homepage)
- `<title>` tag, `html[lang]`
- Meta description, meta robots
- Canonical URL, rel=next/prev
- Hreflang tags
- H1–H6 headings
- Open Graph tags (any `og:*`)
- Twitter Card tags (any `twitter:*`)
- Structured data / schema.org types (JSON-LD `@type` values present)
- Mixed-content flag (https page referencing http:// resources)

## Two data sources — don't cross-compare them

**`snapshots/` + `changelog/`** — automated daily fetch via `curl` (scripts/extract_seo.py), run by the "Daily competitor SEO element watch" cloud routine, cron 7:15 UTC daily. Fully automated, works even if your laptop is off. **Limitation:** several of these domains (studocu.com, chegg.com, quizlet.com, brainly.com) run bot/WAF protection (PerimeterX, Cloudflare challenge, etc.) that blocks plain `curl` requests on any given day, returning a captcha/block page instead of the real homepage. This is real, expected behavior — not a routine bug — and isn't something this project tries to bypass.

**`browser-snapshots/` + `browser-changelog/`** — manual, on-demand fetch using Claude's built-in browser pane (a real Chromium browser), run by asking Claude to check the competitor pages. Gets past the bot protection that blocks curl, since it's indistinguishable from a normal visitor — all 6 domains return real content this way. **Limitation:** not automated/scheduled — only updates when explicitly requested, since it needs an active Claude Code session. A cloud/headless-browser equivalent (Playwright + Chromium in the automated routine) was attempted and abandoned: the cloud environment's network restrictions block the apt/Ubuntu package installs Chromium's system dependencies need, and that path isn't being pursued further.

Diff `snapshots/` days against each other, and `browser-snapshots/` days against each other — never compare across the two, since curl and a real browser can legitimately see different content (JS-rendered elements, geo-redirects, etc.) even with nothing actually wrong.

## Field conventions
- `metaRobots`: if a page has no `<meta name="robots">` tag, this is set to the literal string `"not present (defaults to index, follow)"` rather than `null` — absence of the tag means default crawlable behavior, not a data gap.

## Known issues
- quizlet.com, scribd.com, studocu.com, chegg.com, brainly.com: intermittent or hard bot/WAF blocking via `curl` (see above) — separate from the [Robots.txt-Competitors-Watch](https://github.com/zakariyausman1996/Robots.txt-Competitors-Watch) repo's own documented issue with the same domains.
- Browser-based checks are on-demand only — ask Claude to run one, it isn't scheduled.
