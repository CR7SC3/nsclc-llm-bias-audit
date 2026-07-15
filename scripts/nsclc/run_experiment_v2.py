"""EquityGUIDE v2 experiment runner — clean label demographic injection.

Identical pipeline to run_experiment.py except:
  - Uses variant_injector_v2 (22 Omar-aligned label-only groups)
  - Saves checkpoints under results/baseline/ with 'v2_' prefix
  - Applies variants at runtime from processed notes (no reprocessing needed)

Variant tiers
─────────────
  A  Replicate v1 (cross-experiment comparison)      6 groups
  B  Race only — Omar et al. style                   5 groups
  C  SES only — housing / income                     3 groups
  D  Insurance only — EquityGUIDE contribution       2 groups
  E  Isolation — race vs insurance disentanglement   3 groups
  F  Gender / identity — LGBTQIA+                    3 groups
  ─────────────────────────────────────────────────────────────
  Total                                             22 groups

Usage
-----
    # Structured notes (default model = Gemini)
    python scripts/nsclc/run_experiment_v2.py --subset synthetic_structured

    # GPT-4o on unstructured
    python scripts/nsclc/run_experiment_v2.py --subset synthetic_unstructured --model gpt-4o

    # Resume an interrupted run
    python scripts/nsclc/run_experiment_v2.py --subset synthetic_structured --model gpt-4o
    # (automatically resumes from checkpoint)
"""

from __future__ import annotations

import argparse
import atexit
import json
import logging
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tqdm import tqdm

from src.models.factory import create_model, SUPPORTED_MODELS
from src.generate.variant_injector_v2 import create_all_variants_v2, ALL_VARIANTS_V2
from src.generate.natural_embed import create_all_variants_natural
from src.generate.nccn_labels import load_nccn_index, nccn_fields
from prompts.evaluation.prompt_templates import build_prompt

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

_RESULTS_DIR = Path("results")
_RESULTS_DIR.mkdir(exist_ok=True)


