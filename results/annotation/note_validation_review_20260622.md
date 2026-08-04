# GENIE BPC NSCLC: Oncologist Note Validation Review

**Date:** 20260622  |  **N:** 39 cases  |  **Seed:** 42

## Instructions

For each case, rate the generated clinical note using the 5-item rubric:

1. **Plausibility (1–5):** Does this read like a real oncology consult note?
   `1=implausible, 3=plausible with concerns, 5=indistinguishable from real`
2. **Factual accuracy (Pass/Fail):** Do the stage, histology, and biomarkers
   match the structured profile shown?
3. **Completeness (Pass/Fail):** Are there clinically critical facts in the profile
   that are absent from the note (aside from demographics)?
4. **Treatment-naive (Pass/Fail):** Does the note correctly represent an initial
   consultation for a treatment-naive patient?
5. **Demographic neutrality (Pass/Fail):** Any race, insurance, or SES language?

QA tier key: **PASS** = automated checks passed | **FAIL** = automated check(s) failed

---

## Case 1  [PASS]

### Structured Profile (Ground Truth)
```
Stage         : IIIB
Histology     : adenocarcinoma
Brain mets    : False
Smoking       : current smoker
Molecular     : neg: EGFR-, ALK-, KRAS-
PD-L1         : not_tested
TMB           : intermediate (2–16 mut/Mb)
```
**QA warnings:** brain_mets=False but note appears to mention brain metastasis

### Generated Note

**PATIENT:** [De-identified]
**MRN:** [De-identified]
**DATE OF CONSULT:** [De-identified]

**REASON FOR CONSULTATION:** Initial evaluation of newly diagnosed non-small cell lung cancer.

**HISTORY OF PRESENT ILLNESS:**
This is a 52-year-old with a history of current tobacco use who presented for initial oncologic consultation. The patient was in their usual state of health until approximately two months prior to presentation, when they developed a persistent, non-productive cough and progressive shortness of breath on exertion. This was associated with mild right-sided chest discomfort and an unintentional 10-pound weight loss over the past several months.

The patient initially sought evaluation with their primary care provider, who obtained a chest X-ray revealing a large opacity in the right upper lung. This prompted an urgent referral for further imaging.

**DIAGNOSTIC WORKUP:**
A contrast-enhanced CT of the chest, abdomen, and pelvis was performed. Imaging demonstrated a large, spiculated 5.5 cm mass in the right upper lobe. There was extensive and bulky mediastinal and right supraclavicular lymphadenopathy, concerning for significant nodal involvement. The CT of the abdomen and pelvis was negative for evidence of distant metastatic disease. Given the extent of locoregional disease, a staging MRI of the brain was also performed, which was negative for intracranial metastases.

The patient subsequently underwent a CT-guided core needle biopsy of the right upper lobe lung mass. Pathologic examination of the tissue confirmed a diagnosis of adenocarcinoma, consistent with a non-small cell lung cancer primary.

Based on the combination of a large primary tumor with extensive contralateral mediastinal and supraclavicular nodal involvement (N3) and no evidence of distant metastatic disease (M0), the patient's cancer is formally staged.

**AJCC Stage at Diagnosis:** Stage IIIB Non-Small Cell Lung Cancer

**MOLECULAR STUDIES:**
Pathology from the biopsy specimen was sent for next-generation sequencing to assess for targetable alterations.
-   No actionable driver alteration was identified. Specifically, testing was negative for mutations or rearrangements in EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2.
-   PD-L1 expression was not tested.
-   Tumor Mutational Burden (TMB) was found to be intermediate (2–16 mut/Mb).

**PROBLEM SUMMARY:**
In summary, this is a 52-year-old with a new diagnosis of Stage IIIB non-small cell lung adenocarcinoma, characterized by locally advanced, non-metastatic disease. The patient has a good performance status and is seen today for initial consultation. Molecular profiling is notable for an intermediate tumor mutational burden without an identifiable actionable driver mutation. The diagnosis, staging, and prognostic implications were discussed.

### Reviewer Ratings

| Item | Rating |
|---|---|
| Plausibility (1–5) |  |
| Factual accuracy (Pass/Fail) |  |
| Completeness (Pass/Fail) |  |
| Treatment-naive (Pass/Fail) |  |
| Demographic neutrality (Pass/Fail) |  |
| Comments |  |

---

## Case 2  [FAIL]

### Structured Profile (Ground Truth)
```
Stage         : IV
Histology     : adenocarcinoma
Brain mets    : True
Smoking       : never smoker
Molecular     : EGFR exon_19_del | neg: ALK-, KRAS-
PD-L1         : high
TMB           : intermediate (2–16 mut/Mb)
```

**QA failures:** brain_mets=True but no brain metastasis stated

### Generated Note

**HPI:**
This is a 70-year-old with a new diagnosis of metastatic non-small cell lung cancer. The patient presented to an outside hospital several weeks ago with a persistent, non-productive cough and progressive dyspnea on exertion. This was followed by the onset of intermittent headaches and mild word-finding difficulty, which prompted an urgent care visit. The patient is a lifetime never-smoker and has no significant personal history of cancer. The initial workup began at that time. The patient is here today for an initial oncology consultation to discuss the diagnosis and establish care.

Currently, the patient reports mild fatigue and an ongoing dry cough. The headaches have been partially responsive to over-the-counter analgesics. Appetite is fair with a recent, unintentional weight loss of approximately 10 pounds over the last two months. The patient maintains an excellent performance status (ECOG 0-1), is fully ambulatory, and capable of all self-care.

**Diagnostic Workup:**
A chest CT with contrast was performed as part of the initial evaluation. This study revealed a 4.5 cm spiculated mass in the right upper lobe. Additionally, several small nodules were noted in the contralateral left lung, the largest measuring 1.2 cm, suspicious for metastatic disease. Mediastinal and hilar lymphadenopathy was also present.

A PET/CT was subsequently obtained for staging, which demonstrated intense FDG avidity in the primary right upper lobe mass, as well as in multiple mediastinal lymph nodes and the previously identified contralateral lung nodules. No other sites of FDG-avid metastatic disease were identified in the chest, abdomen, or pelvis.

Given the new neurological symptoms, a brain MRI with and without contrast was performed. This revealed three discrete enhancing lesions in the cerebral hemispheres consistent with metastatic deposits, the largest measuring 1.5 cm in the left frontal lobe with surrounding vasogenic edema.

A CT-guided core needle biopsy of the right upper lobe lung mass was performed. Pathology confirmed poorly differentiated adenocarcinoma, with immunohistochemical staining (TTF-1 positive, Napsin-A positive) supporting a lung primary.

**Molecular Studies:**
Next-generation sequencing was performed on the tumor tissue from the lung biopsy.
- **Actionable Driver Mutations:** A sensitizing EGFR exon 19 deletion was detected.
- **Other Markers:** Testing was negative for ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2 alterations.
- **PD-L1 Immunohistochemistry:** Tumor Proportion Score (TPS) is ≥50%.
- **Tumor Mutational Burden (TMB):** Intermediate (2–16 mutations/megabase).

**Problem Summary:**
In summary, this is a 70-year-old never-smoker presenting with a new diagnosis of Stage IV (cT2b N2 M1c) non-small cell lung cancer, adenocarcinoma histology. The patient has known metastatic disease to the brain and contralateral lung. Molecular profiling of the tumor is notable for the presence of a sensitizing EGFR exon 19 deletion and high PD-L1 expression (TPS ≥50%).

### Reviewer Ratings

| Item | Rating |
|---|---|
| Plausibility (1–5) |  |
| Factual accuracy (Pass/Fail) |  |
| Completeness (Pass/Fail) |  |
| Treatment-naive (Pass/Fail) |  |
| Demographic neutrality (Pass/Fail) |  |
| Comments |  |

---

## Case 3  [PASS]

### Structured Profile (Ground Truth)
```
Stage         : IIIA
Histology     : adenocarcinoma
Brain mets    : False
Smoking       : former smoker (quit >1 year ago)
Molecular     : neg: EGFR-, ALK-, KRAS-
PD-L1         : negative
TMB           : intermediate (2–16 mut/Mb)
```
**QA warnings:** brain_mets=False but note appears to mention brain metastasis

### Generated Note

**HPI:**
This is a 70-year-old with a history of former tobacco use (quit over one year ago) who presents for an initial medical oncology consultation for a new diagnosis of non-small cell lung cancer. The patient was in their usual state of health until approximately three months prior to presentation, when they began to develop a persistent, non-productive cough and mild dyspnea on exertion. These symptoms gradually progressed, prompting a visit to their primary care provider. The patient denies hemoptysis, fevers, or significant chest pain. They report an unintentional weight loss of approximately 8 pounds over the last few months. The patient maintains a good functional status, able to perform all activities of daily living without assistance.

**Diagnostic Workup:**
An initial chest X-ray was obtained which demonstrated a right upper lobe lung mass. This prompted a follow-up contrast-enhanced CT of the chest, abdomen, and pelvis. The chest CT confirmed a 4.2 cm spiculated mass in the right upper lobe. It also revealed multiple enlarged ipsilateral mediastinal and subcarinal lymph nodes, with the largest measuring 2.5 cm in short axis. No suspicious lesions were identified in the contralateral lung, liver, adrenal glands, or bones on the CT imaging.

For definitive staging, a whole-body PET/CT scan was performed. This study demonstrated intense FDG avidity in the primary right upper lobe mass and in the right-sided mediastinal and subcarinal lymph nodes, corresponding to the findings on diagnostic CT. There was no evidence of FDG-avid disease at any distant sites. A staging MRI of the brain was also completed and was negative for intracranial metastases.

The patient subsequently underwent an endobronchial ultrasound (EBUS) with transbronchial needle aspiration (TBNA) of a subcarinal lymph node (station 7). Pathological analysis of the specimen confirmed invasive adenocarcinoma, consistent with a lung primary.

**Molecular Studies:**
Comprehensive molecular profiling was performed on the tumor tissue specimen via next-generation sequencing. No actionable driver alterations were identified. Specifically, the tumor was negative for mutations or rearrangements in EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2.

Immunohistochemistry for PD-L1 expression was performed and was negative, with a Tumor Proportion Score (TPS) of <1%. Tumor Mutational Burden (TMB) was found to be in the intermediate range (2–16 mut/Mb).

**Problem Summary:**
This is a 70-year-old, treatment-naive patient with a new diagnosis of Stage IIIA (cT2bN2M0, AJCC 8th Edition) non-small cell lung cancer of adenocarcinoma histology. Molecular studies are notable for the absence of an identified targetable driver mutation and negative PD-L1 expression. The patient is here today to discuss the diagnosis and implications.

### Reviewer Ratings

| Item | Rating |
|---|---|
| Plausibility (1–5) |  |
| Factual accuracy (Pass/Fail) |  |
| Completeness (Pass/Fail) |  |
| Treatment-naive (Pass/Fail) |  |
| Demographic neutrality (Pass/Fail) |  |
| Comments |  |

---

## Case 4  [FAIL]

### Structured Profile (Ground Truth)
```
Stage         : IV
Histology     : adenocarcinoma
Brain mets    : True
Smoking       : former smoker (quit >1 year ago)
Molecular     : neg: EGFR-, ALK-, KRAS-
PD-L1         : not_tested
TMB           : intermediate (2–16 mut/Mb)
```

**QA failures:** brain_mets=True but no brain metastasis stated

### Generated Note

**REASON FOR CONSULTATION:** New diagnosis of non-small cell lung cancer.

**HISTORY OF PRESENT ILLNESS:**
This is a 76-year-old individual whom I am seeing today in new patient consultation for a recent diagnosis of metastatic non-small cell lung cancer. The patient was in their usual state of health until approximately two months prior to presentation, when they developed a persistent, non-productive cough and progressive dyspnea on exertion. Over the past month, these symptoms were accompanied by the new onset of dull, persistent headaches and a nagging pain in the mid-thoracic back. Due to worsening symptoms, the patient presented to their primary care provider who initiated a diagnostic workup.

The patient is a former smoker, having quit over one year ago. They report a 10-pound unintentional weight loss over the past three months and increasing fatigue, but deny fevers, chills, or night sweats. Their current ECOG performance status is 1, as they remain fully ambulatory and capable of all self-care but are restricted in physically strenuous activity by their symptoms.

**PAST MEDICAL HISTORY:**
*   Hypertension
*   Hyperlipidemia

**PAST SURGICAL HISTORY:**
*   None relevant

**MEDICATIONS:**
*   Reviewed from outside records; will be reconciled.

**ALLERGIES:**
*   No known drug allergies.

**SOCIAL HISTORY:**
*   Tobacco: Former smoker. Quit approximately 18 months ago after a 30-pack-year history.
*   Alcohol: Denies regular use.

**FAMILY HISTORY:**
*   Reviewed and is non-contributory for thoracic or other malignancies.

**REVIEW OF SYSTEMS:**
*   CONSTITUTIONAL: Positive for fatigue and unintentional weight loss. Negative for fever or chills.
*   RESPIRATORY: Positive for cough and dyspnea on exertion. Negative for hemoptysis.
*   NEUROLOGIC: Positive for persistent headaches. Negative for focal weakness, sensory changes, or seizures.
*   MUSCULOSKELETAL: Positive for mid-back pain.

**PHYSICAL EXAMINATION:**
*   VITALS: Blood Pressure 134/78, Pulse 82, Temp 36.9 C, Resp 18, SpO2 96% on room air.
*   GENERAL: Alert and oriented, appears stated age. No acute distress.
*   HENT: Normocephalic, atraumatic. Anicteric sclerae.
*   LUNGS: Decreased breath sounds at the right apex. No wheezes or rhonchi.
*   CARDIOVASCULAR: Regular rate and rhythm. No murmurs, rubs, or gallops.
*   ABDOMEN: Soft, non-tender, non-distended.
*   MUSCULOSKELETAL: Point tenderness to palpation over the T6 spinous process. Full range of motion in all extremities.
*   NEUROLOGICAL: Alert and oriented x3. Cranial nerves II-XII are grossly intact. Strength is 5/5 throughout. Sensation is intact. No dysmetria on finger-to-nose testing. Gait is steady.
*   PERFORMANCE STATUS: ECOG 1.

**DIAGNOSTIC WORKUP:**
I have personally reviewed the available outside records, pathology, and imaging reports.

*   **CT Chest/Abdomen/Pelvis with contrast, [De-identified Date]:** Revealed a 4.5 cm spiculated mass in the right upper lobe of the lung with associated mediastinal adenopathy. A suspicious lytic lesion was noted in the T6 vertebral body. No other sites of visceral metastatic disease were identified in the abdomen or pelvis.

*   **MRI Brain with and without contrast, [De-identified Date]:** Performed to evaluate headaches. This demonstrated three small, ring-enhancing lesions in the left frontal lobe and right cerebellum, consistent with metastatic deposits. The largest lesion measures 1.2 cm.

*   **PET/CT, [De-identified Date]:** Showed intense FDG-avidity in the primary right upper lobe lung mass (SUVmax 14.2), multiple mediastinal lymph nodes, and several osseous sites including the T6 vertebral body and a left rib, confirming metastatic disease.

*   **Pathology, [De-identified Date]:** A CT-guided core needle biopsy of the right upper lobe lung mass was performed. Histopathologic examination confirmed invasive adenocarcinoma.

**MOLECULAR STUDIES:**
Next-generation sequencing was performed on the tumor tissue specimen.
*   No actionable driver alteration was identified. Testing was negative for mutations or rearrangements in EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2.
*   PD-L1 expression was not tested, consistent with the panel utilized (pre-2017 platform).
*   Tumor Mutational Burden (TMB) was intermediate (2–16 mut/Mb).
*   A loss-of-function mutation was detected in the STK11 gene.

**PROBLEM SUMMARY:**
This is a 76-year-old with a new diagnosis of Stage IV non-small cell lung cancer of adenocarcinoma histology, with metastases to the brain and bone. The patient is treatment-naive. Molecular profiling of the tumor is notable for the absence of common actionable driver mutations and the presence of an STK11 loss-of-function mutation, which is associated with primary resistance to PD-1 pathway inhibitors. The patient is seen today for initial consultation to discuss the diagnosis in detail.

### Reviewer Ratings

| Item | Rating |
|---|---|
| Plausibility (1–5) |  |
| Factual accuracy (Pass/Fail) |  |
| Completeness (Pass/Fail) |  |
| Treatment-naive (Pass/Fail) |  |
| Demographic neutrality (Pass/Fail) |  |
| Comments |  |

---

## Case 5  [PASS]

