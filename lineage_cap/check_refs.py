"""Existence-check every bibliography entry against Crossref, arXiv or its URL.

Usage: python -m lineage_cap.check_refs references.bib [document.qmd ...]

Entries cited by the listed documents are marked CITED. An entry fails when its
DOI or arXiv id does not resolve, its title does not match the record, or (for
DOI entries) its year, volume, pages or author surnames disagree. Entries with
no identifier are matched by Crossref title search. Set CROSSREF_MAILTO to use
Crossref's polite pool. This checks that references exist; it does not check
that they support the claims they are cited for.
"""

import difflib
import json
import os
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

MAILTO = os.environ.get("CROSSREF_MAILTO")
HEADERS = {"User-Agent": "lineage-cap-check-refs/1.0" + (f" (mailto:{MAILTO})" if MAILTO else "")}
ATOM = {"a": "http://www.w3.org/2005/Atom"}
TITLE_MATCH = 0.85
LETTERS = str.maketrans({"ð": "d", "Ð": "d", "đ": "d", "Đ": "d", "þ": "th", "ø": "o", "Ø": "o", "ł": "l", "Ł": "l", "ß": "ss", "æ": "ae"})


def fetch(url):
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def words(text):
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = re.sub(r"\\['`^\"~.=uvHc]\{?(\w)\}?", r"\1", text)
    text = unicodedata.normalize("NFKD", text.replace("\\", "").replace("{", "").replace("}", ""))
    text = "".join(c for c in text if not unicodedata.combining(c)).translate(LETTERS)
    return re.sub(r"[^a-z0-9 ]", " ", text.lower()).split()


def title_matches(ours, theirs):
    a, b = " ".join(words(ours)), " ".join(words(theirs))
    # Some records store only the main title, without the subtitle.
    return difflib.SequenceMatcher(None, a, b).ratio() >= TITLE_MATCH or (len(b) > 15 and a.startswith(b))


def surnames(author_field):
    names = []
    for person in author_field.split(" and "):
        person = person.strip()
        if person == "others":
            break
        names.append(" ".join(words(person.split(",")[0] if "," in person else person.split()[-1])))
    return names


def forenames(author_field):
    names = []
    for person in author_field.split(" and "):
        person = person.strip()
        if person == "others":
            break
        given = person.split(",", 1)[1] if "," in person else " ".join(person.split()[:-1])
        names.append(words(given)[0] if words(given) else "")
    return names


def same_forename(a, b):
    """Full names must agree; an initial only has to agree with the first letter."""
    if not a or not b:
        return True
    return a == b if len(a) > 1 and len(b) > 1 else a[0] == b[0]


def pages(value):
    return re.sub(r"[^0-9a-z]+", "-", (value or "").lower()).strip("-")


def parse_bib(text):
    entries = {}
    for match in re.finditer(r"^@(\w+)\{([^,]+),(.*?)^\}", text, re.S | re.M):
        fields = re.findall(r"(\w+)\s*=\s*\{((?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*)\}", match.group(3))
        entries[match.group(2).strip()] = {k.lower(): v.strip() for k, v in fields}
    return entries


def check_doi(entry):
    record = json.loads(fetch("https://api.crossref.org/works/" + urllib.parse.quote(entry["doi"])))["message"]
    title = (record.get("title") or [""])[0]
    problems = [] if title_matches(entry.get("title", ""), title) else [f"title is '{title}'"]
    year = (record.get("issued", {}).get("date-parts") or [[None]])[0][0]
    if entry.get("year") and year and abs(int(entry["year"]) - year) > 1:
        problems.append(f"year is {year}")
    if entry.get("volume") and record.get("volume") and entry["volume"] != record["volume"]:
        problems.append(f"volume is {record['volume']}")
    their_pages = record.get("page") or record.get("article-number")
    if entry.get("pages") and their_pages and pages(entry["pages"]) != pages(their_pages):
        problems.append(f"pages are {their_pages}")
    theirs = [" ".join(words(a.get("family") or a.get("name", ""))) for a in record.get("author", [])]
    ours = surnames(entry.get("author", ""))
    if entry.get("author", "").startswith("{"):
        theirs = []  # corporate author, e.g. {Planck Collaboration}
    if theirs and ours and ours != theirs[: len(ours)]:
        problems.append(f"authors are {'; '.join(theirs[:8])}")
    their_given = [(words(a.get("given", "")) or [""])[0] for a in record.get("author", [])]
    for name, mine, other in zip(ours, forenames(entry.get("author", "")), their_given):
        if theirs and not same_forename(mine, other):
            problems.append(f"{name} forename is {other}, bib has {mine}")
    if theirs and ours and "others" not in entry.get("author", "") and len(ours) != len(theirs):
        problems.append(f"{len(theirs)} authors, bib lists {len(ours)}")
    return problems


def check_arxiv(entry):
    feed = ET.fromstring(fetch("http://export.arxiv.org/api/query?id_list=" + entry["eprint"]))
    time.sleep(3)  # arXiv asks for one request every three seconds
    record = feed.find("a:entry", ATOM)
    if record is None or record.find("a:title", ATOM) is None:
        return ["arXiv id not found"]
    title = re.sub(r"\s+", " ", record.find("a:title", ATOM).text)
    problems = [] if title_matches(entry.get("title", ""), title) else [f"arXiv title is '{title}'"]
    first = record.find("a:author/a:name", ATOM).text
    ours = surnames(entry.get("author", ""))
    if ours and ours[0] not in " ".join(words(first)):
        problems.append(f"arXiv first author is {first}")
    return problems


def check_search(entry):
    query = urllib.parse.urlencode({"query.bibliographic": entry.get("title", "") + " " + entry.get("author", ""), "rows": 3})
    items = json.loads(fetch("https://api.crossref.org/works?" + query))["message"]["items"]
    if any(title_matches(entry.get("title", ""), (i.get("title") or [""])[0]) for i in items):
        return []
    return ["no Crossref record with this title"]


def check(entry):
    results = []
    for kind, field, checker in (("doi", "doi", check_doi), ("arxiv", "eprint", check_arxiv)):
        if field in entry:
            try:
                results.append((kind, checker(entry)))
            except Exception as error:  # noqa: BLE001 - report every lookup failure
                results.append((kind, [f"lookup failed: {error}"]))
    if "url" in entry and "doi" not in entry:
        try:
            fetch(entry["url"])
            results.append(("url", []))
        except Exception as error:  # noqa: BLE001
            results.append(("url", [f"unreachable: {error}"]))
    if not results:
        try:
            results.append(("search", check_search(entry)))
        except Exception as error:  # noqa: BLE001
            results.append(("search", [f"lookup failed: {error}"]))
    return results


def main(argv):
    if not argv:
        sys.exit(__doc__)
    entries = parse_bib(open(argv[0]).read())
    cited = set()
    for path in argv[1:]:
        cited |= set(re.findall(r"(?<![\w.])@([A-Za-z0-9_:-]+)", open(path).read()))
    failures = 0
    for key, entry in entries.items():
        tag = "CITED" if key in cited else "     "
        for kind, problems in check(entry):
            status = "FAIL" if problems else "ok"
            failures += bool(problems)
            print(f"{status:4} {tag} {key:28} {kind:6} {'; '.join(problems)}".rstrip(), flush=True)
    missing = sorted(k for k in cited if k not in entries and not k.startswith(("fig-", "tbl-", "sec-", "eq-")))
    for key in missing:
        print(f"FAIL CITED {key:28} cited but not in {argv[0]}")
    print(f"\n{len(entries)} entries, {failures + len(missing)} problems")
    return 1 if failures or missing else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
