#!/usr/bin/env python3
"""Generate publications.html from a DBLP person XML export.

Usage:
    python3 tools/generate_publications.py [--xml PATH] [--skip-s2]

By default fetches https://dblp.org/pid/78/3993-3.xml (Jianfu Zhang 0003),
falling back to the DBLP SPARQL endpoint when dblp.org's bot protection
blocks the XML export. Pass --xml to use a local copy instead.
Only formal publications are kept
from DBLP (informal/CoRR preprints are skipped as entries), but each unique
preprint is checked against Semantic Scholar BY ARXIV ID (identity-safe:
no author disambiguation involved) — if S2 reports a formal publication
venue, the paper is added with that venue until DBLP catches up, at which
point the DBLP record takes over automatically. tools/extra_publications.json
supplies manual entries and takes precedence over S2 additions.
Output: publications.html in repo root.
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

SELF_PID = "78/3993-3"
SELF_NAME = "Jianfu Zhang"
DBLP_URL = f"https://dblp.org/pid/{SELF_PID}.xml"
USER_AGENT = "matt-sjtu.github.io publications updater"

# dblp.org intermittently puts the XML export behind an Anubis bot challenge
# (observed 5xx / challenge HTML since Sep 2026); the SPARQL endpoint stays
# open to scripts, so it serves as the fallback data source.
SPARQL_URL = "https://sparql.dblp.org/sparql"
SPARQL_QUERY = f"""\
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX dblp: <https://dblp.org/rdf/schema#>
SELECT ?pub ?informal ?title ?year ?yevent ?venue ?ord ?name ?creator ?ee ?primary WHERE {{
  ?pub dblp:authoredBy <https://dblp.org/pid/{SELF_PID}> .
  ?pub dblp:title ?title .
  ?pub dblp:yearOfPublication ?year .
  OPTIONAL {{ ?pub dblp:yearOfEvent ?yevent }}
  ?pub dblp:hasSignature ?sig .
  ?sig dblp:signatureOrdinal ?ord .
  ?sig dblp:signatureDblpName ?name .
  ?sig dblp:signatureCreator ?creator .
  OPTIONAL {{ ?pub rdf:type dblp:Informal . BIND(1 AS ?informal) }}
  OPTIONAL {{ ?pub dblp:publishedIn ?venue }}
  OPTIONAL {{ ?pub dblp:documentPage ?ee }}
  OPTIONAL {{ ?pub dblp:primaryDocumentPage ?primary }}
}}
"""
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXTRA_JSON = os.path.join(REPO, "tools", "extra_publications.json")

# journal abbreviations -> display names
VENUE_MAP = {
    "Pattern Recognit.": "Pattern Recognition",
    "IEEE Trans. Image Process.": "IEEE Transactions on Image Processing",
    "IEEE Signal Process. Lett.": "IEEE Signal Processing Letters",
    "Neural Process. Lett.": "Neural Processing Letters",
    "J. Comput. Sci. Technol.": "Journal of Computer Science and Technology",
}

# Semantic Scholar's long venue names -> the site's display convention
S2_VENUE_MAP = {
    "IEEE International Conference on Acoustics, Speech, and Signal Processing": "ICASSP",
    "IEEE/CVF Conference on Computer Vision and Pattern Recognition": "CVPR",
    "Computer Vision and Pattern Recognition": "CVPR",
    "IEEE/CVF International Conference on Computer Vision": "ICCV",
    "IEEE International Conference on Computer Vision": "ICCV",
    "European Conference on Computer Vision": "ECCV",
    "International Conference on Learning Representations": "ICLR",
    "Neural Information Processing Systems": "NeurIPS",
    "International Conference on Machine Learning": "ICML",
    "AAAI Conference on Artificial Intelligence": "AAAI",
    "ACM International Conference on Multimedia": "ACM Multimedia",
    "ACM Multimedia": "ACM Multimedia",
    "IEEE International Conference on Multimedia and Expo": "ICME",
    "IEEE International Conference on Image Processing": "ICIP",
}


# IEEE conference DOIs embed the proceedings acronym and year:
# 10.1109/ICIP61757.2026.11629184 -> ICIP, 2026. Semantic Scholar files some of
# these under a venue id that collides on the acronym (ICIP papers land on
# "International Conference on Information Photonics", with the wrong year), so
# where the DOI names a conference we recognize it wins over the S2 venue string.
DOI_CONF_ACRONYMS = {"icassp", "icip", "icme", "cvpr", "iccv", "wacv", "ijcnn"}


def clean_author(name):
    """Strip DBLP homonym suffix: 'Liqing Zhang 0001' -> 'Liqing Zhang'."""
    return re.sub(r"\s+\d{4}$", "", name)


def venue_from_doi(doi):
    """(venue, year) from an IEEE conference DOI, else (None, None)."""
    m = re.match(r"10\.1109/([a-z]+)\d*\.(\d{4})\.", (doi or "").lower())
    if m and m.group(1) in DOI_CONF_ACRONYMS:
        return m.group(1).upper(), int(m.group(2))
    return None, None


def clean_venue(venue):
    """Normalize venue: strip '(44)' volume markers, expand journal abbrevs."""
    venue = re.sub(r"\s*\(\d+\)$", "", venue.strip())
    return VENUE_MAP.get(venue, venue)


def pick_links(urls):
    """Preferred links from ee URLs (in order): one DOI, one arXiv, else first."""
    links = []
    for url in urls:
        if "doi.org" in url:
            # DOIs are case-insensitive; the SPARQL endpoint uppercases them,
            # so normalize to keep the generated HTML stable across sources
            url = url.lower()
            if not any(l[0] == "DOI" for l in links):
                links.append(("DOI", url))
        elif "arxiv.org" in url and not any(l[0] == "arXiv" for l in links):
            links.append(("arXiv", url))
    if not links and urls:
        links.append(("Link", urls[0]))
    return links


def dedupe_preprints(pubs, informal):
    """Preprints whose title does not match any formal publication."""
    formal_norms = {norm_title(p["title"]) for p in pubs}
    return [p for p in informal if not is_known(p["title"], formal_norms)]


def parse_pubs(xml_text):
    """Return (formal_pubs, unique_preprints) from the DBLP person XML."""
    root = ET.fromstring(xml_text)
    pubs, informal = [], []
    for r in root.findall("r"):
        e = r[0]
        authors = []
        self_idx = -1
        for a in e.findall("author"):
            if a.get("pid") == SELF_PID:
                self_idx = len(authors)
            authors.append(clean_author(a.text or ""))
        title = (e.findtext("title") or "").rstrip(".")
        year = int(e.findtext("year") or 0)
        if e.get("publtype") == "informal":
            m = re.search(r"corr/abs-(\d{4})-(\d+)", e.get("key") or "")
            if m:
                informal.append({
                    "authors": authors, "self_idx": self_idx, "title": title,
                    "year": year, "arxiv": f"{m.group(1)}.{m.group(2)}",
                })
            continue
        venue = clean_venue(e.findtext("booktitle") or e.findtext("journal") or "")
        links = pick_links([ee.text for ee in e.findall("ee") if ee.text])
        pubs.append({
            "authors": authors, "self_idx": self_idx, "title": title,
            "year": year, "venue": venue, "links": links,
        })
    return pubs, dedupe_preprints(pubs, informal)


def sparql_pubs():
    """Return (formal_pubs, unique_preprints) from the DBLP SPARQL endpoint."""
    print(f"querying {SPARQL_URL} ...")
    url = SPARQL_URL + "?" + urllib.parse.urlencode({"query": SPARQL_QUERY})
    req = urllib.request.Request(
        url, headers={"User-Agent": USER_AGENT,
                      "Accept": "application/sparql-results+json"})
    rows = json.loads(fetch_with_retry(req))["results"]["bindings"]
    recs = {}
    for b in rows:
        val = {k: v["value"] for k, v in b.items()}
        r = recs.setdefault(val["pub"], {
            # yearOfEvent matches the XML <year> for conference papers;
            # yearOfPublication is the (often later) proceedings year
            "title": val["title"].rstrip("."),
            "year": int(val.get("yevent") or val["year"]),
            "venue": val.get("venue", ""), "informal": False,
            "signatures": {}, "ees": set(), "primary": None,
        })
        r["informal"] |= "informal" in val
        r["signatures"][int(val["ord"])] = (val["name"], val["creator"])
        if "ee" in val:
            r["ees"].add(val["ee"])
        if "primary" in val:
            r["primary"] = val["primary"]
    self_uri = f"https://dblp.org/pid/{SELF_PID}"
    pubs, informal = [], []
    for rec_uri, r in recs.items():
        sigs = [r["signatures"][i] for i in sorted(r["signatures"])]
        authors = [clean_author(name) for name, _ in sigs]
        self_idx = next(
            (i for i, (_, creator) in enumerate(sigs) if creator == self_uri), -1)
        if r["informal"]:
            m = re.search(r"corr/abs-(\d{4})-(\d+)", rec_uri)
            if m:
                informal.append({
                    "authors": authors, "self_idx": self_idx, "title": r["title"],
                    "year": r["year"], "arxiv": f"{m.group(1)}.{m.group(2)}",
                })
            continue
        urls = sorted(r["ees"], key=lambda u: u != r["primary"])
        pubs.append({
            "authors": authors, "self_idx": self_idx, "title": r["title"],
            "year": r["year"], "venue": clean_venue(r["venue"]),
            "links": pick_links(urls),
        })
    return pubs, dedupe_preprints(pubs, informal)


def fetch_with_retry(req, attempts=6):
    """Fetch a request, retrying 429/5xx and network errors with backoff."""
    delay = 5
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read()
        except urllib.error.HTTPError as ex:
            # urllib refuses to auto-follow 307/308 for POST; do it ourselves
            if ex.code in (307, 308) and ex.headers.get("Location"):
                req = urllib.request.Request(
                    urllib.parse.urljoin(req.full_url, ex.headers["Location"]),
                    data=req.data, headers=dict(req.header_items()))
                continue
            if ex.code != 429 and ex.code < 500:
                raise
        except Exception:
            pass
        if attempt < attempts - 1:
            time.sleep(delay)
            delay = min(delay * 2, 60)
    raise RuntimeError(f"{req.full_url} kept failing after {attempts} attempts")


def s2_batch_lookup(arxiv_ids):
    """One batched POST for all preprints; list aligned with input (None = unknown)."""
    url = ("https://api.semanticscholar.org/graph/v1/paper/batch"
           "?fields=venue,year,publicationVenue,externalIds")
    body = json.dumps({"ids": [f"ARXIV:{a}" for a in arxiv_ids]}).encode()
    req = urllib.request.Request(
        url, data=body,
        headers={"User-Agent": USER_AGENT, "Content-Type": "application/json"})
    return json.loads(fetch_with_retry(req))


def norm_title(t):
    """Normalize for dedupe: lowercase alnum only."""
    return re.sub(r"[^a-z0-9]", "", t.lower())


def is_known(title, known_norms):
    """True if title matches a known one, incl. renamed formal versions
    ('Deep Image Harmonization...' vs 'DoveNet: Deep Image Harmonization...')."""
    n = norm_title(title)
    return any(n == k or n in k or k in n for k in known_norms)


def augment_from_s2(preprints, known_norms):
    """Preprints that Semantic Scholar reports as formally published.

    Identity-safe by construction: lookups are keyed by the arXiv id of the
    author's own DBLP preprints, so no author disambiguation is involved.
    """
    candidates = [p for p in preprints if not is_known(p["title"], known_norms)]
    if not candidates:
        return []
    results = s2_batch_lookup([p["arxiv"] for p in candidates])
    added = []
    for pre, d in zip(candidates, results):
        if not d:
            continue
        venue_raw = (d.get("venue") or "").strip()
        if not venue_raw or "arxiv" in venue_raw.lower():
            continue
        links = []
        doi = (d.get("externalIds") or {}).get("DOI")
        if doi and "arxiv" not in doi.lower():
            links.append(("DOI", f"https://doi.org/{doi}"))
        links.append(("arXiv", f"https://arxiv.org/abs/{pre['arxiv']}"))
        venue = S2_VENUE_MAP.get(venue_raw, venue_raw)
        year = int(d.get("year") or pre["year"])
        doi_venue, doi_year = venue_from_doi(doi)
        if doi_venue and doi_venue != venue:
            print(f"note: DOI says {doi_venue} {doi_year}, S2 said "
                  f"'{venue}' {year}; trusting the DOI")
            venue, year = doi_venue, doi_year
        entry = {
            "authors": pre["authors"], "self_idx": pre["self_idx"],
            "title": pre["title"], "year": year,
            "venue": venue, "links": links,
        }
        added.append(entry)
        print(f"S2: + {entry['venue']} {entry['year']}: {pre['title'][:60]}")
    return added


def load_extra(dblp_pubs):
    """Merge hand-maintained entries for papers DBLP has not indexed yet.

    An extra entry is dropped (with a notice) once DBLP lists the same title
    formally, so acceptances can be registered early and cleaned up later.
    Optional "aliases" (e.g. the preprint title of a renamed paper) join the
    dedupe set so the S2 pass cannot re-add the same work under its old name.
    Returns (entries, alias_norms).
    """
    if not os.path.exists(EXTRA_JSON):
        return [], set()
    data = json.load(open(EXTRA_JSON, encoding="utf-8"))
    dblp_norms = {norm_title(p["title"]) for p in dblp_pubs}
    merged, alias_norms = [], set()
    for e in data.get("publications", []):
        if is_known(e["title"], dblp_norms):
            print(f"note: '{e['title'][:50]}...' is now on DBLP; "
                  f"remove it from extra_publications.json")
            continue
        authors = e["authors"]
        merged.append({
            "authors": authors,
            "self_idx": authors.index(SELF_NAME) if SELF_NAME in authors else -1,
            "title": e["title"],
            "year": int(e["year"]),
            "venue": e["venue"],
            "links": [tuple(l) for l in e.get("links", [])],
        })
        for alias in e.get("aliases", []):
            alias_norms.add(norm_title(alias))
    return merged, alias_norms


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_entries(pubs):
    out = []
    year = None
    for p in pubs:
        if p["year"] != year:
            if year is not None:
                out.append("                </ul>")
            year = p["year"]
            out.append(f'                <h2 class="pub-year">{year}</h2>')
            out.append('                <ul class="pub-list">')
        names = [
            f"<strong>{esc(n)}</strong>" if i == p["self_idx"] else esc(n)
            for i, n in enumerate(p["authors"])
        ]
        links = " ".join(
            f'<a href="{esc(u)}" target="_blank" rel="noopener">[{label}]</a>'
            for label, u in p["links"]
        )
        out.append("                    <li>")
        out.append(f'                        <span class="pub-title">{esc(p["title"])}</span>')
        out.append(f'                        <span class="pub-authors">{", ".join(names)}</span>')
        out.append(f'                        <span class="pub-meta"><span class="pub-venue">{esc(p["venue"])} {p["year"]}</span>{" " + links if links else ""}</span>')
        out.append("                    </li>")
    out.append("                </ul>")
    return "\n".join(out)


PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Publications | Jianfu Zhang</title>
    <meta name="description" content="Publications of Jianfu Zhang (Associate Professor, School of Computer Science, Shanghai Jiao Tong University): peer-reviewed papers at AAAI, CVPR, ICCV, NeurIPS, ICLR, ACM Multimedia and more.">
    <link rel="canonical" href="https://matt-sjtu.github.io/publications.html">
    <link rel="icon" type="image/png" href="favicon.png">
    <link rel="apple-touch-icon" href="/apple-touch-icon.png">
    <link rel="stylesheet" href="style.css">
    <script>
        try {
            var savedLang = localStorage.getItem('lang');
            if (savedLang === 'en' || savedLang === 'zh-CN') document.documentElement.lang = savedLang;
        } catch (e) {}
    </script>
</head>
<body>
    <div class="page">
        <header>
            <div class="identity">
                <h1 data-i18n="title">Publications</h1>
                <p class="subtitle" data-i18n="subtitle">Jianfu Zhang · School of Computer Science, Shanghai Jiao Tong University</p>
                <p class="quick-links">
                    <a href="index.html" data-i18n="backHome">Back to Homepage</a>
                </p>
            </div>
            <button id="language-toggle" aria-label="Switch language">中文</button>
        </header>
        <main>
            <section id="publications">
                <p class="pub-note" data-i18n-html="note">Peer-reviewed conference and journal papers, in reverse chronological order. Also available on <a href="https://dblp.org/pid/78/3993-3.html" target="_blank" rel="noopener">DBLP</a> and <a href="https://scholar.google.com/citations?hl=en&user=jSiStc4AAAAJ" target="_blank" rel="noopener">Google Scholar</a>.</p>
__ENTRIES__
            </section>
        </main>
        <footer>
            <p>&copy; Jianfu Zhang | __Matt__ @ School of Computer Science, SJTU</p>
        </footer>
    </div>
    <script>
        const i18n = {
            'zh-CN': {
                title: '发表论文',
                subtitle: '张健夫 · 上海交通大学 计算机学院',
                backHome: '返回主页',
                note: '以下为经同行评审的会议与期刊论文，按年份倒序。完整列表亦可见 <a href="https://dblp.org/pid/78/3993-3.html" target="_blank" rel="noopener">DBLP</a> 与 <a href="https://scholar.google.com/citations?hl=en&user=jSiStc4AAAAJ" target="_blank" rel="noopener">Google Scholar</a>。',
                toggleLabel: 'EN',
                docTitle: '发表论文 | 张健夫'
            },
            'en': {
                title: 'Publications',
                subtitle: 'Jianfu Zhang · School of Computer Science, Shanghai Jiao Tong University',
                backHome: 'Back to Homepage',
                note: 'Peer-reviewed conference and journal papers, in reverse chronological order. Also available on <a href="https://dblp.org/pid/78/3993-3.html" target="_blank" rel="noopener">DBLP</a> and <a href="https://scholar.google.com/citations?hl=en&user=jSiStc4AAAAJ" target="_blank" rel="noopener">Google Scholar</a>.',
                toggleLabel: '中文',
                docTitle: 'Publications | Jianfu Zhang'
            }
        };

        function applyLanguage(lang) {
            const dict = i18n[lang];
            document.documentElement.lang = lang;
            document.querySelectorAll('[data-i18n]').forEach(el => {
                el.textContent = dict[el.dataset.i18n];
            });
            document.querySelectorAll('[data-i18n-html]').forEach(el => {
                el.innerHTML = dict[el.dataset.i18nHtml];
            });
            document.title = dict.docTitle;
            document.getElementById('language-toggle').textContent = dict.toggleLabel;
            try { localStorage.setItem('lang', lang); } catch (e) {}
        }

        document.getElementById('language-toggle').addEventListener('click', function () {
            applyLanguage(document.documentElement.lang === 'zh-CN' ? 'en' : 'zh-CN');
        });

        let initialLang = 'en';
        try {
            const saved = localStorage.getItem('lang');
            if (saved && i18n[saved]) initialLang = saved;
        } catch (e) {}
        applyLanguage(initialLang);
    </script>
</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--xml", help="local DBLP XML file (default: fetch from dblp.org)")
    ap.add_argument("--skip-s2", action="store_true",
                    help="skip the Semantic Scholar published-preprint check")
    args = ap.parse_args()

    if args.xml:
        pubs, preprints = parse_pubs(open(args.xml, encoding="utf-8").read())
    else:
        print(f"fetching {DBLP_URL} ...")
        req = urllib.request.Request(DBLP_URL, headers={"User-Agent": USER_AGENT})
        try:
            # Anubis serves its challenge as 200 + HTML, which fails XML parsing.
            pubs, preprints = parse_pubs(fetch_with_retry(req, attempts=2).decode("utf-8"))
        except (urllib.error.URLError, RuntimeError, ET.ParseError) as ex:
            print(f"warning: DBLP XML export unavailable ({ex}); using SPARQL")
            pubs, preprints = sparql_pubs()
    if not pubs:
        sys.exit("no formal publications parsed — aborting")
    extra, alias_norms = load_extra(pubs)
    pubs += extra
    if not args.skip_s2:
        known = {norm_title(p["title"]) for p in pubs} | alias_norms
        try:
            pubs += augment_from_s2(preprints, known)
        except Exception as ex:  # S2 outage must not break the build
            print(f"warning: Semantic Scholar augmentation failed: {ex}")
    pubs.sort(key=lambda p: (-p["year"], p["venue"], p["title"]))
    html = PAGE_TEMPLATE.replace("__ENTRIES__", render_entries(pubs))
    out = os.path.join(REPO, "publications.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    years = sorted({p["year"] for p in pubs}, reverse=True)
    print(f"wrote {out}: {len(pubs)} publications, {years[-1]}-{years[0]}")


if __name__ == "__main__":
    main()
