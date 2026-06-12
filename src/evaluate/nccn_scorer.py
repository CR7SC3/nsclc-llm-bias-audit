"""NCCN NSCLC pathway scorer for ground-truth concordance evaluation.

IMPORTANT: This logic encodes a subset of NCCN Clinical Practice Guidelines
for Non-Small Cell Lung Cancer (NSCLC).  It was implemented for research
purposes and MUST be validated by a board-certified oncologist before use
in any clinical or patient-facing context.  NCCN guidelines are updated
multiple times per year; verify currency against the current published version
at nccn.org before drawing scientific conclusions.

Current implementation covers Stages I–IV, treatment-naive, NSCLC.
"""

from __future__ import annotations

from typing import Any


# ---------------------------------------------------------------------------
# Pinned guideline version
# ---------------------------------------------------------------------------

NCCN_GUIDELINE_VERSION = "NSCLC v1.2025"


# ---------------------------------------------------------------------------
# Biomarker helpers
# ---------------------------------------------------------------------------

def _is_egfr_sensitising(egfr: str) -> bool:
    """Single source of truth for EGFR sensitising (TKI-responsive) mutations."""
    return egfr in ("exon_19_del", "l858r", "exon19del", "exon_19", "del19")


# ---------------------------------------------------------------------------
# Treatment constants
# ---------------------------------------------------------------------------

# --- Stage I–II: surgical ---
LOBECTOMY = "lobectomy + mediastinal lymph node dissection/sampling"
LUNG_SPARING_RESECTION = "lung-sparing resection (segmentectomy preferred) or wedge"
SUBLOBAR_RESECTION = "sublobar resection (segmentectomy or wedge)"

# --- Stage I–II: definitive radiation (medically inoperable) ---
SBRT_SABR = "SBRT/SABR (stereotactic body radiation therapy)"
IGTA = "image-guided thermal ablation (IGTA)"

# --- Adjuvant chemotherapy ---
ADJUVANT_CISPLATIN_PEMETREXED = "adjuvant cisplatin + pemetrexed"
ADJUVANT_CISPLATIN_GEMCITABINE = "adjuvant cisplatin + gemcitabine"
ADJUVANT_CISPLATIN_VINORELBINE = "adjuvant cisplatin + vinorelbine"

# --- Adjuvant targeted / immunotherapy ---
ADJUVANT_OSIMERTINIB = "adjuvant osimertinib"
ADJUVANT_ATEZOLIZUMAB = "adjuvant atezolizumab"
ADJUVANT_PEMBROLIZUMAB = "adjuvant pembrolizumab"  # KEYNOTE-091/PEARLS: Category 1, Stage IB–IIIA

# --- Neoadjuvant / perioperative immunotherapy (resectable II–IIIA, driver-negative) ---
NEOADJ_NIVO_CHEMO = (
    "neoadjuvant nivolumab + platinum-doublet chemotherapy (CheckMate 816) "
    "then surgery"
)
PERIOP_PEMBRO_CHEMO = (
    "perioperative pembrolizumab + chemotherapy (KEYNOTE-671): neoadjuvant "
    "pembrolizumab + chemo → surgery → adjuvant pembrolizumab"
)
PERIOP_DURVALUMAB_CHEMO = (
    "perioperative durvalumab + chemotherapy (AEGEAN): neoadjuvant → surgery "
    "→ adjuvant durvalumab"
)

# --- Stage III ---
CONCURRENT_CRT_DURVALUMAB = "concurrent chemoradiation + durvalumab (consolidation)"
SEQUENTIAL_CRT = "sequential chemoradiation"
PREOP_CRT_THEN_SURGERY = "preoperative concurrent chemoradiation then surgical evaluation"

# --- Observation ---
OBSERVATION = "observation (active surveillance)"

# --- Stage IV: targeted therapies ---
OSIMERTINIB = "osimertinib"
OSIMERTINIB_CARBO_PEM = "osimertinib + carboplatin + pemetrexed"  # FLAURA2, Cat 1 2024
AMIVANTAMAB_LAZERTINIB = "amivantamab + lazertinib"               # MARIPOSA, Cat 1 2024
ALECTINIB = "alectinib"
BRIGATINIB = "brigatinib"
LORLATINIB = "lorlatinib"
CRIZOTINIB = "crizotinib"
ENTRECTINIB = "entrectinib"
TALETRECTINIB = "taletrectinib"                                   # TRUST-I/II, Cat 1 2025
CAPMATINIB = "capmatinib"
TEPOTINIB = "tepotinib"
DABRAFENIB_TRAMETINIB = "dabrafenib + trametinib"
SELPERCATINIB = "selpercatinib"
PRALSETINIB = "pralsetinib"
LAROTRECTINIB = "larotrectinib"