### Structured Profile (Ground Truth)
```
Stage         : IV
Histology     : adenocarcinoma
Brain mets    : True
Smoking       : never smoker
Molecular     : EGFR exon_19_del | neg: ALK-, KRAS-
PD-L1         : intermediate
TMB           : intermediate (2–16 mut/Mb)
```

### Generated Note

**MEDICAL ONCOLOGY INITIAL CONSULTATION**

**PATIENT:** [De-identified]
**MRN:** [De-identified]
**DATE OF VISIT:** [De-identified]

**HISTORY OF PRESENT ILLNESS:**
This is a 55-year-old individual with a history of being a never-smoker who presents for initial medical oncology consultation for a new diagnosis of metastatic non-small cell lung cancer.

The patient was in their usual state of health until approximately three months ago, when they began to experience a persistent, dry cough and progressive shortness of breath with exertion. These symptoms were accompanied by significant fatigue and an unintentional weight loss of approximately 20 pounds. Over the past month, the patient also developed new-onset, persistent headaches and a dull, aching pain in their lower back and right hip, which has limited their mobility.

Due to the persistence and progression of these symptoms, the patient sought medical evaluation. An initial chest X-ray revealed a large right-sided lung mass, which prompted a more comprehensive diagnostic workup. The patient has no prior history of malignancy and has not received any cancer-directed therapy to date. Performance status is estimated at ECOG 1, limited by pain and dyspnea.

**DIAGNOSTIC WORKUP:**
Staging evaluation included a contrast-enhanced CT scan of the chest, abdomen, and pelvis. This imaging confirmed the presence of a large primary mass in the right upper lobe with extensive mediastinal lymphadenopathy. The scan also demonstrated multiple lesions consistent with metastatic disease, including several hypodense lesions throughout the liver, bilateral adrenal masses, and a lytic lesion in the skeleton.

Given the patient's neurological symptoms, a contrast-enhanced MRI of the brain was performed. This study revealed multiple enhancing parenchymal lesions, confirming the presence of cerebral metastases.

To establish a tissue diagnosis, the patient underwent an interventional radiology-guided core needle biopsy of an accessible liver lesion. Pathologic examination of the specimen confirmed a diagnosis of poorly differentiated adenocarcinoma, with an immunoprofile consistent with a lung primary.

Based on the extensive locoregional disease and widespread distant metastases to the brain, liver, bone, and adrenal glands, the patient is diagnosed with AJCC Stage IV non-small cell lung cancer.

**MOLECULAR STUDIES:**
Next-generation sequencing (NGS) was performed on the tumor tissue specimen.
- **Actionable driver mutation:** A sensitizing EGFR exon 19 deletion was detected.
- **Other drivers:** Testing was negative for ALK, ROS1, BRAF, MET exon 14, RET, and NTRK fusions. KRAS and ERBB2 mutations were also not identified.
- **Immunotherapy markers:**
    - PD-L1 expression by immunohistochemistry showed a Tumor Proportion Score (TPS) in the 1–49% range.
    - Tumor Mutational Burden (TMB) was found to be intermediate (2–16 mut/Mb).

**PROBLEM SUMMARY:**
In summary, this is a 55-year-old never-smoker who presents for initial oncologic evaluation of newly diagnosed Stage IV non-small cell lung cancer, adenocarcinoma histology. The patient is treatment-naive. Staging workup has confirmed extensive metastatic disease involving the brain, bone, liver, and adrenal glands. Molecular profiling of the tumor is notable for a sensitizing EGFR exon 19 deletion. The purpose of this visit is to discuss the diagnosis, prognosis, and goals of care.

### Reviewer Ratings

| Item | Rating |
|---|---|
| Plausibility (1–5) |  |
| Factual accuracy (Pass/Fail) |  |
| Completeness (Pass/Fail) |  |
| Treatment-naive (Pass/Fail) |  |
| Demographic neutrality (Pass/Fail) |  |
| Comments |  |

---

## Case 6  [PASS]

### Structured Profile (Ground Truth)
```
Stage         : IIIB
Histology     : adenocarcinoma
Brain mets    : False
Smoking       : never smoker
Molecular     : ROS1+ | neg: EGFR-, ALK-, KRAS-
PD-L1         : not_tested
TMB           : intermediate (2–16 mut/Mb)
```
**QA warnings:** brain_mets=False but note appears to mention brain metastasis

### Generated Note

**HPI:**
This is a 53-year-old individual with an excellent performance status who presents for an initial oncology consultation to discuss a new diagnosis of non-small cell lung cancer. The patient was in their usual state of good health until approximately two months prior to presentation, when they developed a persistent, dry cough and mild shortness of breath with exertion. This prompted a visit to their primary care provider, and an initial chest X-ray revealed a left-sided lung mass. The patient denies any fevers, chills, or significant weight loss. They are a lifetime never-smoker. They continue to work and remain fully active in their daily life with an estimated ECOG performance status of 0.

**Diagnostic Workup:**
Following the abnormal chest X-ray, a contrast-enhanced CT of the chest, abdomen, and pelvis was performed on [De-identified date]. This study characterized a 4.1 cm spiculated mass in the left upper lobe. The scan also revealed extensive mediastinal and supraclavicular lymphadenopathy, including bulky contralateral mediastinal nodes.

For definitive staging, a whole-body PET/CT was performed on [De-identified date]. This confirmed intense FDG-avidity within the primary left upper lobe mass, as well as in multiple nodal stations including the left supraclavicular and contralateral mediastinal regions. Critically, there was no evidence of FDG-avid disease below the diaphragm or in other distant sites to suggest metastatic disease. A dedicated MRI of the brain with contrast was subsequently completed and was negative for any intracranial metastases.

To establish a tissue diagnosis and for molecular analysis, the patient underwent a CT-guided core needle biopsy of the left upper lobe lung mass. Pathology returned as invasive adenocarcinoma, consistent with a lung primary. The cumulative findings of the diagnostic workup are consistent with locally advanced, non-metastatic disease, classified as clinical Stage IIIB non-small cell lung cancer.

**Molecular Studies:**
Next-generation sequencing (NGS) was performed on the tumor tissue obtained from the core biopsy. Molecular profiling was positive for an actionable ROS1 gene rearrangement. The tumor was negative for other tested driver mutations, including EGFR, ALK, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2. PD-L1 immunohistochemistry was not performed on the specimen. The tumor mutational burden (TMB) was found to be intermediate (2–16 mut/Mb).

**Problem Summary:**
In summary, this is a 53-year-old lifetime never-smoker with an excellent performance status who presents with a new diagnosis of Stage IIIB non-small cell lung adenocarcinoma. Staging studies have confirmed locally advanced disease confined to the chest and supraclavicular region, with no evidence of distant metastases. Comprehensive molecular testing of the tumor is notable for the identification of a ROS1 rearrangement.

### Reviewer Ratings

| Item | Rating |
|---|---|
| Plausibility (1–5) |  |
| Factual accuracy (Pass/Fail) |  |
| Completeness (Pass/Fail) |  |
| Treatment-naive (Pass/Fail) |  |
| Demographic neutrality (Pass/Fail) |  |
| Comments |  |

---

## Case 7  [PASS]

### Structured Profile (Ground Truth)
```
Stage         : IV
Histology     : adenocarcinoma
Brain mets    : False
Smoking       : never smoker
Molecular     : EGFR exon_19_del | neg: ALK-, KRAS-
PD-L1         : not_tested
TMB           : low (<2 mut/Mb)
```
**QA warnings:** brain_mets=False but note appears to mention brain metastasis

### Generated Note

**HPI:**
This is a 64-year-old individual referred for an initial oncology consultation for a new diagnosis of non-small cell lung cancer. The patient is a lifetime never-smoker who was in a usual state of good health until approximately three months ago, when a persistent, dry cough developed. Over the subsequent weeks, the patient noted the onset of progressive dyspnea on exertion and right-sided chest wall pain. Due to worsening symptoms, the patient presented for medical evaluation. An initial chest X-ray revealed a right-sided lung mass and a pleural effusion, prompting further workup. The patient has a good performance status (ECOG 1) but reports an unintentional weight loss of approximately 10 pounds over the past two months.

**Diagnostic Workup:**
A contrast-enhanced CT of the chest, abdomen, and pelvis performed on [De-identified] confirmed a 4.2 cm spiculated mass in the right upper lobe. The scan also demonstrated a large, loculated right pleural effusion and multiple sub-centimeter pleural nodules. Additional findings included a 2.1 cm left adrenal nodule and lytic lesions in the thoracic spine and a right rib, all suspicious for metastatic disease.

A subsequent whole-body PET/CT scan on [De-identified] showed intense FDG uptake in the primary right upper lobe mass, the right pleura, the left adrenal gland, and multiple osseous sites, confirming the findings on CT and consistent with widespread metastatic disease.

A CT-guided core needle biopsy of the right upper lobe lung mass was performed on [De-identified]. Pathology review established a diagnosis of lung adenocarcinoma.

A brain MRI with and without contrast was performed as part of the initial staging workup and was negative for intracranial metastases.

**Molecular Studies:**
Next-generation sequencing (NGS) was performed on the tumor tissue.
- An activating EGFR exon 19 deletion was detected.
- The tumor was found to be negative for alterations in ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2.
- PD-L1 expression was not tested.
- Tumor Mutational Burden (TMB) was low at <2 mut/Mb.

**Problem Summary:**
In summary, this is a 64-year-old never-smoker who presents with newly diagnosed Stage IV non-small cell lung cancer, adenocarcinoma histology. The disease is metastatic to bone, pleura, and the contralateral adrenal gland, with a molecular profile notable for a sensitizing EGFR exon 19 deletion.

### Reviewer Ratings

| Item | Rating |
|---|---|
| Plausibility (1–5) |  |
| Factual accuracy (Pass/Fail) |  |
| Completeness (Pass/Fail) |  |
| Treatment-naive (Pass/Fail) |  |
| Demographic neutrality (Pass/Fail) |  |
| Comments |  |

---

## Case 8  [PASS]

### Structured Profile (Ground Truth)
```
Stage         : IV
Histology     : adenocarcinoma
Brain mets    : True
Smoking       : never smoker
Molecular     : BRAF V600E | neg: EGFR-, ALK-, KRAS-
PD-L1         : high
TMB           : low (<2 mut/Mb)
```

### Generated Note

**HPI:**
This is a 50-year-old patient with a history of being a never-smoker who is referred for initial medical oncology consultation for a new diagnosis of metastatic non-small cell lung cancer. The patient was in their usual state of health until approximately six weeks prior to presentation, when they developed a persistent, non-productive cough and progressive dyspnea on exertion. Over the subsequent weeks, they noted increasing fatigue, poor appetite, and an unintentional weight loss of approximately 15 pounds. The patient's course was complicated by the new onset of persistent headaches and mild word-finding difficulties, which prompted an evaluation in the emergency department at [De-identified] Hospital. The patient's performance status is ECOG 1; they are symptomatic but remain fully ambulatory and capable of light work.

**Diagnostic Workup:**
An extensive diagnostic evaluation was initiated. A CT of the chest, abdomen, and pelvis with contrast revealed a 4.5 cm spiculated mass in the right upper lobe of the lung, extensive mediastinal and hilar adenopathy, and numerous bilateral pulmonary nodules consistent with metastatic spread. The scan also demonstrated multiple hypoattenuating lesions throughout the liver, suspicious for metastases, as well as several lytic bone lesions.

Given the neurologic symptoms, a brain MRI with and without contrast was performed. This study confirmed the presence of multiple, peripherally-enhancing intracranial lesions in the cerebral hemispheres, consistent with brain metastases.

A subsequent whole-body PET/CT scan was performed for staging, which showed intense FDG-avidity in the primary right upper lobe lung mass, the mediastinal, hilar, and supraclavicular lymph nodes, the contralateral lung nodules, the multiple liver lesions, and in multiple sites of the axial and appendicular skeleton. These findings confirmed widespread, multi-organ metastatic disease.

To establish a tissue diagnosis, the patient underwent an ultrasound-guided core biopsy of one of the accessible liver metastases by Interventional Radiology. Pathologic examination of the tissue confirmed metastatic adenocarcinoma with features consistent with a lung primary.

**Molecular Studies:**
Next-generation sequencing (NGS) was performed on the tumor tissue. A pathogenic BRAF V600E mutation was identified. Further molecular analysis was negative for other common driver mutations, including EGFR, ALK, ROS1, RET, NTRK, MET exon 14 skipping, ERBB2, and KRAS.

Immunohistochemistry for PD-L1 expression was strongly positive, with a Tumor Proportion Score (TPS) of ≥50%. Tumor Mutational Burden (TMB) was determined to be low at <2 mutations/megabase.

**Problem Summary:**
In summary, this is a 50-year-old never-smoker with a new diagnosis of AJCC Stage IV non-small cell lung adenocarcinoma. The disease is characterized by a right upper lobe primary tumor with widespread metastatic involvement of the brain, contralateral lung, liver, bone, and distant lymph nodes. Molecular profiling of the tumor is notable for the presence of an activating BRAF V600E mutation and high PD-L1 expression (TPS ≥50%). The patient is treatment-naive and is seen today for initial consultation to discuss the diagnosis and the general principles of management.

### Reviewer Ratings

| Item | Rating |
|---|---|
| Plausibility (1–5) |  |
| Factual accuracy (Pass/Fail) |  |
| Completeness (Pass/Fail) |  |
| Treatment-naive (Pass/Fail) |  |
| Demographic neutrality (Pass/Fail) |  |
| Comments |  |

---

## Case 9  [FAIL]

### Structured Profile (Ground Truth)
```
Stage         : IV
Histology     : adenocarcinoma
Brain mets    : True
Smoking       : former smoker (quit >1 year ago)
Molecular     : neg: EGFR-, ALK-, KRAS-
PD-L1         : not_tested
TMB           : intermediate (2–16 mut/Mb)
Prior cancers : Uterus Cancer
```

**QA failures:** brain_mets=True but no brain metastasis stated

### Generated Note

**REASON FOR CONSULTATION:** New diagnosis of metastatic non-small cell lung cancer.

**HISTORY OF PRESENT ILLNESS**
This is a 73-year-old who presents for an initial oncology consultation. The patient was in their usual state of health until approximately two months ago, when they began to experience a persistent, dry cough and progressive shortness of breath with exertion. Over the subsequent weeks, they also developed dull, intermittent headaches and a new, aching pain in their right hip. Due to the progression of these symptoms, the patient sought medical evaluation.

The patient reports being able to perform all self-care but is limited in strenuous activity due to dyspnea, consistent with an ECOG performance status of 1. They deny fevers, chills, or significant weight loss.

**PAST MEDICAL HISTORY**
- Uterus Cancer, status post definitive treatment, with no evidence of recurrence.
- Hypertension

**SOCIAL HISTORY**
- Tobacco: Former smoker, quit more than one year ago.

**DIAGNOSTIC WORKUP**
An initial chest X-ray revealed a left upper lobe lung opacity, prompting further investigation. A staging CT scan of the chest, abdomen, and pelvis was performed, which characterized a 4 cm spiculated mass in the left upper lobe with associated mediastinal adenopathy. The scan also identified a destructive lytic lesion in the right iliac bone.

Given the patient's neurologic symptoms, a contrast-enhanced MRI of the brain was obtained. This study revealed several small, enhancing parenchymal lesions in the bilateral cerebral hemispheres, consistent with metastatic disease.

The patient subsequently underwent a CT-guided core needle biopsy of the primary left lung mass on [De-identified date]. Histopathologic examination confirmed a diagnosis of adenocarcinoma, consistent with a lung primary.

The cumulative findings from imaging and pathology confirm a diagnosis of AJCC Stage IV non-small cell lung cancer.

**MOLECULAR STUDIES**
Next-generation sequencing was performed on the tumor tissue. No actionable driver alteration was identified. Specific findings are as follows:
- Negative for mutations or fusions in: EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, ERBB2.
- Tumor Mutational Burden (TMB): intermediate (2–16 mut/Mb).
- PD-L1: not tested (pre-2017 sequencing — testing not yet standard of care).

**PROBLEM SUMMARY**
This is a 73-year-old former smoker with a new diagnosis of treatment-naive Stage IV NSCLC, adenocarcinoma histology, with metastases to the brain and bone. Molecular profiling did not identify any actionable driver mutations.

### Reviewer Ratings

| Item | Rating |
|---|---|
| Plausibility (1–5) |  |
| Factual accuracy (Pass/Fail) |  |
| Completeness (Pass/Fail) |  |
| Treatment-naive (Pass/Fail) |  |
| Demographic neutrality (Pass/Fail) |  |
| Comments |  |

