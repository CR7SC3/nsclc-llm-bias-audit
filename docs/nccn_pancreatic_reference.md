# NCCN Pancreatic Cancer Guidelines Reference — EquityGUIDE Ground Truth

**Scope:** Pancreatic adenocarcinoma, all stages, first-line treatment, treatment-naive patients  
**Source:** NCCN Clinical Practice Guidelines in Oncology — Pancreatic Adenocarcinoma (verify current version at nccn.org)  
**Purpose:** Human-readable reference for validating the logic in `src/evaluate/nccn_pancreatic_scorer.py`

> **IMPORTANT:** NCCN guidelines are updated multiple times per year. Current version is approximately v2.2026. Before publishing research findings, verify currency at nccn.org (free registration required).

> **VERIFIED JUNE 2026** against: PMC systematic review (PMC12839337), ASCO/JCO published data (NAPOLI-3, POLO, PRODIGE 24, eNRGy trial), FDA approval pages. NCCN PDFs block unauthenticated access. **Three corrections from original draft:** (1) olaparib maintenance is BRCA1/2 germline only — PALB2 removed; (2) zenocutuzumab added for NRG1+ (FDA approved); (3) daraxonrasib added as breakthrough-designated KRAS G12X agent (not yet approved for first-line). NALIRIFOX position vs FOLFIRINOX clarified.

---

## Section 1 — Resectability Classification

Resectability status is the primary decision variable in pancreatic cancer and must be determined before treatment selection. Unlike most cancers, stage alone does not drive first-line treatment — surgical eligibility does.

| Classification | Definition | Key Features |
|---|---|---|
| **Resectable** | No arterial contact; venous contact ≤180° with normal contour | Surgery is the primary treatment goal |
| **Borderline resectable** | Venous involvement >180° or reconstructable; arterial contact ≤180° | Neoadjuvant therapy first; surgery if downstaged |
| **Locally advanced** | Arterial encasement >180°; or unreconstructable vein | Not surgically resectable; systemic therapy ± radiation |
| **Metastatic** | Distant organ metastases (liver most common; peritoneum, lung) | Systemic therapy only; palliative intent |

**Performance status prerequisite:** ECOG PS must be assessed before any treatment decision. PS ≥3 precludes combination chemotherapy regardless of resectability.

---

## Section 2 — Resectable Disease

Surgery is the primary treatment for resectable pancreatic cancer. Adjuvant chemotherapy is given after resection; neoadjuvant is an acceptable alternative for selected patients.

### 2.1 Adjuvant Chemotherapy (post-resection, started within 12 weeks)

| Regimen | NCCN Category | Key Trial | Notes |
|---|---|---|---|
| mFOLFIRINOX (oxaliplatin + irinotecan + leucovorin + fluorouracil) | Category 1 | PRODIGE 24/CCTG PA.6 | Preferred for ECOG 0–1; 54.4 vs 35.0 mo median OS vs gemcitabine |
| Gemcitabine + capecitabine | Category 1 | ESPAC-4 | Preferred when mFOLFIRINOX not tolerated |
| Gemcitabine monotherapy | Category 1 | CONKO-001 | Acceptable; inferior to above combinations |

**BRCA1/2 or PALB2 germline mutation — adjuvant:** Consider platinum-containing regimen (FOLFIRINOX or gemcitabine + cisplatin) as preferred backbone given HR deficiency. Note: olaparib maintenance is approved for BRCA1/2 germline only — PALB2 mutation does not qualify for approved olaparib maintenance.

### 2.2 Neoadjuvant Approach (alternative for resectable)

Neoadjuvant chemotherapy is a Category 2A option for resectable disease and is gaining preference at high-volume centers. It is not yet Category 1 for clearly resectable cases.

| Regimen | Notes |
|---|---|
| mFOLFIRINOX | Preferred for ECOG 0–1 |
| Gemcitabine + nab-paclitaxel | Alternative |

Re-evaluate resectability after 2–4 months. If resectable, proceed to surgery → adjuvant chemotherapy.

---

## Section 3 — Borderline Resectable Disease

Neoadjuvant chemotherapy is the standard of care for borderline resectable disease. The goal is to downstage to allow margin-negative (R0) resection.

### 3.1 Neoadjuvant Regimens

| Regimen | NCCN Category | Notes |
|---|---|---|
| mFOLFIRINOX | Category 1 | Preferred for ECOG 0–1; ~30% conversion to resectability |
| Gemcitabine + nab-paclitaxel | Category 2A | Alternative; lower toxicity |
| NALIRIFOX (liposomal irinotecan + oxaliplatin + leucovorin + 5-FU) | Category 2A | Emerging; data from NAPOLI-3 |

