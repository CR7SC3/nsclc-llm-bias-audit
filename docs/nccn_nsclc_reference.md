# NCCN NSCLC Guidelines Reference — CancerGUIDE Ground Truth

**Scope:** Stage IV Non-Small Cell Lung Cancer (NSCLC), first-line treatment, treatment-naive patients  
**Source:** NCCN Clinical Practice Guidelines in Oncology — Non-Small Cell Lung Cancer (verify current version at nccn.org)  
**Purpose:** Human-readable reference for validating the logic in `src/evaluate/nccn_scorer.py`  
**Last verified:** July 2026 against the **NCCN NSCLC Guidelines Version 6.2026 (06/12/26)** algorithm PDF (`nscl.pdf`), read from the extracted algorithm text (pages NSCL-1..37). Earlier cross-checks against NCCN Guidelines Insights v7.2025 [JNCCN], ASCO Living Guideline 2026.3.0, and PMC trial data retained where consistent.

> **IMPORTANT:** NCCN guidelines are updated multiple times per year. This document now reflects **NCCN NSCLC v6.2026** — the version the scorer (`src/evaluate/nccn_scorer.py`, `NCCN_GUIDELINE_VERSION = "NSCLC v6.2026"`) is pinned to. Before publishing research findings, verify currency against the current version at nccn.org (free registration required).

> **UPDATED JULY 2026 (v6.2026 reconciliation):** Added the v6.2026 first-line preferred agents confirmed against the algorithm PDF — **ensartinib** (ALK, NSCL-27), **repotrectinib** (ROS1 NSCL-30 and NTRK NSCL-33), **binimetinib + encorafenib** (BRAF V600E, NSCL-32, now co-preferred with dabrafenib/trametinib). Added the **atypical-EGFR (S768I/L861Q/G719X) NSCL-24 pathway** (afatinib/osimertinib preferred; FLAURA2/MARIPOSA explicitly NOT indicated). Confirmed and documented that **ERBB2/HER2 (NSCL-36)** and **NRG1 (NSCL-37)** targeted agents are **SUBSEQUENT-line** — first-line remains PD-L1-driven systemic therapy (same as KRAS G12C). Prior additions (June 2026): FLAURA2 and MARIPOSA for classic EGFR; taletrectinib for ROS1.

---

## Section 1 — Biomarker-Driven Pathways

For Stage IV NSCLC, molecular profiling is required before first-line treatment. Actionable driver mutations take precedence over PD-L1 status — if a driver is found, the targeted therapy is preferred regardless of PD-L1 expression.

### 1.1 EGFR Mutations

| Driver | Preferred Regimen | NCCN Category | Key Trial | Notes |
|---|---|---|---|---|
| Exon 19 deletion | Osimertinib monotherapy | Category 1 | FLAURA | Superior PFS, OS, and CNS penetration vs. 1st-gen TKIs |
| Exon 19 deletion | Osimertinib + carboplatin + pemetrexed | Category 1 | FLAURA2 | **Added 2024.** Superior PFS vs osimertinib mono (median +8.8 mo); preferred for high-burden/high-risk disease |
| Exon 19 deletion | Amivantamab + lazertinib | Category 1 | MARIPOSA | **Added 2024.** Superior PFS (23.7 vs 16.6 mo) and OS vs osimertinib; FDA + EMA approved first-line |
| L858R (exon 21) | Osimertinib monotherapy | Category 1 | FLAURA | Same evidence base as exon 19 del |
| L858R (exon 21) | Osimertinib + carboplatin + pemetrexed | Category 1 | FLAURA2 | Same as exon 19 del indication |
| L858R (exon 21) | Amivantamab + lazertinib | Category 1 | MARIPOSA | Same as exon 19 del indication |
| Exon 20 insertion | Amivantamab + carboplatin + pemetrexed | Category 1 | PAPILLON | Exon 20 ins not sensitised to standard EGFR TKIs |

