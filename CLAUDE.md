# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Personal academic homepage of Jianfu Zhang (张健夫), Associate Professor at the School of Computer Science, SJTU, hosted on GitHub Pages. Pure static site — no build system, no dependencies, no tests. Pushing to `main` deploys the live site at matt-sjtu.github.io.

To preview locally, open `index.html` in a browser or run `python3 -m http.server`.

## Architecture

- `index.html` — the homepage. `style.css` is the shared stylesheet for all pages.
- `publications.html` — GENERATED, do not hand-edit. Regenerate with `python3 tools/generate_publications.py` (fetches DBLP pid 78/3993-3; `--xml PATH` to use a local export). Formal publications only; CoRR preprints are filtered out.
- `courses/cs3964.html`, `courses/cs3969.html` — per-course lecture pages; their PDFs live in `courses/cs3964/` and `courses/cs3969/` with ASCII-safe names (`NN-topic.pdf`). Lecture display titles live in the page's i18n dictionary, not the filenames. CS7353 links to an external site (cs7353.pages.dev).
- **Bilingual toggle**: every page has an `i18n` dictionary (`zh-CN` / `en`) in an inline `<script>`; `applyLanguage()` fills elements marked with `data-i18n` (textContent) or `data-i18n-html` (innerHTML, for strings containing links). The chosen language persists across pages via `localStorage('lang')`. To add translatable content: add the attribute to the element and a key to both dictionaries. The static Chinese text in the HTML body is only a pre-JS fallback — keep it in sync with the `zh-CN` dictionary.
- `topic.png` (1800×900 word cloud in the Research section) is generated from curated keyword weights in `~/research/outputs/academic_keyword_cloud/`; regenerate with a wordcloud script rather than editing by hand.