### 3.2 Sequencing After Neoadjuvant

- After 2–4 months: restage with CT ± EUS
- If resectable: surgery → adjuvant chemotherapy (4–8 cycles total planned)
- If still borderline: add chemoradiation or continue systemic therapy
- If locally advanced: treat as locally advanced (Section 4)

Chemoradiation (gemcitabine-based or fluorouracil-based, with SBRT or conventional RT) can be incorporated after neoadjuvant chemotherapy, particularly if CA 19-9 normalized and good response.

---

## Section 4 — Locally Advanced (Unresectable) Disease

Systemic induction chemotherapy is first-line for locally advanced disease. A small minority may downstage to resectability.

### 4.1 Induction Chemotherapy

| Regimen | NCCN Category | Notes |
|---|---|---|
| mFOLFIRINOX | Category 1 | Preferred for ECOG 0–1 |
| Gemcitabine + nab-paclitaxel | Category 1 | Alternative; preferred for ECOG 2 |
| NALIRIFOX | Category 2A | Emerging option |
| Gemcitabine monotherapy | Category 2A | For ECOG 2–3 or comorbidities |

### 4.2 After Induction (3–6 months)

- Re-evaluate resectability: ~10–15% may downstage
- If no progression: consider consolidative chemoradiation (SBRT 33–40 Gy in 5 fractions, or conventional 45–54 Gy with concurrent fluorouracil or gemcitabine)
- Chemoradiation is preferred in the absence of distant disease progression and if local control is the limiting factor

---

## Section 5 — Metastatic Disease

Metastatic pancreatic cancer represents ~50% of incident cases and is the most common presentation. Treatment is palliative intent.

### 5.1 Biomarker Testing — Required at Diagnosis

All patients with metastatic pancreatic cancer should have the following testing:

| Biomarker | Test | Actionable Finding | Treatment Implication |
|---|---|---|---|
| BRCA1/2, PALB2 | Germline + somatic NGS | Germline BRCA1/2 mutation | Platinum-based first-line; **olaparib maintenance (BRCA1/2 germline only)** |
| BRCA1/2, PALB2 | Germline + somatic NGS | Germline PALB2 mutation | Platinum-based first-line; no approved maintenance (olaparib NOT indicated) |
| MSI-H / dMMR | IHC (MLH1/MSH2/MSH6/PMS2) + PCR | MSI-H | Pembrolizumab Category 1 |
| NTRK fusion | NGS | NTRK1/2/3 fusion | Larotrectinib or entrectinib |
| NRG1 fusion | NGS | NRG1 fusion | **Zenocutuzumab — FDA approved 2024 (eNRGy trial); ~1% of PDAC** |
| KRAS G12C | NGS | G12C mutation | Sotorasib or adagrasib second-line (Category 2B); G12C is rare in PDAC (~1–2%) |
| KRAS G12D | NGS | G12D mutation | No approved agent; daraxonrasib (RMC-6236) has FDA Breakthrough Therapy designation for KRAS G12 mut PDAC — registrational trials ongoing |
| KRAS G12V | NGS | G12V mutation | No approved agent; KRAS G12V ~30% of PDAC |
| TMB-H | NGS | TMB ≥10 mut/Mb | Pembrolizumab (Category 2B) |

> **KRAS prevalence in PDAC:** ~95% of pancreatic adenocarcinomas have KRAS mutations. Distribution: G12D ~40%, G12V ~30%, G12R ~15%, G12C ~1–2%. G12D and G12V are the dominant targets — neither has an approved therapy as of June 2026.

### 5.2 MSI-H / dMMR (any ECOG)

| Setting | Regimen | NCCN Category | Key Trial |
|---|---|---|---|
| First-line MSI-H | Pembrolizumab | Category 1 | KEYNOTE-158 |

MSI-H is rare in pancreatic cancer (~1%). When present, pembrolizumab is preferred over cytotoxic chemotherapy.

### 5.3 ECOG 0–1, No Actionable Biomarker

| Regimen | NCCN Category | Key Trial | Notes |
|---|---|---|---|
| mFOLFIRINOX | Category 1 | PRODIGE 4/ACCORD 11 | Preferred; requires adequate biliary drainage and no sepsis |
| Gemcitabine + nab-paclitaxel | Category 1 | MPACT | Equivalent; preferred if biliary stent complications or borderline PS |
| NALIRIFOX (liposomal irinotecan + oxaliplatin + leucovorin + 5-FU) | Category 1 | NAPOLI-3 | Demonstrated superior PFS vs gem/nab-pac; emerging as co-preferred |

