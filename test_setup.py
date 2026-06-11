"""Setup verification script for EquityGUIDE.

Checks that all dependencies are installed, the API key is reachable, and
every src module can be imported without errors.

Usage
-----
    python test_setup.py
"""

from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

# Ensure the project root is on the path
sys.path.insert(0, str(Path(__file__).parent))

PASS = "  [PASS]"
FAIL = "  [FAIL]"
SKIP = "  [SKIP]"


def check(label: str, fn) -> bool:
    """Run a single check function, print result, return True on pass."""
    try:
        result = fn()
        if result is True or result is None:
            print(f"{PASS} {label}")
            return True
        # fn() returned a failure message string
        print(f"{FAIL} {label}: {result}")
        return False
    except Exception as exc:  # noqa: BLE001
        print(f"{FAIL} {label}: {exc}")
        return False


def main() -> None:
    print("=" * 60)
    print("EquityGUIDE Setup Verification")
    print("=" * 60)
    results: list[bool] = []

    # ------------------------------------------------------------------
    # 1. Third-party package availability
    # ------------------------------------------------------------------
    print("\n[1] Third-party dependencies")
    packages = [
        ("vertexai", "google-cloud-aiplatform"),
        ("dotenv", "python-dotenv"),
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        ("scipy", "scipy"),
        ("sklearn", "scikit-learn"),
        ("matplotlib", "matplotlib"),
        ("seaborn", "seaborn"),
        ("tqdm", "tqdm"),
        ("datasets", "datasets"),
        ("jsonschema", "jsonschema"),
        ("requests", "requests"),
    ]
    for import_name, pip_name in packages:
        results.append(
            check(
                f"import {import_name} ({pip_name})",
                lambda n=import_name: importlib.import_module(n) and True,
            )
        )

    # ------------------------------------------------------------------
    # 2. .env file and API key presence
    # ------------------------------------------------------------------
    print("\n[2] Environment configuration")

    def check_env_file():
        env_path = Path(".env")
        if env_path.exists():
            return True
        example_path = Path(".env.example")
        if example_path.exists():
            return f".env not found. Copy .env.example to .env and fill in GOOGLE_API_KEY."
        return ".env and .env.example both missing."

    results.append(check(".env file present", check_env_file))

    def check_project():
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass
        project = os.getenv("GOOGLE_CLOUD_PROJECT", "")
        if not project:
            return "GOOGLE_CLOUD_PROJECT is not set in .env"
        return True

    results.append(check("GOOGLE_CLOUD_PROJECT present in .env", check_project))

    # ------------------------------------------------------------------
    # 3. Project src module imports
    # ------------------------------------------------------------------
    print("\n[3] Project module imports")

    src_modules = [
        "src",
        "src.models.gemini_model",
        "src.generate.variant_injector",
        "src.evaluate.nccn_scorer",
        "src.evaluate.quality_checker",
        "src.evaluate.runner",
        "src.analyze.flip_rate",
        "prompts.evaluation.prompt_templates",
    ]
    for module in src_modules:
        results.append(
            check(
                f"import {module}",
                lambda m=module: importlib.import_module(m) and True,
            )
        )

    # ------------------------------------------------------------------
    # 4. Quick functional smoke tests (no API calls)
    # ------------------------------------------------------------------
    print("\n[4] Functional smoke tests (no API calls)")

    def test_build_prompt():
        from prompts.evaluation.prompt_templates import build_prompt
        prompt = build_prompt("baseline", "Sample clinical note.")
        assert "Sample clinical note." in prompt
        assert len(prompt) > 50

    results.append(check("build_prompt() formats prompt correctly", test_build_prompt))

    def test_variant_injector():
        from src.generate.variant_injector import create_all_variants
        base = (
            "CHIEF COMPLAINT:\nCough.\n\n"
            "SOCIAL HISTORY:\nPlaceholder.\n\n"
            "ASSESSMENT:\nNSCLC."
        )
        variants = create_all_variants(base)
        assert len(variants) == 6
        assert "white_male_private" in variants
        assert "no_demographics" in variants

    results.append(check("create_all_variants() returns 6 variants", test_variant_injector))

    def test_quality_checker():
        from src.evaluate.quality_checker import QualityChecker
        qc = QualityChecker()
        assert hasattr(qc, "check_note")

    results.append(check("QualityChecker instantiates correctly", test_quality_checker))

    def test_flip_calculator():
        from src.analyze.flip_rate import FlipRateCalculator
        profile = {
            "cancer_type": "nsclc",
            "stage": "IV",
            "histology": "adenocarcinoma",
            "egfr_status": "exon_19_del",
            "alk_status": "negative",
            "ros1_status": "negative",
            "braf_status": "negative",
            "met_status": "negative",
            "ret_status": "negative",
            "ntrk_status": "negative",
            "pdl1_tps_category": "intermediate",
            "ecog_ps": 1,
            "prior_therapy": "naive",
            "brain_mets": False,
        }
        calc = FlipRateCalculator(profile)
        assert hasattr(calc, "compute_flip")

    results.append(check("FlipRateCalculator instantiates correctly", test_flip_calculator))

    def test_build_prompt_all_strategies():
        from prompts.evaluation.prompt_templates import PROMPTS, build_prompt
        for strategy in PROMPTS:
            p = build_prompt(strategy, "Test note.")
            assert "Test note." in p, f"Strategy '{strategy}' did not embed clinical note."

    results.append(check("All 5 prompt strategies format correctly", test_build_prompt_all_strategies))

    # ------------------------------------------------------------------
    # 5. Directory structure
    # ------------------------------------------------------------------
    print("\n[5] Required directories")
    required_dirs = [
        "data/raw", "data/processed", "data/variants", "data/validated",
        "prompts/generation", "prompts/evaluation", "prompts/mitigation",
        "src/models", "src/generate", "src/evaluate", "src/analyze", "src/utils",
        "results/baseline", "results/variants", "results/mitigation", "results/raw",
        "figures", "notebooks", "docs", "tests",
    ]
    for d in required_dirs:
        results.append(
            check(
                f"Directory exists: {d}",
                lambda path=d: True if Path(path).is_dir() else f"Missing: {path}",
            )
        )

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    passed = sum(results)
    total = len(results)
    failed = total - passed

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed}/{total} checks passed  |  {failed} failed")
    if failed == 0:
        print("All checks passed. EquityGUIDE is ready to run.")
    else:
        print("Some checks failed. Resolve the issues above before running experiments.")
    print("=" * 60)

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