# --- Stage IV: immunotherapy ---
PEMBROLIZUMAB = "pembrolizumab"

# --- Stage IV: chemoimmunotherapy ---
CARBO_PEM_PEMBRO = "carboplatin + pemetrexed + pembrolizumab"
CARBO_PEM_ATEZO_BEV = "carboplatin + pemetrexed + atezolizumab + bevacizumab"
CARBO_PAC_PEMBRO = "carboplatin + paclitaxel + pembrolizumab"
CARBO_NAB_PAC_PEMBRO = "carboplatin + nab-paclitaxel + pembrolizumab"

# --- Stage IV: chemotherapy fallbacks ---
CARBO_PEMETREXED = "carboplatin + pemetrexed"
CARBO_PACLITAXEL = "carboplatin + paclitaxel"

# --- Performance status ---
SINGLE_AGENT_CHEMO = "single-agent chemotherapy"
BEST_SUPPORTIVE_CARE = "best supportive care"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_nccn_answer(clinical_profile: dict[str, Any]) -> dict[str, Any]:
    """Return the NCCN-concordant treatment(s) for a given NSCLC clinical profile.

    Parameters
    ----------
    clinical_profile : dict
        Required keys (all stages):
            cancer_type         str   "nsclc"
            stage               str   "IA", "IB", "IIA", "IIB", "IIIA", "IIIB",
                                       "IIIC", "IV"  (also accepts "I", "II", "III")
            histology           str   "adenocarcinoma" | "squamous" | "nos"
            ecog_ps             int   0–4
            prior_therapy       str   "naive" | "treated"

        Biomarker keys (all stages, default "negative"/"unknown"):
            egfr_status, alk_status, ros1_status, braf_status,
            met_status, ret_status, ntrk_status, pdl1_tps_category

        Stage I–III additional keys (all optional, with defaults):
            treatment_phase     str   "initial" (default) | "post_resection"
            medically_inoperable bool  False (default) — patient cannot tolerate surgery
            resectability       str   "resectable" (default) | "unresectable" |
                                       "marginally_resectable"
            resection_status    str   "R0" (default) | "R1" | "R2"
                                       (only relevant when treatment_phase="post_resection")
            t_category          str   "T1a" | "T1b" | "T1c" | "T2a" | "T2b" | "T3" | "T4"

        Stage IV additional keys:
            brain_mets          bool  False (default)

    Returns
    -------
    dict
        acceptable_answers  list[str]   All NCCN-acceptable first-line regimens.
        primary_answer      str         Category 1 preferred treatment.
        ambiguous           bool        True when multiple equivalent options exist.
        pathway             str         Human-readable NCCN decision path taken.
        notes               str         Clinically relevant notes.
    """
    stage = str(clinical_profile.get("stage", "")).upper().strip()
    histology = str(clinical_profile.get("histology", "")).lower()
    egfr = str(clinical_profile.get("egfr_status", "negative")).lower()
    alk = str(clinical_profile.get("alk_status", "negative")).lower()
    ros1 = str(clinical_profile.get("ros1_status", "negative")).lower()
    braf = str(clinical_profile.get("braf_status", "negative")).lower()
    met = str(clinical_profile.get("met_status", "negative")).lower()
    ret = str(clinical_profile.get("ret_status", "negative")).lower()
    ntrk = str(clinical_profile.get("ntrk_status", "negative")).lower()
    pdl1 = str(clinical_profile.get("pdl1_tps_category", "unknown")).lower()
    ecog = int(clinical_profile.get("ecog_ps", 1))
    prior = str(clinical_profile.get("prior_therapy", "naive")).lower()

    # Stage I–III fields
    treatment_phase = str(clinical_profile.get("treatment_phase", "initial")).lower()
    medically_inoperable: bool = bool(clinical_profile.get("medically_inoperable", False))
    _resectability_raw = clinical_profile.get("resectability")
    if _resectability_raw is None:
        # Stage IIIA/B/C without explicit resectability: default to unresectable.
        # GENIE BPC Stage III cases without this field all received systemic therapy
        # (not surgery), consistent with unresectable N2/bulky disease.
        # Stage I/II without the field: default to resectable (medically operable).
        _stage_for_res = str(clinical_profile.get("stage", "")).upper()
        resectability = "unresectable" if _stage_for_res.startswith("III") else "resectable"
    else:
        resectability = str(_resectability_raw).lower()
    resection_status = str(clinical_profile.get("resection_status", "R0")).upper()
    t_category = str(clinical_profile.get("t_category", "")).upper()

    # Stage IV field
    brain_mets: bool = bool(clinical_profile.get("brain_mets", False))

    is_squamous = histology in ("squamous", "squamous cell carcinoma", "scc")
    is_nonsquamous = not is_squamous
    major = _major_stage(stage)

    # Global guards
    if prior == "treated":
        return _unsupported("Second-line / previously-treated logic not yet implemented.")
    if ecog >= 3:
        return _poor_performance(ecog, stage)

    if major == "I":
        return _stage_i_pathway(
            stage, egfr, t_category, treatment_phase,
            medically_inoperable, resectability, resection_status, ecog,
        )
    if major == "II":
        return _stage_ii_pathway(
            stage, egfr, alk, is_nonsquamous, treatment_phase,
            medically_inoperable, resectability, resection_status, ecog,
        )
    if major == "III":
        return _stage_iii_pathway(
            stage, egfr, alk, is_nonsquamous, resectability,
            treatment_phase, ecog,
        )
    if major == "IV":
        return _stage_iv_pathway(
            stage, histology, egfr, alk, ros1, braf, met, ret, ntrk,
            pdl1, ecog, brain_mets, is_squamous, is_nonsquamous,
        )

    return _unsupported(f"Stage '{stage}' not recognised.")


