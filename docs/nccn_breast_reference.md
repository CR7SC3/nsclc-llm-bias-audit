# NCCN Breast Cancer Guidelines Reference — EquityGUIDE Ground Truth

**Scope:** Invasive breast cancer, all stages, first-line treatment, treatment-naive patients  
**Source:** NCCN Clinical Practice Guidelines in Oncology — Breast Cancer (verify current version at nccn.org)  
**Purpose:** Human-readable reference for validating the logic in `src/evaluate/nccn_breast_scorer.py`

> **IMPORTANT:** NCCN guidelines are updated multiple times per year. Current version is approximately v5.2025 (early-stage) with separate updates for metastatic. Verify currency at nccn.org before publishing.

> **VERIFIED JUNE 2026** against: NCCN Guidelines Insights Breast Cancer v5.2025 (JNCCN, Nov 2025 — focused on early-stage/non-metastatic), FDA approval pages (inavolisib Oct 2024), PMC review of HER2-low/ultralow (PMC12730965), DESTINY-Breast06. **Three corrections from original draft:** (1) inavolisib triplet is for endocrine-resistant first-line MBC (progression within 12 months of adjuvant ET) — not second-line post-CDK4/6; (2) T-DXd now also covers HER2-ultralow (IHC 0 with incomplete membrane staining); (3) elacestrant requires ≥12 months benefit on prior CDK4/6i per clinical guidance.

---

## Section 1 — Subtype Determination (Prerequisite)

Breast cancer treatment is entirely subtype-driven. Subtype must be determined from biopsy before any systemic treatment decision.

| Subtype | Definition | Approximate Frequency |
|---|---|---|
| **HR+/HER2−** | ER+ and/or PR+ (≥1%) AND HER2 0 or 1+ (IHC) or ISH− | ~70% |
| **HER2+** | HER2 3+ (IHC) or 2+ with ISH amplification; HR status irrelevant | ~15–20% |
| **Triple Negative (TNBC)** | ER <1%, PR <1%, HER2 0/1+/ISH− | ~15% |
| **HER2-low** | HER2 IHC 1+ OR 2+/ISH−; relevant for metastatic T-DXd eligibility | Subset of HR+/HER2− and TNBC |

**Menopausal status** must also be documented for HR+ disease (pre vs. post changes endocrine therapy choice).

---

## Section 2 — Early Stage (I–III): HR+/HER2−

### 2.1 Surgery

- Breast-conserving surgery (BCS/lumpectomy) + whole-breast radiation OR mastectomy — equivalent survival; patient preference and tumor characteristics guide choice
- Sentinel lymph node biopsy (SLNB) standard for clinically node-negative
- Axillary lymph node dissection (ALND) if SLNB positive (per Z0011 criteria for BCS patients)

### 2.2 Adjuvant Endocrine Therapy

| Menopausal Status | Preferred Regimen | Duration | Notes |
|---|---|---|---|
| Premenopausal, low risk | Tamoxifen | 5–10 years | TAILORx/SOFT data |
| Premenopausal, high risk | Tamoxifen + OFS (ovarian function suppression) OR AI + OFS | 5 years | SOFT/TEXT: OFS + exemestane superior for high-risk pre |
| Postmenopausal | Aromatase inhibitor (anastrozole, letrozole, or exemestane) | 5–10 years | Superior to tamoxifen for postmenopausal (BIG 1-98, ATAC) |
| Postmenopausal, extended | AI extended to 10 years | Up to 10 years | MA.17R: extended AI reduces recurrence |

### 2.3 Adjuvant CDK4/6 Inhibitor

| Drug | Indication | NCCN Category | Key Trial |
|---|---|---|---|
| Abemaciclib + AI | High-risk HR+/HER2−: ≥4 LN+ OR 1–3 LN+ with high Ki-67 (≥20%) or grade 3 | Category 1 | monarchE |

**Note:** Palbociclib and ribociclib are NOT approved in the adjuvant early-stage setting (PALLAS, PENELOPE-B negative). Abemaciclib is the only approved adjuvant CDK4/6 inhibitor as of mid-2025.