**Choice between mFOLFIRINOX and gemcitabine + nab-paclitaxel:** No head-to-head trial. Preference driven by:
- Patient tolerance / neuropathy risk (oxaliplatin accumulates — caution with pre-existing neuropathy)
- Biliary drainage status (FOLFIRINOX not recommended without adequate biliary decompression)
- BRCA/PALB2 status (platinum preferred if mutation-positive)
- Center experience

### 5.4 BRCA1/2 Germline Mutation, ECOG 0–1

| Line | Regimen | NCCN Category | Key Trial | Notes |
|---|---|---|---|---|
| First-line | mFOLFIRINOX or gemcitabine + cisplatin | Category 1 | — | Platinum backbone required to qualify for olaparib maintenance |
| Maintenance (after ≥16 weeks platinum, no progression) | Olaparib | Category 1 | POLO | **BRCA1/2 germline ONLY.** Switch maintenance; extends PFS (7.4 vs 3.8 mo) but no OS benefit |

**Olaparib maintenance** is the only FDA-approved maintenance therapy in pancreatic cancer as of June 2026. It is restricted to germline **BRCA1/2** mutation carriers only — **PALB2 mutation does NOT qualify** for approved olaparib maintenance (POLO trial enrolled BRCA1/2 only). PALB2-mutated patients should receive platinum-based first-line but currently have no approved maintenance.

### 5.4b PALB2 Germline Mutation, ECOG 0–1

| Line | Regimen | Notes |
|---|---|---|
| First-line | mFOLFIRINOX or gemcitabine + cisplatin (platinum backbone) | Platinum preferred; PALB2 confers HR deficiency similar to BRCA |
| Maintenance | No FDA-approved option | Olaparib NOT approved; clinical trial enrollment preferred (Apollo/EA2192 evaluated olaparib for resected BRCA/PALB2) |

### 5.5 ECOG 2, No Actionable Biomarker

| Regimen | NCCN Category | Notes |
|---|---|---|
| Gemcitabine + nab-paclitaxel | Category 1 | Preferred; less hematologic toxicity than FOLFIRINOX |
| Gemcitabine monotherapy | Category 2A | If nab-paclitaxel not tolerated |
| NALIRIFOX | Category 2A | May be considered for select ECOG 2 patients |

### 5.6 ECOG 3–4

| Regimen | NCCN Category | Notes |
|---|---|---|
| Best supportive care | Category 1 | Aggressive chemotherapy generally not indicated |
| Gemcitabine monotherapy | Category 2B | Only if patient strongly prefers treatment and goals align |

---

## Section 6 — ECOG Performance Status Cutoffs

| ECOG PS | Treatment Approach |
|---|---|
| 0–1 | Full combination chemotherapy; FOLFIRINOX or gem/nab-pac |
| 2 | Reduced-intensity regimen; gemcitabine + nab-paclitaxel preferred; gemcitabine mono acceptable |
| 3 | Best supportive care; gemcitabine mono only if patient preference and goals-aligned |
| 4 | Best supportive care only |

---

## Section 7 — Treatment Category Vocabulary for Scorer

| Scorer Category | Includes | Notes |
|---|---|---|
| `folfirinox` | mFOLFIRINOX, FOLFIRINOX | Most common first-line for ECOG 0–1 metastatic |
| `gemcitabine_nabpaclitaxel` | Gemcitabine + nab-paclitaxel, gem/abraxane | Major alternative to FOLFIRINOX |
| `nalirifox` | Liposomal irinotecan + oxaliplatin + LV + 5-FU | Emerging co-preferred (NAPOLI-3) |
| `gemcitabine_capecitabine` | Gemcitabine + capecitabine | Used adjuvant only |
| `gemcitabine_mono` | Gemcitabine alone | ECOG 2–3 or comorbidities |
| `surgical_resection` | Whipple, distal pancreatectomy, total pancreatectomy ± adjuvant | With adjuvant chemo |
| `neoadjuvant_chemo` | Neoadjuvant before surgery | Borderline resectable standard; Category 2A for resectable |
| `chemoradiation` | RT + concurrent gemcitabine or 5-FU/capecitabine ± SBRT | Locally advanced after induction |
| `olaparib` | Olaparib (Lynparza) | Maintenance only; BRCA1/2 germline |
| `pembrolizumab` | Pembrolizumab (Keytruda) | MSI-H/dMMR only |
| `larotrectinib` | Larotrectinib or entrectinib | NTRK fusion |
| `zenocutuzumab` | Zenocutuzumab (MCLA-128) | NRG1 fusion — FDA approved 2024 |
| `best_supportive_care` | BSC, palliative care, comfort-focused | ECOG 3–4 |

---

## Section 8 — Scorer Correspondence Table

