#!/usr/bin/env python3
"""Extract SEO elements from a raw HTML file and print JSON."""
import json
import re
import sys
from html.parser import HTMLParser


class SEOParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = None
        self.meta_description = None
        self.meta_robots = None
        self.canonical = None
        self.og_tags = {}
        self.h1 = []
        self.h2 = []
        self.schema_types = []
        self._in_title = False
        self._in_h1 = False
        self._in_h2 = False
        self._in_ldjson = False
        self._ldjson_buffer = ""
        self._text_buffer = ""

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "title":
            self._in_title = True
            self._text_buffer = ""
        elif tag == "h1":
            self._in_h1 = True
            self._text_buffer = ""
        elif tag == "h2":
            self._in_h2 = True
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
        elif tag == "link":
            rel = (attrs.get("rel") or "").lower()
            if rel == "canonical" and attrs.get("href"):
                self.canonical = attrs.get("href")
        elif tag == "script":
            script_type = (attrs.get("type") or "").lower()
            if script_type == "application/ld+json":
                self._in_ldjson = True
                self._ldjson_buffer = ""

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
            self.title = self._text_buffer.strip() or None
        elif tag == "h1":
            self._in_h1 = False
            text = self._text_buffer.strip()
            if text:
                self.h1.append(text)
        elif tag == "h2":
            self._in_h2 = False
            text = self._text_buffer.strip()
            if text and len(self.h2) < 10:
                self.h2.append(text)
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
        if self._in_title or self._in_h1 or self._in_h2:
            self._text_buffer += data
        if self._in_ldjson:
            self._ldjson_buffer += data


def main():
    if len(sys.argv) != 2:
        print("Usage: extract_seo.py <html_file>", file=sys.stderr)
        sys.exit(1)
    with open(sys.argv[1], "r", encoding="utf-8", errors="replace") as f:
        html = f.read()

    parser = SEOParser()
    parser.feed(html)

    result = {
        "title": parser.title,
        "metaDescription": parser.meta_description,
        "h1": parser.h1,
        "h2": parser.h2,
        "canonical": parser.canonical,
        "metaRobots": parser.meta_robots,
        "ogTags": parser.og_tags,
        "schemaTypes": parser.schema_types,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