**Choice among exon 19 del / L858R options:** No head-to-head trial comparing all three. Osimertinib monotherapy remains the most widely used given long track record and tolerability. FLAURA2 combination preferred for CNS-heavy or high-volume disease. Amivantamab + lazertinib preferred when resistance mechanism profiling post-progression matters. All three are Category 1.

**Brain metastases note:** All three exon 19 del / L858R regimens have intracranial activity. Osimertinib (mono or combo) and amivantamab + lazertinib are both appropriate. CNS-directed therapy (SRS/WBRT) may be added for symptomatic lesions but does not displace systemic targeted therapy.

#### 1.1a Atypical EGFR mutations (S768I / L861Q / G719X) — NSCL-24 *(separate pathway)*

Atypical/uncommon EGFR TKI-sensitive mutations follow a **distinct** NCCN pathway (NSCL-24), not the exon 19 del / L858R pathway. In the cohort these are coded `egfr_status = "other_sensitising"` (19 cases).

| Preferred Regimens | Other Recommended | NCCN Category | Notes |
|---|---|---|---|
| Afatinib **or** Osimertinib | Dacomitinib, Erlotinib, Gefitinib | Preferred (afatinib/osimertinib) | Afatinib has the broadest label for atypical mutations |

**Critical distinction:** FLAURA2 (osimertinib + chemo) and MARIPOSA (amivantamab + lazertinib) are **NOT** indicated for atypical EGFR mutations — those are specific to classic exon 19 del / L858R (NSCL-21). A scorer that credits FLAURA2/MARIPOSA for S768I/L861Q/G719X is wrong.

### 1.2 ALK Rearrangements

| Preferred Regimens | NCCN Category | Key Trials | Notes |
|---|---|---|---|
| Alectinib | Category 1 | ALEX | Superior CNS penetration vs. crizotinib |
| Brigatinib | Category 1 | ALTA-1L | Category 1; comparable to alectinib |
| Ensartinib | Category 1 | eXalt3 | **Added v6.2026.** Category 1 preferred first-line (NSCL-27) |
| Lorlatinib | Category 1 | CROWN | 3rd-gen; 5-year CROWN data support as preferred — median PFS not yet reached; strongest CNS data |
| Crizotinib | Category 2A | PROFILE 1014 | No longer preferred; inferior CNS activity |

**Preferred first-line for ALK+:** Lorlatinib is increasingly favored based on CROWN 5-year outcomes (median PFS not reached vs 9.3 mo for crizotinib). All three 3rd/2nd-gen agents are Category 1; lorlatinib preferred especially with brain metastases.

**Brain metastases note:** Alectinib, brigatinib, and lorlatinib all have intracranial activity. Lorlatinib has the most robust CNS data and is the preferred choice when brain metastases are present.

### 1.3 ROS1 Rearrangements

| Preferred Regimens | NCCN Category | Notes |
|---|---|---|
| Entrectinib | Category 1 | Preferred when brain metastases present (CNS-penetrant) |
| Repotrectinib | Category 1 (preferred) | **Added v6.2026 (NSCL-30).** TRIDENT-1; preferred first-line, strong intracranial activity |
| Taletrectinib | Category 1 | **Added 2025.** FDA approved first- and later-line; robust intracranial activity (TRUST-I/II) |
| Crizotinib | Category 1 | Active against ROS1; inferior CNS penetration vs. entrectinib, repotrectinib, and taletrectinib |

**Brain metastases note:** Entrectinib, repotrectinib, and taletrectinib are all preferred over crizotinib when brain metastases are present.

### 1.4 BRAF V600E Mutation

| Preferred Regimens | NCCN Category | Rationale |
|---|---|---|
| Dabrafenib + trametinib | Category 1 | BRAF/MEK combination; BRAF monotherapy not recommended (resistance) |
| Binimetinib + encorafenib | Preferred | **Added v6.2026 (NSCL-32).** PHAROS; co-preferred BRAF/MEK combination |

