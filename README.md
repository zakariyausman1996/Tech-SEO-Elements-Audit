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
- `<title>` tag
- Meta description
- H1 and H2 headings
- Canonical URL
- Meta robots directive (index/noindex, follow/nofollow)
- Open Graph tags (og:title, og:description, og:image, og:type)
- Structured data / schema.org types (JSON-LD `@type` values present)

## Structure
- `snapshots/<YYYY-MM-DD>/<domain>.json` — raw extracted elements for that day, one file per domain
- `changelog/<domain>.md` — per-domain, change-only log. A dated entry is added ONLY when one or more tracked elements change since the last known-good snapshot. No entry = no change that day.

## Known issues
Some competitor domains (quizlet.com, scribd.com) have intermittent or hard bot/WAF blocking that can prevent automated fetches on some days — this is expected and separate from the [Robots.txt-Competitors-Watch](https://github.com/zakariyausman1996/Robots.txt-Competitors-Watch) repo's own documented issue with the same domains.