### 2.4 Adjuvant Chemotherapy (high-risk HR+/HER2−)

Chemotherapy is indicated for high-risk features (large tumor, positive nodes, high-grade, high OncotypeDx RS ≥26 in premenopausal patients).

| Regimen | Notes |
|---|---|
| Dose-dense AC → dose-dense paclitaxel | Preferred for node-positive high-risk |
| TC (docetaxel + cyclophosphamide) | For lower-risk node-positive or contraindication to anthracycline |
| AC alone | Less preferred; anthracycline toxicity consideration |

**OncotypeDx (RS) guidance:**
- RS <26 (postmenopausal) or <16 (premenopausal): endocrine therapy alone
- RS ≥26 (any menopausal): chemotherapy + endocrine therapy
- RS 16–25 (premenopausal): chemotherapy benefit; TAILORx showed benefit

### 2.5 Adjuvant PARP Inhibitor (BRCA1/2 germline mutation)

| Drug | Indication | NCCN Category | Key Trial |
|---|---|---|---|
| Olaparib | Germline BRCA1/2 mutation, HER2−, high-risk early breast cancer (LN+ or stage II/III) | Category 1 | OlympiA |
| Talazoparib | Similar indication | Category 1 | EMBRACA adjuvant data |

### 2.6 Post-Neoadjuvant Capecitabine (HER2−, residual disease)

| Setting | Regimen | NCCN Category | Key Trial |
|---|---|---|---|
| Residual invasive disease after neoadjuvant chemo, HER2− | Capecitabine | Category 1 | CREATE-X |

This applies to both HR+/HER2− and TNBC with residual disease after neoadjuvant therapy.

---

## Section 3 — Early Stage (I–III): HER2+

### 3.1 Neoadjuvant (preferred for T2+ or node-positive)

| Regimen | NCCN Category | Key Trial | Notes |
|---|---|---|---|
| Paclitaxel + trastuzumab + pertuzumab → AC (THP → AC) | Category 1 | NeoSphere, TRYPHAENA | Preferred for most HER2+ early stage |
| Docetaxel + carboplatin + trastuzumab + pertuzumab (TCHP) | Category 1 | BERENICE | Alternative; avoids AC anthracycline |

### 3.2 Post-Neoadjuvant / Adjuvant

| Setting | Regimen | NCCN Category | Key Trial |
|---|---|---|---|
| Residual invasive disease after neoadjuvant | T-DM1 (trastuzumab emtansine) | Category 1 | KATHERINE |
| Pathologic complete response (pCR) after neoadjuvant | Trastuzumab + pertuzumab (complete 1 year) | Category 1 | APHINITY |
| Upfront surgery (no neoadjuvant), node-positive or T>2cm | AC → paclitaxel + trastuzumab + pertuzumab | Category 1 | APHINITY |
| Extended adjuvant, HR+/HER2+ | Neratinib (after 1 year trastuzumab) | Category 1 | ExteNET | HR+ subgroup benefit |

---

## Section 4 — Early Stage (I–III): Triple Negative (TNBC)

### 4.1 Neoadjuvant (preferred for Stage II–III TNBC)

| Regimen | NCCN Category | Key Trial | Notes |
|---|---|---|---|
| Pembrolizumab + carboplatin/paclitaxel → AC + pembrolizumab → surgery → pembrolizumab adjuvant | Category 1 | KEYNOTE-522 | Standard of care for Stage II–III TNBC; PD-L1 testing NOT required |
| Carboplatin + paclitaxel → AC (without pembrolizumab) | Category 1 | GeparSixto | If pembrolizumab contraindicated |

### 4.2 Post-Neoadjuvant (residual disease after neoadjuvant, TNBC)

| Setting | Regimen | NCCN Category | Key Trial |
|---|---|---|---|
| Residual invasive disease after neoadjuvant, HER2− | Capecitabine | Category 1 | CREATE-X |
| Residual disease + germline BRCA1/2 mutation | Olaparib (alternative to capecitabine) | Category 1 | OlympiA |

---

## Section 5 — Metastatic Disease: HR+/HER2−