Both BRAF/MEK combinations are preferred first-line as of v6.2026; the node is therefore **ambiguous** (two acceptable co-preferred regimens).

### 1.5 MET Exon 14 Skipping Mutation

| Preferred Regimens | NCCN Category | Key Trials |
|---|---|---|
| Capmatinib | Category 1 | GEOMETRY mono-1 |
| Tepotinib | Category 1 | VISION |

Both agents are Category 1; either is acceptable as primary recommendation.

### 1.6 RET Fusions

| Preferred Regimens | NCCN Category | Notes |
|---|---|---|
| Selpercatinib | Category 1 | High response rate including intracranial activity |
| Pralsetinib | Category 1 | Comparable to selpercatinib |

### 1.7 NTRK Fusions

| Preferred Regimens | NCCN Category | Notes |
|---|---|---|
| Larotrectinib | Category 1 | Tumour-agnostic FDA approval |
| Entrectinib | Category 1 | Tumour-agnostic; also covers ROS1 |
| Repotrectinib | Category 1 (preferred) | **Added v6.2026 (NSCL-33).** Preferred first-line NTRK option |

NTRK fusions are rare in NSCLC (<1%). All three approvals are tumour-agnostic (histology-independent).

### 1.8 KRAS G12C Mutation *(first-line: PD-L1 driven; KRAS inhibitors are second-line)*

KRAS G12C is present in ~13% of NSCLC adenocarcinomas and is now a required biomarker test at diagnosis. **First-line treatment follows the PD-L1 driven pathway (Section 2)** — KRAS G12C inhibitors are not yet approved or recommended first-line.

| Setting | Regimen | Notes |
|---|---|---|
| First-line | Per PD-L1 pathway (Section 2) | Standard chemoimmunotherapy |
| Second-line | Sotorasib (CodeBreaK 100/200) or adagrasib (KRYSTAL-1) | Category 1 second-line; not first-line scope |

**Scorer implication:** For first-line cases with KRAS G12C, correct answer is pembrolizumab monotherapy (if PD-L1 ≥50%) or chemoimmunotherapy — NOT sotorasib/adagrasib.

### 1.9 HER2 (ERBB2) Mutations — NSCL-36 *(first-line: PD-L1 driven; HER2-directed agents are SUBSEQUENT-line)*

HER2/ERBB2 mutations (exon 20 insertions, most commonly) are present in ~3% of NSCLC (26 cases in the cohort, 18 stage IV). **On NSCL-36 the FIRST-LINE column is "Systemic therapy (NSCL-K 1 of 6)" — i.e., the PD-L1-driven pathway (Section 2).** All HER2-directed agents sit in the **SUBSEQUENT-THERAPY** column (given on progression).

| Setting | Regimen | Notes |
|---|---|---|
| **First-line** | Per PD-L1 pathway (Section 2) | Standard chemoimmunotherapy — this is what the scorer returns |
| Subsequent (preferred) | Fam-trastuzumab deruxtecan-nxki (T-DXd) | Category 1; DESTINY-Lung02 |
| Subsequent (preferred) | Zongertinib | **Added 2025.** FDA accelerated approval Aug 2025; Beamion LUNG-1 |
| Subsequent (preferred) | Sevabertinib | **Added 2025.** SOHO-1 |
| Subsequent (certain circ.) | Ado-trastuzumab emtansine | Useful in certain circumstances |

**Scorer implication:** For treatment-naive first-line cases with a HER2 mutation, the correct answer is the PD-L1-driven pathway — **NOT** T-DXd, zongertinib, or sevabertinib. (This was a self-caught scorer bug: an initial v6.2026 draft returned the HER2 agents as first-line; corrected 2026-07-10 so ERBB2 falls through to the PD-L1 branch.)

### 1.10 NRG1 Gene Fusion — NSCL-37 *(first-line: PD-L1 driven; zenocutuzumab is SUBSEQUENT-line)*

