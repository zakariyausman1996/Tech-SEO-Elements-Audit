#!/usr/bin/env python3
"""Extract SEO elements from a live URL using a real headed Chrome browser.

Using a real browser (not headless, not curl) reliably gets past the bot/WAF
protection that blocks automated fetches for some of these domains, and
extracts the fully-rendered DOM (unlike curl, which only sees server HTML).
"""
import json
import sys

from playwright.sync_api import sync_playwright

EXTRACT_JS = r"""
() => {
  const q = (sel) => document.querySelector(sel);
  const qa = (sel) => Array.from(document.querySelectorAll(sel));
  const metaContent = (name) => {
    const el = document.querySelector(`meta[name="${name}"]`);
    return el ? el.getAttribute('content') : null;
  };
  const ogTags = {};
  qa('meta[property^="og:"]').forEach(el => { ogTags[el.getAttribute('property')] = el.getAttribute('content'); });
  const twitterTags = {};
  qa('meta[name^="twitter:"]').forEach(el => { twitterTags[el.getAttribute('name')] = el.getAttribute('content'); });
  const hreflang = qa('link[rel="alternate"][hreflang]').map(el => ({ hreflang: el.getAttribute('hreflang'), href: el.getAttribute('href') }));
  const headings = {};
  for (let i = 1; i <= 6; i++) { headings['h' + i] = qa('h' + i).map(el => el.innerText.trim()).filter(Boolean).slice(0, 10); }
  const schemaTypes = [];
  qa('script[type="application/ld+json"]').forEach(el => {
    try {
      const data = JSON.parse(el.textContent);
      const items = Array.isArray(data) ? data : [data];
      items.forEach(item => {
        if (item && item['@type']) {
          const types = Array.isArray(item['@type']) ? item['@type'] : [item['@type']];
          types.forEach(t => { if (!schemaTypes.includes(t)) schemaTypes.push(t); });
        }
      });
    } catch (e) {}
  });
  const canonicalEl = q('link[rel="canonical"]');
  const nextEl = q('link[rel="next"]');
  const prevEl = q('link[rel="prev"]');
  let mixedContent = false;
  if (location.protocol === 'https:') {
    qa('img[src], script[src], link[href], iframe[src]').forEach(el => {
      const url = el.getAttribute('src') || el.getAttribute('href');
      if (url && url.startsWith('http://')) mixedContent = true;
    });
  }
  const metaRobots = metaContent('robots');
  return {
    url: location.href,
    title: document.title || null,
    htmlLang: document.documentElement.getAttribute('lang'),
    metaDescription: metaContent('description'),
    metaRobots: metaRobots || "not present (defaults to index, follow)",
    canonical: canonicalEl ? canonicalEl.getAttribute('href') : null,
    relNext: nextEl ? nextEl.getAttribute('href') : null,
    relPrev: prevEl ? prevEl.getAttribute('href') : null,
    hreflang,
    h1: headings.h1, h2: headings.h2, h3: headings.h3,
    h4: headings.h4, h5: headings.h5, h6: headings.h6,
    ogTags, twitterTags, schemaTypes, mixedContent
  };
}
"""


def main():
    if len(sys.argv) != 2:
        print("Usage: extract_seo_local.py <url>", file=sys.stderr)
        sys.exit(1)
    url = sys.argv[1]

    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
        )
        context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        page = context.new_page()
        page.goto(url, wait_until="load", timeout=45000)
        page.wait_for_timeout(3000)
        result = page.evaluate(EXTRACT_JS)
        browser.close()

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
