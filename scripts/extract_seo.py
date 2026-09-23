#!/usr/bin/env python3
"""Extract SEO elements from a raw HTML file and print JSON."""
import json
import sys
from html.parser import HTMLParser
from urllib.parse import urlparse

HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
HEADING_LIMIT = 10  # per level


class SEOParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = None
        self.html_lang = None
        self.meta_description = None
        self.meta_robots = None
        self.canonical = None
        self.rel_next = None
        self.rel_prev = None
        self.hreflang = []  # list of {"hreflang": ..., "href": ...}
        self.og_tags = {}
        self.twitter_tags = {}
        self.headings = {tag: [] for tag in HEADING_TAGS}
        self.schema_types = []
        self.resource_urls = []  # src/href values seen, for mixed-content check

        self._in_title = False
        self._current_heading = None
        self._in_ldjson = False
        self._ldjson_buffer = ""
        self._text_buffer = ""

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "html":
            lang = attrs.get("lang")
            if lang:
                self.html_lang = lang
        elif tag == "title":
            self._in_title = True
            self._text_buffer = ""
        elif tag in HEADING_TAGS:
            self._current_heading = tag
            self._text_buffer = ""
        elif tag == "meta":
            name = (attrs.get("name") or "").lower()
            prop = (attrs.get("property") or "").lower()
            content = attrs.get("content")
            if name == "description" and content:
                self.meta_description = content
            elif name == "robots" and content:
                self.meta_robots = content
            elif prop.startswith("og:") and content:
                self.og_tags[prop] = content
            elif name.startswith("twitter:") and content:
                self.twitter_tags[name] = content
        elif tag == "link":
            rel = (attrs.get("rel") or "").lower()
            href = attrs.get("href")
            if rel == "canonical" and href:
                self.canonical = href
            elif rel == "next" and href:
                self.rel_next = href
            elif rel == "prev" and href:
                self.rel_prev = href
            elif rel == "alternate" and attrs.get("hreflang") and href:
                self.hreflang.append({"hreflang": attrs.get("hreflang"), "href": href})
            if href:
                self.resource_urls.append(href)
        elif tag == "script":
            script_type = (attrs.get("type") or "").lower()
            if script_type == "application/ld+json":
                self._in_ldjson = True
                self._ldjson_buffer = ""
            src = attrs.get("src")
            if src:
                self.resource_urls.append(src)
        elif tag in ("img", "iframe", "source", "video", "audio"):
            src = attrs.get("src")
            if src:
                self.resource_urls.append(src)

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
            self.title = self._text_buffer.strip() or None
        elif tag in HEADING_TAGS and self._current_heading == tag:
            text = self._text_buffer.strip()
            if text and len(self.headings[tag]) < HEADING_LIMIT:
                self.headings[tag].append(text)
            self._current_heading = None
        elif tag == "script" and self._in_ldjson:
            self._in_ldjson = False
            try:
                data = json.loads(self._ldjson_buffer)
                items = data if isinstance(data, list) else [data]
                for item in items:
                    if isinstance(item, dict) and "@type" in item:
                        t = item["@type"]
                        types = t if isinstance(t, list) else [t]
                        for tt in types:
                            if tt not in self.schema_types:
                                self.schema_types.append(tt)
            except Exception:
                pass

    def handle_data(self, data):
        if self._in_title or self._current_heading:
            self._text_buffer += data
        if self._in_ldjson:
            self._ldjson_buffer += data


def check_mixed_content(page_url, resource_urls):
    """True if an https page references http:// resources."""
    if not page_url or not page_url.lower().startswith("https://"):
        return None  # not applicable / unknown page scheme
    for u in resource_urls:
        if u.lower().startswith("http://"):
            return True
    return False


def main():
    if len(sys.argv) < 2:
        print("Usage: extract_seo.py <html_file> [page_url]", file=sys.stderr)
        sys.exit(1)
    html_file = sys.argv[1]
    page_url = sys.argv[2] if len(sys.argv) > 2 else None

    with open(html_file, "r", encoding="utf-8", errors="replace") as f:
        html = f.read()

    parser = SEOParser()
    parser.feed(html)

    result = {
        "title": parser.title,
        "htmlLang": parser.html_lang,
        "metaDescription": parser.meta_description,
        "metaRobots": parser.meta_robots,
        "canonical": parser.canonical,
        "relNext": parser.rel_next,
        "relPrev": parser.rel_prev,
        "hreflang": parser.hreflang,
        "h1": parser.headings["h1"],
        "h2": parser.headings["h2"],
        "h3": parser.headings["h3"],
        "h4": parser.headings["h4"],
        "h5": parser.headings["h5"],
        "h6": parser.headings["h6"],
        "ogTags": parser.og_tags,
        "twitterTags": parser.twitter_tags,
        "schemaTypes": parser.schema_types,
        "mixedContent": check_mixed_content(page_url, parser.resource_urls),
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