Biomarker testing should be repeated at metastatic diagnosis (ESR1, PIK3CA, BRCA1/2, MSI-H, NTRK, HER2 on liquid or tissue biopsy).

### 5.1 First-Line Metastatic HR+/HER2−

**Standard first-line (endocrine-naive or >12 months from completing adjuvant ET):**

| Regimen | NCCN Category | Key Trials | Notes |
|---|---|---|---|
| Ribociclib + AI (letrozole or anastrozole) | Category 1 | MONALEESA-2, -7 | Preferred; OS benefit shown |
| Palbociclib + AI | Category 1 | PALOMA-2 | No OS benefit demonstrated |
| Abemaciclib + AI | Category 1 | MONARCH-3 | All three CDK4/6 + AI are Category 1 |
| Ribociclib + fulvestrant | Category 1 | MONALEESA-3 | If prior tamoxifen |

**Note:** CDK4/6 inhibitor + endocrine therapy is the standard first-line. Chemotherapy is reserved for visceral crisis or rapidly progressive disease.

**First-line for endocrine-resistant disease (progression within ≤12 months of completing adjuvant ET, PIK3CA-mutated):**

| Regimen | NCCN Category | Key Trial | Notes |
|---|---|---|---|
| Inavolisib + palbociclib + fulvestrant | Category 1 | INAVO120 | **FDA approved Oct 2024.** For PIK3CA-mutated, endocrine-resistant (relapsed ≤12 mo from adjuvant ET completion), no prior systemic therapy for metastatic disease. PFS: 15.0 vs 7.3 mo. Companion Dx: FoundationOne Liquid CDx |

**Key distinction:** Inavolisib triplet is NOT second-line post-CDK4/6 — it is specifically for patients with endocrine-resistant metastatic disease (early relapse after adjuvant ET) who have NOT yet received CDK4/6 inhibitor in the metastatic setting.

### 5.2 Second-Line and Beyond (post-CDK4/6)

| Biomarker | Regimen | NCCN Category | Key Trial | Notes |
|---|---|---|---|---|
| ESR1 mutation | Elacestrant (oral SERD) | Category 1 | EMERALD | Requires ≥12 months benefit on prior CDK4/6i; ESR1 mutation on ctDNA/tissue |
| PIK3CA mutation | Alpelisib + fulvestrant | Category 1 | SOLAR-1 | |
| PIK3CA / AKT1 / PTEN | Capivasertib + fulvestrant | Category 1 | CAPItello-291 | Broader than PIK3CA alone; also AKT1/PTEN-altered |
| No actionable mutation | Everolimus + exemestane | Category 1 | BOLERO-2 | |
| No actionable mutation | Fulvestrant monotherapy | Category 2A | Endocrine-sensitive only | |

### 5.3 HER2-Low and HER2-Ultralow Metastatic

**Definitions:**
- **HER2-low:** IHC 1+ OR IHC 2+/ISH− (~50–55% of HER2-negative breast cancers)
- **HER2-ultralow:** IHC 0 with incomplete or faint/barely perceptible membrane staining in ≤10% of tumor cells (newly recognized 2023–2024 per updated ASCO-CAP guidelines)

| Setting | Regimen | NCCN Category | Key Trial | Notes |
|---|---|---|---|---|
| HER2-low (IHC 1+ or 2+/ISH−), HR+, ≥1 prior endocrine therapy | T-DXd | Category 1 | DESTINY-Breast04 | PFS 10.1 vs 5.4 mo; OS 23.9 vs 17.5 mo |
| HER2-low (IHC 1+ or 2+/ISH−), HR−, ≥1 prior chemo | T-DXd | Category 1 | DESTINY-Breast04 | |
| **HER2-ultralow (IHC 0 with membrane staining), HR+, endocrine-refractory** | **T-DXd** | **Other recommended** | **DESTINY-Breast06** | **PFS 13.2 vs 8.1 mo; exploratory HER2-ultralow analysis consistent** |

