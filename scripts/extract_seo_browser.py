#!/usr/bin/env python3
"""Fetch a URL with a real headless browser (Playwright/Chromium) and extract SEO elements as JSON."""
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
  return {
    url: location.href,
    title: document.title || null,
    htmlLang: document.documentElement.getAttribute('lang'),
    metaDescription: metaContent('description'),
    metaRobots: metaContent('robots'),
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
        print("Usage: extract_seo_browser.py <url>", file=sys.stderr)
        sys.exit(1)
    url = sys.argv[1]

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(user_agent=(
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        ))
        page.goto(url, wait_until="networkidle", timeout=30000)
        result = page.evaluate(EXTRACT_JS)
        browser.close()

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
