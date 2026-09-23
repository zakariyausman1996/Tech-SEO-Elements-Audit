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

**`snapshots/` + `changelog/`** — automated daily fetch via `curl` (scripts/extract_seo.py), run by the "Daily competitor SEO element watch" cloud routine, cron 7:15 UTC daily. Works even if your laptop is off. Several domains (studocu.com, chegg.com, quizlet.com, brainly.com) run bot/WAF protection that blocks plain `curl` on any given day, returning a captcha/block page instead of the real homepage — expected, not a bug.

**`browser-snapshots/` + `browser-changelog/`** — on-demand fetch via `scripts/extract_seo_local.py` (Playwright driving the real installed Chrome, headed mode), run locally when asked. Gets past the bot protection that blocks curl — all 6 domains return real content this way. Not scheduled; only updates when requested. Run it with:
```bash
python3 scripts/extract_seo_local.py https://www.chegg.com/
```

Diff `snapshots/` days against each other, and `browser-snapshots/` days against each other — never compare across the two, since curl and a real browser can legitimately see different content even with nothing actually wrong.

## Field conventions
- `metaRobots`: if a page has no `<meta name="robots">` tag, this is set to `"not present (defaults to index, follow)"` rather than `null` — absence of the tag means default crawlable behavior, not a data gap.