---

## Case 10  [PASS]

### Structured Profile (Ground Truth)
```
Stage         : IIB
Histology     : adenocarcinoma
Brain mets    : False
Smoking       : former smoker (quit <1 year ago)
Molecular     : neg: EGFR-, ALK-, KRAS-
PD-L1         : not_tested
TMB           : intermediate (2–16 mut/Mb)
```
**QA warnings:** brain_mets=False but note appears to mention brain metastasis

### Generated Note

**HPI:**
This is an initial consultation for a 61-year-old with a new diagnosis of non-small cell lung cancer. The patient presented to an outside facility approximately one month ago with a persistent, non-productive cough and mild exertional dyspnea. These symptoms had been progressive over the prior two months. The patient also reports an unintentional weight loss of approximately 10 pounds over the past three months. There is no reported hemoptysis, fevers, or significant chest pain. A history of tobacco use is noted, with the patient having quit less than one year ago after a 30-pack-year history. Due to the persistent cough, a chest X-ray was obtained which revealed a right upper lobe opacity, prompting further evaluation. The patient remains fully ambulatory and independent in all activities of daily living, with an ECOG performance status of 1. The patient is referred to medical oncology for evaluation and discussion of this new diagnosis.

**Diagnostic Workup:**
A comprehensive staging workup has been completed.

A CT scan of the chest with contrast identified a 4.8 cm spiculated mass in the apical segment of the right upper lobe. There was no evidence of chest wall invasion. Mediastinal and hilar lymph nodes appeared radiographically normal in size.

A subsequent PET/CT scan was performed for staging. This demonstrated intense FDG-avidity within the known right upper lobe primary mass (SUVmax 12.4). No FDG-avid hilar, mediastinal, or supraclavicular lymphadenopathy was identified. Importantly, there was no evidence of FDG-avid disease elsewhere in the body to suggest distant metastatic disease.

A CT-guided core needle biopsy of the right upper lobe mass was performed. Pathology confirmed invasive adenocarcinoma, consistent with a lung primary.

A brain MRI with and without contrast was performed as part of the standard staging evaluation and was negative for any evidence of intracranial metastases.

**Molecular Studies:**
Next-generation sequencing was performed on the tumor biopsy specimen. No actionable driver alterations were identified. Testing was negative for mutations or rearrangements in EGFR, ALK, ROS1, BRAF, MET exon 14, RET, and NTRK. KRAS and ERBB2 mutations were also absent. Tumor Mutational Burden (TMB) was reported as intermediate (2–16 mut/Mb). PD-L1 expression was not tested, as this was not standard of care for this stage of disease at the time of tissue acquisition.

**Problem Summary:**
In summary, this is a 61-year-old former smoker with a good performance status who presents with a new diagnosis of Stage IIB (pT2b N0 M0, AJCC 8th Edition) non-small cell lung cancer of adenocarcinoma histology. Staging workup, including PET/CT and brain MRI, has confirmed disease localized to the lung without evidence of nodal or distant metastatic involvement. Molecular profiling of the tumor is notable for an absence of targetable driver mutations. The patient is here today for initial consultation to discuss the diagnosis and its implications.

### Reviewer Ratings

| Item | Rating |
|---|---|
| Plausibility (1–5) |  |
| Factual accuracy (Pass/Fail) |  |
| Completeness (Pass/Fail) |  |
| Treatment-naive (Pass/Fail) |  |
| Demographic neutrality (Pass/Fail) |  |
| Comments |  |

---

## Case 11  [PASS]

### Structured Profile (Ground Truth)
```
Stage         : IV
Histology     : adenocarcinoma
Brain mets    : False
Smoking       : former smoker (quit >1 year ago)
Molecular     : KRAS G12C | neg: EGFR-, ALK-
PD-L1         : not_tested
TMB           : intermediate (2–16 mut/Mb)
```

### Generated Note

**Initial Oncology Consultation**
Patient ID: [De-identified]
Date of Visit: [De-identified]

**HISTORY OF PRESENT ILLNESS:**
This is a 63-year-old former smoker who presents for initial oncology consultation for a new diagnosis of metastatic non-small cell lung cancer.

The patient was in their usual state of health until approximately two months prior to presentation, when they developed a persistent, non-productive cough and progressive right-sided chest wall pain. This was initially managed with over-the-counter analgesics without significant relief. Over the subsequent weeks, they also noted the onset of new, dull pain in the left hip, which worsened with ambulation. Due to the persistence of symptoms, they presented to their primary care provider.

An initial chest X-ray was obtained which demonstrated a right upper lobe lung opacity. This prompted a follow-up CT scan of the chest, abdomen, and pelvis. The scan confirmed a spiculated mass in the right upper lobe, associated mediastinal lymphadenopathy, and a lytic lesion in the left iliac bone, suspicious for metastatic disease.

The patient was subsequently referred for a PET/CT scan for staging, which demonstrated intense FDG-avidity in the primary right lung mass, multiple mediastinal lymph nodes, and the solitary lesion in the left iliac bone. A dedicated MRI of the brain was performed as part of the staging workup and was negative for intracranial metastases. The patient then underwent a CT-guided core needle biopsy of the right upper lobe lung mass, which established the diagnosis. The patient has remained active with a good performance status but continues to have intermittent chest and hip pain.

**DIAGNOSTIC WORKUP:**
**Imaging:**
*   **CT Chest/Abdomen/Pelvis with contrast [Date]:** Revealed a 4.2 x 3.5 cm spiculated mass in the right upper lobe. Associated mediastinal and hilar lymphadenopathy was noted. A 2.1 cm lytic lesion was identified in the left iliac bone.
*   **PET/CT [Date]:** Confirmed a hypermetabolic primary mass in the right upper lobe (SUV max 12.4), hypermetabolic mediastinal lymph nodes (SUV max 8.9), and a solitary focus of intense hypermetabolic activity in the left iliac bone (SUV max 9.5), consistent with metastatic disease. No other sites of distant metastatic disease were identified.
*   **MRI Brain with and without contrast [Date]:** No evidence of intracranial metastatic disease.

**Pathology:**
*   **CT-guided core needle biopsy, right upper lobe lung mass [Date]:** Invasive adenocarcinoma, moderately differentiated.

**MOLECULAR STUDIES:**
Next-generation sequencing (NGS) was performed on the tumor tissue obtained from the lung biopsy.
*   **Actionable Driver Mutation:** KRAS G12C mutation detected.
*   **Additional Testing:** Negative for targetable alterations in EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, and ERBB2.
*   **Tumor Mutational Burden (TMB):** Intermediate (11 mutations/megabase).
*   **PD-L1 Expression:** Not tested.

**PROBLEM SUMMARY:**
This is a 63-year-old with a new diagnosis of Stage IV non-small cell lung cancer, adenocarcinoma histology, metastatic to bone. The patient is a former smoker and is treatment-naive. Molecular profiling of the tumor is notable for the presence of a KRAS G12C mutation. The patient is seen today for initial consultation to discuss the diagnosis and establish care.

### Reviewer Ratings

| Item | Rating |
|---|---|
| Plausibility (1–5) |  |
| Factual accuracy (Pass/Fail) |  |
| Completeness (Pass/Fail) |  |
| Treatment-naive (Pass/Fail) |  |
| Demographic neutrality (Pass/Fail) |  |
| Comments |  |

---

## Case 12  [PASS]

### Structured Profile (Ground Truth)
```
Stage         : IV
Histology     : adenocarcinoma
Brain mets    : True
Smoking       : former smoker (quit >1 year ago)
Molecular     : neg: EGFR-, ALK-, KRAS-
PD-L1         : not_tested
TMB           : intermediate (2–16 mut/Mb)
```

### Generated Note

**HPI:**
This is a 69-year-old who presents for an initial oncology consultation for a new diagnosis of metastatic non-small cell lung cancer. The patient was in their usual state of health until approximately six weeks prior to presentation, when they developed a persistent, non-productive cough and progressive fatigue. Over the subsequent weeks, they noted the onset of intermittent headaches and a 15-pound unintentional weight loss. Due to worsening symptoms, they presented for medical evaluation.

Initial workup included a chest X-ray which was suspicious for a right-sided lung mass. This prompted a staging CT scan of the chest, abdomen, and pelvis with contrast. This imaging confirmed a large mass in the right upper lobe of the lung and also revealed numerous suspicious lesions in the liver, a contralateral lung nodule, and destructive bone lesions. Given the finding of headaches, a contrast-enhanced MRI of the brain was performed, which demonstrated multiple intracranial metastatic deposits. The patient is a former smoker, having quit more than one year ago. They remain fully ambulatory and capable of all self-care, though report significant fatigue. ECOG performance status is 1.

**Diagnostic Workup:**
A comprehensive staging evaluation was completed prior to this consultation.

*   **Imaging:** A PET/CT scan performed on [De-identified date] confirmed a hypermetabolic primary mass in the right upper lobe. It also demonstrated FDG-avid metastatic disease involving the contralateral lung, multiple segments of the liver, bone (thoracic spine), and distant lymph nodes (supraclavicular). An MRI of the brain on [De-identified date] confirmed the presence of multiple enhancing lesions in the cerebral and cerebellar hemispheres, consistent with brain metastases.

*   **Pathology:** A CT-guided core needle biopsy of the right lung mass was performed on [De-identified date]. Histopathologic review confirmed a diagnosis of adenocarcinoma, consistent with a lung primary.

**Molecular Studies:**
Next-generation sequencing was performed on the tumor tissue obtained from the lung biopsy.

*   No actionable driver alteration was identified. The tumor was found to be negative for mutations or rearrangements involving EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2.
*   Tumor Mutational Burden (TMB) was determined to be intermediate (2–16 mutations/megabase).
*   PD-L1 expression was not tested on this specimen.

**Problem Summary:**
1.  Non-small cell lung cancer, adenocarcinoma histology.
2.  Stage IV (AJCC 8th Edition) at diagnosis, with metastatic disease to the brain, bone, liver, contralateral lung, and distant lymph nodes.
3.  Molecular profiling notable for no identified actionable driver mutations and an intermediate tumor mutational burden.

### Reviewer Ratings

| Item | Rating |
|---|---|
| Plausibility (1–5) |  |
| Factual accuracy (Pass/Fail) |  |
| Completeness (Pass/Fail) |  |
| Treatment-naive (Pass/Fail) |  |
| Demographic neutrality (Pass/Fail) |  |
| Comments |  |

---

## Case 13  [PASS]

### Structured Profile (Ground Truth)
```
Stage         : IIIB
Histology     : squamous
Brain mets    : False
Smoking       : former smoker (quit <1 year ago)
Molecular     : neg: EGFR-, ALK-, KRAS-
PD-L1         : negative
TMB           : intermediate (2–16 mut/Mb)
```
**QA warnings:** brain_mets=False but note appears to mention brain metastasis

### Generated Note

**HPI:**
This is an initial consultation for a 62-year-old with a new diagnosis of non-small cell lung cancer. The patient is a former smoker who quit within the last year and presented to an outside facility approximately one month ago with a persistent, non-productive cough and progressive dyspnea on exertion. Initial evaluation with a chest radiograph revealed a large left upper lobe opacity. The patient reports feeling generally well otherwise, with a stable appetite and no significant weight loss. Performance status is excellent, estimated at ECOG 1. The patient is here today to establish care and discuss the diagnosis and findings.

**Diagnostic Workup:**
Following the abnormal chest X-ray, a contrast-enhanced CT of the chest, abdomen, and pelvis was performed for staging. This imaging confirmed a large, spiculated 6 cm mass in the left upper lobe. The mass was noted to have direct mediastinal invasion. There was extensive ipsilateral mediastinal and hilar lymphadenopathy, as well as contralateral mediastinal and left supraclavicular lymphadenopathy concerning for N3 disease. The CT of the abdomen and pelvis demonstrated no evidence of distant metastatic disease to the liver, adrenal glands, or other viscera. A dedicated MRI of the brain with contrast was subsequently performed and was negative for intracranial metastases.

To establish a tissue diagnosis and complete staging, the patient underwent bronchoscopy with endobronchial ultrasound (EBUS). Fine-needle aspiration (FNA) of a subcarinal lymph node (station 7) was performed. Pathologic review of the biopsy specimen confirmed invasive, poorly differentiated squamous cell carcinoma.

Based on the combination of a large primary tumor with extensive contralateral mediastinal and supraclavicular nodal involvement (cT4N3M0), the patient is diagnosed with AJCC Stage IIIB non-small cell lung cancer.

**Molecular Studies:**
The tissue obtained from the EBUS-FNA was sent for comprehensive molecular profiling via next-generation sequencing. No actionable driver alterations were identified; testing was negative for mutations or rearrangements in EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2.

Immunohistochemistry for PD-L1 expression was performed and was negative. Tumor Mutational Burden (TMB) was assessed and found to be intermediate (2–16 mut/Mb).

**Problem Summary:**
In summary, this is a 62-year-old with a new diagnosis of treatment-naive, unresectable Stage IIIB squamous cell non-small cell lung cancer. The diagnostic workup is complete and has confirmed locally advanced disease without evidence of distant metastases. Molecular profiling is notable for the absence of targetable driver mutations and negative PD-L1 expression. The patient is seen today for initial oncology consultation to review these findings.

### Reviewer Ratings

| Item | Rating |
|---|---|
| Plausibility (1–5) |  |
| Factual accuracy (Pass/Fail) |  |
| Completeness (Pass/Fail) |  |
| Treatment-naive (Pass/Fail) |  |
| Demographic neutrality (Pass/Fail) |  |
| Comments |  |

---

## Case 14  [PASS]

### Structured Profile (Ground Truth)
```
Stage         : IA
Histology     : squamous
Brain mets    : False
Smoking       : former smoker (quit <1 year ago)
Molecular     : neg: EGFR-, ALK-, KRAS-
PD-L1         : not_tested
TMB           : intermediate (2–16 mut/Mb)
```
**QA warnings:** brain_mets=False but note appears to mention brain metastasis

### Generated Note

**HPI:**
This is a 63-year-old individual with a history of tobacco use who presents for initial medical oncology consultation for a new diagnosis of non-small cell lung cancer. The patient was recently evaluated for a persistent cough, which prompted a chest X-ray. This imaging revealed a suspicious nodule in the right lung. The patient is a former smoker, having quit approximately 6 months ago after a significant pack-year history. The patient otherwise feels well, denies chest pain, shortness of breath, hemoptysis, or unintentional weight loss. Performance status is excellent; the patient is fully active and asymptomatic from this diagnosis (ECOG 0).

**Diagnostic Workup:**
Following the abnormal chest X-ray, a contrast-enhanced CT of the chest, abdomen, and pelvis was performed. This confirmed the presence of a 2.2 cm solid, spiculated mass in the right upper lobe. There was no evidence of hilar or mediastinal lymphadenopathy. No suspicious lesions were identified in the liver, adrenal glands, or other visualized portions of the abdomen and pelvis.

To complete staging, a whole-body PET/CT was obtained, which demonstrated intense FDG-avidity localized to the right upper lobe mass, with no other sites of metabolically active disease concerning for nodal or distant metastases. A brain MRI with and without contrast was also performed and was negative for intracranial metastatic disease.

The patient subsequently underwent a CT-guided core needle biopsy of the right upper lobe mass. Pathologic analysis confirmed the diagnosis of invasive, moderately differentiated squamous cell carcinoma.

**Molecular Studies:**
Next-generation sequencing (NGS) was performed on the tumor tissue. No actionable driver alteration was identified. The tumor was negative for mutations or rearrangements in EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2. PD-L1 expression was not tested. Tumor mutational burden (TMB) was reported as intermediate (2–16 mut/Mb).

**Problem Summary:**
In summary, this is a 63-year-old former smoker with a new diagnosis of AJCC Stage IA non-small cell lung cancer, squamous cell histology. The workup is consistent with localized disease (T1bN0M0) without evidence of regional or distant spread. Molecular profiling did not identify any targetable driver mutations. The patient is seen today for initial consultation to discuss the diagnosis and review management options.

### Reviewer Ratings

| Item | Rating |
|---|---|
| Plausibility (1–5) |  |
| Factual accuracy (Pass/Fail) |  |
| Completeness (Pass/Fail) |  |
| Treatment-naive (Pass/Fail) |  |
| Demographic neutrality (Pass/Fail) |  |
| Comments |  |

---

## Case 15  [PASS]

