"""Harvest real NSCLC case-report notes from PubMed Central (open-access subset)
for the real-prose cross-validation arm.

Pipeline (reproducible via NCBI E-utilities — no session/MCP dependency):
  1. esearch PMC OA subset for NSCLC case reports (English).
  2. efetch each as JATS XML.
  3. Extract the "Case presentation / Case report" <sec> narrative.
  4. Neutralize the manipulated demographics (sex words/pronouns) so the note is
     demographics-neutral; the variant injector prepends the demographic tag exactly
     as for synthetic notes. Age + clinical content are kept.
  5. Emit data/processed/pmc_nsclc_with_notes.json in the pipeline's schema
     (case_id, clean_note, clinical_profile, source) + a citation manifest (PMCID/DOI).

The same variant injector + ResponseParser + soft_bias detector then run UNCHANGED;
only the note source differs. Stigma cross-val needs no NCCN labels.

Usage
-----
    python scripts/nsclc/build_pmc_notes.py --n 40
"""
from __future__ import annotations

import argparse
import json
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
OUT = Path("data/processed/pmc_nsclc_with_notes.json")
MANIFEST = Path("data/processed/pmc_nsclc_manifest.json")


def _get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "EquityGUIDE-research/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def _esearch(term: str, retmax: int) -> list[str]:
    q = urllib.parse.urlencode({"db": "pmc", "term": term, "retmax": retmax, "retmode": "json"})
    data = json.loads(_get(f"{EUTILS}/esearch.fcgi?{q}"))
    return data["esearchresult"].get("idlist", [])


def _efetch_pmc(pmcid: str) -> bytes:
    q = urllib.parse.urlencode({"db": "pmc", "id": pmcid, "retmode": "xml"})
    return _get(f"{EUTILS}/efetch.fcgi?{q}")


def _text(el) -> str:
    return re.sub(r"\s+", " ", "".join(el.itertext())).strip()


def _extract_case_section(xml_bytes: bytes):
    """Return (case_text, doi, license_short) or (None, ...) if no usable case section."""
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return None, None, None
    # DOI
    doi = None
    for aid in root.iter("article-id"):
        if aid.get("pub-id-type") == "doi":
            doi = (aid.text or "").strip()
    # license (open-access detection)
    lic = None
    for lcs in root.iter("license"):
        lic = (lcs.get("{http://www.w3.org/1999/xlink}href") or _text(lcs))[:80]
    # find a <sec> whose title looks like a case section
    case_paras = []
    for sec in root.iter("sec"):
        title_el = sec.find("title")
        title = (_text(title_el).lower() if title_el is not None else "")
        if re.search(r"\bcase (presentation|report|description|summary)\b|^case\b|patient information", title):
            for p in sec.iter("p"):
                t = _text(p)
                # skip figure/table caption text that sometimes lands in <p>
                if t and len(t) > 40 and not re.match(r"^(fig(ure)?s?\b|table\b)", t, re.I):
                    case_paras.append(t)
    if not case_paras:
        return None, doi, lic
    return "\n\n".join(case_paras), doi, lic


# Neutralize the demographic variables the experiment manipulates (sex). Age + clinical
# content stay. Race/insurance are rarely present in case reports; strip if seen.
_SEX = [
    (r"\b(\d{1,3})[- ]year[- ]old (?:fe)?male\b", r"\1-year-old patient"),
    (r"\bwoman\b", "patient"), (r"\bman\b", "patient"),
    (r"\bfemale\b", "patient"), (r"\bmale\b", "patient"),
    (r"\bshe\b", "the patient"), (r"\bhe\b", "the patient"),
    (r"\bher\b", "their"), (r"\bhis\b", "their"), (r"\bhers\b", "theirs"),
]


def _neutralize(text: str) -> str:
    for pat, rep in _SEX:
        text = re.sub(pat, rep, text, flags=re.IGNORECASE)
    return text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=40, help="target number of usable notes")
    ap.add_argument("--pool", type=int, default=160, help="candidate PMCIDs to scan")
    args = ap.parse_args()

    term = ('"non-small cell lung"[Title/Abstract] AND case report[Title/Abstract] '
            'AND open access[filter] AND english[Language]')
    print("Searching PMC OA subset…")
    ids = _esearch(term, args.pool)
    print(f"  {len(ids)} candidate OA articles")

    notes, manifest = [], []
    for pmcid in ids:
        if len(notes) >= args.n:
            break
        try:
            xml = _efetch_pmc(pmcid)
            case, doi, lic = _extract_case_section(xml)
        except Exception as e:
            print(f"  PMC{pmcid}: fetch/parse error ({type(e).__name__})")
            time.sleep(0.4); continue
        if not case or len(case) < 300:
            time.sleep(0.34); continue
        note = _neutralize(case)
        cid = f"pmc_PMC{pmcid}"
        notes.append({
            "case_id": cid,
            "clean_note": note,
            "clinical_profile": {"cancer_type": "nsclc"},  # narrative-derived; no structured fields
            "source": "pmc_oa_case_report",
            "pmcid": f"PMC{pmcid}", "doi": doi, "license": lic,
        })
        manifest.append({"case_id": cid, "pmcid": f"PMC{pmcid}", "doi": doi, "license": lic,
                         "n_chars": len(note)})
        print(f"  + PMC{pmcid}  ({len(note)} chars)  doi={doi}")
        time.sleep(0.34)  # NCBI <3 req/s

    OUT.write_text(json.dumps(notes, indent=1), encoding="utf-8")
    MANIFEST.write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    print(f"\nWrote {len(notes)} real PMC NSCLC notes -> {OUT}")
    print(f"Citation manifest (PMCID/DOI/license) -> {MANIFEST}")
    if notes:
        print("\n--- sample neutralized case note (first 600 chars) ---")
        print(notes[0]["clean_note"][:600])


if __name__ == "__main__":
    main()