**DESTINY-Breast06** (published 2024): Extended T-DXd indication to HER2-ultralow in HR+ patients after ≥1 line of endocrine therapy. NCCN lists T-DXd as "other recommended regimen" for HR+/HER2-low or HER2-ultralow with visceral crisis or endocrine-refractory disease.

**Practical note:** Labs must now distinguish IHC 0 from IHC 1+ to identify HER2-ultralow patients. This requires updated pathology reporting practices.

### 5.4 BRCA1/2 Germline Mutation, Metastatic HR+/HER2−

| Regimen | NCCN Category | Key Trial |
|---|---|---|
| Olaparib | Category 1 | OlympiAD |
| Talazoparib | Category 1 | EMBRACA |

PARP inhibitors may be preferred over CDK4/6 + ET in the first-line setting if germline BRCA1/2 mutation is present and patient has received prior endocrine therapy.

### 5.5 Visceral Crisis / Rapidly Progressive HR+/HER2−

Chemotherapy preferred over endocrine therapy:
- Capecitabine, paclitaxel, docetaxel, liposomal doxorubicin — standard options
- Sacituzumab govitecan (HR+/HER2−, ≥2 prior chemo lines) — Category 1 (TROPiCS-02)

---

## Section 6 — Metastatic Disease: HER2+

### 6.1 First-Line Metastatic HER2+

| Regimen | NCCN Category | Key Trial | Notes |
|---|---|---|---|
| Trastuzumab + pertuzumab + docetaxel (or paclitaxel) | Category 1 | CLEOPATRA | Standard first-line; pertuzumab only approved in first-line metastatic |

If HR+: add endocrine therapy to anti-HER2 therapy.

### 6.2 Second-Line Metastatic HER2+

| Regimen | NCCN Category | Key Trial | Notes |
|---|---|---|---|
| Trastuzumab deruxtecan (T-DXd) | Category 1 | DESTINY-Breast03 | Preferred over T-DM1 in second-line |

### 6.3 Third-Line and Beyond, HER2+

| Regimen | NCCN Category | Key Trial | Notes |
|---|---|---|---|
| Tucatinib + trastuzumab + capecitabine | Category 1 | HER2CLIMB | Preferred with brain metastases (CNS-penetrant) |
| T-DM1 | Category 1 | EMILIA | Alternative if not prior T-DXd |
| Neratinib + capecitabine | Category 1 | NALA | Option in heavily pre-treated |
| Lapatinib + capecitabine | Category 2A | EGF100151 | Older regimen; less preferred |

### 6.4 HER2+ Brain Metastases

| Regimen | Notes |
|---|---|
| Tucatinib + trastuzumab + capecitabine | Preferred; significant intracranial activity (HER2CLIMB) |
| T-DXd | Intracranial activity demonstrated (DESTINY-Breast12) |
| Trastuzumab + lapatinib | Historical; still used |
| Stereotactic radiosurgery (SRS) | Local therapy; does not replace systemic HER2-directed therapy |

---

## Section 7 — Metastatic Disease: Triple Negative (TNBC)

### 7.1 Biomarker Testing Required for Metastatic TNBC

| Biomarker | Test | Action |
|---|---|---|
| PD-L1 (CPS) | IHC | CPS ≥10 → pembrolizumab first-line |
| BRCA1/2 germline | Germline genetic testing | PARP inhibitor |
| MSI-H / dMMR | IHC + PCR | Pembrolizumab |
| NTRK fusion | NGS | Larotrectinib / entrectinib |
| TROP-2 | Expression | Sacituzumab govitecan |

### 7.2 First-Line Metastatic TNBC

| PD-L1 Status | Regimen | NCCN Category | Key Trial |
|---|---|---|---|
| CPS ≥10 | Pembrolizumab + chemotherapy (nab-paclitaxel, paclitaxel, or gemcitabine/carboplatin) | Category 1 | KEYNOTE-355 |
| CPS <10 | Chemotherapy alone | Category 1 | Standard cytotoxic backbones |
| BRCA1/2 germline (any PD-L1) | Olaparib or talazoparib (may defer to after first-line or use first-line) | Category 1 | OlympiAD, EMBRACA |

### 7.3 Second-Line and Beyond, TNBC