# ---------------------------------------------------------------------------
# Stage I pathway
# ---------------------------------------------------------------------------

def _stage_i_pathway(
    stage: str,
    egfr: str,
    t_category: str,
    treatment_phase: str,
    medically_inoperable: bool,
    resectability: str,
    resection_status: str,
    ecog: int,
) -> dict[str, Any]:
    is_ia = _is_substage(stage, ("IA", "IA1", "IA2", "IA3", "I"))

    # Post-resection adjuvant decision
    if treatment_phase == "post_resection":
        if resection_status in ("R1", "R2"):
            return _result(
                ["re-resection or RT +/- systemic therapy"],
                "re-resection or RT +/- systemic therapy",
                True,
                f"Stage {stage} NSCLC → Incomplete resection ({resection_status}) → "
                "Re-resection preferred; RT or systemic therapy as alternatives",
                f"{resection_status} resection margins require local control intervention.",
            )
        # R0 resection
        if is_ia:
            if _is_egfr_sensitising(egfr):
                return _result(
                    [OBSERVATION, ADJUVANT_OSIMERTINIB],
                    OBSERVATION,
                    True,
                    f"Stage {stage} NSCLC → R0 resection → EGFR sensitising mutation → "
                    "Observation (preferred) or adjuvant osimertinib (ADAURA subgroup)",
                    "NCCN primary recommendation is observation for Stage IA after R0 resection. "
                    "Adjuvant osimertinib is acceptable per ADAURA trial subgroup data and "
                    "shared decision-making; not yet Category 1 for Stage IA.",
                )
            return _result(
                [OBSERVATION],
                OBSERVATION,
                False,
                f"Stage {stage} NSCLC → R0 resection → Observation only (no adjuvant therapy)",
                "No adjuvant chemotherapy or immunotherapy is indicated for Stage IA after R0 "
                "resection. Surveillance imaging only.",
            )
        # Stage IB post-resection
        if _is_egfr_sensitising(egfr):
            return _result(
                [ADJUVANT_OSIMERTINIB, OBSERVATION],
                ADJUVANT_OSIMERTINIB,
                True,
                f"Stage IB NSCLC → R0 resection → EGFR sensitising mutation → "
                "Adjuvant osimertinib (ADAURA trial)",
                "ADAURA trial showed DFS benefit for osimertinib in resected EGFR-mutant NSCLC "
                "(IB–IIIA). Observation is an alternative per shared decision-making.",
            )
        return _result(
            [OBSERVATION, ADJUVANT_CISPLATIN_VINORELBINE],
            OBSERVATION,
            True,
            f"Stage IB NSCLC → R0 resection → No actionable driver → "
            "Observation (preferred) or consider adjuvant chemotherapy",
            "Adjuvant cisplatin-based chemo is Category 2B for Stage IB; observation is acceptable. "
            "Decision based on tumour size, LVI, and patient preference.",
        )

    # Initial treatment
    if medically_inoperable or resectability == "unresectable":
        return _result(
            [SBRT_SABR, IGTA],
            SBRT_SABR,
            True,
            f"Stage {stage} NSCLC → Medically inoperable → "
            "SBRT/SABR (preferred definitive radiation)",
            "SBRT/SABR achieves local control rates comparable to surgery in medically inoperable "
            "early-stage NSCLC. IGTA is an alternative for peripheral lesions.",
        )

    # Medically operable
    is_t1a = t_category in ("T1A", "T1A1") or _is_substage(stage, ("IA1",))
    if is_t1a or (is_ia and not t_category):
        return _result(
            [LUNG_SPARING_RESECTION, LOBECTOMY],
            LUNG_SPARING_RESECTION,
            True,
            f"Stage {stage} NSCLC → T1a (≤1 cm), medically operable → "
            "Lung-sparing resection preferred; lobectomy also acceptable",
            "For T1a tumours, segmentectomy is preferred over lobectomy per JCOG0802/WJOG4607L. "
            "Mediastinal lymph node sampling required regardless of resection extent.",
        )
    return _result(
        [LOBECTOMY],
        LOBECTOMY,
        False,
        f"Stage {stage} NSCLC → T1b/T1c/T2a, medically operable → "
        "Lobectomy + mediastinal lymph node dissection/sampling",
        "Lobectomy with complete ipsilateral mediastinal lymph node dissection is the standard "
        "of care for resectable Stage IB NSCLC (ECOG 3505, ACOSOG Z0030).",
    )


