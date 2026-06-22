---
name: zotero-opml-radar
description: Build Zotero RSS/OPML literature radars from a user's research field, priority journals, PubMed keywords, and follow-up needs. Use when the user wants to monitor new papers, create Zotero RSS feeds, generate OPML files, design PubMed RSS search strategies, rank journal subscriptions, or turn the workflow into a shareable tutorial/social post.
---

# Zotero OPML Radar

## Overview

Use this skill to turn a research interest into a practical Zotero RSS subscription system. The output is usually one or more `.opml` files that Zotero can import, plus an optional index table documenting the PubMed queries behind each feed.

## Workflow

1. Clarify the user's tracking scope:
   - Research field or disease area.
   - Must-follow journals.
   - Keywords or databases to monitor.
   - Whether feeds should be broad, focused, or split by theme.
   - Whether the user wants a single master OPML or several OPML files.

2. Prefer PubMed RSS for biomedical feeds:
   - Use journal abbreviations with `[jour]`, e.g. `"Crit Care"[jour]`.
   - Use explicit OR groups for top journals and keywords.
   - Keep feed names short and ordered with prefixes such as `01.`, `02.`, `03.` because Zotero may flatten OPML groups.
   - Set PubMed RSS `limit` to `100` for high-volume feeds unless the user asks otherwise.

3. Generate deliverables:
   - `.opml` for Zotero import.
   - `.csv` index with feed name, PubMed term, RSS URL, and search URL.
   - Optional plain-text posting copy or tutorial notes.

4. Validate before delivery:
   - Parse each OPML as XML.
   - Count the feed items and confirm ordering.
   - Confirm the index has no empty RSS URLs.
   - Remove failed or obsolete draft files from final deliverables.

## PubMed RSS Generation

For deterministic RSS URL generation, use `scripts/pubmed_opml_builder.py` rather than manually calling PubMed in ad hoc code.

Typical use:

```bash
python scripts/pubmed_opml_builder.py --config feeds.json --out-dir outputs --limit 100
```

The config JSON should look like:

```json
{
  "title": "Critical Care Master RSS",
  "opml": "critical-care-master-rss.opml",
  "index": "critical-care-master-rss-index.csv",
  "feeds": [
    {
      "name": "01. Intensive Care Medicine",
      "term": "\"Intensive Care Med\"[jour]"
    },
    {
      "name": "12. Top4 Medical Journals - Critical Care",
      "term": "(\"N Engl J Med\"[jour] OR \"Lancet\"[jour] OR \"JAMA\"[jour] OR \"BMJ\"[jour]) AND (\"critical care\" OR ICU OR sepsis OR ARDS OR \"mechanical ventilation\")"
    }
  ]
}
```

## Zotero-Friendly Naming

Zotero may display imported feeds as a flat list. To preserve a useful order:

- Prefix names with numbers: `01.`, `02.`, `03.`.
- Put high-priority or high-impact feeds first.
- Use one broad integrated feed when a topic does not need multiple subfolders.
- Avoid long names that become hard to scan in the Zotero sidebar.

## Tutorial And Social Copy

When the user wants to share the workflow, use the small-audience explanation style in `references/xiaohongshu-guide.md`. Emphasize:

- Zotero RSS automatically shows new articles.
- OPML is simply a batch RSS subscription list.
- AI's role is to convert a research direction into a clean OPML.
- The user still reads and judges papers; AI builds the information entrance.