def _atomic_dump(obj, path: Path) -> None:
    """Write JSON to *path* atomically: dump to a temp file in the same dir, then
    os.replace(). A crash mid-write can never leave a truncated checkpoint."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def _acquire_lock(checkpoint_path: Path) -> Path:
    """Prevent two processes writing the same checkpoint (silent data loss /
    double-spend). Creates an exclusive lock file; errors out if one exists and
    its PID is still alive. Returns the lock path (released atexit)."""
    lock_path = checkpoint_path.with_suffix(checkpoint_path.suffix + ".lock")
    if lock_path.exists():
        try:
            old_pid = int(lock_path.read_text().strip())
            os.kill(old_pid, 0)  # raises if pid is dead
            raise SystemExit(
                f"ERROR: another run already owns {checkpoint_path.name} "
                f"(PID {old_pid}). Refusing to start a second writer. "
                f"If that process is dead, remove {lock_path.name}."
            )
        except (ValueError, ProcessLookupError):
            pass  # stale lock from a dead/garbled process — reclaim it
    lock_path.write_text(str(os.getpid()))
    atexit.register(lambda: lock_path.exists() and lock_path.unlink())
    return lock_path

_PROCESSED_PATHS = {
    "synthetic_structured":   "data/processed/cancerguide_synthetic_structured_processed.json",
    "synthetic_unstructured": "data/processed/cancerguide_synthetic_unstructured_processed.json",
    # GENIE BPC NSCLC: real-derived structured profiles -> LLM-generated free-text notes.
    # Routes to unstructured injection (subset != "synthetic_structured").
    "genie_bpc_nsclc":        "data/processed/genie_bpc_nsclc_with_notes.json",
    "genie_bpc_nsclc_pilot50": "data/processed/genie_bpc_nsclc_pilot50_with_notes.json",
    # Circularity control: deterministic-template notes (no LLM generator).
    # Same case_ids/labels; routes to unstructured injection. See generate_template_notes.py.
    "genie_bpc_nsclc_templates":    "data/processed/genie_bpc_nsclc_templates_with_notes.json",
    "genie_bpc_nsclc_templates100": "data/processed/genie_bpc_nsclc_templates100_with_notes.json",
    # Shared stratified frame for credited extra arms (GPT-4o/Claude) — Gemini notes,
    # same case_ids as the full arms so head-to-head analysis is paired.
    "genie_bpc_nsclc_n300":         "data/processed/genie_bpc_nsclc_n300_with_notes.json",
    # Natural-prose embedding control (M4 salience artifact): same case_ids as the
    # full arm, demographics woven into narrative instead of a bracketed tag.
    "genie_bpc_nsclc_natural150":   "data/processed/genie_bpc_nsclc_natural150_with_notes.json",
    # Real-prose cross-validation: open-access PMC NSCLC case-report notes (no NCCN labels).
    "pmc_nsclc":                    "data/processed/pmc_nsclc_with_notes.json",
    # Paper 2 (BRCA + PANC prognosis-gradient study). Same runtime variant injection.
    # BRCA subsets are female-only at load (see _FEMALE_ONLY_SUBSETS).
    "genie_bpc_brca":               "data/processed/genie_bpc_brca_with_notes.json",
    "genie_bpc_brca_pilot50":       "data/processed/genie_bpc_brca_pilot50_with_notes.json",
    "genie_bpc_panc":               "data/processed/genie_bpc_panc_with_notes.json",
    "genie_bpc_panc_pilot50":       "data/processed/genie_bpc_panc_pilot50_with_notes.json",
    # Paper 2 circularity control (C2'): deterministic-template notes (no LLM generator),
    # ported per-cohort from Paper 1's NSCLC C2. Same case_ids/labels; routes to
    # unstructured injection. See scripts/brca_panc/generate_template_notes_brca_panc.py.
    "genie_bpc_brca_templates100":  "data/processed/genie_bpc_brca_templates100_with_notes.json",
    "genie_bpc_panc_templates100":  "data/processed/genie_bpc_panc_templates100_with_notes.json",
}

# BRCA analysis cohort excludes male + unknown-sex cases: male breast cancer is a rare
# distinct clinical entity, so injecting demographic variants there would measure clinical
# differentiation, not demographic bias (PREREGISTRATION_PAPER2 §2, council req #7).
_FEMALE_ONLY_SUBSETS = {"genie_bpc_brca", "genie_bpc_brca_pilot50", "genie_bpc_brca_templates100"}


def _load_processed(subset: str) -> list[dict]:
    path = Path(_PROCESSED_PATHS[subset])
    if not path.exists():
        raise FileNotFoundError(
            f"Processed cases not found at {path}. "
            "Run `python -m src.generate.load_cases` first."
        )
    with open(path, encoding="utf-8") as fh:
        cases = json.load(fh)

    if subset in _FEMALE_ONLY_SUBSETS:
        kept = [c for c in cases if (c.get("demographics") or {}).get("sex") == "Female"]
        n_excl = len(cases) - len(kept)
        if n_excl:
            print(f"BRCA cohort: excluded {n_excl} male/unknown-sex case(s) "
                  f"-> {len(kept)} female cases (council req #7).")
        cases = kept

    return cases


def run_experiment_v2(
    subset: str = "synthetic_structured",
    model_name: str = "gemini-2.5-flash",
    n_samples: int = 1,
    max_workers: int = 1,
    temperature: float = 0.0,
    prompt_strategy: str = "baseline",
) -> None:
    n_variants = len(ALL_VARIANTS_V2)
    # Non-baseline prompt strategies write to a distinct checkpoint so the
    # baseline run is never overwritten, and tag results with the strategy name.
    strategy_tag = "baseline_v2" if prompt_strategy == "baseline" else prompt_strategy
    prefix_suffix = "" if prompt_strategy == "baseline" else f"_{prompt_strategy}"

    print(f"\n{'='*70}")
    print(f"EquityGUIDE v2 — Clean Label Experiment")
    print(f"Subset    : {subset}")
    print(f"Model     : {model_name}")
    print(f"Variants  : {n_variants} (Omar-aligned label-only groups)")
    print(f"Samples   : {n_samples} per variant @ temperature {temperature}")
    print(f"Workers   : {max_workers} concurrent request(s)")
    print(f"{'='*70}\n")

    # Load processed (demographics-stripped) notes
    cases = _load_processed(subset)
    label_index = {c["case_id"]: c.get("label", "") for c in cases}

    # Attach validated NCCN ground-truth labels (primary + acceptable) so the
    # adherence metric scores natively. Empty/absent for non-GENIE subsets.
    nccn_index = load_nccn_index()
    n_labeled = sum(1 for c in cases if c["case_id"] in nccn_index)
    if n_labeled:
        print(f"NCCN labels: {n_labeled}/{len(cases)} cases matched ground-truth file")

    # Checkpoint path
    model_slug = model_name.replace("/", "-")
    if model_name == "gemini-2.5-flash":
        file_prefix = f"v2_{subset}{prefix_suffix}"
    else:
        file_prefix = f"v2_{subset}_{model_slug}{prefix_suffix}"

    strategy_dir = _RESULTS_DIR / "baseline"
    strategy_dir.mkdir(exist_ok=True)
    checkpoint_path = strategy_dir / f"{file_prefix}_checkpoint.json"
    _acquire_lock(checkpoint_path)

    if checkpoint_path.exists():
        with open(checkpoint_path, encoding="utf-8") as fh:
            results = json.load(fh)
        # Treat a case as done only if EVERY variant succeeded. A case that
        # partially failed (e.g. balance ran out mid-run) is dropped so it is
        # cleanly retried on resume — this is what makes "top up and continue" work.
        completed = {
            cid for cid, cres in results.items()
            if cres and not any("error" in v for v in cres.values())
        }
        incomplete = len(results) - len(completed)
        results = {cid: results[cid] for cid in completed}
        msg = f"Resuming from checkpoint: {len(completed)} cases complete."
        if incomplete:
            msg += f" Dropping {incomplete} partial/failed case(s) to retry."
        print(msg)
    else:
        results = {}
        completed = set()

    remaining = [c for c in cases if c["case_id"] not in completed]
    total_calls = len(cases) * n_variants * n_samples
    est_min = len(remaining) * n_variants * n_samples * 1.0 / 60 / max(max_workers, 1)

    print(f"Cases     : {len(cases)} total / {len(remaining)} remaining")
    print(f"Variants  : {n_variants} per case = {total_calls} total calls")
    print(f"Est. time : ~{est_min:.0f} minutes")

    from src.models.factory import _GROQ_MODELS
    is_groq = model_name in _GROQ_MODELS

    if model_name == "gpt-4o":
        est_cost = len(remaining) * n_variants * n_samples * (1500 * 2.50 + 600 * 10.0) / 1_000_000
        print(f"Est. cost : ~${est_cost:.2f} (GPT-4o @ avg 1500 input + 600 output tokens)")
    elif model_name in ("gpt-4o-mini", "gemini-2.5-flash"):
        est_cost = len(remaining) * n_variants * n_samples * 0.0002
        print(f"Est. cost : ~${est_cost:.2f}")
    elif is_groq:
        print("Est. cost : free (Groq free tier)")
    print()

    # Groq free tier: 6,000 TPM. Avg call ~1,174 tokens → max ~5.1 calls/min → 12s min spacing.
    # Also hit 1,000 RPD cap; runner resumes from checkpoint each day.
    sleep = 12.0 if is_groq else 1.0
    model = create_model(model_name, temperature=temperature, inter_call_sleep=sleep, max_retries=5, retry_wait=30.0)

    failed = []
    start = time.time()

    pbar = tqdm(remaining, total=len(remaining), desc="v2 experiment", unit="case")

    for case in pbar:
        case_id = case["case_id"]
        base_note = case["clean_note"]
        pbar.set_postfix({"case": case_id[-20:]})

        # Generate all v2 variants for this note. Natural-embedding subsets weave
        # demographics into the prose (salience-artifact control) instead of the
        # bracketed [PATIENT DEMOGRAPHICS] tag.
        if subset.startswith("genie_bpc_nsclc_natural"):
            variants = create_all_variants_natural(base_note)
        else:
            variants = create_all_variants_v2(base_note, subset)

        case_results: dict = {}

        # Build every call this case needs: 30 variants x n_samples repeats,
        # each at temperature 1.0 with a distinct id so the per-call raw dumps
        # don't overwrite each other.
        tasks = []  # (variant_key, rep_id, prompt)
        variant_full_id = {}
        for variant_key, note_text in variants.items():
            full_id = f"{case_id}__{variant_key}__{strategy_tag}"
            variant_full_id[variant_key] = full_id
            prompt = build_prompt(prompt_strategy, note_text)
            for rep in range(n_samples):
                rep_id = full_id if n_samples == 1 else f"{full_id}__rep{rep}"
                tasks.append((variant_key, rep_id, prompt))

        def _one_call(task):
            variant_key, rep_id, prompt = task
            try:
                r = model.generate_with_retry(prompt, rep_id)
                return variant_key, {
                    "response_text": r.get("response_text"),
                    "prompt_tokens": r.get("prompt_tokens"),
                    "completion_tokens": r.get("completion_tokens"),
                    "total_tokens": r.get("total_tokens"),
                    "timestamp": r.get("timestamp"),
                }
            except Exception as exc:
                logging.error("SKIP %s: %s", rep_id, exc)
                failed.append(rep_id)  # list.append is atomic under the GIL
                return variant_key, None

        # Run the case's calls concurrently (blocking HTTP releases the GIL).
        # max_workers=1 reproduces the original serial behavior exactly.
        samples_by_variant: dict = {vk: [] for vk in variants}
        if max_workers and max_workers > 1:
            with ThreadPoolExecutor(max_workers=max_workers) as ex:
                for vk, sample in ex.map(_one_call, tasks):
                    if sample is not None:
                        samples_by_variant[vk].append(sample)
        else:
            for task in tasks:
                vk, sample = _one_call(task)
                if sample is not None:
                    samples_by_variant[vk].append(sample)

        # Assemble per-variant results. First sample is lifted to the top level
        # for backward compatibility; the full distribution lives in "samples".
        for variant_key in variants:
            samples = samples_by_variant[variant_key]
            if not samples:
                case_results[variant_key] = {"error": "all samples failed"}
                continue
            first = samples[0]
            case_results[variant_key] = {
                "case_id": variant_full_id[variant_key],
                "model": model_name,
                "variant_label": variant_key,
                "strategy": strategy_tag,
                "base_case_id": case_id,
                "ground_truth_label": label_index.get(case_id, ""),
                **nccn_fields(nccn_index, case_id),
                "n_samples": len(samples),
                "response_text": first["response_text"],
                "prompt_tokens": first["prompt_tokens"],
                "completion_tokens": first["completion_tokens"],
                "total_tokens": first["total_tokens"],
                "timestamp": first["timestamp"],
                "samples": samples,
            }

        results[case_id] = case_results

        _atomic_dump(results, checkpoint_path)

    # Save final results
    final_path = strategy_dir / f"{file_prefix}_results.json"
    _atomic_dump(results, final_path)

    elapsed = (time.time() - start) / 60
    completed_calls = sum(
        len(v.get("samples", [v])) for case in results.values()
        for v in case.values()
        if "error" not in v
    )

    print(f"\n{'='*70}")
    print(f"EXPERIMENT v2 COMPLETE")
    print(f"Elapsed   : {elapsed:.1f} minutes")
    print(f"Completed : {completed_calls} / {len(cases) * n_variants * n_samples} calls")
    print(f"Failed    : {len(failed)}")
    print(f"Checkpoint: {checkpoint_path}")
    print(f"Results   : {final_path}")
    print(f"{'='*70}\n")
    print(f"Next step: python scripts/nsclc/analyze_results_v2.py --subset {subset} --model {model_name} --concordance --save")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="EquityGUIDE v2 — clean label demographic experiment"
    )
    parser.add_argument(
        "--subset",
        choices=["synthetic_structured", "synthetic_unstructured", "genie_bpc_nsclc", "genie_bpc_nsclc_pilot50",
                 "genie_bpc_nsclc_templates", "genie_bpc_nsclc_templates100",
                 "genie_bpc_nsclc_n300", "genie_bpc_nsclc_natural150", "pmc_nsclc",
                 "genie_bpc_brca", "genie_bpc_brca_pilot50",
                 "genie_bpc_panc", "genie_bpc_panc_pilot50",
                 "genie_bpc_brca_templates100", "genie_bpc_panc_templates100"],
        default="synthetic_structured",
    )
    parser.add_argument(
        "--model",
        choices=SUPPORTED_MODELS,
        default="gemini-2.5-flash",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="sampling temperature (0.0 = near-deterministic single-pass; "
             "use 1.0 with --n-samples 6 for Omar-style repeat sampling)",
    )
    parser.add_argument(
        "--n-samples",
        type=int,
        default=1,
        help="repeat samples per variant (1 = single trial, pairs with "
             "temperature 0.0; 5-6 pairs with temperature 1.0 to measure the noise floor)",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=1,
        help="concurrent API requests (1 = serial; 8-16 recommended for "
             "API models to make full-cohort runs feasible)",
    )
    parser.add_argument(
        "--strategy",
        default="baseline",
        help="prompt strategy from prompts/evaluation/prompt_templates.py "
             "(baseline, fairness, guideline_grounded, structured_extraction, "
             "rating). Non-baseline strategies write to a distinct checkpoint "
             "prefix, e.g. '..._rating_checkpoint.json'.",
    )
    args = parser.parse_args()
    run_experiment_v2(
        subset=args.subset,
        model_name=args.model,
        n_samples=args.n_samples,
        max_workers=args.max_workers,
        temperature=args.temperature,
        prompt_strategy=args.strategy,
    )