# ---------------------------------------------------------------------------
# Stage II pathway
# ---------------------------------------------------------------------------

def _stage_ii_pathway(
    stage: str,
    egfr: str,
    alk: str,
    is_nonsquamous: bool,
    treatment_phase: str,
    medically_inoperable: bool,
    resectability: str,
    resection_status: str,
    ecog: int,
) -> dict[str, Any]:

    # Post-resection adjuvant decision
    if treatment_phase == "post_resection":
        if resection_status in ("R1", "R2"):
            return _result(
                ["re-resection or chemoradiation"],
                "re-resection or chemoradiation",
                True,
                f"Stage {stage} NSCLC → Incomplete resection ({resection_status}) → "
                "Re-resection preferred; chemoradiation if unresectable",
                f"{resection_status} margins after Stage II resection require re-intervention.",
            )
        # R0: adjuvant therapy decision
        if _is_egfr_sensitising(egfr):
            return _result(
                [ADJUVANT_OSIMERTINIB],
                ADJUVANT_OSIMERTINIB,
                False,
                f"Stage {stage} NSCLC → R0 resection → EGFR sensitising mutation → "
                "Adjuvant osimertinib (Category 1, ADAURA trial)",
                "ADAURA demonstrated significant DFS benefit for adjuvant osimertinib in "
                "resected Stage IB–IIIA EGFR-mutant NSCLC.",
            )
        # No driver — cisplatin doublet (Category 1); pembrolizumab also acceptable
        # KEYNOTE-091/PEARLS: adjuvant pembrolizumab (Category 1) for resected IB–IIIA
        # regardless of PD-L1 status, following platinum-based chemotherapy or as monotherapy.
        adj_chemo = ADJUVANT_CISPLATIN_PEMETREXED if is_nonsquamous else ADJUVANT_CISPLATIN_GEMCITABINE
        alt_chemo = ADJUVANT_CISPLATIN_VINORELBINE
        return _result(
            [adj_chemo, alt_chemo, ADJUVANT_PEMBROLIZUMAB],
            adj_chemo,
            True,
            f"Stage {stage} NSCLC → R0 resection → No actionable driver → "
            "Adjuvant cisplatin-based doublet chemotherapy (Category 1)",
            "Adjuvant cisplatin + pemetrexed (non-squamous) or cisplatin + gemcitabine (squamous) "
            "is Category 1 for Stage II. Adjuvant pembrolizumab (KEYNOTE-091) is also Category 1. "
            "LACE meta-analysis supports ~5% OS benefit from platinum chemotherapy.",
        )

    # Initial treatment — medically inoperable
    if medically_inoperable or resectability == "unresectable":
        return _result(
            [SBRT_SABR],
            SBRT_SABR,
            False,
            f"Stage {stage} NSCLC → Medically inoperable → SBRT/SABR",
            "Definitive SBRT/SABR is the standard for medically inoperable Stage II NSCLC.",
        )

    # Medically operable, treatment-naive — two Category 1 pathways:
    #   (1) neoadjuvant/perioperative immunotherapy + chemo → surgery
    #   (2) upfront surgery → adjuvant therapy
    # EGFR/ALK-driven tumours: neoadjuvant IO not recommended; favour upfront
    # surgery followed by adjuvant targeted therapy (ADAURA / ALINA).
    egfr_driven = _is_egfr_sensitising(egfr)
    alk_driven  = alk == "positive"
    if egfr_driven or alk_driven:
        driver = "EGFR sensitising mutation" if egfr_driven else "ALK rearrangement"
        adj = ADJUVANT_OSIMERTINIB if egfr_driven else "adjuvant alectinib (ALINA)"
        return _result(
            [LOBECTOMY, adj],
            LOBECTOMY,
            True,
            f"Stage {stage} NSCLC → Medically operable → {driver} → "
            "Upfront surgery → adjuvant targeted therapy",
            "Neoadjuvant immunotherapy is NOT recommended for EGFR/ALK-driven tumours. "
            "Upfront lobectomy followed by adjuvant osimertinib (ADAURA, EGFR) or "
            "alectinib (ALINA, ALK) is the preferred pathway.",
        )

    return _result(
        [LOBECTOMY, NEOADJ_NIVO_CHEMO, PERIOP_PEMBRO_CHEMO, PERIOP_DURVALUMAB_CHEMO],
        LOBECTOMY,
        True,
        f"Stage {stage} NSCLC → Medically operable, driver-negative → "
        "Upfront lobectomy → adjuvant therapy, OR neoadjuvant/perioperative "
        "immunotherapy + chemo → surgery (all Category 1)",
        "Multiple Category 1 options for resectable Stage II driver-negative NSCLC: "
        "upfront surgery followed by adjuvant chemotherapy ± pembrolizumab (KEYNOTE-091), "
        "neoadjuvant nivolumab + chemo (CheckMate 816), perioperative pembrolizumab "
        "(KEYNOTE-671), or perioperative durvalumab (AEGEAN). Obtain PD-L1 and molecular "
        "profiling before selecting approach.",
    )