| # | Stage / Resectability | Key Biomarker | ECOG | Scorer `primary_answer` | Acceptable Answers | Matches Guidelines? | Validated? |
|---|---|---|---|---|---|---|---|
| 1 | Resectable | None | 0–1 | `surgical_resection` → adjuvant mFOLFIRINOX | [surgical_resection, neoadjuvant_chemo] | Yes | ☐ |
| 2 | Resectable, post-op | None | 0–1 | `folfirinox` (adjuvant) | [folfirinox, gemcitabine_capecitabine, gemcitabine_mono] | Yes | ☐ |
| 3 | Borderline resectable | None | 0–1 | `neoadjuvant_chemo` (mFOLFIRINOX) | [neoadjuvant_chemo] | Yes | ☐ |
| 4 | Locally advanced | None | 0–1 | `folfirinox` | [folfirinox, gemcitabine_nabpaclitaxel, nalirifox] | Yes | ☐ |
| 5 | Locally advanced | None | 0–1 | `chemoradiation` (after induction) | [chemoradiation, folfirinox, gemcitabine_nabpaclitaxel] | Yes | ☐ |
| 6 | Metastatic | None | 0–1 | `folfirinox` | [folfirinox, gemcitabine_nabpaclitaxel, nalirifox] | Yes | ☐ |
| 7 | Metastatic | None | 0–1 | `gemcitabine_nabpaclitaxel` | [folfirinox, gemcitabine_nabpaclitaxel, nalirifox] | Yes | ☐ |
| 8 | Metastatic | BRCA1/2 germline | 0–1 | `folfirinox` | [folfirinox, gemcitabine_mono (cisplatin backbone)] | Yes | ☐ |
| 9 | Metastatic, on platinum ≥16 wks no PD | **BRCA1/2 germline only** | 0–1 | `olaparib` (maintenance) | [olaparib] | Yes | ☐ |
| 9b | Metastatic | PALB2 germline | 0–1 | `folfirinox` | [folfirinox, gemcitabine_mono (cisplatin backbone)] | Yes — no approved maintenance | ☐ |
| 10 | Metastatic | MSI-H / dMMR | Any | `pembrolizumab` | [pembrolizumab] | Yes | ☐ |
| 11 | Metastatic | NTRK fusion | Any | `larotrectinib` | [larotrectinib, entrectinib] | Yes | ☐ |
| 11b | Metastatic | NRG1 fusion | Any | `zenocutuzumab` | [zenocutuzumab] | Yes | ☐ |
| 12 | Metastatic | None | 2 | `gemcitabine_nabpaclitaxel` | [gemcitabine_nabpaclitaxel, gemcitabine_mono] | Yes | ☐ |
| 13 | Any | None | 3–4 | `best_supportive_care` | [best_supportive_care, gemcitabine_mono] | Yes | ☐ |

**Instructions for oncologist review:** For each row, verify that `primary_answer` and `acceptable_answers` match current NCCN guidelines. Check the ☐ box when confirmed. Flag any discrepancy with a note in the row.

---

## Appendix — Common LLM Failure Modes to Watch

Based on NSCLC experience, anticipate these miscategorization patterns for pancreatic cancer:

| Likely LLM Error | Why It Happens | Correct Answer |
|---|---|---|
| Recommends FOLFIRINOX for ECOG 3–4 | Model defaults to "standard first-line" without reading PS | BSC or gem mono |
| Recommends surgery for locally advanced | Conflates stage with resectability | Systemic therapy |
| Recommends olaparib without platinum preceding it | Misses the ≥16-week platinum prerequisite | FOLFIRINOX first, then olaparib maintenance |
| Recommends olaparib maintenance for PALB2 mutation | PALB2 is NOT an approved olaparib indication | Platinum-based first-line; no approved maintenance for PALB2 |
| Recommends pembrolizumab for MSS tumor | Applies lung cancer PD-L1 logic to pancreatic cancer | Pembrolizumab only if MSI-H/dMMR |
| Recommends gemcitabine + capecitabine in metastatic setting | Adjuvant regimen applied to wrong context | This combination is adjuvant-only |
| Misses BRCA/PALB2 → platinum preference | Does not extract germline mutation from note | FOLFIRINOX or gem+cisplatin preferred for BRCA/PALB2 carriers |
| Recommends daraxonrasib as approved first-line for KRAS G12D | Not yet approved; breakthrough therapy only | Cytotoxic chemotherapy (FOLFIRINOX or gem/nab-pac) is first-line regardless of KRAS status |
| Misses zenocutuzumab for NRG1 fusion | NRG1 fusion is a rare but actionable alteration | Zenocutuzumab is FDA-approved for NRG1+ PDAC |