### Structured Profile (Ground Truth)
```
Stage         : IV
Histology     : adenocarcinoma
Brain mets    : False
Smoking       : former smoker (quit >1 year ago)
Molecular     : BRAF V600E | neg: EGFR-, ALK-, KRAS-
PD-L1         : not_tested
TMB           : low (<2 mut/Mb)
```
**QA warnings:** brain_mets=False but note appears to mention brain metastasis

### Generated Note

**HPI:**
This is an initial oncology consultation for a 60-year-old with a new diagnosis of metastatic non-small cell lung cancer. The patient is a former smoker, having quit over a year ago. The patient was in their usual state of health until approximately two months prior to presentation, when they developed a persistent, non-productive cough and progressive dyspnea on exertion. These symptoms initially did not respond to a course of antibiotics from their primary care provider. Due to worsening shortness of breath, a chest radiograph was obtained, which revealed a lung mass and a pleural effusion. The patient was subsequently referred for further diagnostic evaluation. The patient reports some fatigue but maintains an excellent performance status (ECOG 0), continuing to perform all activities of daily living without restriction. A review of systems is otherwise negative for fevers, chills, night sweats, or significant weight loss.

**Diagnostic Workup:**
A contrast-enhanced CT scan of the chest, abdomen, and pelvis was performed for staging. Imaging revealed a primary mass in the right lower lobe of the lung measuring approximately 4.5 cm. There was a moderate-sized, malignant-appearing right-sided pleural effusion. Pathologic lymphadenopathy was noted in the mediastinum as well as in the contralateral supraclavicular region, consistent with distant nodal metastasis. No metastatic lesions were identified in the liver, adrenal glands, or bones. A subsequent MRI of the brain with and without contrast was performed and was negative for intracranial metastases.

The patient underwent a CT-guided core needle biopsy of the right lower lobe lung mass. Histopathologic examination of the tissue confirmed a diagnosis of poorly differentiated adenocarcinoma, consistent with a lung primary.

**Molecular Studies:**
Next-generation sequencing (NGS) was performed on the tumor tissue. An actionable driver mutation was identified in **BRAF (V600E)**. The tumor was negative for pathogenic alterations in EGFR, ALK, ROS1, MET exon 14, RET, NTRK, KRAS, and ERBB2. Tumor mutational burden (TMB) was determined to be low (<2 mutations/megabase). PD-L1 immunohistochemistry was not performed on this specimen.

**Problem Summary:**
This is a 60-year-old with an excellent performance status who presents for an initial oncology evaluation. The patient is treatment-naive and has a new diagnosis of Stage IV non-small cell lung cancer, adenocarcinoma histology, with metastatic disease involving the pleura and distant lymph nodes. Molecular profiling of the tumor is notable for a BRAF V600E mutation. The patient is here today to discuss these findings.

### Reviewer Ratings

| Item | Rating |
|---|---|
| Plausibility (1–5) |  |
| Factual accuracy (Pass/Fail) |  |
| Completeness (Pass/Fail) |  |
| Treatment-naive (Pass/Fail) |  |
| Demographic neutrality (Pass/Fail) |  |
| Comments |  |

---

## Case 16  [FAIL]

### Structured Profile (Ground Truth)
```
Stage         : IV
Histology     : adenocarcinoma
Brain mets    : True
Smoking       : current smoker
Molecular     : neg: EGFR-, ALK-, KRAS-
PD-L1         : not_tested
TMB           : high (>16 mut/Mb)
```

**QA failures:** brain_mets=True but no brain metastasis stated

### Generated Note

**HPI:**
This is a 43-year-old individual with a significant smoking history who presents for an initial medical oncology consultation regarding a new diagnosis of non-small cell lung cancer. The patient was in a usual state of health until approximately two months prior to presentation, when they began to experience a persistent, non-productive cough and progressive dyspnea on exertion. Over the subsequent weeks, this was associated with an unintentional weight loss of approximately 15 pounds, generalized fatigue, and the new onset of intermittent headaches and mild dizziness.

These symptoms prompted an evaluation with their primary care provider, leading to a chest X-ray that showed a right-sided lung opacity. A subsequent contrast-enhanced CT of the chest, abdomen, and pelvis was performed. This confirmed the presence of a large mass in the right upper lobe with associated mediastinal and hilar lymphadenopathy, as well as suspicious contralateral supraclavicular lymph nodes. Given the new neurological symptoms, a brain MRI was obtained which revealed multiple intracranial lesions consistent with metastatic disease. The patient has a good performance status, ECOG 1, and remains fully ambulatory and capable of self-care, though is limited in strenuous activity by dyspnea.

**Diagnostic Workup:**
A comprehensive staging evaluation was completed prior to this consultation. I have personally reviewed the relevant imaging and pathology reports.

- **CT Chest/Abdomen/Pelvis:** Revealed a 5.2 cm spiculated mass in the right upper lobe of the lung. There was extensive ipsilateral mediastinal and hilar lymphadenopathy. Additionally, pathologically enlarged contralateral supraclavicular lymph nodes were identified, consistent with distant metastatic disease. No other sites of visceral metastasis were identified in the chest, abdomen, or pelvis.

- **MRI Brain with and without contrast:** Demonstrated at least three distinct, ring-enhancing intraparenchymal lesions in the bilateral cerebral hemispheres, consistent with metastatic deposits. The largest lesion is located in the left frontal lobe.

- **Pathology:** The patient underwent a CT-guided core needle biopsy of the right upper lobe lung mass at [De-identified] Hospital. Histopathologic examination confirmed a diagnosis of poorly differentiated adenocarcinoma, consistent with a lung primary.

**Molecular Studies:**
Next-generation sequencing (NGS) was performed on the tumor tissue specimen. The results are as follows:
- No actionable driver alteration was identified. The tumor was negative for mutations, fusions, or amplifications in EGFR, ALK, ROS1, BRAF, MET exon 14, RET, KRAS, and ERBB2.
- Tumor Mutational Burden (TMB) was reported as high (>16 mutations/megabase).
- PD-L1 expression testing was not performed on this sample.

**Problem Summary:**
In summary, this is a 43-year-old current smoker with a new diagnosis of Stage IV (AJCC 8th Edition) non-small cell lung cancer, adenocarcinoma histology. The disease is metastatic at presentation, with confirmed involvement of the brain and distant (supraclavicular) lymph nodes. Comprehensive molecular profiling did not identify any targetable driver alterations but did reveal a high tumor mutational burden. The patient is treatment-naive and presents today for initial consultation to discuss these findings.

### Reviewer Ratings

| Item | Rating |
|---|---|
| Plausibility (1–5) |  |
| Factual accuracy (Pass/Fail) |  |
| Completeness (Pass/Fail) |  |
| Treatment-naive (Pass/Fail) |  |
| Demographic neutrality (Pass/Fail) |  |
| Comments |  |

---

## Case 17  [PASS]

### Structured Profile (Ground Truth)
```
Stage         : IV
Histology     : adenocarcinoma
Brain mets    : True
Smoking       : never smoker
Molecular     : neg: EGFR-, ALK-, KRAS-
PD-L1         : positive_no_tps
TMB           : intermediate (2–16 mut/Mb)
```

### Generated Note

**HPI:**
This is a 66-year-old with a history of being a never-smoker who is seen today for an initial medical oncology consultation. The patient was in their usual state of good health until approximately six weeks ago when they began experiencing intermittent headaches and a sense of imbalance. These symptoms progressively worsened, prompting a visit to their primary care provider. An outpatient MRI of the brain was ordered, which revealed multiple enhancing intracranial lesions suspicious for metastatic disease.

Subsequent staging evaluation with a CT of the chest, abdomen, and pelvis was performed. This imaging identified a primary spiculated mass in the left upper lobe of the lung, along with mediastinal lymphadenopathy. No other sites of distant metastatic disease were identified in the torso. The patient was referred for a CT-guided core needle biopsy of the lung mass for definitive diagnosis. The patient reports a good energy level and is fully ambulatory and self-caring, with an ECOG performance status of 1. They have noted a mild, non-productive cough but deny significant dyspnea, hemoptysis, or chest pain. There has been no significant weight loss.

**Diagnostic Workup:**
A CT-guided core biopsy of the left upper lobe lung mass was performed on [De-identified date]. The pathology returned as poorly differentiated adenocarcinoma, consistent with a primary lung malignancy.

Imaging studies have been reviewed. An MRI of the brain confirmed the presence of multiple parenchymal metastatic lesions. A contrast-enhanced CT of the chest, abdomen, and pelvis demonstrated a 3.2 cm primary mass in the left upper lobe and ipsilateral mediastinal lymphadenopathy. No evidence of metastatic disease was noted in the liver, adrenal glands, or bones. The combination of a primary lung adenocarcinoma and brain metastases confirms a diagnosis of Stage IV disease.

**Molecular Studies:**
Next-generation sequencing was performed on the tumor tissue obtained from the lung biopsy.
- No actionable driver alteration was identified. The tumor was negative for mutations or rearrangements in EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2.
- PD-L1 expression was positive (TPS percentage not available).
- Tumor mutational burden (TMB) was determined to be intermediate (2–16 mut/Mb).
- A loss-of-function mutation in STK11 was detected.

**Problem Summary:**
This is a 66-year-old never-smoker with a new diagnosis of AJCC Stage IV non-small cell lung cancer, adenocarcinoma histology, metastatic to the brain. Molecular profiling is notable for positive PD-L1 expression and an STK11 loss-of-function mutation, with no identified actionable driver mutations. The patient is treatment-naive and presents for initial consultation to discuss the diagnosis.

### Reviewer Ratings

| Item | Rating |
|---|---|
| Plausibility (1–5) |  |
| Factual accuracy (Pass/Fail) |  |
| Completeness (Pass/Fail) |  |
| Treatment-naive (Pass/Fail) |  |
| Demographic neutrality (Pass/Fail) |  |
| Comments |  |

---

## Case 18  [PASS]

### Structured Profile (Ground Truth)
```
Stage         : IB
Histology     : adenocarcinoma
Brain mets    : False
Smoking       : former smoker (quit <1 year ago)
Molecular     : neg: EGFR-, ALK-, KRAS-
PD-L1         : not_tested
TMB           : low (<2 mut/Mb)
```
**QA warnings:** brain_mets=False but note appears to mention brain metastasis

### Generated Note

**HPI:**
This is a 78-year-old individual with a recent history of smoking cessation (quit within the last year) who presents for initial medical oncology consultation for a new diagnosis of non-small cell lung cancer. The patient was in their usual state of health until approximately two months prior to presentation, when they developed a new, persistent, non-productive cough. This prompted a visit to their primary care provider, who obtained a chest radiograph that demonstrated a right upper lobe opacity. The patient denies hemoptysis, chest pain, or significant weight loss. Performance status is excellent, and the patient remains fully active and independent with all activities of daily living.

**Diagnostic Workup:**
Following the abnormal chest X-ray, a contrast-enhanced CT of the chest, abdomen, and pelvis was performed on [De-identified Date]. This study confirmed the presence of a 2.8 cm spiculated solid nodule in the right upper lobe. There was no evidence of mediastinal or hilar lymphadenopathy. The visualized portions of the abdomen and pelvis were negative for metastatic disease.

To complete staging, a PET/CT scan was subsequently obtained. This demonstrated intense FDG-avidity localized to the known right upper lobe nodule, with no other sites of abnormal uptake to suggest regional nodal involvement or distant metastatic disease. A staging MRI of the brain was also performed and was negative for intracranial metastases.

A CT-guided core needle biopsy of the right upper lobe lung nodule was performed on [De-identified Date]. Pathologic analysis of the tissue confirmed the diagnosis of invasive adenocarcinoma, consistent with a primary lung origin.

Based on this workup, the patient is diagnosed with clinical Stage IB (T2aN0M0) non-small cell lung cancer.

**Molecular Studies:**
Next-generation sequencing was performed on the tumor tissue obtained from the biopsy. No actionable driver alteration was identified. Specific testing was negative for mutations or rearrangements in EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2. Tumor mutational burden (TMB) was determined to be low at <2 mutations/megabase. PD-L1 expression was not tested on this specimen.

**Problem Summary:**
In summary, this is a 78-year-old former smoker who presents for evaluation of a newly diagnosed, treatment-naive, clinical Stage IB (T2aN0M0) non-small cell lung cancer of adenocarcinoma histology. The workup has been notable for localized disease without evidence of regional or distant metastases. Comprehensive molecular profiling of the tumor did not identify an actionable oncogenic driver.

### Reviewer Ratings

| Item | Rating |
|---|---|
| Plausibility (1–5) |  |
| Factual accuracy (Pass/Fail) |  |
| Completeness (Pass/Fail) |  |
| Treatment-naive (Pass/Fail) |  |
| Demographic neutrality (Pass/Fail) |  |
| Comments |  |

---

## Case 19  [FAIL]

### Structured Profile (Ground Truth)
```
Stage         : IV
Histology     : adenocarcinoma
Brain mets    : True
Smoking       : current smoker
Molecular     : neg: EGFR-, ALK-, KRAS-
PD-L1         : intermediate
TMB           : intermediate (2–16 mut/Mb)
```

**QA failures:** brain_mets=True but no brain metastasis stated

### Generated Note

**HPI:**
This is a 68-year-old individual who presents for an initial medical oncology consultation following a new diagnosis of non-small cell lung cancer. The patient initially sought medical attention several weeks ago for new-onset persistent headaches and mild word-finding difficulties. An initial evaluation in the emergency department led to brain imaging, which was concerning for metastatic disease. The patient reports a several-month history of a mild, intermittent cough and an unintentional 10-pound weight loss but had attributed these to a long-standing smoking history. The patient is a current smoker. The patient remains fully ambulatory and independent in all activities of daily living.

**Diagnostic Workup:**
A comprehensive staging workup was initiated. A CT scan of the chest, abdomen, and pelvis revealed a 3.5 cm spiculated mass in the upper lobe of the right lung with associated mediastinal lymphadenopathy. No other sites of extracranial metastatic disease were identified in the liver, adrenal glands, or bones. A subsequent MRI of the brain confirmed the presence of multiple enhancing parenchymal lesions in the cerebral hemispheres, consistent with metastatic disease.

A CT-guided core needle biopsy of the right upper lobe lung mass was performed. Pathologic analysis of the tissue specimen confirmed a diagnosis of invasive adenocarcinoma, consistent with a lung primary.

**Molecular Studies:**
Tumor tissue was sent for comprehensive molecular profiling and immunohistochemistry.
- PD-L1 expression was positive, with a Tumor Proportion Score (TPS) in the 1-49% range.
- Tumor Mutational Burden (TMB) was intermediate (2-16 mutations/megabase).
- Next-generation sequencing did not identify any actionable driver mutations. Specifically, the tumor was negative for alterations in EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2.
- A loss-of-function mutation was identified in the STK11 gene.

**Problem Summary:**
In summary, this is a 68-year-old, treatment-naive patient with a new diagnosis of Stage IV non-small cell lung cancer of adenocarcinoma histology, metastatic to the brain. Molecular studies are notable for PD-L1 positivity (TPS 1-49%) and an STK11 loss-of-function mutation, with no other targetable driver alterations identified. The patient is here for initial consultation to discuss the diagnosis and the implications of these findings.

### Reviewer Ratings

| Item | Rating |
|---|---|
| Plausibility (1–5) |  |
| Factual accuracy (Pass/Fail) |  |
| Completeness (Pass/Fail) |  |
| Treatment-naive (Pass/Fail) |  |
| Demographic neutrality (Pass/Fail) |  |
| Comments |  |

---

## Case 20  [PASS]

### Structured Profile (Ground Truth)
```
Stage         : IV
Histology     : adenocarcinoma
Brain mets    : False
Smoking       : former smoker (quit >1 year ago)
Molecular     : neg: EGFR-, ALK-, KRAS-
PD-L1         : high
TMB           : intermediate (2–16 mut/Mb)
```
**QA warnings:** brain_mets=False but note appears to mention brain metastasis

### Generated Note

**MEDICAL ONCOLOGY INITIAL CONSULTATION**

**PATIENT:** [De-identified]
**MRN:** [De-identified]
**DATE OF CONSULTATION:** [De-identified]

**HISTORY OF PRESENT ILLNESS:**
This is an 80-year-old individual with a history of hypertension and hyperlipidemia, who is referred for initial oncology consultation for a new diagnosis of non-small cell lung cancer. The patient is a former smoker, having quit over one year ago.

The patient was in their usual state of health until approximately two months prior to presentation, when they developed a persistent, non-productive cough and progressive exertional dyspnea. This was followed by the onset of new, constant mid-back pain, which was not relieved by over-the-counter analgesics. Over this period, the patient also reports an estimated 10-pound weight loss and increasing fatigue. Due to the progression of these symptoms, they presented to their primary care provider for evaluation, which initiated a diagnostic workup. The patient remains ambulatory and capable of all self-care but is restricted in physically strenuous activity. ECOG Performance Status is 1.