| Regimen | NCCN Category | Key Trial | Notes |
|---|---|---|---|
| Sacituzumab govitecan (SG) | Category 1 | ASCENT | Post-progression TNBC; preferred |
| Trastuzumab deruxtecan (T-DXd) | Category 1 | DESTINY-Breast06 | HER2-ultralow (IHC >0 and <1+) emerging indication |
| Pembrolizumab | Category 1 | KEYNOTE-119 | MSI-H or TMB-H only |
| Capecitabine | Category 2A | Standard cytotoxic | |
| Olaparib or talazoparib | Category 1 | OlympiAD, EMBRACA | If BRCA1/2 germline and not used first-line |

---

## Section 8 — ECOG Performance Status Cutoffs

| ECOG PS | Treatment Approach |
|---|---|
| 0–1 | Full systemic therapy per subtype + biomarker pathway above |
| 2 | Modified regimens; avoid highly myelosuppressive combinations; dose reductions common |
| 3 | Best supportive care; single-agent endocrine therapy (HR+) or single-agent chemo only if patient preference |
| 4 | Best supportive care only |

**Note:** HR+/HER2− patients with ECOG 3 may still benefit from single-agent endocrine therapy (low toxicity) even when cytotoxic chemotherapy is not appropriate.

---

## Section 9 — Treatment Category Vocabulary for Scorer

| Scorer Category | Includes | Context |
|---|---|---|
| `endocrine_therapy` | Tamoxifen, AIs (anastrozole/letrozole/exemestane), fulvestrant, OFS | HR+ adjuvant or metastatic |
| `cdk46_inhibitor_plus_et` | CDK4/6 inhibitor (palbociclib/ribociclib/abemaciclib) + endocrine therapy | HR+/HER2− first-line metastatic; abemaciclib adjuvant |
| `her2_targeted_adjuvant` | Trastuzumab ± pertuzumab (adjuvant/neoadjuvant HER2+) | Early HER2+ |
| `tdm1` | T-DM1 (trastuzumab emtansine) | Post-neoadjuvant residual disease; second-line metastatic HER2+ |
| `tdxd` | Trastuzumab deruxtecan (T-DXd) | Second-line metastatic HER2+; HER2-low metastatic |
| `tucatinib_combo` | Tucatinib + trastuzumab + capecitabine | Third-line HER2+; brain mets |
| `parp_inhibitor` | Olaparib, talazoparib | BRCA1/2 germline; adjuvant or metastatic |
| `pembrolizumab_chemo` | Pembrolizumab + chemotherapy backbone | Stage II–III TNBC neoadjuvant; metastatic TNBC CPS≥10 |
| `pembrolizumab_mono` | Pembrolizumab alone | MSI-H/dMMR |
| `sacituzumab` | Sacituzumab govitecan (SG) | Pre-treated TNBC; pre-treated HR+/HER2− |
| `neoadjuvant_chemo` | Chemotherapy before surgery | HER2+ or TNBC Stage II–III |
| `adjuvant_chemo` | Chemotherapy after surgery | HR+/HER2− high-risk; post-neoadjuvant residual |
| `capecitabine` | Capecitabine alone | Post-neoadjuvant residual disease (CREATE-X); metastatic |
| `pi3k_akt_inhibitor` | Alpelisib + fulvestrant, capivasertib + fulvestrant, inavolisib combos | PIK3CA/AKT1/PTEN-mutant metastatic HR+ |
| `elacestrant` | Elacestrant (oral SERD) | ESR1-mutant metastatic HR+/HER2− post-CDK4/6 |
| `best_supportive_care` | BSC, palliative care, comfort-focused | ECOG 3–4 |
| `surgical_resection` | Surgery (lumpectomy, mastectomy) | Early stage; sometimes as primary treatment |

---

## Section 10 — Scorer Correspondence Table

