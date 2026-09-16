#!/usr/bin/env python3
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
DOCKERFILE = ROOT / "Dockerfile"
COMPOSE = ROOT / "docker-compose.yml"


class SiteParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.anchor_targets: set[str] = set()
        self.stylesheets: list[str] = []
        self.lang: str | None = None
        self.has_viewport = False
        self.in_title = False
        self.title_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "html":
            self.lang = values.get("lang")
        element_id = values.get("id")
        if element_id:
            self.ids.add(element_id)
        if tag == "a":
            href = values.get("href") or ""
            if href.startswith("#") and len(href) > 1:
                self.anchor_targets.add(href[1:])
        if tag == "link" and values.get("rel") == "stylesheet":
            href = values.get("href")
            if href:
                self.stylesheets.append(href)
        if tag == "meta" and values.get("name") == "viewport":
            self.has_viewport = True
        if tag == "title":
            self.in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)


def main() -> int:
    html = INDEX.read_text(encoding="utf-8")
    parser = SiteParser()
    parser.feed(html)

    title = "".join(parser.title_parts).strip()
    if not title:
        raise AssertionError("document title is missing")
    if not parser.lang:
        raise AssertionError("html lang attribute is missing")
    if not parser.has_viewport:
        raise AssertionError("viewport metadata is missing")

    unresolved = sorted(parser.anchor_targets - parser.ids)
    if unresolved:
        raise AssertionError(f"navigation anchors without matching IDs: {unresolved}")

    if not parser.stylesheets:
        raise AssertionError("no stylesheet is referenced")
    for stylesheet in parser.stylesheets:
        if stylesheet.startswith(("http://", "https://")):
            continue
        path = ROOT / stylesheet.lstrip("/")
        if not path.is_file():
            raise AssertionError(f"referenced stylesheet does not exist: {stylesheet}")

    dockerfile = DOCKERFILE.read_text(encoding="utf-8")
    if "nginxinc/nginx-unprivileged" not in dockerfile:
        raise AssertionError("Dockerfile must retain the unprivileged Nginx base image")
    if not re.search(r"^EXPOSE\s+8080\s*$", dockerfile, re.MULTILINE):
        raise AssertionError("Dockerfile must expose port 8080")
    if "HEALTHCHECK" not in dockerfile:
        raise AssertionError("Dockerfile health check is missing")

    compose = COMPOSE.read_text(encoding="utf-8")
    if '"8080:8080"' not in compose:
        raise AssertionError("Compose must publish host 8080 to container 8080")
    if "read_only: true" not in compose:
        raise AssertionError("Compose should retain a read-only root filesystem")
    if "no-new-privileges:true" not in compose:
        raise AssertionError("Compose should retain no-new-privileges")

    print("Static site contract validation passed")
    print(f"- title: {title}")
    print(f"- language: {parser.lang}")
    print(f"- internal anchors checked: {len(parser.anchor_targets)}")
    print(f"- stylesheets checked: {len(parser.stylesheets)}")
    print("- container runs on unprivileged port 8080 with health check")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"validation failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