**DIAGNOSTIC WORKUP:**
An initial chest X-ray revealed a right upper lobe lung mass with an associated right-sided pleural effusion.

A subsequent CT of the chest, abdomen, and pelvis with contrast confirmed a 4.5 cm spiculated mass in the right upper lobe. It also characterized a moderate right malignant-appearing pleural effusion and identified multiple sclerotic lesions in the thoracic spine and ribs, suspicious for osseous metastases.

A whole-body PET/CT scan was performed for staging purposes. This study demonstrated intense FDG-avidity in the primary right upper lobe lung mass, as well as in the right pleura and multiple sites of the axial skeleton, consistent with metastatic disease.

A CT-guided core needle biopsy of the right upper lobe lung mass was performed by Interventional Radiology. Pathology from this specimen returned as a poorly differentiated adenocarcinoma, consistent with a lung primary.

A brain MRI with and without contrast was performed to complete staging and was negative for intracranial metastases.

**MOLECULAR STUDIES:**
Comprehensive next-generation sequencing was performed on the tumor tissue specimen.
- No actionable driver alteration was identified. Specifically, testing was negative for mutations or rearrangements in EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2.
- PD-L1 expression by immunohistochemistry (IHC) was determined to be high, with a Tumor Proportion Score (TPS) of ≥50%.
- Tumor Mutational Burden (TMB) was found to be intermediate (2–16 mut/Mb).

**PROBLEM SUMMARY:**
In summary, this is an 80-year-old former smoker with a new diagnosis of Stage IV (AJCC 8th Edition) non-small cell lung adenocarcinoma. The disease is metastatic to bone and the pleura, with no evidence of central nervous system involvement. Molecular profiling of the tumor is notable for the absence of an actionable driver mutation and for high PD-L1 expression (TPS ≥50%). The patient is treatment-naive and presents today for comprehensive evaluation and to discuss the implications of these findings.

### Reviewer Ratings

| Item | Rating |
|---|---|
| Plausibility (1–5) |  |
| Factual accuracy (Pass/Fail) |  |
| Completeness (Pass/Fail) |  |
| Treatment-naive (Pass/Fail) |  |
| Demographic neutrality (Pass/Fail) |  |
| Comments |  |

---

## Case 21  [PASS]

### Structured Profile (Ground Truth)
```
Stage         : IV
Histology     : adenocarcinoma
Brain mets    : True
Smoking       : former smoker (quit >1 year ago)
Molecular     : neg: EGFR-, ALK-, KRAS-
PD-L1         : not_tested
TMB           : intermediate (2–16 mut/Mb)
```

### Generated Note

**HPI:**
This is a 70-year-old individual with a history of smoking (quit >1 year ago) who is referred for initial oncology consultation for a new diagnosis of non-small cell lung cancer. The patient was in their usual state of health until approximately 6 weeks prior to this evaluation, when they began to develop a persistent, non-productive cough and mild dyspnea on exertion. Over the past month, these symptoms have been accompanied by new-onset intermittent headaches and a feeling of unsteadiness. Due to the progression of these symptoms, the patient presented for medical evaluation. They report increased fatigue but remain ambulatory and are able to perform all activities of daily living, with an ECOG performance status of 1.

**Diagnostic Workup:**
The patient's initial workup began with a chest X-ray that revealed a suspicious right upper lobe lung opacity.

A subsequent contrast-enhanced CT of the chest, abdomen, and pelvis was performed. This study characterized a 3.8 cm spiculated mass in the right upper lobe, with associated bulky mediastinal and right hilar adenopathy.

Given the patient's presenting neurologic symptoms, a brain MRI with and without contrast was obtained. This imaging demonstrated multiple, well-circumscribed, ring-enhancing lesions in the bilateral cerebral hemispheres, consistent with metastatic disease.

A whole-body PET/CT scan was performed for staging, which confirmed high FDG-avidity in the primary right lung mass, the mediastinal/hilar lymph nodes, and the known cerebral metastases. No other sites of FDG-avid disease were identified in the neck, chest, abdomen, or pelvis.

A CT-guided core needle biopsy of the right upper lobe mass was performed on [De-identified date]. Pathologic analysis confirmed a diagnosis of lung adenocarcinoma.

**Molecular Studies:**
Next-generation sequencing was performed on the tumor tissue. No actionable driver alteration was identified. Comprehensive testing was negative for mutations or rearrangements involving EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2.

Tumor Mutational Burden (TMB) was reported as intermediate (2–16 mut/Mb).

PD-L1 expression was not tested, as this was not standard practice at the time of the initial tissue analysis.

**Problem Summary:**
In summary, this is a 70-year-old former smoker presenting for initial evaluation of a new diagnosis of treatment-naive, Stage IV non-small cell lung cancer of adenocarcinoma histology, metastatic to the brain. Molecular profiling of the tumor is negative for common actionable driver mutations. The patient is here today to discuss the diagnosis and establish care.

### Reviewer Ratings

| Item | Rating |
|---|---|
| Plausibility (1–5) |  |
| Factual accuracy (Pass/Fail) |  |
| Completeness (Pass/Fail) |  |
| Treatment-naive (Pass/Fail) |  |
| Demographic neutrality (Pass/Fail) |  |
| Comments |  |

---

## Case 22  [FAIL]

### Structured Profile (Ground Truth)
```
Stage         : IV
Histology     : adenocarcinoma
Brain mets    : True
Smoking       : former smoker (quit >1 year ago)
Molecular     : EGFR other_sensitising | neg: ALK-, KRAS-
PD-L1         : intermediate
TMB           : intermediate (2–16 mut/Mb)
```

**QA failures:** brain_mets=True but no brain metastasis stated

### Generated Note

**HISTORY OF PRESENT ILLNESS:**
The patient is a 55-year-old with a history of former tobacco use who presents for an initial medical oncology consultation for a new diagnosis of non-small cell lung cancer.

The patient was in their usual state of good health until approximately two months prior to presentation, when they began to experience intermittent, dull headaches and a new, persistent, non-productive cough. The headaches gradually increased in frequency and were not fully relieved by over-the-counter analgesics. An episode of dizziness and word-finding difficulty prompted a visit to an emergency department.

An initial non-contrast head CT revealed several parenchymal lesions concerning for metastatic disease. A subsequent contrast-enhanced CT of the chest, abdomen, and pelvis was performed, which identified a spiculated mass in the right upper lobe of the lung with associated mediastinal and hilar lymphadenopathy. No other sites of distant disease were identified in the chest or abdomen.

The patient was admitted for further evaluation. A contrast-enhanced MRI of the brain was performed, which confirmed the presence of multiple enhancing cerebral lesions consistent with metastases. To establish a tissue diagnosis, the patient underwent a CT-guided core needle biopsy of the right upper lobe lung mass.

The patient has had a mild decline in appetite but reports no significant weight loss. They remain fully ambulatory and capable of all self-care, though they note increased fatigue. Their ECOG performance status is 1. The patient is now referred to our clinic to discuss the diagnosis and establish care.

**DIAGNOSTIC WORKUP:**
I have personally reviewed the available outside records, imaging, and pathology reports.

*   **MRI Brain, with and without contrast [De-identified Date]:** Multiple ring-enhancing lesions within the bilateral cerebral hemispheres, consistent with metastatic deposits.
*   **CT Chest/Abdomen/Pelvis, with contrast [De-identified Date]:** A 3.5 cm spiculated mass in the right upper lobe. Prominent mediastinal and right hilar lymphadenopathy. No evidence of metastatic disease to the liver, adrenal glands, or bone.
*   **Pathology, CT-guided biopsy of right lung mass [De-identified Date]:** Adenocarcinoma, consistent with a lung primary origin.

**MOLECULAR STUDIES:**
Next-generation sequencing was performed on the lung tumor tissue.
*   **Actionable Driver Mutations:** An EGFR uncommon sensitizing mutation was detected.
*   **Other Genes:** The tumor was negative for alterations in ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2.
*   **PD-L1 Expression:** Positive, with a Tumor Proportion Score (TPS) of 1-49%.
*   **Tumor Mutational Burden (TMB):** Intermediate (2-16 mutations/megabase).

**PROBLEM SUMMARY:**
This is a 55-year-old, treatment-naive patient with a new diagnosis of AJCC Stage IV non-small cell lung cancer, adenocarcinoma histology, metastatic to the brain. Molecular profiling is notable for the presence of an EGFR uncommon sensitizing mutation.

### Reviewer Ratings

| Item | Rating |
|---|---|
| Plausibility (1–5) |  |
| Factual accuracy (Pass/Fail) |  |
| Completeness (Pass/Fail) |  |
| Treatment-naive (Pass/Fail) |  |
| Demographic neutrality (Pass/Fail) |  |
| Comments |  |

---

## Case 23  [PASS]

### Structured Profile (Ground Truth)
```
Stage         : IIIA
Histology     : squamous
Brain mets    : False
Smoking       : current smoker
Molecular     : neg: EGFR-, ALK-, KRAS-
PD-L1         : negative
TMB           : intermediate (2–16 mut/Mb)
Prior cancers : Bladder Cancer
```
**QA warnings:** brain_mets=False but note appears to mention brain metastasis; possible prior-treatment language (should be naive): 'status post transurethral resection'

### Generated Note

**HISTORY OF PRESENT ILLNESS**
This is a 56-year-old individual with a past medical history of bladder cancer who is referred for initial medical oncology consultation regarding a new diagnosis of non-small cell lung cancer.

The patient was in their usual state of health until approximately three months prior to presentation, when they developed a persistent, dry cough and mild shortness of breath with exertion. These symptoms progressively worsened, prompting a visit to their primary care provider. An initial chest X-ray was performed which revealed a right upper lobe lung mass.

A subsequent contrast-enhanced CT of the chest, abdomen, and pelvis was obtained for staging. This confirmed a 4.8 cm spiculated mass in the right upper lobe. The scan also revealed extensive ipsilateral mediastinal lymphadenopathy, with a conglomerate of nodes in the right paratracheal and subcarinal stations. No suspicious lesions were identified in the liver, adrenal glands, or other visualized portions of the abdomen and pelvis. The patient then underwent a CT-guided core needle biopsy of the right lung mass, which established the diagnosis of squamous cell carcinoma. A staging PET/CT scan demonstrated intense FDG uptake in the primary lung mass and the mediastinal lymph nodes, with no evidence of distant metastatic disease. A dedicated MRI of the brain was also performed and was negative for intracranial metastases.

The patient reports a 10-pound unintentional weight loss over the past few months but otherwise denies fevers, chills, or significant chest pain. Their appetite is fair. They remain fully ambulatory and independent in all activities of daily living, with an ECOG performance status of 0. The patient is a current smoker and has been counseled on cessation.

**PAST MEDICAL HISTORY**
- Bladder cancer, status post transurethral resection, under routine urologic surveillance.
- Hypertension

**ALLERGIES**
- No known drug allergies.

**MEDICATIONS**
- Lisinopril 10 mg daily

**SOCIAL HISTORY**
- Current smoker with an approximately 40-pack-year history.

**PHYSICAL EXAM**
Vitals: Blood pressure 132/78, pulse 84, temperature 36.8 C, resp. rate 16, SpO2 97% on room air.
General: Well-appearing, in no acute distress.
HEENT: Oropharynx is clear, mucous membranes are moist. No cervical or supraclavicular lymphadenopathy.
Lungs: Clear to auscultation bilaterally. No wheezes or rales.
Cardiovascular: Regular rate and rhythm, no murmurs.
Abdomen: Soft, non-tender, non-distended.
Extremities: No clubbing, cyanosis, or edema.
Neuro: Alert and oriented. Grossly non-focal.

**DIAGNOSTIC WORKUP**
- **CT Chest/Abdomen/Pelvis with Contrast ([De-identified Date]):** Revealed a 4.8 cm spiculated mass in the right upper lobe with associated bulky ipsilateral mediastinal lymphadenopathy. No evidence of distant metastatic disease.
- **PET/CT ([De-identified Date]):** Intense FDG-avidity corresponding to the right upper lobe mass and right-sided mediastinal and hilar lymph nodes. No other sites of FDG-avid disease to suggest distant metastases.
- **MRI Brain ([De-identified Date]):** Negative for intracranial metastatic disease.
- **CT-Guided Biopsy, Right Lung Mass ([De-identified Date]):** Pathology consistent with invasive, moderately differentiated squamous cell carcinoma.

**MOLECULAR STUDIES**
Next-generation sequencing performed on the tumor specimen showed no actionable driver alterations, including negative results for EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2.
- **PD-L1:** Negative (Tumor Proportion Score < 1%).
- **Tumor Mutational Burden (TMB):** Intermediate (12 mutations/megabase).

**PROBLEM SUMMARY**
In summary, this is a 56-year-old with an excellent performance status who presents with a new diagnosis of locally advanced, non-metastatic Stage IIIA non-small cell lung cancer, squamous cell histology. Staging workup including PET/CT and brain MRI confirms disease is confined to the right hemithorax and ipsilateral mediastinum. Molecular profiling is notable for negative PD-L1 expression, an intermediate tumor mutational burden, and no identifiable targetable driver mutations. The patient is here for initial consultation to discuss the diagnosis and review potential treatment strategies.

### Reviewer Ratings

| Item | Rating |
|---|---|
| Plausibility (1–5) |  |
| Factual accuracy (Pass/Fail) |  |
| Completeness (Pass/Fail) |  |
| Treatment-naive (Pass/Fail) |  |
| Demographic neutrality (Pass/Fail) |  |
| Comments |  |

---

## Case 24  [PASS]

### Structured Profile (Ground Truth)
```
Stage         : IIB
Histology     : squamous
Brain mets    : False
Smoking       : former smoker (quit >1 year ago)
Molecular     : neg: EGFR-, ALK-, KRAS-
PD-L1         : intermediate
TMB           : intermediate (2–16 mut/Mb)
```
**QA warnings:** brain_mets=False but note appears to mention brain metastasis

### Generated Note

**HPI:**
This is an initial medical oncology consultation for a 73-year-old with a new diagnosis of non-small cell lung cancer. The patient is a former smoker (quit >1 year ago) who was in their usual state of good health until approximately two months prior to presentation, when they developed a persistent, non-productive cough. Over the subsequent weeks, the cough worsened and was associated with intermittent right-sided chest discomfort and one episode of scant hemoptysis, which prompted them to seek evaluation with their primary care provider. The patient denies fevers, chills, night sweats, or significant weight loss. They maintain an excellent performance status, ECOG 0, and are fully independent in all activities of daily living.

**Diagnostic Workup:**
An initial chest X-ray revealed a right upper lobe opacity, prompting further investigation.

A CT of the chest with contrast was performed on [De-identified Date], which demonstrated a 4.5 cm spiculated mass in the right upper lobe. There was no evidence of mediastinal or hilar lymphadenopathy.

For staging purposes, a PET/CT was performed on [De-identified Date]. This study confirmed a hypermetabolic primary mass in the right upper lobe corresponding to the lesion seen on CT, with a maximum SUV of 12.4. Importantly, there was no evidence of FDG-avid mediastinal, hilar, or supraclavicular lymphadenopathy (N0). There were no PET-avid lesions identified in the contralateral lung, liver, adrenal glands, or skeleton to suggest distant metastatic disease (M0).

A brain MRI with and without contrast was completed on [De-identified Date] as part of the standard staging workup and was negative for any evidence of intracranial metastases.

On [De-identified Date], the patient underwent a CT-guided core needle biopsy of the right upper lobe mass. Pathology returned as invasive, moderately differentiated squamous cell carcinoma.

The combination of these findings establishes a diagnosis of clinical Stage IIB (cT2b N0 M0) non-small cell lung cancer.

**Molecular Studies:**
Next-generation sequencing (NGS) was performed on the tumor tissue specimen.
- No actionable driver alterations were identified. The tumor was negative for mutations or rearrangements in EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2.
- PD-L1 expression by immunohistochemistry (IHC) was positive, with a Tumor Proportion Score (TPS) in the 1–49% range.
- Tumor Mutational Burden (TMB) was found to be intermediate (2–16 mutations/megabase).

**Problem Summary:**
This is a 73-year-old with an excellent performance status and a new diagnosis of Stage IIB (cT2b N0 M0) squamous non-small cell lung cancer of the right upper lobe. The patient is treatment-naive. Molecular profiling is notable for PD-L1 expression (TPS 1-49%) but is negative for any actionable driver mutations. The patient presents today for initial consultation to discuss the diagnosis and establish care.