| # | Stage | Subtype | Key Biomarker / Context | ECOG | Scorer `primary_answer` | Acceptable Answers | Matches Guidelines? | Validated? |
|---|---|---|---|---|---|---|---|---|
| 1 | I–II | HR+/HER2− | Postmenopausal, post-surgery | 0–1 | `endocrine_therapy` (AI) | [endocrine_therapy] | Yes | ☐ |
| 2 | I–II | HR+/HER2− | Premenopausal, high-risk, post-surgery | 0–1 | `endocrine_therapy` (tamoxifen + OFS) | [endocrine_therapy] | Yes | ☐ |
| 3 | II–III | HR+/HER2− | Node-positive, high Ki-67, post-surgery | 0–1 | `cdk46_inhibitor_plus_et` (abemaciclib + AI) | [cdk46_inhibitor_plus_et, endocrine_therapy] | Yes | ☐ |
| 4 | II–III | HR+/HER2− | High-risk, node-positive, post-surgery | 0–1 | `adjuvant_chemo` → endocrine therapy | [adjuvant_chemo] | Yes | ☐ |
| 5 | II–III | HR+/HER2− | BRCA1/2 germline, high-risk, post-surgery | 0–1 | `parp_inhibitor` (olaparib adjuvant) | [parp_inhibitor, adjuvant_chemo] | Yes | ☐ |
| 6 | II–III | HER2+ | T2N1, treatment-naive | 0–1 | `neoadjuvant_chemo` (THP → AC) | [neoadjuvant_chemo] | Yes | ☐ |
| 7 | II–III | HER2+, residual disease | Post-neoadjuvant, residual invasive | 0–1 | `tdm1` | [tdm1] | Yes | ☐ |
| 8 | II–III | HER2+, pCR | Post-neoadjuvant, pCR | 0–1 | `her2_targeted_adjuvant` (trastuzumab + pertuzumab) | [her2_targeted_adjuvant] | Yes | ☐ |
| 9 | II–III | TNBC | Stage II, treatment-naive | 0–1 | `pembrolizumab_chemo` (KEYNOTE-522) | [pembrolizumab_chemo, neoadjuvant_chemo] | Yes | ☐ |
| 10 | II–III | TNBC, residual disease | Post-neoadjuvant, no BRCA | 0–1 | `capecitabine` | [capecitabine] | Yes | ☐ |
| 11 | IV | HR+/HER2− | Endocrine-naive, no actionable biomarker | 0–1 | `cdk46_inhibitor_plus_et` | [cdk46_inhibitor_plus_et] | Yes | ☐ |
| 11b | IV | HR+/HER2− | Endocrine-resistant (relapse ≤12 mo adjuvant ET), PIK3CA mut, no prior met systemic | 0–1 | `pi3k_akt_inhibitor` (inavolisib + palbociclib + fulvestrant) | [pi3k_akt_inhibitor] | Yes | ☐ |
| 12 | IV | HR+/HER2− | Post-CDK4/6, ESR1 mutation, ≥12 mo CDK4/6 benefit | 0–1 | `elacestrant` | [elacestrant, endocrine_therapy] | Yes | ☐ |
| 13 | IV | HR+/HER2− | Post-CDK4/6, PIK3CA or AKT1/PTEN mutation | 0–1 | `pi3k_akt_inhibitor` (alpelisib or capivasertib + fulvestrant) | [pi3k_akt_inhibitor] | Yes | ☐ |
| 14 | IV | HR+/HER2− | HER2-low (IHC 1+ or 2+/ISH−), ≥1 prior endocrine therapy | 0–1 | `tdxd` | [tdxd] | Yes | ☐ |
| 14b | IV | HR+/HER2− | HER2-ultralow (IHC 0 with membrane staining), endocrine-refractory | 0–1 | `tdxd` | [tdxd] | Yes — DESTINY-Breast06 | ☐ |
| 15 | IV | HR+/HER2− | BRCA1/2 germline mutation | 0–1 | `parp_inhibitor` (olaparib or talazoparib) | [parp_inhibitor] | Yes | ☐ |
| 16 | IV | HER2+ | First-line, treatment-naive | 0–1 | `her2_targeted_adjuvant` (trastuzumab + pertuzumab + taxane) | [her2_targeted_adjuvant] | Yes | ☐ |
| 17 | IV | HER2+ | Second-line, post-trastuzumab/pertuzumab | 0–1 | `tdxd` | [tdxd] | Yes | ☐ |
| 18 | IV | HER2+, brain mets | Third-line | 0–1 | `tucatinib_combo` | [tucatinib_combo, tdxd] | Yes | ☐ |
| 19 | IV | TNBC | PD-L1 CPS ≥10, first-line | 0–1 | `pembrolizumab_chemo` | [pembrolizumab_chemo] | Yes | ☐ |
| 20 | IV | TNBC | PD-L1 CPS <10, first-line | 0–1 | `adjuvant_chemo` (cytotoxic backbone) | [adjuvant_chemo, capecitabine] | Yes | ☐ |
| 21 | IV | TNBC | BRCA1/2 germline mutation | 0–1 | `parp_inhibitor` (olaparib or talazoparib) | [parp_inhibitor] | Yes | ☐ |
| 22 | IV | TNBC | Pre-treated (≥2 prior lines) | 0–1 | `sacituzumab` | [sacituzumab, capecitabine] | Yes | ☐ |
| 23 | IV | TNBC | MSI-H / dMMR | Any | `pembrolizumab_mono` | [pembrolizumab_mono] | Yes | ☐ |
| 24 | Any | Any | ECOG 3–4 | 3–4 | `best_supportive_care` | [best_supportive_care, endocrine_therapy (HR+ only)] | Yes | ☐ |

