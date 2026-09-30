"""Measure how many responses each parser fix in commit 0a5cf68 reclassified.

Supports the eMethods "Response parser and corrections" paragraph (Paper 1,
NSCLC): 4.27% of responses for the chemoimmunotherapy fix and 3.17% for the
chemoradiation fix. Excludes the dropped elderly_patient_75 variant.

Three parser versions are compared on all 182,352 analyzed responses:
  old  - src/analyze/response_parser.py at 0a5cf68^ (read with git show)
  fix1 - old, with the chemoimmunotherapy / immunotherapy-monotherapy / dual-IO
         drug patterns bounded to 1 sentence ([^.]*?) instead of .* under DOTALL
  new  - the current parser (fix1 plus the chemoradiation fix: modality-qualified
         "regimen:" tags skipped and an opening chemoradiation statement checked
         first)
Fix 1 is measured as old vs fix1 and fix 2 as fix1 vs new, the order in which
the defects were found. Fix 2 is also broken down by label (reference vs the 28
labels, pooled and per model), which supports the eMethods statement that this
defect did not affect all labels equally.

Run:  venv/bin/python scripts/nsclc/measure_parser_fix_impact.py
"""
from pathlib import Path
import collections
import importlib.util
import json
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from src.analyze.response_parser import ResponseParser
from scripts.nsclc.count_unparsed_responses import MODELS, DROPPED

REFERENCE = "no_demographics"
OLD_REV = "0a5cf68^"
FIX1_SUBS = [
    (r'r"carboplatin.*pembrolizumab"', r'r"carboplatin[^.]*?pembrolizumab"'),
    (r'r"cisplatin.*pembrolizumab"', r'r"cisplatin[^.]*?pembrolizumab"'),
    (r'r"carbo.*pem.*pembro"', r'r"carbo[^.]*?pem[^.]*?pembro"'),
    (r'r"platinum.*(?:pembrolizumab|atezolizumab|nivolumab)"',
     r'r"platinum[^.]*?(?:pembrolizumab|atezolizumab|nivolumab)"'),
    (r'r"(?:pembrolizumab|atezolizumab|nivolumab).*platinum"',
     r'r"(?:pembrolizumab|atezolizumab|nivolumab)[^.]*?platinum"'),
    (r'r"(?!.*(?:carboplatin|cisplatin|paclitaxel|pemetrexed))"',
     r'r"(?![^.]*(?:carboplatin|cisplatin|paclitaxel|pemetrexed))"'),
    (r'(?!.*(?:carboplatin|cisplatin|chemo))', r'(?![^.]*(?:carboplatin|cisplatin|chemo))'),
]


def _load(name: str, source: str):
    path = Path(tempfile.mkdtemp()) / f"{name}.py"
    path.write_text(source)
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod.ResponseParser()


def main():
    old_src = subprocess.run(["git", "show", f"{OLD_REV}:src/analyze/response_parser.py"],
                             cwd=ROOT, capture_output=True, text=True, check=True).stdout
    fix1_src = old_src
    for a, b in FIX1_SUBS:
        assert a in fix1_src, a
        fix1_src = fix1_src.replace(a, b)
    old, fix1, new = _load("parser_old", old_src), _load("parser_fix1", fix1_src), ResponseParser()

    n = d1 = d2 = 0
    into = collections.Counter()
    # fix-2 reclassification by label: [changed, total], pooled and per model
    by_label = collections.defaultdict(lambda: [0, 0])
    by_model_label = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
    for model, path in MODELS.items():
        raw = json.loads((ROOT / path).read_text())
        mn = m1 = m2 = 0
        for res in raw.values():
            for v, r in res.items():
                if v in DROPPED or not isinstance(r, dict):
                    continue
                t = r.get("response_text") or ""
                a, b, c = old.parse(t).category, fix1.parse(t).category, new.parse(t).category
                mn += 1; m1 += a != b; m2 += b != c
                if b != c:
                    into[c] += 1
                for cell in (by_label[v], by_model_label[model][v]):
                    cell[0] += b != c; cell[1] += 1
        n += mn; d1 += m1; d2 += m2
        print(f"{model:18s} fix1 {m1:>5,} ({100 * m1 / mn:.2f}%)  fix2 {m2:>5,} ({100 * m2 / mn:.2f}%)",
              flush=True)
    print(f"TOTAL {n:,} responses  fix1 {d1:,} ({100 * d1 / n:.2f}%)  fix2 {d2:,} ({100 * d2 / n:.2f}%)")
    print(f"fix2 changes into chemoradiation: {100 * into['chemoradiation'] / d2:.1f}%")

    # Was fix 2 differential by label? Reference vs the 28 labels.
    print("\nfix2 reclassification rate by label (reference vs range across the 28 labels):")
    for name, cells in [("all models", by_label)] + list(by_model_label.items()):
        rate = {v: 100 * k / t for v, (k, t) in cells.items()}
        labels = [rate[v] for v in rate if v != REFERENCE]
        print(f"  {name:18s} reference {rate[REFERENCE]:.2f}%  labels {min(labels):.2f}-{max(labels):.2f}%  "
              f"white_male_private {rate['white_male_private']:.2f}%  unhoused {rate['unhoused_patient']:.2f}%")


if __name__ == "__main__":
    main()