### Reviewer Ratings

| Item | Rating |
|---|---|
| Plausibility (1–5) |  |
| Factual accuracy (Pass/Fail) |  |
| Completeness (Pass/Fail) |  |
| Treatment-naive (Pass/Fail) |  |
| Demographic neutrality (Pass/Fail) |  |
| Comments |  |

---

## Case 25  [PASS]

### Structured Profile (Ground Truth)
```
Stage         : IV
Histology     : adenocarcinoma
Brain mets    : False
Smoking       : former smoker (quit >1 year ago)
Molecular     : neg: EGFR-, ALK-, KRAS-
PD-L1         : intermediate
TMB           : intermediate (2–16 mut/Mb)
```
**QA warnings:** brain_mets=False but note appears to mention brain metastasis

### Generated Note

**HPI:**
This is a 68-year-old individual with a history of tobacco use (former smoker, quit over one year ago) who presents for initial medical oncology consultation regarding a new diagnosis of non-small cell lung cancer. The patient was in a usual state of health until approximately two months prior to presentation, when a persistent, non-productive cough developed, accompanied by progressive fatigue. Over the past month, the patient noted the onset of new, persistent mid-back pain, which prompted an evaluation with their primary care provider. The patient reports a 10-pound unintentional weight loss over the last three months. Performance status is ECOG 1; the patient is fully ambulatory and capable of all self-care but is restricted in physically strenuous activity by symptoms.

**Diagnostic Workup:**
An initial chest X-ray revealed a right-sided lung mass, leading to a staging PET/CT scan performed on [De-identified Date]. This study demonstrated a hypermetabolic 4.2 cm primary mass in the right upper lobe. There was evidence of extensive metastatic disease, including hypermetabolic mediastinal and contralateral supraclavicular lymphadenopathy. Distant metastatic disease was identified with avid uptake in a 2.5 cm left adrenal nodule and multiple osseous lesions, including a lytic lesion in the T8 vertebral body corresponding to the patient's site of pain.

A CT-guided core biopsy of the right upper lobe lung mass was performed by Interventional Radiology on [De-identified Date]. Pathologic review confirmed the diagnosis of non-small cell lung cancer with adenocarcinoma histology.

A brain MRI with and without contrast was performed for staging purposes and was negative for intracranial metastases.

**Molecular Studies:**
Next-generation sequencing (NGS) was performed on the tumor tissue. No actionable driver alteration was identified; results were negative for mutations or rearrangements in EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2.

Immunohistochemistry for PD-L1 was performed, showing a Tumor Proportion Score (TPS) in the 1–49% range. Tumor Mutational Burden (TMB) was calculated and found to be intermediate (2–16 mut/Mb).

**Problem Summary:**
This is a 68-year-old former smoker presenting with newly diagnosed, treatment-naive, AJCC Stage IV non-small cell lung adenocarcinoma, with metastatic disease to bone, adrenal gland, and distant lymph nodes. Molecular profiling is notable for a PD-L1 TPS of 1-49% and the absence of an identifiable targetable driver mutation.

### Reviewer Ratings

| Item | Rating |
|---|---|
| Plausibility (1–5) |  |
| Factual accuracy (Pass/Fail) |  |
| Completeness (Pass/Fail) |  |
| Treatment-naive (Pass/Fail) |  |
| Demographic neutrality (Pass/Fail) |  |
| Comments |  |

---

## Case 26  [PASS]

### Structured Profile (Ground Truth)
```
Stage         : IIIA
Histology     : adenocarcinoma
Brain mets    : False
Smoking       : never smoker
Molecular     : EGFR exon_19_del | neg: ALK-, KRAS-
PD-L1         : intermediate
TMB           : intermediate (2–16 mut/Mb)
```

### Generated Note

**History of Present Illness**

This is a 58-year-old individual with a history of being a never-smoker who presents for initial oncology consultation regarding a new diagnosis of non-small cell lung cancer. The patient was in their usual state of good health until approximately three months prior to presentation, when they developed a persistent, dry cough. This was initially attributed to seasonal allergies but did not resolve with over-the-counter remedies. Over the subsequent weeks, the patient also noted the onset of mild shortness of breath with significant exertion. They deny any fevers, chills, hemoptysis, or unintentional weight loss.

Due to the persistence of symptoms, the patient sought evaluation with their primary care provider. A chest X-ray was performed which revealed a right-sided pulmonary opacity, prompting a referral for further diagnostic imaging. A contrast-enhanced CT of the chest, abdomen, and pelvis was obtained, which confirmed the presence of a primary mass in the right upper lobe, along with prominent ipsilateral mediastinal and subcarinal lymphadenopathy. No evidence of distant metastatic disease was identified in the chest, abdomen, or pelvis.

To complete staging and obtain a tissue diagnosis, the patient underwent a PET/CT scan which demonstrated intense FDG-avidity corresponding to the right upper lobe mass and the mediastinal lymph nodes, with no other suspicious sites of hypermetabolic activity. A subsequent MRI of the brain was negative for intracranial metastases. The patient then underwent bronchoscopy with endobronchial ultrasound (EBUS)-guided fine-needle aspiration of both the primary lung mass and a subcarinal lymph node, which established the diagnosis. The patient has a good performance status (ECOG 1) and remains active, with symptoms that are present but not debilitating.

**Diagnostic Workup**

*   **CT Chest/Abdomen/Pelvis with contrast [De-identified Date]:** Revealed a 4.2 cm spiculated mass in the posterior segment of the right upper lobe. Associated enlarged right paratracheal (station 4R) and subcarinal (station 7) lymph nodes were noted, with the largest measuring 2.1 cm in short-axis. The liver, adrenal glands, and osseous structures were free of metastatic lesions.
*   **PET/CT [De-identified Date]:** Showed intense hypermetabolic activity in the right upper lobe mass (SUVmax 11.8) and in the right paratracheal and subcarinal lymph nodes (SUVmax 9.2). No other sites of abnormal FDG uptake to suggest distant metastatic disease.
*   **MRI Brain with and without contrast [De-identified Date]:** No evidence of intracranial metastatic disease.
*   **Bronchoscopy with EBUS-FNA [De-identified Date]:** Biopsy of the right upper lobe mass and a subcarinal lymph node was performed. Pathology from both sites was consistent with invasive adenocarcinoma.

**Pathology Report Summary (from EBUS-FNA):**
*   **Specimen:** Right upper lobe lung mass and subcarinal lymph node (Station 7).
*   **Final Diagnosis:** Invasive Adenocarcinoma, consistent with lung primary.
*   **Staging:** The combination of a >4 cm primary tumor (T2b) and ipsilateral mediastinal/subcarinal nodal involvement (N2) in the absence of distant metastases (M0) is consistent with **AJCC 8th Edition Pathologic Stage Group IIIA (pT2bN2M0)**.

**Molecular Studies**

Next-generation sequencing (NGS) performed on the tumor tissue returned the following results:
*   **Actionable Driver Mutation:** EGFR exon 19 deletion detected.
*   **Additional Markers (Negative):** ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2 rearrangements/mutations were not detected.
*   **PD-L1 Expression:** Positive, Tumor Proportion Score (TPS) 1-49%.
*   **Tumor Mutational Burden (TMB):** Intermediate (2-16 mutations/megabase).

**Problem Summary**

In summary, this is a 58-year-old never-smoker with a new diagnosis of Stage IIIA (T2bN2M0) non-small cell lung cancer, adenocarcinoma histology. The patient has completed a full staging workup which confirms locoregionally advanced disease without distant metastases. Molecular profiling of the tumor is notable for a sensitizing EGFR exon 19 deletion and PD-L1 expression of 1-49%. The patient is seen today for initial consultation to discuss the diagnosis and establish a plan for oncologic care.

### Reviewer Ratings

| Item | Rating |
|---|---|
| Plausibility (1–5) |  |
| Factual accuracy (Pass/Fail) |  |
| Completeness (Pass/Fail) |  |
| Treatment-naive (Pass/Fail) |  |
| Demographic neutrality (Pass/Fail) |  |
| Comments |  |

---

## Case 27  [PASS]

### Structured Profile (Ground Truth)
```
Stage         : IV
Histology     : adenocarcinoma
Brain mets    : True
Smoking       : never smoker
Molecular     : EGFR exon_19_del | neg: ALK-, KRAS-
PD-L1         : low
TMB           : intermediate (2–16 mut/Mb)
```

### Generated Note

**HPI:**
This is a 52-year-old individual with a history of never smoking who presents for an initial medical oncology consultation following a new diagnosis of metastatic non-small cell lung cancer. The patient was in their usual state of health until approximately two months prior to presentation, when they began to experience a persistent, non-productive cough and progressive exertional dyspnea. Over the subsequent weeks, they also developed new-onset headaches and intermittent right-sided rib pain, which prompted a visit to their primary care provider. The patient is otherwise active and maintains a good performance status, though is noted to have some fatigue related to symptoms.

**Diagnostic Workup:**
An initial chest X-ray revealed a right-sided lung mass, which led to further cross-sectional imaging.

A CT of the chest, abdomen, and pelvis with contrast was performed, which demonstrated a large primary mass in the right upper lobe with associated mediastinal and hilar adenopathy. The scan also identified multiple bilateral pulmonary nodules consistent with contralateral metastatic disease, a left adrenal metastasis, and suspicious supraclavicular lymphadenopathy.

A whole-body PET/CT scan was subsequently obtained for staging. This confirmed high metabolic activity in the known right upper lobe primary mass, as well as in sites of metastatic disease involving the contralateral lung, mediastinal/hilar/supraclavicular lymph nodes, the left adrenal gland, and multiple osseous sites, including the ribs.

Given the presenting complaint of headaches, a brain MRI with contrast was performed. This revealed multiple small parenchymal metastases consistent with intracranial metastatic disease.

A CT-guided core biopsy of the right upper lobe lung mass was performed. Pathology confirmed non-small cell lung cancer with adenocarcinoma histology.

**Molecular Studies:**
Next-generation sequencing (NGS) and immunohistochemistry were performed on the tumor tissue.
- **Driver Mutations:** An actionable sensitizing EGFR exon 19 deletion was detected.
- **Other Markers:** The tumor was negative for alterations in ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2.
- **PD-L1:** Tumor Proportion Score (TPS) was <1%.
- **TMB:** Tumor Mutational Burden was intermediate (2–16 mut/Mb).

**Problem Summary:**
In summary, this is a 52-year-old with a new diagnosis of Stage IV non-small cell lung cancer, adenocarcinoma histology. Staging studies confirm metastatic disease to the brain, bone, adrenal gland, contralateral lung, and distant lymph nodes. The patient is a never-smoker. Molecular profiling of the tumor is notable for a sensitizing EGFR exon 19 deletion. The patient is treatment-naive and is seen today for initial evaluation and discussion of the diagnosis.

### Reviewer Ratings

| Item | Rating |
|---|---|
| Plausibility (1–5) |  |
| Factual accuracy (Pass/Fail) |  |
| Completeness (Pass/Fail) |  |
| Treatment-naive (Pass/Fail) |  |
| Demographic neutrality (Pass/Fail) |  |
| Comments |  |

---

## Case 28  [PASS]

### Structured Profile (Ground Truth)
```
Stage         : IV
Histology     : adenocarcinoma
Brain mets    : False
Smoking       : current smoker
Molecular     : neg: EGFR-, ALK-, KRAS-
PD-L1         : negative
TMB           : intermediate (2–16 mut/Mb)
```
**QA warnings:** brain_mets=False but note appears to mention brain metastasis

### Generated Note

**MEDICAL ONCOLOGY INITIAL CONSULTATION**

**DATE OF SERVICE:** [De-identified]
**PATIENT:** [De-identified]
**MRN:** [De-identified]
**REFERRING PROVIDER:** [De-identified]

**HISTORY OF PRESENT ILLNESS:**
This is a 69-year-old individual referred for initial oncology evaluation of a new diagnosis of non-small cell lung cancer. The patient presented to their primary care provider several weeks ago with a persistent, non-productive cough and progressive dyspnea on exertion. An initial chest X-ray demonstrated a right-sided opacity, prompting further investigation. The patient has a significant history of tobacco use and is a current smoker. The patient is otherwise active with an ECOG performance status of 1, limited only by respiratory symptoms.

**DIAGNOSTIC WORKUP:**
A staging CT of the chest, abdomen, and pelvis was performed, which identified a spiculated 4.5 cm mass in the right upper lobe. The scan also revealed multiple suspicious nodules in the contralateral (left) lung, a moderate right-sided pleural effusion with associated pleural thickening, and pathologically enlarged right supraclavicular and contralateral mediastinal lymph nodes.

A subsequent PET/CT scan confirmed high FDG avidity in the primary right upper lobe mass, the contralateral lung nodules, the right pleura, and in the supraclavicular and mediastinal nodal stations, consistent with widespread metastatic disease. A staging MRI of the brain was performed and was negative for intracranial metastases.

A CT-guided core needle biopsy of the primary right lung mass was performed. Pathology confirmed invasive adenocarcinoma, consistent with a primary lung malignancy. Based on the imaging and pathology findings, the patient is diagnosed with AJCC Stage IV disease.

**MOLECULAR STUDIES:**
Next-generation sequencing (NGS) was performed on the tumor tissue. No actionable driver alterations were identified; testing was negative for mutations or rearrangements in EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2.

Immunohistochemistry for PD-L1 expression was negative. Tumor Mutational Burden (TMB) was determined to be intermediate (2–16 mut/Mb). Somatic testing did reveal a loss-of-function mutation in the STK11 gene.

**PROBLEM SUMMARY:**
This is a 69-year-old with a new diagnosis of metastatic (Stage IV) non-small cell lung cancer, adenocarcinoma histology. Molecular profiling is notable for the absence of an actionable driver mutation, negative PD-L1 expression, and the presence of an STK11 loss-of-function mutation. The patient is treatment-naive and is seen today to discuss the diagnosis and establish care.

### Reviewer Ratings

| Item | Rating |
|---|---|
| Plausibility (1–5) |  |
| Factual accuracy (Pass/Fail) |  |
| Completeness (Pass/Fail) |  |
| Treatment-naive (Pass/Fail) |  |
| Demographic neutrality (Pass/Fail) |  |
| Comments |  |

---

## Case 29  [PASS]

### Structured Profile (Ground Truth)
```
Stage         : IV
Histology     : adenocarcinoma
Brain mets    : False
Smoking       : former smoker (quit >1 year ago)
Molecular     : neg: EGFR-, ALK-, KRAS-
PD-L1         : not_tested
TMB           : intermediate (2–16 mut/Mb)
```
**QA warnings:** brain_mets=False but note appears to mention brain metastasis

### Generated Note

**HPI:**
This is an 83-year-old individual with a history of former tobacco use who is seen for an initial medical oncology consultation regarding a new diagnosis of metastatic non-small cell lung cancer. The patient presented to their primary care provider several weeks ago with a persistent, non-productive cough and progressive fatigue. An initial chest x-ray was concerning for a right-sided lung mass, prompting further evaluation.

The patient is currently experiencing mild fatigue but is able to perform all activities of daily living without assistance and remains ambulatory. There is no significant shortness of breath, chest pain, or hemoptysis reported. Appetite is fair with no significant weight loss. ECOG performance status is 1.

**Diagnostic Workup:**
A CT of the chest, abdomen, and pelvis with contrast was performed on [Date of Scan] which revealed a 4.2 cm spiculated mass in the right upper lobe. Additionally, a 3.1 cm enhancing nodule was identified in the left adrenal gland, highly suspicious for a metastatic deposit. No other suspicious thoracic or abdominal visceral or nodal disease was noted.

For comprehensive staging, a whole-body PET/CT was subsequently obtained. This study demonstrated intense FDG-avidity in the right upper lobe lung mass as well as in the left adrenal nodule, confirming the suspicion of metastatic disease. No other sites of hypermetabolic activity were identified. An MRI of the brain with and without contrast was performed and was negative for any evidence of intracranial metastases.

On [Date of Biopsy], the patient underwent a CT-guided core needle biopsy of the right upper lobe lung mass. Pathology confirmed the diagnosis of adenocarcinoma, consistent with a lung primary.

**Molecular Studies:**
Tumor tissue from the core biopsy was sent for comprehensive next-generation sequencing.
- No actionable driver alteration was identified. The tumor was negative for mutations or rearrangements in *EGFR, ALK, ROS1, BRAF, MET* exon 14, *RET, NTRK, KRAS,* and *ERBB2*.
- Tumor Mutational Burden (TMB) was reported as intermediate (2–16 mut/Mb).
- PD-L1 expression was not tested, as initial sequencing was performed pre-2017 when this was not yet standard of care.