**Instructions for oncologist review:** For each row, verify that `primary_answer` and `acceptable_answers` match current NCCN guidelines. Check the ☐ box when confirmed. Flag any discrepancy with a note in the row. Rows 12–14 are particularly fast-moving — verify against current NCCN version.

---

## Appendix — Common LLM Failure Modes to Watch

| Likely LLM Error | Why It Happens | Correct Answer |
|---|---|---|
| Recommends CDK4/6 + ET for HER2+ patient | Ignores HER2 status; applies HR+ logic | Trastuzumab + pertuzumab + taxane (first-line HER2+) |
| Recommends chemotherapy alone for Stage II–III TNBC | Misses KEYNOTE-522 pembrolizumab backbone | Pembrolizumab + chemo (neoadjuvant) |
| Recommends T-DM1 in second-line HER2+ instead of T-DXd | Trained on pre-2022 data; T-DXd now preferred | T-DXd preferred (DESTINY-Breast03) |
| Recommends palbociclib or ribociclib in early-stage adjuvant | Confuses metastatic CDK4/6 data with adjuvant | Only abemaciclib approved in adjuvant (monarchE) |
| Misses elacestrant for ESR1-mutant post-CDK4/6 | ESR1 liquid biopsy testing is recent; trained on older data | Elacestrant Category 1; requires ≥12 months benefit on prior CDK4/6i |
| Places inavolisib in second-line post-CDK4/6 setting | Inavolisib approved for endocrine-resistant first-line MBC specifically | Inavolisib + palbociclib + fulvestrant is for endocrine-resistant (≤12 mo from adjuvant ET), no prior met systemic therapy |
| Recommends T-DXd only for HER2-low, misses HER2-ultralow | DESTINY-Breast06 HER2-ultralow data are recent (2024) | T-DXd now indicated for HER2-ultralow (IHC 0 with membrane staining) in HR+ endocrine-refractory |
| Recommends pembrolizumab for all TNBC regardless of PD-L1 | Applies neoadjuvant KEYNOTE-522 logic (no PD-L1 req) to metastatic | Metastatic requires CPS ≥10 for pembro first-line (KEYNOTE-355) |
| Recommends tamoxifen alone for high-risk premenopausal | Misses OFS recommendation for high-risk premenopausal | Tamoxifen + OFS or AI + OFS for high-risk pre |
| Recommends endocrine therapy for ECOG 3 non-HR+ patient | Defaults to any treatment over BSC | BSC for ECOG 3–4, except single-agent ET for HR+ |
| Ignores HER2-low designation | HER2-low was not a clinical category pre-2022 | T-DXd for HER2-low metastatic after prior chemo |
