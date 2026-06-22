#!/usr/bin/env python3
"""Build Zotero-ready OPML files from PubMed RSS queries.

Input: JSON config with title, opml, index, and feeds [{name, term}].
Output: OPML + CSV index.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import os
import re
import sys
import time
from pathlib import Path
from urllib.parse import quote

import requests


def create_pubmed_rss(session: requests.Session, name: str, term: str, limit: int) -> tuple[str, str, str]:
    search_url = "https://pubmed.ncbi.nlm.nih.gov/?term=" + quote(term)
    last_error = ""

    for attempt in range(1, 7):
        try:
            page = session.get(search_url, timeout=45)
            page.raise_for_status()
            csrf = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', page.text)
            if not csrf:
                raise RuntimeError("missing PubMed CSRF token")

            response = session.post(
                "https://pubmed.ncbi.nlm.nih.gov/create-rss-feed-url/",
                data={"name": name, "limit": str(limit), "term": term},
                headers={"Referer": search_url, "X-CSRFToken": csrf.group(1)},
                timeout=45,
            )
            response.raise_for_status()
            return response.json()["rss_feed_url"], search_url, ""
        except Exception as exc:  # noqa: BLE001 - CLI should report and retry network/API issues.
            last_error = str(exc)
            time.sleep(1.5 * attempt)

    return "", search_url, last_error


def write_opml(path: Path, title: str, rows: list[dict[str, str]]) -> None:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<opml version="2.0">',
        "  <head>",
        f"    <title>{html.escape(title)}</title>",
        "  </head>",
        "  <body>",
    ]
    for row in rows:
        if not row["rss"]:
            continue
        lines.append(
            '    <outline text="{name}" title="{name}" type="rss" xmlUrl="{rss}" htmlUrl="{search}" />'.format(
                name=html.escape(row["name"]),
                rss=html.escape(row["rss"]),
                search=html.escape(row["search"]),
            )
        )
    lines.extend(["  </body>", "</opml>"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="JSON config file")
    parser.add_argument("--out-dir", required=True, help="Output directory")
    parser.add_argument("--limit", type=int, default=100, help="PubMed RSS item limit")
    args = parser.parse_args()

    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (Zotero OPML Radar Skill)"})

    rows: list[dict[str, str]] = []
    for feed in config["feeds"]:
        name = feed["name"]
        term = feed["term"]
        rss, search, error = create_pubmed_rss(session, name, term, args.limit)
        rows.append({"name": name, "term": term, "rss": rss, "search": search, "error": error})
        print(("OK  " if rss else "ERR ") + name, flush=True)
        time.sleep(1)

    write_opml(out_dir / config.get("opml", "zotero-rss.opml"), config.get("title", "Zotero RSS"), rows)

    index_name = config.get("index", "zotero-rss-index.csv")
    with (out_dir / index_name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["name", "term", "rss", "search", "error"])
        writer.writeheader()
        writer.writerows(rows)

    failures = [row for row in rows if not row["rss"]]
    if failures:
        print(f"{len(failures)} feed(s) failed; see index CSV.", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