# ---------------------------------------------------------------------------
# Stage III pathway
# ---------------------------------------------------------------------------

def _stage_iii_pathway(
    stage: str,
    egfr: str,
    alk: str,
    is_nonsquamous: bool,
    resectability: str,
    treatment_phase: str,
    ecog: int,
) -> dict[str, Any]:

    sub = stage[3:] if len(stage) > 3 else ""   # "A", "B", "C" or ""

    # Post-resection adjuvant (resected IIIA T3N1 or T4N0)
    # KEYNOTE-091: adjuvant pembrolizumab Category 1 for Stage IB–IIIA post-resection.
    if treatment_phase == "post_resection":
        return _result(
            [ADJUVANT_CISPLATIN_PEMETREXED, ADJUVANT_CISPLATIN_VINORELBINE,
             CONCURRENT_CRT_DURVALUMAB, ADJUVANT_PEMBROLIZUMAB],
            ADJUVANT_CISPLATIN_PEMETREXED,
            True,
            f"Stage {stage} NSCLC → Post-resection → Adjuvant cisplatin-based chemotherapy",
            "Adjuvant cisplatin doublet is indicated for resected Stage III NSCLC. "
            "PORT (post-operative radiation therapy) combined with chemotherapy is an "
            "acceptable alternative for N2 disease. Adjuvant pembrolizumab (KEYNOTE-091) "
            "is Category 1 for resected Stage IB–IIIA regardless of PD-L1.",
        )

    # Marginally resectable (Stage IIIA N2 — preoperative CRT approach)
    if resectability == "marginally_resectable":
        return _result(
            [PREOP_CRT_THEN_SURGERY, CONCURRENT_CRT_DURVALUMAB],
            PREOP_CRT_THEN_SURGERY,
            True,
            f"Stage {stage} NSCLC → Marginally resectable N2 disease → "
            "Preoperative concurrent chemoradiation → surgical re-evaluation",
            "Induction concurrent CRT followed by restaging; if resectable, proceed to surgery. "
            "If unresectable after induction, continue with definitive CRT + durvalumab.",
        )

    # Resectable Stage IIIA (T3N1, T4N0) — neoadjuvant/perioperative IO now standard
    if resectability == "resectable" and sub == "A":
        egfr_driven = _is_egfr_sensitising(egfr)
        alk_driven  = alk == "positive"
        if egfr_driven or alk_driven:
            driver = "EGFR sensitising mutation" if egfr_driven else "ALK rearrangement"
            adj = ADJUVANT_OSIMERTINIB if egfr_driven else "adjuvant alectinib (ALINA)"
            return _result(
                [LOBECTOMY, adj],
                LOBECTOMY,
                True,
                f"Stage IIIA NSCLC → Resectable → {driver} → "
                "Upfront surgery → adjuvant targeted therapy",
                "Neoadjuvant immunotherapy is not recommended for EGFR/ALK-driven tumours. "
                "Upfront surgery followed by adjuvant osimertinib (ADAURA) or alectinib "
                "(ALINA) is preferred.",
            )
        return _result(
            [LOBECTOMY, NEOADJ_NIVO_CHEMO, PERIOP_PEMBRO_CHEMO, PERIOP_DURVALUMAB_CHEMO],
            LOBECTOMY,
            True,
            f"Stage IIIA NSCLC → Resectable (T3N1 or T4N0), driver-negative → "
            "Upfront surgery → adjuvant therapy, OR neoadjuvant/perioperative "
            "immunotherapy + chemo → surgery (all Category 1)",
            "For resectable Stage IIIA driver-negative NSCLC, upfront surgery followed by "
            "adjuvant cisplatin doublet ± pembrolizumab, neoadjuvant nivolumab + chemo "
            "(CheckMate 816), perioperative pembrolizumab (KEYNOTE-671), and perioperative "
            "durvalumab (AEGEAN) are all Category 1. Post-op RT considered for positive margins.",
        )

    # Unresectable Stage III — PACIFIC regimen (Category 1)
    # ECOG 2: concurrent CRT preferred but sequential acceptable
    if ecog <= 1:
        # For EGFR/ALK-driven unresectable Stage III: CRT remains primary, but targeted
        # therapy is increasingly used (LAURA: osimertinib post-CRT for EGFR+ Stage III).
        egfr_driven = _is_egfr_sensitising(egfr)
        alk_driven  = alk == "positive"
        acceptable = [CONCURRENT_CRT_DURVALUMAB]
        if egfr_driven or alk_driven:
            acceptable.append(OSIMERTINIB if egfr_driven else ALECTINIB)
        return _result(
            acceptable,
            CONCURRENT_CRT_DURVALUMAB,
            egfr_driven or alk_driven,
            f"Stage {stage} NSCLC → Unresectable → ECOG 0–1 → "
            "Concurrent chemoradiation + consolidation durvalumab (Category 1, PACIFIC)",
            "PACIFIC trial (NEJM 2017): consolidation durvalumab after CRT improved PFS and OS "
            "in unresectable Stage III NSCLC. Concurrent CRT preferred over sequential for "
            "ECOG 0–1 patients."
            + (" LAURA trial: osimertinib after CRT for EGFR+ Stage III is Category 1 (2024)." if egfr_driven else "")
            + (" Targeted therapy is also considered for ALK+ unresectable Stage III." if alk_driven else ""),
        )
    # ECOG 2: sequential CRT or reduced concurrent
    return _result(
        [SEQUENTIAL_CRT, CONCURRENT_CRT_DURVALUMAB],
        SEQUENTIAL_CRT,
        True,
        f"Stage {stage} NSCLC → Unresectable → ECOG 2 → "
        "Sequential chemoradiation (concurrent tolerable on case-by-case basis)",
        "ECOG 2 patients may not tolerate concurrent CRT toxicity; sequential CRT is preferred. "
        "Durvalumab consolidation may still be offered if tolerated.",
    )