**Problem Summary:**
In summary, this is an 83-year-old former smoker with a new diagnosis of Stage IV non-small cell lung cancer, adenocarcinoma histology. Staging workup has confirmed metastatic disease to a single site in the left adrenal gland, with no evidence of central nervous system involvement. Comprehensive molecular profiling did not identify an actionable oncogenic driver. The patient is treatment-naive with a good performance status (ECOG 1) and is here today to discuss the diagnosis and potential management options.

### Reviewer Ratings

| Item | Rating |
|---|---|
| Plausibility (1–5) |  |
| Factual accuracy (Pass/Fail) |  |
| Completeness (Pass/Fail) |  |
| Treatment-naive (Pass/Fail) |  |
| Demographic neutrality (Pass/Fail) |  |
| Comments |  |

---

## Case 30  [PASS]

### Structured Profile (Ground Truth)
```
Stage         : IA
Histology     : adenocarcinoma
Brain mets    : False
Smoking       : never smoker
Molecular     : EGFR l858r | neg: ALK-, KRAS-
PD-L1         : negative
TMB           : intermediate (2–16 mut/Mb)
```
**QA warnings:** brain_mets=False but note appears to mention brain metastasis

### Generated Note

**HPI:**
This is an 83-year-old individual with an excellent performance status who presents for an initial oncology consultation regarding a new diagnosis of non-small cell lung cancer. The patient was in their usual state of health until a persistent, non-productive cough prompted a chest X-ray, which showed a subtle opacity. This led to further imaging. The patient is an active individual who denies any constitutional symptoms, including fevers, chills, night sweats, or unintentional weight loss. There is no report of hemoptysis, chest pain, or increasing dyspnea. Notably, the patient is a lifetime never-smoker.

**Diagnostic Workup:**
Following the abnormal chest X-ray, a diagnostic CT of the chest was performed. This imaging confirmed the presence of a 1.8 cm solid, spiculated nodule in the right upper lobe. No mediastinal or hilar lymphadenopathy was appreciated.

To establish a tissue diagnosis, the patient underwent a CT-guided core biopsy of the right upper lobe nodule on [De-identified date]. Pathologic evaluation of the tissue confirmed a primary lung adenocarcinoma.

Staging evaluation was completed with a PET/CT scan. This study demonstrated intense FDG uptake localized to the known right upper lobe primary tumor only. There was no evidence of FDG-avid disease in the mediastinal or hilar lymph nodes, nor were there any findings suspicious for distant metastatic disease in the chest, abdomen, or pelvis. A dedicated MRI of the brain with and without contrast was also performed and was negative for intracranial metastases.

Collectively, this workup establishes a clinical Stage IA (cT1bN0M0) non-small cell lung cancer.

**Molecular Studies:**
Next-generation sequencing (NGS) and immunohistochemistry were performed on the tumor tissue obtained from the biopsy. The following results were reported:
-   **Actionable driver mutation:** An EGFR L858R point mutation was detected.
-   **Other drivers:** Testing was negative for ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2 alterations.
-   **Immunotherapy markers:** PD-L1 expression was negative. The tumor mutational burden (TMB) was intermediate (2–16 mut/Mb).

**Problem Summary:**
In summary, this is an 83-year-old never-smoker with a new diagnosis of clinical Stage IA (cT1bN0M0) non-small cell lung adenocarcinoma, characterized by a sensitizing EGFR L858R mutation.

### Reviewer Ratings

| Item | Rating |
|---|---|
| Plausibility (1–5) |  |
| Factual accuracy (Pass/Fail) |  |
| Completeness (Pass/Fail) |  |
| Treatment-naive (Pass/Fail) |  |
| Demographic neutrality (Pass/Fail) |  |
| Comments |  |

---

## Case 31  [FAIL]

### Structured Profile (Ground Truth)
```
Stage         : IV
Histology     : adenocarcinoma
Brain mets    : True
Smoking       : never smoker
Molecular     : neg: EGFR-, ALK-, KRAS-
PD-L1         : high
TMB           : intermediate (2–16 mut/Mb)
```

**QA failures:** brain_mets=True but no brain metastasis stated

### Generated Note

**HPI:**
This is a 71-year-old individual who presents to the thoracic oncology clinic for an initial consultation regarding a new diagnosis of metastatic non-small cell lung cancer. The patient was in their usual state of excellent health until approximately six weeks prior to presentation, when they developed a persistent, dry cough and mild shortness of breath with exertion. Over the past month, they noted the onset of intermittent dull headaches and a subtle feeling of imbalance, which prompted an evaluation with their primary care physician. The patient is a lifetime never-smoker.

The initial workup included a chest CT scan which identified a large mass in the right upper lobe of the lung with associated mediastinal lymphadenopathy. The scan also revealed multiple lesions in the liver and a nodule on the left adrenal gland, concerning for metastatic disease. Given the new neurological symptoms, a brain MRI was subsequently performed and confirmed the presence of multiple intracranial lesions. The patient was referred for a CT-guided biopsy of the primary lung mass to establish a tissue diagnosis.

At present, the patient reports mild fatigue and intermittent headaches, which are managed with over-the-counter analgesics. Their appetite is fair, and their weight has been stable. They remain fully ambulatory and independent in all activities of daily living, with an ECOG performance status of 1.

**Diagnostic Workup:**
A review of outside records and imaging was performed.

**CT Chest, Abdomen, and Pelvis with IV contrast, performed [De-identified Date]:**
Revealed a 4.8 cm spiculated mass in the posterior segment of the right upper lobe. There was associated right hilar and subcarinal lymphadenopathy. Multiple low-density, sub-centimeter lesions were identified throughout both lobes of the liver, consistent with metastatic deposits. A 2.5 cm enhancing nodule was noted in the left adrenal gland, also highly suspicious for a metastasis.

**MRI Brain with and without IV contrast, performed [De-identified Date]:**
Demonstrated at least three enhancing intracranial lesions consistent with metastases. The largest lesion, measuring 1.5 cm, is located in the left cerebellar hemisphere with associated mild vasogenic edema.

**CT-guided Core Needle Biopsy, Right Lung Mass, performed [De-identified Date]:**
Pathology demonstrated invasive adenocarcinoma. Immunohistochemical stains were positive for TTF-1 and Napsin-A, confirming a lung primary origin.

**Molecular Studies:**
Comprehensive next-generation sequencing was performed on the tumor tissue from the lung biopsy specimen.
- **Driver Mutations:** No actionable driver alteration was identified. The tumor was negative for mutations or fusions involving *EGFR, ALK, ROS1, BRAF, MET* exon 14, *RET, NTRK, KRAS,* and *ERBB2*.
- **PD-L1 Expression:** Immunohistochemistry for PD-L1 demonstrated a Tumor Proportion Score (TPS) of ≥50%.
- **Tumor Mutational Burden (TMB):** The TMB was reported as intermediate (2–16 mutations/megabase).

**Problem Summary:**
In summary, this is a 71-year-old never-smoker who presents with a new diagnosis of Stage IV (AJCC 8th edition) non-small cell lung cancer of adenocarcinoma histology. The diagnosis was confirmed via biopsy of a right upper lobe primary tumor. Staging evaluation has documented metastatic disease involving the brain, liver, and left adrenal gland. Comprehensive molecular profiling is notable for high PD-L1 expression (TPS ≥50%) but is negative for any actionable oncogenic driver alterations. The patient is treatment-naive and presents today for discussion of the diagnosis and management options.

### Reviewer Ratings

| Item | Rating |
|---|---|
| Plausibility (1–5) |  |
| Factual accuracy (Pass/Fail) |  |
| Completeness (Pass/Fail) |  |
| Treatment-naive (Pass/Fail) |  |
| Demographic neutrality (Pass/Fail) |  |
| Comments |  |

---

## Case 32  [FAIL]

### Structured Profile (Ground Truth)
```
Stage         : IV
Histology     : adenocarcinoma
Brain mets    : True
Smoking       : former smoker (quit >1 year ago)
Molecular     : neg: EGFR-, ALK-, KRAS-
PD-L1         : intermediate
TMB           : intermediate (2–16 mut/Mb)
```

**QA failures:** brain_mets=True but no brain metastasis stated

### Generated Note

**HPI:**
This is a 69-year-old individual with a new diagnosis of metastatic non-small cell lung cancer. The patient presented to their primary care provider several weeks ago with a persistent, non-productive cough and increasing dyspnea on exertion. More recently, the patient noted the onset of intermittent headaches and a 10-pound unintentional weight loss over the past two months. The patient is a former smoker, having quit approximately 5 years ago. Initial evaluation included a chest radiograph which was concerning for a right upper lobe mass, prompting further investigation. The patient remains functional with an ECOG performance status of 1, able to perform all self-care but restricted in physically strenuous activity.

**Diagnostic Workup:**
A contrast-enhanced CT of the chest, abdomen, and pelvis was performed. This confirmed the presence of a 4.5 cm spiculated mass in the right upper lobe. The scan also revealed multiple hepatic lesions consistent with metastases, a lytic lesion in the T7 vertebral body, and extensive mediastinal and supraclavicular lymphadenopathy. Given the new-onset headaches, a brain MRI with contrast was subsequently obtained, which demonstrated several small enhancing cerebral lesions consistent with metastatic disease.

An interventional radiology-guided core needle biopsy of the primary right lung mass was performed on [De-identified Date]. Pathology review confirmed invasive adenocarcinoma, consistent with a non-small cell lung primary.

**Molecular Studies:**
Next-generation sequencing was performed on the tissue specimen. No actionable driver alteration was identified; testing was negative for mutations or rearrangements in EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2. Immunohistochemistry for PD-L1 was positive, with a Tumor Proportion Score (TPS) of 1-49%. Tumor Mutational Burden (TMB) was determined to be intermediate (2-16 mut/Mb).

**Problem Summary:**
This is a 69-year-old, treatment-naive patient with a new diagnosis of Stage IV non-small cell lung adenocarcinoma, with metastatic disease to the brain, liver, bone, and distant lymph nodes. Molecular profiling is notable for a PD-L1 TPS of 1-49% and the absence of an identified actionable driver mutation. The patient is here for initial consultation and to discuss the diagnosis.

### Reviewer Ratings

| Item | Rating |
|---|---|
| Plausibility (1–5) |  |
| Factual accuracy (Pass/Fail) |  |
| Completeness (Pass/Fail) |  |
| Treatment-naive (Pass/Fail) |  |
| Demographic neutrality (Pass/Fail) |  |
| Comments |  |

---

## Case 33  [FAIL]

### Structured Profile (Ground Truth)
```
Stage         : IIIA
Histology     : squamous
Brain mets    : False
Smoking       : former smoker (quit >1 year ago)
Molecular     : neg: EGFR-, ALK-, KRAS-
PD-L1         : negative
TMB           : intermediate (2–16 mut/Mb)
```

**QA failures:** stage 'IIIA' not stated in note
**QA warnings:** brain_mets=False but note appears to mention brain metastasis

### Generated Note

**HPI:**
This is a 73-year-old who presents for initial oncology consultation for a new diagnosis of non-small cell lung cancer. The patient was in their usual state of health until approximately two months ago, when they developed a persistent dry cough and a new onset of mild shortness of breath with exertion. They were evaluated by their primary care provider, and an initial chest X-ray showed a right-sided lung mass. This prompted a follow-up CT scan of the chest which confirmed the presence of a large mass in the right upper lobe with associated enlarged lymph nodes in the mediastinum.

The patient is a former smoker, having quit more than 10 years ago. They continue to live an active and independent lifestyle, with an ECOG performance status of 0-1. They deny any constitutional B-symptoms such as fevers or unintentional weight loss. They also deny any new headaches, visual changes, focal weakness, or bone pain. Following the imaging findings, the patient was referred for a definitive diagnostic evaluation and is now here to discuss the results.

**Diagnostic Workup:**
A comprehensive staging workup was completed. A contrast-enhanced CT of the chest, abdomen, and pelvis on [De-identified] revealed a 5.1 cm spiculated mass in the posterior segment of the right upper lobe. There was significant associated ipsilateral mediastinal lymphadenopathy noted, involving the right paratracheal and subcarinal stations.

A PET/CT scan performed on [De-identified] confirmed high metabolic activity within the primary right upper lobe tumor (SUVmax 13.8) and in the right paratracheal (station 4R) and subcarinal (station 7) lymph nodes (SUVmax 8.5). Importantly, there was no evidence of FDG-avid disease suggestive of distant metastases in the contralateral lung, liver, adrenal glands, or skeleton.

A staging MRI of the brain was performed on [De-identified] and was negative for any evidence of intracranial metastatic disease.

The patient subsequently underwent bronchoscopy with endobronchial ultrasound (EBUS) for tissue acquisition. Biopsies of the primary mass and fine-needle aspiration of the subcarinal lymph node were performed. Pathology from both sites returned as poorly differentiated squamous cell carcinoma.

**Molecular Studies:**
Next-generation sequencing performed on the tumor tissue revealed no actionable driver alteration. Specifically, testing was negative for mutations, fusions, or amplifications in EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2.

Immunohistochemistry for PD-L1 was performed, and the result was negative (Tumor Proportion Score < 1%).

Tumor Mutational Burden (TMB) was found to be intermediate (2–16 mut/Mb).

**Problem Summary:**
This is a 73-year-old with a new diagnosis of treatment-naive, locally advanced non-small cell lung cancer. Pathology confirms squamous cell carcinoma, with a clinical stage of IIIA (cT3N2M0) based on AJCC 8th Edition staging. Molecular profiling is negative for targetable driver alterations and PD-L1 expression.

### Reviewer Ratings

| Item | Rating |
|---|---|
| Plausibility (1–5) |  |
| Factual accuracy (Pass/Fail) |  |
| Completeness (Pass/Fail) |  |
| Treatment-naive (Pass/Fail) |  |
| Demographic neutrality (Pass/Fail) |  |
| Comments |  |

---

## Case 34  [PASS]

### Structured Profile (Ground Truth)
```
Stage         : IV
Histology     : nos
Brain mets    : False
Smoking       : never smoker
Molecular     : neg: EGFR-, ALK-, KRAS-
PD-L1         : not_tested
TMB           : intermediate (2–16 mut/Mb)
```
**QA warnings:** brain_mets=False but note appears to mention brain metastasis

### Generated Note

**HPI:**
I had the pleasure of evaluating this 32-year-old for an initial oncology consultation regarding a new diagnosis of non-small cell lung cancer. The patient is a lifetime never-smoker who was in their usual state of good health until approximately six weeks prior to presentation, when they developed a persistent, non-productive cough and progressive dyspnea on exertion. These symptoms prompted a visit to an urgent care center, where a chest radiograph revealed a right-sided lung mass and a moderate pleural effusion. The patient was subsequently referred for further evaluation.

**Diagnostic Workup:**
A contrast-enhanced CT of the chest, abdomen, and pelvis was performed on [De-identified date]. This confirmed a 4.5 cm spiculated mass in the right upper lobe. It also demonstrated a moderate right-sided pleural effusion and several small contralateral pulmonary nodules in the left lung, consistent with M1a disease. There was no evidence of metastatic disease in the abdomen or pelvis, with the liver, adrenal glands, and bones appearing unremarkable. A subsequent MRI of the brain with contrast was negative for intracranial metastases.

A CT-guided core needle biopsy of the right upper lobe mass was performed. Concurrently, a thoracentesis was performed, and analysis of the pleural fluid cytology was positive for malignant cells. The pathology from the core biopsy confirmed the diagnosis of non-small cell lung cancer, not otherwise specified (NOS).

**Molecular Studies:**
Next-generation sequencing was performed on the tumor tissue from the core biopsy. No actionable driver alterations were identified. Specifically, the tumor was negative for mutations or rearrangements in *EGFR*, *ALK*, *ROS1*, *BRAF*, *MET* exon 14, *RET*, *NTRK*, *KRAS*, and *ERBB2*. Tumor mutational burden (TMB) was found to be intermediate at 2–16 mut/Mb. PD-L1 expression was not tested, as this was not standard practice at the time of the initial diagnostic workup.