NRG1 fusions are very rare in NSCLC (<1%; **0 cases carry an `nrg1_status` field in the cohort**, so this node never fires — documented for guideline parity). On NSCL-37 the FIRST-LINE column is again "Systemic therapy (NSCL-K 1 of 6)"; **zenocutuzumab-zbco (eNRGy) is SUBSEQUENT therapy only.**

| Setting | Regimen | Notes |
|---|---|---|
| **First-line** | Per PD-L1 pathway (Section 2) | Standard systemic therapy |
| Subsequent | Zenocutuzumab-zbco | eNRGy trial; biomarker-directed on progression |

**Scorer implication:** first-line NRG1 → PD-L1 pathway, not zenocutuzumab.

---

## Section 2 — Driver-Negative Pathways (PD-L1 / Chemoimmunotherapy)

These pathways apply when all tested drivers (EGFR, ALK, ROS1, BRAF, MET, RET, NTRK) are negative or unknown. Treatment selection is then guided by **histology**, **PD-L1 TPS**, and **ECOG performance status**.

### 2.1 Adenocarcinoma / Non-Squamous Histology

| PD-L1 TPS | Preferred Regimen | NCCN Category | Key Trial |
|---|---|---|---|
| ≥50% (high) | Pembrolizumab monotherapy | Category 1 | KEYNOTE-024 |
| 1–49% (intermediate) | Carboplatin + pemetrexed + pembrolizumab | Category 1 | KEYNOTE-189 |
| <1% (low) | Carboplatin + pemetrexed + pembrolizumab | Category 1 | KEYNOTE-189 |

**Alternative for any PD-L1 level (non-squamous):** Carboplatin + pemetrexed + atezolizumab + bevacizumab (IMpower150) — also Category 1. Not suitable if EGFR/ALK positive.

### 2.2 Squamous Cell Carcinoma

| PD-L1 TPS | Preferred Regimen | NCCN Category | Key Trial |
|---|---|---|---|
| ≥50% (high) | Pembrolizumab monotherapy | Category 1 | KEYNOTE-024 |
| 1–49% (intermediate) | Carboplatin + paclitaxel + pembrolizumab | Category 1 | KEYNOTE-407 |
| <1% (low) | Carboplatin + paclitaxel + pembrolizumab | Category 1 | KEYNOTE-407 |

**Alternative (squamous):** Carboplatin + nab-paclitaxel + pembrolizumab — equivalent to paclitaxel backbone.

**Note:** Pemetrexed is NOT used in squamous histology (inferior efficacy; histology-specific difference).

---

## Section 3 — ECOG Performance Status Cutoffs

| ECOG PS | Treatment Approach |
|---|---|
| 0–1 | Full systemic therapy per biomarker/PD-L1 pathway above |
| 2 | Reduced-intensity regimens; clinical judgement required; single-agent chemotherapy or reduced-dose doublet may be preferred |
| 3 | Best supportive care or single-agent chemotherapy only; goals-of-care discussion essential |
| 4 | Best supportive care; aggressive systemic therapy generally not appropriate |

---

## Section 4 — Brain Metastases Summary

| Drug | CNS Activity | Notes |
|---|---|---|
| Osimertinib | High | Preferred for EGFR+ with brain mets |
| Alectinib | High | Category 1 for ALK+ with brain mets |
| Brigatinib | High | Category 1 for ALK+ with brain mets |
| Lorlatinib | Highest among ALK TKIs | Most robust intracranial data |
| Entrectinib | Moderate | Preferred over crizotinib for ROS1+ with brain mets |
| Selpercatinib | High | Active intracranially for RET+ |
| Pembrolizumab | Limited | Immunotherapy has modest intracranial activity; typically combined with local CNS therapy |

---

## Section 5 — Scorer Correspondence Table

This table maps each clinical profile to the scorer's output and whether it matches these guidelines. The **Validated?** column is for oncologist review.

