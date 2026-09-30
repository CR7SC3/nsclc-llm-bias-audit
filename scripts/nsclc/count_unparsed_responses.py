"""Count responses the rule-based parser leaves as "unknown", per model and per
variant, and tag which regimen each missed response names.

Supports the Methods sentence and eMethods "Unclassified responses" paragraph
(Paper 1, NSCLC). Excludes the dropped elderly_patient_75 variant. A
variant-reference pair is usable only when both responses parse, matching the
pairwise exclusion in scripts/nsclc/correct_analysis.py.

Run:  venv/bin/python scripts/nsclc/count_unparsed_responses.py
"""
from pathlib import Path
import collections
import json
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.analyze.response_parser import ResponseParser

REFERENCE = "no_demographics"
DROPPED = {"elderly_patient_75"}
MODELS = {
    "gemini-2.5-flash": "results/baseline/v2_genie_bpc_nsclc_results.json",
    "deepseek-chat":    "results/baseline/v2_genie_bpc_nsclc_deepseek-chat_results.json",
    "llama-3.3-70b":    "results/baseline/v2_genie_bpc_nsclc_meta-llama-Llama-3.3-70B-Instruct-Turbo_results.json",
    "llama-3.1-8b":     "results/baseline/v2_genie_bpc_nsclc_openrouter-meta-llama-llama-3.1-8b-instruct_results.json",
    "gpt-4o":           "results/baseline/v2_genie_bpc_nsclc_gpt-4o_results.json",
    "gpt-4o-mini":      "results/baseline/v2_genie_bpc_nsclc_gpt-4o-mini_results.json",
}

# Regimen tags for missed responses, checked in order on the opening 1,200 characters.
ICI = r"pembrolizumab|atezolizumab|nivolumab|durvalumab|cemiplimab|ipilimumab|tremelimumab|keytruda|tecentriq|opdivo"
PLAT = r"carboplatin|cisplatin"
TARGETED = (r"osimertinib|alectinib|lorlatinib|brigatinib|crizotinib|entrectinib|selpercatinib|pralsetinib|"
            r"capmatinib|tepotinib|dabrafenib|sotorasib|adagrasib|erlotinib|gefitinib|afatinib|larotrectinib|"
            r"trastuzumab|tucatinib|amivantamab|mobocertinib")
TAGS = [
    ("checkpoint inhibitor + platinum", lambda h: re.search(ICI, h) and re.search(PLAT, h)),
    ("targeted or HER2-directed agent", lambda h: re.search(TARGETED, h)),
    ("platinum chemotherapy", lambda h: re.search(PLAT, h)),
    ("checkpoint inhibitor alone", lambda h: re.search(ICI, h)),
    ("radiation", lambda h: re.search(r"radiation|radiotherapy|sbrt|sabr", h)),
    ("surgery", lambda h: re.search(r"lobectomy|resection|segmentectomy|surgery", h)),
]


def tag(text: str) -> str:
    head = text[:1200].lower()
    return next((name for name, hit in TAGS if hit(head)), "no regimen named")


def main() -> None:
    parser = ResponseParser()
    tot = collections.Counter()
    for model, path in MODELS.items():
        raw = json.loads(Path(path).read_text())
        n = unk = pairs = usable = 0
        by_var_n, by_var_unk = collections.Counter(), collections.Counter()
        tags = collections.Counter()
        for variants in raw.values():
            cats = {}
            for vk, vv in variants.items():
                if vk in DROPPED:
                    continue
                text = vv.get("response_text", "") or ""
                cats[vk] = parser.parse(text).category if text.strip() else "unknown"
                n += 1
                by_var_n[vk] += 1
                if cats[vk] == "unknown":
                    unk += 1
                    by_var_unk[vk] += 1
                    tags[tag(text)] += 1
            ref = cats.get(REFERENCE, "unknown")
            for vk, c in cats.items():
                if vk == REFERENCE:
                    continue
                pairs += 1
                usable += c != "unknown" and ref != "unknown"
        rates = {v: 100 * by_var_unk[v] / by_var_n[v] for v in by_var_n}
        others = [r for v, r in rates.items() if v != REFERENCE]
        print(f"{model:17} unknown {unk:5}/{n} ({100*unk/n:.2f}%)  usable pairs {100*usable/pairs:.1f}%  "
              f"by-variant {min(others):.1f}-{max(others):.1f}% (reference {rates[REFERENCE]:.1f}%)")
        print(f"{'':17} tags: {dict(tags.most_common())}")
        tot.update(n=n, unk=unk, pairs=pairs, usable=usable)
        tot.update({f"tag:{k}": v for k, v in tags.items()})
    print(f"\nTOTAL unknown {tot['unk']}/{tot['n']} ({100*tot['unk']/tot['n']:.2f}%)  "
          f"usable pairs {tot['usable']}/{tot['pairs']} ({100*tot['usable']/tot['pairs']:.1f}%)")
    print({k[4:]: v for k, v in tot.items() if k.startswith("tag:")})


if __name__ == "__main__":
    main()