**Problem Summary:**
In summary, this is a 32-year-old never-smoker who presents for initial consultation with a new diagnosis of Stage IV (M1a) non-small cell lung cancer, histology not otherwise specified. The diagnosis was established via CT-guided biopsy of a right upper lobe mass. Staging studies confirmed metastatic disease based on a malignant pleural effusion and contralateral lung nodules, with no evidence of distant organ or brain metastases. Comprehensive molecular profiling of the tumor did not identify any targetable driver mutations. The patient has an excellent performance status and is here today to discuss the diagnosis.

### Reviewer Ratings

| Item | Rating |
|---|---|
| Plausibility (1–5) |  |
| Factual accuracy (Pass/Fail) |  |
| Completeness (Pass/Fail) |  |
| Treatment-naive (Pass/Fail) |  |
| Demographic neutrality (Pass/Fail) |  |
| Comments |  |

---

## Case 35  [PASS]

### Structured Profile (Ground Truth)
```
Stage         : IIIA
Histology     : adenocarcinoma
Brain mets    : False
Smoking       : former smoker (quit >1 year ago)
Molecular     : KRAS G12C | neg: EGFR-, ALK-
PD-L1         : intermediate
TMB           : intermediate (2–16 mut/Mb)
```
**QA warnings:** brain_mets=False but note appears to mention brain metastasis

### Generated Note

**HPI:**
This is a 68-year-old with a new diagnosis of non-small cell lung cancer, referred for initial oncology consultation. The patient presented to their primary care provider several weeks ago with a persistent, non-productive cough. An initial chest x-ray revealed a right upper lobe opacity, which prompted further investigation. A subsequent CT scan of the chest confirmed the presence of a primary lung mass. The patient is a former smoker, having quit over a year ago. They report good baseline functional status, maintaining independence in all activities of daily living and without significant weight loss or constitutional symptoms. They are here today to discuss the diagnosis and potential management options.

**Diagnostic Workup:**
A comprehensive diagnostic and staging workup has been completed.

A CT of the chest, abdomen, and pelvis with contrast identified a 3.5 cm spiculated mass in the right upper lobe, as well as several enlarged right-sided mediastinal lymph nodes, the largest measuring 1.8 cm in short axis. No suspicious liver, adrenal, or osseous lesions were identified.

A subsequent PET/CT scan was performed for staging. This demonstrated intense FDG avidity in the primary right upper lobe mass and in ipsilateral mediastinal (N2) lymph node stations, consistent with the CT findings. Importantly, there was no evidence of FDG-avid disease elsewhere in the body to suggest distant metastasis.

An MRI of the brain with and without contrast was performed for central nervous system staging and was negative for any evidence of intracranial metastasis.

A CT-guided core needle biopsy of the right upper lobe lung mass was performed on [De-identified]. Pathology confirmed a diagnosis of invasive adenocarcinoma, consistent with a non-small cell lung cancer primary.

Based on these findings, the patient is diagnosed with AJCC Stage IIIA non-small cell lung cancer.

**Molecular Studies:**
Next-generation sequencing was performed on the tumor biopsy specimen. Results are as follows:
- **Actionable driver mutation detected:** KRAS G12C
- **Negative for mutations/rearrangements in:** EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, ERBB2
- **PD-L1 Tumor Proportion Score (TPS):** Positive, 1-49%
- **Tumor Mutational Burden (TMB):** Intermediate (2-16 mut/Mb)

**Problem Summary:**
In summary, this is a 68-year-old with a new diagnosis of Stage IIIA (non-metastatic) KRAS G12C-mutant, PD-L1 positive (TPS 1-49%) non-small cell lung adenocarcinoma.

### Reviewer Ratings

| Item | Rating |
|---|---|
| Plausibility (1–5) |  |
| Factual accuracy (Pass/Fail) |  |
| Completeness (Pass/Fail) |  |
| Treatment-naive (Pass/Fail) |  |
| Demographic neutrality (Pass/Fail) |  |
| Comments |  |

---

## Case 36  [PASS]

### Structured Profile (Ground Truth)
```
Stage         : IV
Histology     : adenocarcinoma
Brain mets    : False
Smoking       : former smoker (quit <1 year ago)
Molecular     : neg: EGFR-, ALK-, KRAS-
PD-L1         : intermediate
TMB           : low (<2 mut/Mb)
```
**QA warnings:** brain_mets=False but note appears to mention brain metastasis

### Generated Note

**HPI:**
This is an initial oncology consultation for a 56-year-old who presents for evaluation of a new diagnosis of non-small cell lung cancer. The patient is a former smoker, having quit less than one year ago. They were in their usual state of health until approximately three months prior to presentation when they developed a persistent, non-productive cough and progressive right-sided back pain. The pain was initially managed with over-the-counter analgesics but worsened, prompting a visit to their primary care provider. An initial chest X-ray revealed a right upper lobe lung mass. The patient reports a good appetite but has noted an unintentional weight loss of approximately 10 pounds over the past two months. Performance status is excellent, ECOG 1, limited only by pain.

**Diagnostic Workup:**
Following the abnormal chest X-ray, a contrast-enhanced CT of the chest, abdomen, and pelvis was performed on [De-identified]. This study confirmed a 4.5 cm spiculated mass in the right upper lobe with adjacent mediastinal and hilar lymphadenopathy. The scan also revealed a lytic lesion in the T7 vertebral body, suspicious for metastatic disease. A subsequent whole-body PET/CT scan demonstrated intense FDG-avidity in the primary right upper lobe mass, the mediastinal lymph nodes, and the T7 vertebral lesion, consistent with metastatic malignancy. A dedicated MRI of the brain with and without contrast was performed for staging and was negative for intracranial metastases.

A CT-guided core needle biopsy of the right upper lobe lung mass was performed. Pathology confirmed a diagnosis of adenocarcinoma, consistent with a non-small cell lung cancer primary.

**Molecular Studies:**
Tissue from the lung mass biopsy was sent for comprehensive next-generation sequencing and immunohistochemistry.
- No actionable driver alteration was identified. The tumor was negative for mutations or rearrangements in EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2.
- PD-L1 expression by immunohistochemistry was positive, with a Tumor Proportion Score (TPS) in the 1–49% range.
- Tumor Mutational Burden (TMB) was low at <2 mutations/megabase.

**Problem Summary:**
This is a 56-year-old with a new diagnosis of Stage IV (cT2b N2 M1b) non-small cell lung cancer, adenocarcinoma histology, with metastasis to bone. Molecular profiling is notable for the absence of an actionable driver mutation and a PD-L1 TPS of 1-49%. The patient is treatment-naive and is seen today to discuss the diagnosis and implications.

### Reviewer Ratings

| Item | Rating |
|---|---|
| Plausibility (1–5) |  |
| Factual accuracy (Pass/Fail) |  |
| Completeness (Pass/Fail) |  |
| Treatment-naive (Pass/Fail) |  |
| Demographic neutrality (Pass/Fail) |  |
| Comments |  |

---

## Case 37  [PASS]

### Structured Profile (Ground Truth)
```
Stage         : IV
Histology     : adenocarcinoma
Brain mets    : False
Smoking       : never smoker
Molecular     : EGFR exon_19_del | neg: ALK-, KRAS-
PD-L1         : not_tested
TMB           : intermediate (2–16 mut/Mb)
```

### Generated Note

INITIAL MEDICAL ONCOLOGY CONSULTATION
Date of Service: [De-identified]
Patient: [De-identified]
MRN: [De-identified]

**History of Present Illness**
This is a 75-year-old individual seen in consultation for a new diagnosis of non-small cell lung cancer. The patient was in their usual state of health until approximately six weeks prior to presentation, when they began to experience progressive shortness of breath with exertion and a persistent, non-productive cough. These symptoms prompted a visit to an outside hospital.

An initial chest X-ray revealed a right-sided lung mass and a large pleural effusion. A subsequent CT of the chest, abdomen, and pelvis was performed for staging, which confirmed a primary mass in the right lung with an extensive pleural effusion. The patient underwent a diagnostic and therapeutic thoracentesis, which drained a significant volume of fluid and provided some symptomatic relief.

The patient is a lifetime never-smoker. They report feeling fatigued but remain ambulatory and capable of all self-care, with an ECOG performance status of 1. They are here today to discuss the diagnosis and establish care.

**Diagnostic Workup**

**Imaging:**
I have personally reviewed the following imaging studies:

*   **CT Chest/Abdomen/Pelvis with IV Contrast ([De-identified date]):**
    *   A 4.2 cm spiculated mass is identified in the right upper lobe.
    *   A large, loculated right-sided pleural effusion is present, with associated pleural thickening suspicious for malignant involvement.
    *   No definite mediastinal or hilar lymphadenopathy by size criteria.
    *   The liver, adrenal glands, and visualized bones are without evidence of metastatic disease.
    *   Impression: Right upper lobe primary malignancy with malignant pleural effusion.

*   **MRI Brain with and without IV Contrast ([De-identified date]):**
    *   No evidence of intracranial metastatic disease.

**Pathology:**
*   **Right Pleural Fluid Cytology ([De-identified date]):**
    *   Specimen shows malignant cells, arranged in glandular formations.
    *   Immunohistochemical stains are positive for TTF-1 and Napsin-A, consistent with a primary lung adenocarcinoma.

**Molecular Studies**
Next-generation sequencing was performed on the pleural fluid cell block with the following results:

*   **Actionable driver(s) detected:** EGFR exon 19 deletion (sensitizing)
*   **Negative for:** ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, ERBB2
*   **PD-L1:** Not tested
*   **Tumor Mutational Burden (TMB):** Intermediate (2–16 mut/Mb)

**Problem Summary**
In summary, this is a 75-year-old never-smoker with a new diagnosis of Stage IV (cT2, cN0, M1a) non-small cell lung cancer of adenocarcinoma histology. The disease is metastatic based on a malignant pleural effusion. Molecular profiling of the tumor is notable for a sensitizing EGFR exon 19 deletion. The patient has a good performance status (ECOG 1) at the time of this initial evaluation.

### Reviewer Ratings

| Item | Rating |
|---|---|
| Plausibility (1–5) |  |
| Factual accuracy (Pass/Fail) |  |
| Completeness (Pass/Fail) |  |
| Treatment-naive (Pass/Fail) |  |
| Demographic neutrality (Pass/Fail) |  |
| Comments |  |

---

## Case 38  [PASS]

### Structured Profile (Ground Truth)
```
Stage         : IIB
Histology     : adenocarcinoma
Brain mets    : False
Smoking       : former smoker (quit <1 year ago)
Molecular     : KRAS G12C | neg: EGFR-, ALK-
PD-L1         : not_tested
TMB           : low (<2 mut/Mb)
```
**QA warnings:** brain_mets=False but note appears to mention brain metastasis

### Generated Note

**HPI:**
This is a 58-year-old individual with a history of smoking (former, quit within the last year) who presents for an initial medical oncology consultation to discuss a new diagnosis of non-small cell lung cancer. The patient initially presented to an outside facility several weeks ago with a persistent, non-productive cough and progressive dyspnea on exertion. This was initially treated as a possible respiratory infection without improvement. Due to the persistence of symptoms, a chest X-ray was obtained which revealed a right-sided lung mass, prompting further evaluation. The patient has an ECOG performance status of 1, remaining fully ambulatory and capable of light activity despite symptoms.

**Diagnostic Workup:**
Following the abnormal chest X-ray, a contrast-enhanced CT of the chest, abdomen, and pelvis was performed. This demonstrated a 4.8 cm spiculated mass in the right upper lobe with associated ipsilateral hilar and subcarinal lymphadenopathy. No suspicious lesions were identified in the contralateral lung, liver, adrenal glands, or bones.

A subsequent PET/CT scan was performed for staging purposes. This confirmed high FDG-avidity within the primary right upper lobe mass and in the ipsilateral hilar and subcarinal lymph nodes. Importantly, the PET/CT showed no evidence of distant FDG-avid metastatic disease.

A staging MRI of the brain was performed and was negative for any evidence of intracranial metastases.

To establish a tissue diagnosis, the patient underwent a CT-guided core needle biopsy of the right upper lobe lung mass. Pathology confirmed a diagnosis of poorly differentiated adenocarcinoma, consistent with a primary lung origin.

Based on this comprehensive workup, the patient is diagnosed with clinical Stage IIB (T2bN1M0) non-small cell lung cancer.

**Molecular Studies:**
Tissue from the diagnostic biopsy was sent for next-generation sequencing. The results are as follows:
- An actionable driver mutation was detected in KRAS (G12C).
- The tumor was negative for pathogenic alterations in EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, and ERBB2.
- Tumor Mutational Burden (TMB) was determined to be low (<2 mutations/megabase).
- PD-L1 expression was not tested on this specimen, as this was not standard of care at the time of initial sequencing.

**Problem Summary:**
In summary, this is a 58-year-old former smoker who presents for initial evaluation of a newly diagnosed Stage IIB non-small cell lung adenocarcinoma of the right upper lobe. The diagnostic workup is complete and shows locoregionally confined disease with no evidence of distant metastases. Molecular profiling of the tumor is notable for a KRAS G12C mutation. The patient is treatment-naive.

### Reviewer Ratings

| Item | Rating |
|---|---|
| Plausibility (1–5) |  |
| Factual accuracy (Pass/Fail) |  |
| Completeness (Pass/Fail) |  |
| Treatment-naive (Pass/Fail) |  |
| Demographic neutrality (Pass/Fail) |  |
| Comments |  |

---

## Case 39  [PASS]

### Structured Profile (Ground Truth)
```
Stage         : IV
Histology     : adenocarcinoma
Brain mets    : True
Smoking       : former smoker (quit >1 year ago)
Molecular     : neg: EGFR-, ALK-, KRAS-
PD-L1         : negative
TMB           : intermediate (2–16 mut/Mb)
```

### Generated Note

**MEDICAL ONCOLOGY INITIAL CONSULTATION**
**DATE OF SERVICE:** [De-identified]
**PATIENT:** [De-identified]
**MRN:** [De-identified]

**HPI:**
This is a 62-year-old individual referred for initial consultation and management of newly diagnosed metastatic non-small cell lung cancer. The patient presented to their primary care provider several weeks ago with a progressive, non-productive cough and increasing dyspnea on exertion. This was associated with significant fatigue and an unintentional weight loss of approximately 15 pounds over the past two months. More recently, the patient noted the onset of dull, persistent headaches. The patient is a former smoker, having quit over one year ago. The patient remains ambulatory and capable of self-care but is limited in more strenuous physical activity.

An initial chest X-ray revealed a large right upper lobe lung mass, prompting further investigation. The patient was subsequently sent for comprehensive staging imaging. The patient is here today to discuss the results of this workup and establish care.

**Diagnostic Workup:**
A contrast-enhanced CT of the chest, abdomen, and pelvis was performed, which confirmed a large, spiculated mass in the right upper lobe of the lung with associated mediastinal and hilar lymphadenopathy. The scan also revealed multiple lesions suspicious for metastatic disease, including several hypodensities in the liver, a nodule in the left adrenal gland, and a lytic lesion in the thoracic spine.

A subsequent PET/CT scan demonstrated intense FDG-avidity in the primary right lung mass, mediastinal lymph nodes, and confirmed hypermetabolic activity consistent with metastatic disease in the liver, left adrenal gland, and multiple sites of bone, including the thoracic spine. Additional distant nodal disease was also noted.

Given the new onset of headaches, a brain MRI with contrast was obtained. This revealed multiple enhancing parenchymal lesions consistent with brain metastases.

To establish a tissue diagnosis, the patient underwent a CT-guided core needle biopsy of one of the accessible liver lesions. Pathology confirmed metastatic adenocarcinoma, with morphology and immunohistochemical staining consistent with a lung primary.

**Molecular Studies:**
Next-generation sequencing (NGS) was performed on the biopsy specimen. Molecular profiling did not identify an actionable driver alteration. Results were negative for mutations or rearrangements in EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2.

Immunohistochemistry for PD-L1 expression was performed, and the result was negative. Tumor Mutational Burden (TMB) was assessed and found to be intermediate (2–16 mut/Mb).

**Problem Summary:**
In summary, this is a 62-year-old with a new diagnosis of Stage IV non-small cell lung cancer, adenocarcinoma histology. The diagnostic workup confirms widespread metastatic disease involving the brain, bone, liver, adrenal glands, and distant lymph nodes. Molecular studies are notable for the absence of any identified actionable driver alterations and negative PD-L1 expression. The patient is treatment-naive.

### Reviewer Ratings

| Item | Rating |
|---|---|
| Plausibility (1–5) |  |
| Factual accuracy (Pass/Fail) |  |
| Completeness (Pass/Fail) |  |
| Treatment-naive (Pass/Fail) |  |
| Demographic neutrality (Pass/Fail) |  |
| Comments |  |

---