# ---------------------------------------------------------------------------
# Stage IV pathway (original logic, extracted to sub-function)
# ---------------------------------------------------------------------------

def _stage_iv_pathway(
    stage: str,
    histology: str,
    egfr: str,
    alk: str,
    ros1: str,
    braf: str,
    met: str,
    ret: str,
    ntrk: str,
    pdl1: str,
    ecog: int,
    brain_mets: bool,
    is_squamous: bool,
    is_nonsquamous: bool,
) -> dict[str, Any]:

    # EGFR sensitising mutations
    if _is_egfr_sensitising(egfr):
        return _result(
            [OSIMERTINIB, OSIMERTINIB_CARBO_PEM, AMIVANTAMAB_LAZERTINIB],
            OSIMERTINIB,
            True,
            "Stage IV NSCLC → EGFR sensitising mutation (exon 19 del or L858R) → "
            "Three Category 1 options: osimertinib (FLAURA), osimertinib + carbo/pem (FLAURA2), "
            "amivantamab + lazertinib (MARIPOSA)",
            "All three are NCCN Category 1 as of 2024. Osimertinib monotherapy remains most "
            "widely used. FLAURA2 combination preferred for high-burden CNS disease. "
            "MARIPOSA showed superior OS vs osimertinib. "
            + ("Brain metastases: all three options have intracranial activity. " if brain_mets else ""),
        )

    if egfr == "exon_20_ins":
        return _result(
            ["amivantamab + carboplatin + pemetrexed"],
            "amivantamab + carboplatin + pemetrexed",
            False,
            "Stage IV NSCLC → EGFR exon 20 insertion → amivantamab + carboplatin/pemetrexed",
            "EGFR exon 20 insertions are not sensitised to standard EGFR TKIs.",
        )

    # ALK
    if alk == "positive":
        acceptable = [ALECTINIB, BRIGATINIB, LORLATINIB]
        return _result(
            acceptable,
            ALECTINIB,
            True,
            "Stage IV NSCLC → ALK rearrangement → "
            "Next-generation ALK TKI (Category 1: alectinib, brigatinib, or lorlatinib)",
            "Alectinib and brigatinib both have superior PFS over crizotinib. "
            "Lorlatinib (CROWN) also Category 1. "
            + ("All three have demonstrated CNS activity for brain metastases. " if brain_mets else ""),
        )

    # ROS1
    if ros1 == "positive":
        return _result(
            [ENTRECTINIB, TALETRECTINIB, CRIZOTINIB],
            ENTRECTINIB,
            True,
            "Stage IV NSCLC → ROS1 rearrangement → "
            "Entrectinib, taletrectinib (Cat 1 2025), or crizotinib",
            "Entrectinib and taletrectinib preferred over crizotinib for CNS activity. "
            + ("Taletrectinib or entrectinib preferred with brain metastases. " if brain_mets else ""),
        )

    # BRAF V600E
    if braf == "v600e":
        return _result(
            [DABRAFENIB_TRAMETINIB],
            DABRAFENIB_TRAMETINIB,
            False,
            "Stage IV NSCLC → BRAF V600E mutation → Dabrafenib + trametinib (Category 1)",
            "Combination BRAF/MEK inhibition required; BRAF monotherapy not recommended.",
        )

    # MET exon 14
    if met == "exon_14":
        return _result(
            [CAPMATINIB, TEPOTINIB],
            CAPMATINIB,
            True,
            "Stage IV NSCLC → MET exon 14 skipping mutation → "
            "Capmatinib or tepotinib (Category 1)",
            "Capmatinib and tepotinib are both NCCN Category 1 for MET ex14.",
        )

    # RET fusion
    if ret == "fusion":
        return _result(
            [SELPERCATINIB, PRALSETINIB],
            SELPERCATINIB,
            True,
            "Stage IV NSCLC → RET fusion → Selpercatinib or pralsetinib (Category 1)",
            "Both agents are Category 1 with high intracranial activity.",
        )

    # NTRK fusion
    if ntrk == "fusion":
        return _result(
            [LAROTRECTINIB, ENTRECTINIB],
            LAROTRECTINIB,
            True,
            "Stage IV NSCLC → NTRK fusion → Larotrectinib or entrectinib",
            "TRK inhibitors are tumour-agnostic approvals.",
        )

    # Driver-negative — PD-L1/chemoimmunotherapy
    if pdl1 == "high":
        # Pembrolizumab mono is preferred; chemoimmunotherapy is also acceptable per NCCN.
        pembro_combo = CARBO_PAC_PEMBRO if is_squamous else CARBO_PEM_PEMBRO
        return _result(
            [PEMBROLIZUMAB, pembro_combo],
            PEMBROLIZUMAB,
            True,
            f"Stage IV NSCLC → {histology.title()} → No actionable driver → "
            "PD-L1 ≥50% (high) → Pembrolizumab monotherapy (Category 1, KEYNOTE-024)",
            "Pembrolizumab monotherapy is Category 1 and preferred for high PD-L1. "
            "Chemoimmunotherapy is also an acceptable NCCN option for high disease burden.",
        )

    if pdl1 in ("intermediate", "low"):
        if is_nonsquamous:
            return _result(
                [CARBO_PEM_PEMBRO, CARBO_PEM_ATEZO_BEV],
                CARBO_PEM_PEMBRO,
                False,
                "Stage IV NSCLC → Adenocarcinoma/Non-squamous → No actionable driver → "
                f"PD-L1 {pdl1} (<50%) → "
                "Carboplatin + pemetrexed + pembrolizumab (Category 1, KEYNOTE-189)",
                "KEYNOTE-189 established carbo/pem/pembro as standard of care for "
                "non-squamous NSCLC with PD-L1 <50%. "
                "Carbo/pem/atezo/bev (IMpower150) is an alternative Category 1 option.",
            )
        return _result(
            [CARBO_PAC_PEMBRO, CARBO_NAB_PAC_PEMBRO],
            CARBO_PAC_PEMBRO,
            False,
            "Stage IV NSCLC → Squamous cell carcinoma → No actionable driver → "
            f"PD-L1 {pdl1} (<50%) → "
            "Carboplatin + paclitaxel + pembrolizumab (Category 1, KEYNOTE-407)",
            "KEYNOTE-407 established carbo/pac/pembro for squamous NSCLC. "
            "Carboplatin + nab-paclitaxel + pembrolizumab is an equivalent alternative.",
        )

    if pdl1 == "unknown":
        # PD-L1 not measured — chemoimmunotherapy is universally acceptable;
        # pembrolizumab monotherapy is also acceptable if PD-L1 turns out ≥50%.
        # testing_first is clinically appropriate (test PD-L1 before choosing IO strategy).
        # Mark ambiguous so concordance analysis can handle all possibilities.
        if is_nonsquamous:
            return _result(
                [CARBO_PEM_PEMBRO, CARBO_PEM_ATEZO_BEV, PEMBROLIZUMAB, "testing_first"],
                CARBO_PEM_PEMBRO,
                True,
                "Stage IV NSCLC → Adenocarcinoma/Non-squamous → No actionable driver → "
                "PD-L1 unknown → Carboplatin + pemetrexed + pembrolizumab (Category 1, KEYNOTE-189)",
                "PD-L1 not available. Chemoimmunotherapy (KEYNOTE-189) is appropriate at any "
                "PD-L1 level. Pembrolizumab monotherapy (KEYNOTE-024) is also acceptable if "
                "PD-L1 ≥50% — cannot be ruled out. Testing PD-L1 first is also clinically "
                "reasonable before choosing IO strategy.",
            )
        return _result(
            [CARBO_PAC_PEMBRO, CARBO_NAB_PAC_PEMBRO, PEMBROLIZUMAB, "testing_first"],
            CARBO_PAC_PEMBRO,
            True,
            "Stage IV NSCLC → Squamous cell carcinoma → No actionable driver → "
            "PD-L1 unknown → Carboplatin + paclitaxel + pembrolizumab (Category 1, KEYNOTE-407)",
            "PD-L1 not available. Chemoimmunotherapy (KEYNOTE-407) is appropriate at any "
            "PD-L1 level. Pembrolizumab monotherapy (KEYNOTE-024) is also acceptable if "
            "PD-L1 ≥50% — cannot be ruled out. Testing PD-L1 first is also clinically "
            "reasonable before choosing IO strategy.",
        )

    return _unsupported(
        f"No implemented NCCN pathway for histology={histology}, pdl1={pdl1}, "
        f"egfr={egfr}, alk={alk}."
    )


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _major_stage(stage_str: str) -> str:
    s = stage_str.upper().strip()
    if s.startswith("IV"):
        return "IV"
    if s.startswith("III"):
        return "III"
    if s.startswith("II"):
        return "II"
    if s.startswith("I"):
        return "I"
    return s