| # | Histology | Driver | PD-L1 | ECOG | Prior Tx | Scorer `primary_answer` | Acceptable Answers | Matches Guidelines? | Validated? |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Adeno | EGFR exon 19 del | any | 0–1 | Naive | osimertinib | [osimertinib, osimertinib+carbo/pem, amivantamab+lazertinib] | Yes | ☐ |
| 2 | Adeno | EGFR L858R | any | 0–1 | Naive | osimertinib | [osimertinib, osimertinib+carbo/pem, amivantamab+lazertinib] | Yes | ☐ |
| 3 | Adeno | EGFR exon 20 ins | any | 0–1 | Naive | amivantamab + carboplatin + pemetrexed | [amivantamab + carboplatin + pemetrexed] | Yes | ☐ |
| 3a | Adeno | EGFR atypical (S768I/L861Q/G719X) | any | 0–1 | Naive | afatinib | [afatinib, osimertinib, dacomitinib, erlotinib, gefitinib] | Yes (NSCL-24; no FLAURA2/MARIPOSA) | ☐ |
| 4 | Any | ALK+ | any | 0–1 | Naive | alectinib | [alectinib, brigatinib, ensartinib, lorlatinib] | Yes | ☐ |
| 5 | Any | ROS1+ | any | 0–1 | Naive | entrectinib | [entrectinib, repotrectinib, taletrectinib, crizotinib] | Yes | ☐ |
| 6 | Any | BRAF V600E | any | 0–1 | Naive | dabrafenib + trametinib | [dabrafenib + trametinib, binimetinib + encorafenib] | Yes (ambiguous, both preferred) | ☐ |
| 7 | Any | MET exon 14 | any | 0–1 | Naive | capmatinib | [capmatinib, tepotinib] | Yes | ☐ |
| 8 | Any | RET fusion | any | 0–1 | Naive | selpercatinib | [selpercatinib, pralsetinib] | Yes | ☐ |
| 9 | Any | NTRK fusion | any | 0–1 | Naive | larotrectinib | [larotrectinib, entrectinib, repotrectinib] | Yes | ☐ |
| 9a | Adeno | KRAS G12C | High ≥50% | 0–1 | Naive | pembrolizumab | [per PD-L1 pathway] | Yes (G12C TKIs are subsequent-line) | ☐ |
| 9b | Adeno | ERBB2/HER2 mutation | High ≥50% | 0–1 | Naive | pembrolizumab | [per PD-L1 pathway] | Yes (HER2 agents subsequent-line, NSCL-36) | ☐ |
| 9c | Adeno | NRG1 fusion | High ≥50% | 0–1 | Naive | pembrolizumab | [per PD-L1 pathway] | Yes (zenocutuzumab subsequent-line, NSCL-37) | ☐ |
| 10 | Adeno | None | High ≥50% | 0–1 | Naive | pembrolizumab | [pembrolizumab] | Yes | ☐ |
| 11 | Adeno | None | Intermediate 1–49% | 0–1 | Naive | carboplatin + pemetrexed + pembrolizumab | [carbo/pem/pembro, carbo/pem/atezo/bev] | Yes | ☐ |
| 12 | Squamous | None | High ≥50% | 0–1 | Naive | pembrolizumab | [pembrolizumab] | Yes | ☐ |
| 13 | Squamous | None | Low <1% | 0–1 | Naive | carboplatin + paclitaxel + pembrolizumab | [carbo/pac/pembro, carbo/nab-pac/pembro] | Yes | ☐ |
| 14 | Any | Any | Any | 3 | Any | best supportive care | [single-agent chemo, best supportive care] | Yes | ☐ |
| 15 | Any | Any | Any | 4 | Any | best supportive care | [best supportive care] | Yes | ☐ |

**Instructions for oncologist review:** For each row, verify that `primary_answer` and `acceptable_answers` match current NCCN guidelines. Check the ☐ box when confirmed. Flag any discrepancy with a note in the row.