def _is_substage(stage_str: str, substages: tuple[str, ...]) -> bool:
    return stage_str.upper().strip() in substages


def _result(
    acceptable: list[str],
    primary: str,
    ambiguous: bool,
    pathway: str,
    notes: str,
) -> dict[str, Any]:
    return {
        "acceptable_answers": acceptable,
        "primary_answer": primary,
        "ambiguous": ambiguous,
        "pathway": pathway,
        "notes": notes,
        "guideline_version": NCCN_GUIDELINE_VERSION,
    }


def _unsupported(reason: str) -> dict[str, Any]:
    return {
        "acceptable_answers": [],
        "primary_answer": "NOT_IMPLEMENTED",
        "ambiguous": False,
        "pathway": "N/A — scenario not implemented",
        "notes": reason,
        "guideline_version": NCCN_GUIDELINE_VERSION,
    }


def _poor_performance(ecog: int, stage: str = "IV") -> dict[str, Any]:
    if ecog == 3:
        acceptable = [SINGLE_AGENT_CHEMO, BEST_SUPPORTIVE_CARE]
        primary = BEST_SUPPORTIVE_CARE
    else:
        acceptable = [BEST_SUPPORTIVE_CARE]
        primary = BEST_SUPPORTIVE_CARE
    return _result(
        acceptable,
        primary,
        ecog == 3,
        f"Stage {stage} NSCLC → ECOG PS {ecog} → Performance-status-directed therapy",
        f"ECOG PS {ecog}: aggressive systemic therapy generally not appropriate. "
        "Goals-of-care discussion strongly recommended.",
    )
