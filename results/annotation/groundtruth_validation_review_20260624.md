# GENIE BPC NSCLC: Oncologist Ground-Truth Validation

**Date:** 20260624  |  **N:** 50 cases  |  **Seed:** 42

## Task

For each case, read the clinical note and judge whether the **proposed treatment**
(the guideline-concordant ground-truth label) is correct for this patient. The
historically-administered treatment is deliberately omitted: these cases predate
the 2025 standard, so it would mislead rather than help.

## Fields to complete

| Field | Allowed values |
|---|---|
| `label_agreement` | **Agree** / **Acceptable-not-preferred** / **Disagree** |
| `preferred_treatment` | free text, fill only if Disagree |
| `note_sufficiency` | **Yes** / **Partial** / **No** (enough info to recommend?) |
| `confidence` | **1** Low / **2** Medium / **3** High |
| `case_complexity` | **Easy** / **Moderate** / **Complex** |
| `reviewer_comments` | free text |

---

## Case 1

**Stage:** IIIA  |  **Histology:** adenocarcinoma

### Clinical Note

**HPI:**
This is a 54-year-old individual who presents for initial medical oncology consultation for a new diagnosis of non-small cell lung cancer. The patient is a lifetime never-smoker and was in their usual state of health until approximately two months ago, when they noted the insidious onset of a dry, persistent cough and mild shortness of breath with exertion. These symptoms prompted an evaluation with their primary care provider. An initial chest X-ray was notable for a right upper lobe opacity, which led to further diagnostic imaging. The patient reports good appetite and has not had any significant weight loss. They remain fully ambulatory and active, with an estimated ECOG performance status of 0-1.

**Diagnostic Workup:**
A contrast-enhanced CT scan of the chest, performed on [Date], confirmed the presence of a 4 cm spiculated mass in the right upper lobe. This scan also revealed prominent right paratracheal and subcarinal lymphadenopathy, raising suspicion for locoregional nodal involvement.

To complete staging, a whole-body PET/CT was performed on [Date]. This study demonstrated intense FDG-avidity corresponding to the known right upper lobe primary tumor and the mediastinal lymph nodes. Critically, the PET/CT showed no evidence of FDG-avid disease in the contralateral lung, liver, adrenal glands, bones, or elsewhere to suggest distant metastatic disease. A dedicated MRI of the brain with and without contrast on [Date] was also performed and was negative for any intracranial metastases.

The patient subsequently underwent a CT-guided core needle biopsy of the right upper lobe mass on [Date]. Pathologic analysis of the tissue established a diagnosis of invasive adenocarcinoma of the lung. Based on the combined imaging and pathology findings, the patient is diagnosed with clinical Stage IIIA (AJCC 8th Edition) disease.

**Molecular Studies:**
Tissue obtained from the lung biopsy was sent for comprehensive next-generation sequencing and immunohistochemistry. The results are notable for the following:
-   An activating mutation was detected in the EGFR gene, specifically an exon 19 deletion.
-   The tumor was negative for alterations in ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2.
-   PD-L1 expression by immunohistochemistry showed a Tumor Proportion Score (TPS) of 1-49%.
-   Tumor Mutational Burden (TMB) was low (<2 mutations/Mb).

**Problem Summary:**
In summary, this is a 54-year-old lifetime never-smoker with an excellent performance status who presents with a new diagnosis of Stage IIIA non-small cell lung adenocarcinoma of the right lung. The diagnostic workup, including PET/CT and brain MRI, confirms locoregionally advanced disease without evidence of distant metastases. Molecular profiling is significant for the presence of a sensitizing EGFR exon 19 deletion. The patient is here today for initial consultation to discuss these findings.

### Proposed Ground Truth

**Recommended treatment:** concurrent chemoradiation + durvalumab (consolidation)

**Also NCCN-acceptable:** concurrent chemoradiation + durvalumab (consolidation); osimertinib

### Your Assessment

| Field | Your answer |
|---|---|
| Label agreement (Agree / Acceptable-not-preferred / Disagree) |  |
| Preferred treatment (if disagree) |  |
| Note sufficiency (Yes / Partial / No) |  |
| Confidence (1–3) |  |
| Case complexity (Easy / Moderate / Complex) |  |
| Comments |  |

---

## Case 2

**Stage:** IV  |  **Histology:** adenocarcinoma

### Clinical Note

**INITIAL MEDICAL ONCOLOGY CONSULTATION**
**Patient Name:** [De-identified]
**MRN:** [De-identified]
**Date of Service:** [De-identified]
**Referring Provider:** [De-identified]

**History of Present Illness:**
This is a 45-year-old individual with a history of smoking (quit over one year ago) who is seen for an initial oncology evaluation regarding a new diagnosis of non-small cell lung cancer.

The patient was in their usual state of health until approximately two months prior to presentation, when they developed a persistent, non-productive cough and progressive dyspnea on exertion. This was associated with mild fatigue and an unintentional weight loss of approximately 10 pounds over the preceding three months. The patient initially sought evaluation with their primary care provider, who obtained a chest radiograph revealing a left-sided pleural effusion and a subtle left upper lobe opacity.

This prompted an urgent referral for a CT scan of the chest, abdomen, and pelvis with contrast. The scan confirmed a spiculated 3.5 cm mass in the left upper lobe, a large, malignant-appearing left pleural effusion, and a new 2.2 cm nodule in the right adrenal gland, suspicious for metastatic disease. No evidence of brain metastases was reported on initial staging imaging. Given the findings, the patient was referred for thoracic surgery consultation and underwent a diagnostic and therapeutic thoracentesis. The patient reports some improvement in dyspnea following the procedure. The patient is currently ambulatory and managing most activities of daily living, with an ECOG performance status of 1.

**Diagnostic Workup:**
*   **CT Chest/Abdomen/Pelvis with IV Contrast, [De-identified Date]:** Revealed a 3.5 cm primary mass in the left upper lobe. Findings consistent with a large malignant left pleural effusion. A 2.2 cm enhancing nodule was identified in the right adrenal gland, concerning for a metastasis. No other distant metastatic disease was identified.
*   **Thoracentesis, [De-identified Date]:** 1.5 liters of serosanguinous fluid were removed. Pleural fluid cytology was performed.
*   **Pathology (Pleural Fluid Cytology):** Final diagnosis of Adenocarcinoma, consistent with a lung primary.

**Molecular Studies:**
Next-generation sequencing (NGS) was performed on the cell block from the pleural fluid specimen.
*   **Actionable Driver Mutation:** An NTRK fusion was detected.
*   **Negative for Mutations/Rearrangements:** EGFR, ALK, ROS1, BRAF, MET exon 14, RET, KRAS, ERBB2.
*   **Tumor Mutational Burden (TMB):** Intermediate (reported as 11 mutations/megabase).
*   **PD-L1 Immunohistochemistry:** Not performed.

**Problem Summary:**
In summary, this is a 45-year-old former smoker with a new diagnosis of treatment-naive, Stage IV non-small cell lung adenocarcinoma, metastatic to the pleura and adrenal gland. Molecular profiling is notable for the presence of an NTRK fusion.

### Proposed Ground Truth

**Recommended treatment:** larotrectinib

**Also NCCN-acceptable:** larotrectinib; entrectinib

### Your Assessment

| Field | Your answer |
|---|---|
| Label agreement (Agree / Acceptable-not-preferred / Disagree) |  |
| Preferred treatment (if disagree) |  |
| Note sufficiency (Yes / Partial / No) |  |
| Confidence (1–3) |  |
| Case complexity (Easy / Moderate / Complex) |  |
| Comments |  |

---

## Case 3

**Stage:** IIB  |  **Histology:** nos

### Clinical Note

**REASON FOR CONSULTATION:**
New diagnosis of non-small cell lung cancer.

**HISTORY OF PRESENT ILLNESS:**
This is a 56-year-old with a past medical history of melanoma and former tobacco use who presents for initial oncology consultation. The patient was in their usual state of health until approximately three months prior to presentation, when they developed a persistent, dry cough. This was initially attributed to a seasonal illness, but due to lack of resolution, they presented to their primary care provider.

An initial chest X-ray was performed which revealed a suspicious opacity in the right upper lung. This prompted a follow-up contrast-enhanced CT of the chest, which confirmed the presence of a spiculated mass in the right upper lobe. Given the high suspicion for malignancy, the patient was referred for a CT-guided core needle biopsy of the mass.

Following the biopsy, a full staging evaluation was undertaken including a PET/CT scan and a brain MRI. The PET/CT demonstrated avidity in the primary right upper lobe mass and in a single ipsilateral hilar lymph node, with no evidence of mediastinal, contralateral, or distant metastatic disease. The subsequent brain MRI was negative for any intracranial metastases. The patient has remained active with an ECOG performance status of 0-1 and reports no significant weight loss, hemoptysis, or bone pain. They are here today to discuss the findings and establish care.

**DIAGNOSTIC WORKUP:**
A review of outside records and imaging was performed.

**CT Chest, [De-identified Date]:**
Revealed a 3.8 cm spiculated solid mass in the posterior segment of the right upper lobe. A 1.2 cm right hilar lymph node was noted.

**PET/CT, [De-identified Date]:**
FINDINGS: Intense FDG uptake within the known 3.8 cm right upper lobe mass (SUVmax 11.8). Avid uptake is also noted in a right hilar lymph node (SUVmax 7.2). No other sites of abnormal FDG avidity to suggest regional nodal spread beyond the hilum or distant metastatic disease.

**MRI Brain with and without contrast, [De-identified Date]:**
FINDINGS: No evidence of intracranial mass, hemorrhage, or metastatic disease.

**Pathology, CT-guided biopsy of right lung mass, [De-identified Date]:**
DIAGNOSIS: Non-small cell lung cancer, not otherwise specified (NOS).

**MOLECULAR STUDIES:**
Next-generation sequencing was performed on the tumor biopsy specimen with the following results:
- **Actionable driver mutation detected:** KRAS G12C
- **Additional mutation:** STK11 loss-of-function mutation identified.
- **Tumor Mutational Burden (TMB):** Intermediate (reported as 2-16 mut/Mb).
- **Other markers:** The tumor was negative for targetable alterations in EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, and ERBB2.
- **PD-L1 Expression:** Not tested.

**PROBLEM SUMMARY:**
This is a 56-year-old former smoker presenting for initial oncologic evaluation. The patient has a new diagnosis of clinical Stage IIB non-small cell lung cancer of the right upper lobe, histology not otherwise specified. Staging workup, including PET/CT and brain MRI, is negative for distant metastatic disease. Molecular profiling of the tumor is significant for a KRAS G12C mutation and a concurrent STK11 loss-of-function mutation. The patient is treatment-naive.

### Proposed Ground Truth

**Recommended treatment:** lobectomy + mediastinal lymph node dissection/sampling

**Also NCCN-acceptable:** lobectomy + mediastinal lymph node dissection/sampling; neoadjuvant nivolumab + platinum-doublet chemotherapy (CheckMate 816) then surgery; perioperative pembrolizumab + chemotherapy (KEYNOTE-671): neoadjuvant pembrolizumab + chemo → surgery → adjuvant pembrolizumab; perioperative durvalumab + chemotherapy (AEGEAN): neoadjuvant → surgery → adjuvant durvalumab

### Your Assessment

| Field | Your answer |
|---|---|
| Label agreement (Agree / Acceptable-not-preferred / Disagree) |  |
| Preferred treatment (if disagree) |  |
| Note sufficiency (Yes / Partial / No) |  |
| Confidence (1–3) |  |
| Case complexity (Easy / Moderate / Complex) |  |
| Comments |  |

---

## Case 4

**Stage:** IIA  |  **Histology:** adenocarcinoma

### Clinical Note

**HPI:**
This is a 65-year-old with a history of tobacco use (former smoker, quit >1 year ago) who presents for initial oncology consultation for a new diagnosis of non-small cell lung cancer. The patient was in their usual state of health until approximately two months prior to presentation, when they developed a persistent, non-productive cough. This prompted an evaluation by their primary care provider, which included a chest radiograph revealing a right upper lobe lung nodule. The patient is otherwise feeling well, reporting no significant shortness of breath, chest pain, hemoptysis, or constitutional symptoms such as fevers or weight loss. Performance status is excellent, ECOG 0.

**Diagnostic Workup:**
A comprehensive staging evaluation was pursued. A contrast-enhanced CT of the chest, abdomen, and pelvis was performed on [De-identified], which characterized a 3.8 cm spiculated mass in the posterior segment of the right upper lobe. There was no evidence of mediastinal or hilar lymphadenopathy. The visualized portions of the abdomen and pelvis were negative for metastatic disease, with no suspicious lesions in the liver, adrenal glands, or bones.

A PET/CT scan performed on [De-identified] confirmed a hypermetabolic primary mass in the right upper lobe (SUVmax 12.4) without evidence of FDG-avid regional nodal or distant metastatic disease. A dedicated MRI of the brain with and without contrast was subsequently performed and was negative for intracranial metastases.

On [De-identified], the patient underwent a CT-guided core needle biopsy of the right upper lobe mass. Pathology from this procedure confirmed the diagnosis of invasive adenocarcinoma, consistent with a primary lung origin.

Based on this workup, the patient is diagnosed with clinical Stage IIA (AJCC 8th Edition) non-small cell lung cancer.

**Molecular Studies:**
Next-generation sequencing was performed on the biopsy specimen.
-   Actionable driver mutation detected: **KRAS G12C**
-   Tumor was negative for pathogenic mutations in EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, and ERBB2.
-   Tumor Mutational Burden (TMB) was determined to be intermediate (2–16 mut/Mb).
-   PD-L1 immunohistochemistry was not performed on this specimen.

**Problem Summary:**
In summary, this is a 65-year-old with a new diagnosis of treatment-naive, Stage IIA (pT2aN0M0) non-small cell lung adenocarcinoma, notable for a KRAS G12C mutation.

### Proposed Ground Truth

**Recommended treatment:** lobectomy + mediastinal lymph node dissection/sampling

**Also NCCN-acceptable:** lobectomy + mediastinal lymph node dissection/sampling; neoadjuvant nivolumab + platinum-doublet chemotherapy (CheckMate 816) then surgery; perioperative pembrolizumab + chemotherapy (KEYNOTE-671): neoadjuvant pembrolizumab + chemo → surgery → adjuvant pembrolizumab; perioperative durvalumab + chemotherapy (AEGEAN): neoadjuvant → surgery → adjuvant durvalumab

### Your Assessment

| Field | Your answer |
|---|---|
| Label agreement (Agree / Acceptable-not-preferred / Disagree) |  |
| Preferred treatment (if disagree) |  |
| Note sufficiency (Yes / Partial / No) |  |
| Confidence (1–3) |  |
| Case complexity (Easy / Moderate / Complex) |  |
| Comments |  |

---

## Case 5

**Stage:** IV  |  **Histology:** adenocarcinoma

### Clinical Note

**HPI:**
This is a 62-year-old who presents for initial oncology consultation for a new diagnosis of non-small cell lung cancer. The patient was in their usual state of health until approximately six weeks prior to presentation, when they began to develop a persistent, non-productive cough and progressive shortness of breath on exertion. These symptoms were initially attributed to a possible respiratory infection, but worsened over several weeks, prompting an evaluation in an urgent care setting.

A chest X-ray performed at that time was notable for a large left-sided pleural effusion and a suspicious opacity in the left lung. The patient was referred for further diagnostic evaluation. The patient denies any significant fevers, chills, or hemoptysis. They report a mild decrease in appetite and an unintentional weight loss of approximately 10 pounds over the past two months. The patient is a lifetime never-smoker.

**Diagnostic Workup:**
Following the abnormal chest X-ray, a contrast-enhanced CT of the chest, abdomen, and pelvis was obtained. This study confirmed a 4.5 cm primary mass in the left upper lobe of the lung. It also demonstrated a large, loculated left pleural effusion with associated pleural thickening and nodularity concerning for malignant involvement. Additionally, the scan revealed multiple pathologically enlarged lymph nodes, including contralateral mediastinal and supraclavicular nodes.

For diagnostic and therapeutic purposes, the patient underwent a left-sided thoracentesis with ultrasound-guided pleural biopsy on [De-identified Date]. Pathologic examination of the pleural fluid and biopsy tissue confirmed a diagnosis of invasive adenocarcinoma, consistent with a lung primary.

A staging PET/CT scan was subsequently performed, which demonstrated intense FDG-avidity in the known left upper lobe primary mass, extensive uptake throughout the left pleura, and in the contralateral mediastinal and supraclavicular lymph nodes, confirming metastatic disease. No other distant metastatic sites were identified in the chest, abdomen, or pelvis. A staging MRI of the brain was also performed and was negative for intracranial metastases.

**Molecular Studies:**
Tumor tissue obtained from the pleural biopsy was sent for comprehensive molecular profiling, including next-generation sequencing (NGS) and immunohistochemistry (IHC).
-   NGS analysis was positive for an actionable **ROS1 gene rearrangement**.
-   Testing was negative for other driver mutations, including EGFR, ALK, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2.
-   PD-L1 expression by IHC was found to be high, with a Tumor Proportion Score (TPS) of **≥50%**.
-   Tumor Mutational Burden (TMB) was reported as **intermediate (2–16 mut/Mb)**.

**Problem Summary:**
In summary, this is a 62-year-old never-smoker with a new diagnosis of Stage IV non-small cell lung cancer, adenocarcinoma histology. Staging studies confirm metastatic disease involving the pleura and distant lymph nodes (M1b). Molecular analysis of the tumor is notable for the presence of a ROS1 rearrangement and high PD-L1 expression (TPS ≥50%). The patient is treatment-naive and presents today to discuss the diagnosis and establish care.

### Proposed Ground Truth

**Recommended treatment:** entrectinib

**Also NCCN-acceptable:** entrectinib; taletrectinib; crizotinib

### Your Assessment

| Field | Your answer |
|---|---|
| Label agreement (Agree / Acceptable-not-preferred / Disagree) |  |
| Preferred treatment (if disagree) |  |
| Note sufficiency (Yes / Partial / No) |  |
| Confidence (1–3) |  |
| Case complexity (Easy / Moderate / Complex) |  |
| Comments |  |

---

## Case 6

**Stage:** IV  |  **Histology:** adenocarcinoma

### Clinical Note

**HPI:**
This is an 82-year-old individual with a history of former tobacco use who presents for an initial medical oncology consultation to discuss a new diagnosis of metastatic non-small cell lung cancer. The patient was in their usual state of health until approximately two months prior to presentation, when they began to develop a persistent, non-productive cough and progressive dyspnea on exertion. These symptoms prompted an evaluation by their primary care provider, leading to initial imaging studies. The patient reports some fatigue but denies fevers, chills, or significant unintentional weight loss. They remain fully ambulatory and capable of all self-care, with an estimated ECOG performance status of 1.

**Diagnostic Workup:**
An initial chest radiograph demonstrated a right-sided lung opacity, prompting a follow-up CT scan of the chest, abdomen, and pelvis with contrast. This study revealed a large, spiculated 4.5 cm mass in the right upper lobe. The scan also identified multiple small nodules in the contralateral (left) lung, suspicious for metastatic disease. Additionally, a moderate right-sided pleural effusion was noted.

To establish a tissue diagnosis, the patient underwent a CT-guided core needle biopsy of the primary right upper lobe mass. Pathological examination of the tissue confirmed the diagnosis of lung adenocarcinoma. A subsequent thoracentesis was performed on the right-sided pleural effusion, and cytological analysis of the pleural fluid was also positive for malignant cells, confirming malignant pleural disease.

A staging PET/CT scan was performed, which confirmed high FDG avidity in the primary right upper lobe mass, the contralateral pulmonary nodules, and the right pleura, consistent with widespread metastatic disease. No other distant metastatic sites were identified. A dedicated MRI of the brain was negative for intracranial metastases.

Based on these findings, the patient is diagnosed with AJCC 8th Edition Stage IV non-small cell lung cancer, with metastases to the contralateral lung and pleura (cT3 N0 M1a).

**Molecular Studies:**
Next-generation sequencing was performed on the tumor tissue obtained from the lung biopsy. The analysis identified two actionable driver mutations: a **MET exon 14 skipping mutation** and a **KRAS G12C mutation**.

The tumor was found to be negative for pathogenic alterations in **EGFR, ALK, ROS1, BRAF, RET, NTRK, and ERBB2**.

Tumor Mutational Burden (TMB) was characterized as **intermediate (2–16 mutations/megabase)**. PD-L1 expression was **not tested**, as the tissue was analyzed prior to this becoming a standard reflex test.

**Problem Summary:**
In summary, this is an 82-year-old former smoker with a new diagnosis of Stage IV NSCLC, adenocarcinoma histology, with metastatic disease involving the contralateral lung and pleura. The patient is treatment-naive and maintains a good performance status (ECOG 1). Molecular profiling of the tumor is notable for the co-occurrence of a MET exon 14 skipping mutation and a KRAS G12C mutation. The patient is seen today to review these findings and discuss the goals of care and management options.

### Proposed Ground Truth

**Recommended treatment:** capmatinib

**Also NCCN-acceptable:** capmatinib; tepotinib

### Your Assessment

| Field | Your answer |
|---|---|
| Label agreement (Agree / Acceptable-not-preferred / Disagree) |  |
| Preferred treatment (if disagree) |  |
| Note sufficiency (Yes / Partial / No) |  |
| Confidence (1–3) |  |
| Case complexity (Easy / Moderate / Complex) |  |
| Comments |  |

---

## Case 7

**Stage:** IV  |  **Histology:** adenocarcinoma

### Clinical Note

**HPI:**
This is an initial medical oncology consultation for a 37-year-old with a new diagnosis of metastatic non-small cell lung cancer. The patient is a lifetime never-smoker and was in their usual state of good health until approximately two months prior to presentation, when they developed a persistent, non-productive cough and progressive dyspnea on exertion. Over the subsequent weeks, they also noted the onset of new, localized mid-thoracic back pain, which was constant and worsened with movement. These symptoms prompted a visit to an urgent care center, which led to an initial chest X-ray.

**Diagnostic Workup:**
The outpatient chest X-ray was abnormal, showing a right-sided lung opacity and a moderate pleural effusion. The patient was referred for further imaging. A CT of the chest, abdomen, and pelvis with contrast was performed on [De-identified date]. This study confirmed a 4.5 cm spiculated mass in the right upper lobe of the lung, extensive malignant-appearing right-sided pleural thickening and a large pleural effusion, and a lytic lesion in the T7 vertebral body.

A subsequent PET/CT scan was obtained for staging purposes. This demonstrated intense FDG-avidity in the right upper lobe primary mass, the right pleura, and the T7 vertebral body lesion, consistent with metastatic disease. A brain MRI with and without contrast was also performed as part of the standard staging workup and was negative for intracranial metastases.

On [De-identified date], the patient underwent a CT-guided core needle biopsy of the right upper lobe lung mass. Pathology from this specimen confirmed a diagnosis of invasive adenocarcinoma, moderately differentiated. Cytology from a concurrent thoracentesis of the right pleural effusion also showed malignant cells consistent with adenocarcinoma.

Based on this workup, the patient is diagnosed with AJCC Stage IV non-small cell lung cancer.

**Molecular Studies:**
Tumor tissue obtained from the lung biopsy was sent for comprehensive next-generation sequencing. The results revealed the presence of two actionable driver alterations: a sensitizing EGFR exon 19 deletion and high-level MET amplification.

The tumor was negative for alterations in ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2.

Tumor mutational burden (TMB) was determined to be intermediate (2–16 mut/Mb). PD-L1 immunohistochemistry was not performed on this sample.

**Problem Summary:**
This is a 37-year-old never-smoker who presents for initial evaluation of a new diagnosis of Stage IV NSCLC, adenocarcinoma histology, with metastases to the bone and pleura. The patient is treatment-naive. Molecular profiling of the tumor is notable for a sensitizing EGFR exon 19 deletion and concurrent high-level MET amplification. The purpose of this visit is to discuss the diagnosis in detail and review the implications of these findings.

### Proposed Ground Truth

**Recommended treatment:** osimertinib

**Also NCCN-acceptable:** osimertinib; osimertinib + carboplatin + pemetrexed; amivantamab + lazertinib

### Your Assessment

| Field | Your answer |
|---|---|
| Label agreement (Agree / Acceptable-not-preferred / Disagree) |  |
| Preferred treatment (if disagree) |  |
| Note sufficiency (Yes / Partial / No) |  |
| Confidence (1–3) |  |
| Case complexity (Easy / Moderate / Complex) |  |
| Comments |  |

---

## Case 8

**Stage:** IV  |  **Histology:** adenocarcinoma

### Clinical Note

**INITIAL MEDICAL ONCOLOGY CONSULTATION**
**Date of Service:** [De-identified]
**Patient Name:** [De-identified]
**MRN:** [De-identified]

**REASON FOR CONSULTATION:** Newly diagnosed metastatic non-small cell lung cancer.

**HISTORY OF PRESENT ILLNESS:**
This is a 33-year-old individual with a recent diagnosis of metastatic non-small cell lung cancer. The patient was in their usual state of health until approximately two months prior to presentation, when they began to develop a persistent, dry cough and progressive dyspnea on exertion. These symptoms were initially attributed to a viral illness but persisted, accompanied by increasing fatigue.

The patient presented to an outside facility for evaluation. A chest radiograph revealed a right upper lobe lung mass, prompting further investigation. A contrast-enhanced CT scan of the chest, abdomen, and pelvis was subsequently performed. This imaging confirmed the presence of a primary mass in the right lung and additionally identified multiple small nodules in the contralateral (left) lung and enlarged distant lymph nodes, suspicious for metastatic disease.

To establish a tissue diagnosis, the patient underwent a CT-guided core needle biopsy of the right lung mass. A staging MRI of the brain was also performed, which was negative for intracranial metastases. The patient has a history as a never-smoker. The patient's performance status is excellent, ECOG 1, remaining fully ambulatory and capable of self-care but restricted in physically strenuous activity. The patient is now referred to medical oncology for discussion of the diagnosis and to establish care.

**DIAGNOSTIC WORKUP:**
**Imaging:**
- **CT Chest/Abdomen/Pelvis with contrast:** Revealed a 4.2 cm spiculated mass in the right upper lobe. Multiple bilateral pulmonary nodules were noted, with several in the left lung concerning for metastatic deposits. Pathologic mediastinal and supraclavicular lymphadenopathy was also identified, consistent with distant nodal metastasis.
- **MRI Brain with and without contrast:** No evidence of intracranial metastatic disease.

**Pathology:**
- **CT-guided core biopsy, right upper lobe lung mass:** Invasive adenocarcinoma. Morphologic features are consistent with a lung primary.

**MOLECULAR STUDIES:**
Next-generation sequencing (NGS) and immunohistochemistry were performed on the tumor tissue with the following results:
- **Actionable driver mutation:** ROS1 rearrangement detected.
- **Other drivers:** No pathogenic mutations detected in EGFR, ALK, BRAF, MET exon 14, RET, NTRK, KRAS, or ERBB2.
- **PD-L1 Expression:** Positive (Tumor Proportion Score percentage not available).
- **Tumor Mutational Burden (TMB):** Intermediate (2–16 mut/Mb).

**PROBLEM SUMMARY:**
This is a 33-year-old never-smoker with a new diagnosis of Stage IV non-small cell lung cancer, adenocarcinoma histology, positive for a ROS1 rearrangement. The patient is treatment-naive and presents for initial evaluation.

### Proposed Ground Truth

**Recommended treatment:** entrectinib

**Also NCCN-acceptable:** entrectinib; taletrectinib; crizotinib

### Your Assessment

| Field | Your answer |
|---|---|
| Label agreement (Agree / Acceptable-not-preferred / Disagree) |  |
| Preferred treatment (if disagree) |  |
| Note sufficiency (Yes / Partial / No) |  |
| Confidence (1–3) |  |
| Case complexity (Easy / Moderate / Complex) |  |
| Comments |  |

---

## Case 9

**Stage:** IIA  |  **Histology:** adenocarcinoma

### Clinical Note

**Patient ID:** [De-identified]
**Date of Consultation:** [De-identified]

**HISTORY OF PRESENT ILLNESS:**
This is a 74-year-old individual with a history of smoking (quit over one year ago) who is referred for initial medical oncology evaluation of a newly diagnosed right lung cancer.

The patient was in their usual state of health until approximately two months prior to presentation, when they developed a persistent, dry cough. This prompted a visit to their primary care provider. An initial chest radiograph was performed which showed a right upper lobe opacity. The patient denies any associated hemoptysis, chest pain, fevers, chills, or unintentional weight loss. They report good energy levels and maintain their daily activities without limitation. Performance status is excellent, ECOG 0.

**DIAGNOSTIC WORKUP:**
Following the abnormal chest x-ray, a diagnostic CT of the chest with contrast was obtained. This confirmed the presence of a 4.2 cm spiculated solid mass in the posterior segment of the right upper lobe. No significant mediastinal or hilar lymphadenopathy was identified.

For definitive diagnosis, the patient underwent a CT-guided core needle biopsy of the right upper lobe mass. Pathologic analysis of the tissue confirmed invasive adenocarcinoma, consistent with a primary non-small cell lung cancer.

Staging evaluation was completed with a PET/CT scan, which demonstrated intense FDG uptake localized to the known right upper lobe mass. There was no evidence of hypermetabolic activity in the hilar or mediastinal lymph nodes, nor in any distant sites to suggest metastatic disease. A staging MRI of the brain was also performed and was negative for intracranial metastases.

Based on this workup, the patient has clinically staged disease confined to the lung.

**MOLECULAR STUDIES:**
Next-generation sequencing was performed on the tumor tissue obtained from the biopsy.
-   No actionable driver alteration was identified. The tumor was negative for mutations or fusions involving EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2.
-   Tumor Mutational Burden (TMB) was low at <2 mut/Mb.
-   PD-L1 expression was not tested.

**PROBLEM SUMMARY:**
In summary, this is a 74-year-old former smoker who presents with a new diagnosis of Stage IIA (clinical T2b N0 M0) non-small cell lung cancer of adenocarcinoma histology. The diagnostic workup demonstrates disease localized to the right upper lobe without evidence of regional nodal involvement or distant metastatic disease. Molecular profiling of the tumor did not reveal any targetable driver mutations. The patient is treatment-naive and has an excellent performance status.

### Proposed Ground Truth

**Recommended treatment:** lobectomy + mediastinal lymph node dissection/sampling

**Also NCCN-acceptable:** lobectomy + mediastinal lymph node dissection/sampling; neoadjuvant nivolumab + platinum-doublet chemotherapy (CheckMate 816) then surgery; perioperative pembrolizumab + chemotherapy (KEYNOTE-671): neoadjuvant pembrolizumab + chemo → surgery → adjuvant pembrolizumab; perioperative durvalumab + chemotherapy (AEGEAN): neoadjuvant → surgery → adjuvant durvalumab

### Your Assessment

| Field | Your answer |
|---|---|
| Label agreement (Agree / Acceptable-not-preferred / Disagree) |  |
| Preferred treatment (if disagree) |  |
| Note sufficiency (Yes / Partial / No) |  |
| Confidence (1–3) |  |
| Case complexity (Easy / Moderate / Complex) |  |
| Comments |  |

---

## Case 10

**Stage:** IV  |  **Histology:** adenocarcinoma

### Clinical Note

**HPI:**
This is a 59-year-old with a history of smoking (quit >1 year ago) who presents for initial medical oncology consultation regarding a new diagnosis of non-small cell lung cancer. The patient initially presented to an outside emergency department several weeks ago with a persistent, non-productive cough and new-onset headaches. An initial chest X-ray was concerning for a right-sided lung mass, and the patient was referred for further diagnostic evaluation. The patient reports mild fatigue and intermittent pain in the right posterior ribs but is otherwise maintaining weight and appetite. Performance status is excellent, ECOG 1, with the patient remaining fully ambulatory and capable of all self-care.

**Diagnostic Workup:**
Following the abnormal chest X-ray, a contrast-enhanced CT of the chest, abdomen, and pelvis was performed on [De-identified]. This study revealed a 4.5 cm spiculated mass in the right upper lobe, associated with bulky mediastinal lymphadenopathy. The scan also demonstrated a 1.2 cm nodule in the left lower lobe, suspicious for a contralateral metastasis, and a lytic lesion in the right 7th rib, concerning for osseous metastatic disease.

Given the presenting symptom of headaches, a brain MRI with and without contrast was subsequently obtained. This imaging demonstrated multiple, small, ring-enhancing lesions in the bilateral cerebral hemispheres, consistent with metastatic disease.

A CT-guided core needle biopsy of the primary right upper lobe lung mass was performed by Interventional Radiology on [De-identified]. Pathologic examination of the tissue confirmed the diagnosis of a primary lung adenocarcinoma.

A staging PET/CT scan was performed which confirmed intense FDG-avidity in the primary right upper lobe mass, the mediastinal lymph nodes, the contralateral lung nodule, and the right 7th rib lesion, corroborating the findings of metastatic disease. No other distant sites of FDG-avid disease were identified in the neck, abdomen, or pelvis.

**Molecular Studies:**
Tissue from the lung mass biopsy was sent for comprehensive molecular profiling and immunohistochemistry. Next-generation sequencing (NGS) of the tumor tissue detected an actionable driver mutation, specifically an EGFR L858R point mutation in exon 21. Further molecular analysis was negative for ALK and ROS1 rearrangements, as well as for mutations in BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2.

PD-L1 expression was assessed by immunohistochemistry (IHC) and was found to be positive, with a Tumor Proportion Score (TPS) in the 1-49% range. Tumor Mutational Burden (TMB) was reported as intermediate (2–16 mut/Mb).

**Problem Summary:**
This is a 59-year-old who presents for initial evaluation of a new diagnosis of treatment-naive, AJCC Stage IV non-small cell lung cancer, adenocarcinoma histology. The diagnostic workup has confirmed metastatic disease involving the brain, bone (right rib), and contralateral lung. Molecular testing of the tumor is notable for the presence of a sensitizing EGFR L858R mutation and PD-L1 expression of 1-49%. The patient has a good performance status and is here to establish care and discuss the implications of these findings.

### Proposed Ground Truth

**Recommended treatment:** osimertinib

**Also NCCN-acceptable:** osimertinib; osimertinib + carboplatin + pemetrexed; amivantamab + lazertinib

### Your Assessment

| Field | Your answer |
|---|---|
| Label agreement (Agree / Acceptable-not-preferred / Disagree) |  |
| Preferred treatment (if disagree) |  |
| Note sufficiency (Yes / Partial / No) |  |
| Confidence (1–3) |  |
| Case complexity (Easy / Moderate / Complex) |  |
| Comments |  |

---

## Case 11

**Stage:** IV  |  **Histology:** squamous

### Clinical Note

**HPI:**
This is a 47-year-old who presents for an initial oncology consultation for a new diagnosis of non-small cell lung cancer. The patient was in a usual state of health until approximately two months prior to presentation, when they developed a persistent, non-productive cough and mild exertional dyspnea. An initial course of antibiotics for presumed bronchitis was unhelpful. Due to persistent symptoms, a chest radiograph was obtained which revealed a right upper lobe opacity. The patient has a remote history of smoking but is functionally a never-smoker. They are otherwise active and maintain an excellent performance status, continuing to work full-time. They deny hemoptysis, fevers, chills, or significant weight loss.

**Diagnostic Workup:**
Following the abnormal chest x-ray, a contrast-enhanced CT of the chest, abdomen, and pelvis was performed on [De-identified Date]. This study confirmed a 3.8 cm spiculated mass in the right upper lobe. There was associated mediastinal and right hilar lymphadenopathy. Critically, the scan also identified pathologically enlarged contralateral supraclavicular lymph nodes, the largest measuring 2.1 cm, confirming distant metastatic disease. No evidence of metastatic disease was noted in the liver, adrenal glands, or bones.

A staging MRI of the brain with and without contrast was subsequently performed and was negative for intracranial metastases.

To establish a tissue diagnosis, the patient underwent a CT-guided core needle biopsy of the right upper lobe lung mass. Pathology from this procedure confirmed a diagnosis of non-small cell lung cancer with squamous cell carcinoma histology.

**Molecular Studies:**
Next-generation sequencing (NGS) was performed on the tumor biopsy specimen.
-   An actionable RET fusion was detected.
-   The tumor was negative for mutations or rearrangements in EGFR, ALK, ROS1, BRAF, MET exon 14, NTRK, KRAS, and ERBB2.
-   Tumor Mutational Burden (TMB) was low at <2 mut/Mb.
-   PD-L1 immunohistochemistry was not performed on this specimen.

**Problem Summary:**
This is a 47-year-old never-smoker with a new diagnosis of metastatic, treatment-naive, non-small cell lung cancer of squamous cell histology. Staging workup confirmed a primary right upper lobe mass with distant lymph node metastases, consistent with AJCC Stage IV disease. Molecular profiling of the tumor is notable for the presence of a RET fusion. The patient is seen today for initial consultation and discussion of this new diagnosis.

### Proposed Ground Truth

**Recommended treatment:** selpercatinib

**Also NCCN-acceptable:** selpercatinib; pralsetinib

### Your Assessment

| Field | Your answer |
|---|---|
| Label agreement (Agree / Acceptable-not-preferred / Disagree) |  |
| Preferred treatment (if disagree) |  |
| Note sufficiency (Yes / Partial / No) |  |
| Confidence (1–3) |  |
| Case complexity (Easy / Moderate / Complex) |  |
| Comments |  |

---

## Case 12

**Stage:** IV  |  **Histology:** adenocarcinoma

### Clinical Note

**HPI:**
This is a 47-year-old individual with a recent diagnosis of metastatic non-small cell lung cancer, presenting for initial medical oncology consultation. The patient was in a usual state of health until approximately two months prior to presentation, when a persistent, non-productive cough developed. This was followed by progressive dyspnea on exertion and the self-discovery of a firm, non-tender nodule on the left anterior chest wall. An initial evaluation with a primary care provider prompted a chest radiograph which revealed a right-sided lung mass and a moderate pleural effusion. The patient is a current smoker with a significant pack-year history. The patient denies fevers, chills, or significant weight loss. Performance status is ECOG 1, fully ambulatory and able to carry out light work, limited only by some shortness of breath with strenuous activity.

**Diagnostic Workup:**
The patient was referred for further evaluation. A CT of the chest, abdomen, and pelvis with contrast was performed on [De-identified Date]. This study confirmed a 4.5 cm spiculated mass in the right upper lobe. It also demonstrated multiple enhancing pleural nodules and a moderate-to-large malignant-appearing right pleural effusion. A 1.5 cm enhancing subcutaneous nodule was noted in the left anterior chest wall, corresponding to the palpated lesion. No suspicious metastatic lesions were identified in the liver, adrenal glands, or bones. A subsequent MRI of the brain with and without contrast was performed for staging and was negative for intracranial metastases.

To establish a tissue diagnosis, the patient underwent an ultrasound-guided core biopsy of the accessible left chest wall subcutaneous nodule. Pathologic examination confirmed metastatic adenocarcinoma, with an immunoprofile consistent with a lung primary (TTF-1 positive, Napsin-A positive).

**Molecular Studies:**
Next-generation sequencing was performed on the tissue obtained from the subcutaneous nodule biopsy.
- Actionable driver mutation detected: EGFR L858R point mutation.
- The following genes were negative for known driver mutations: ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, ERBB2.
- Tumor Mutational Burden (TMB) was reported as intermediate (2–16 mut/Mb).
- PD-L1 expression was not tested.

**Problem Summary:**
This is a 47-year-old with a new diagnosis of Stage IV non-small cell lung cancer of adenocarcinoma histology, with metastatic disease involving the pleura and subcutaneous tissue. The patient is a current smoker with an ECOG performance status of 1. Molecular profiling of the tumor is notable for a sensitizing EGFR L858R mutation. The patient is treatment-naive and is seen today to discuss the diagnosis and establish care.

### Proposed Ground Truth

**Recommended treatment:** osimertinib

**Also NCCN-acceptable:** osimertinib; osimertinib + carboplatin + pemetrexed; amivantamab + lazertinib

### Your Assessment

| Field | Your answer |
|---|---|
| Label agreement (Agree / Acceptable-not-preferred / Disagree) |  |
| Preferred treatment (if disagree) |  |
| Note sufficiency (Yes / Partial / No) |  |
| Confidence (1–3) |  |
| Case complexity (Easy / Moderate / Complex) |  |
| Comments |  |

---

## Case 13

**Stage:** IV  |  **Histology:** adenocarcinoma

### Clinical Note

**REASON FOR CONSULTATION:**
New diagnosis of metastatic non-small cell lung cancer.

**HISTORY OF PRESENT ILLNESS:**
This is a 47-year-old who presents for initial oncology consultation for a new diagnosis of metastatic lung cancer. The patient was in their usual state of health until approximately one month prior to diagnosis, when they developed a persistent dry cough and focal pain in the right posterior chest wall. This prompted an evaluation with their primary care provider.

An initial chest radiograph was abnormal, showing a right upper lobe opacity. A subsequent contrast-enhanced CT of the chest confirmed a 3.5 cm spiculated mass in the right upper lobe with adjacent mediastinal lymphadenopathy. Given the concern for malignancy, the patient was referred for a CT-guided core needle biopsy of the lung mass.

Pathology from this procedure confirmed the diagnosis of adenocarcinoma. Staging evaluation was completed with a PET/CT, which demonstrated intense FDG-avidity in the primary lung mass and mediastinal nodes. The scan also revealed a solitary, intensely avid lytic lesion in a right posterior rib, consistent with osseous metastatic disease. A staging MRI of the brain was performed and was negative for intracranial metastases.

The patient is a former smoker, having quit more than one year ago. They report their cough is stable and the rib pain is intermittent and manageable. They maintain a good performance status, are fully ambulatory, and continue to work.

**DIAGNOSTIC WORKUP:**
*   **CT Chest, Abdomen, and Pelvis [De-identified Date]:** Revealed a 3.5 cm spiculated mass in the right upper lobe with mediastinal lymphadenopathy. No other sites of visceral metastatic disease were identified.
*   **PET/CT Scan [De-identified Date]:** Showed hypermetabolic activity corresponding to the right upper lobe mass and mediastinal nodes. A solitary focus of intense FDG uptake was noted in a right-sided rib, confirming M1b disease.
*   **MRI Brain [De-identified Date]:** Negative for intracranial metastatic disease.
*   **CT-Guided Biopsy of Right Lung Mass [De-identified Date]:** Pathology confirmed invasive adenocarcinoma, consistent with a lung primary.

**MOLECULAR STUDIES:**
Tissue from the lung biopsy was sent for next-generation sequencing and immunohistochemistry. The results are as follows:
*   **Actionable Driver Mutation:** EGFR exon 20 insertion detected.
*   **Other Genes:** Negative for ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2 alterations.
*   **PD-L1 Expression:** Tumor Proportion Score (TPS) ≥50%.
*   **Tumor Mutational Burden (TMB):** Intermediate (2–16 mut/Mb).

**PROBLEM SUMMARY:**
This is a 47-year-old with newly diagnosed, treatment-naive Stage IV non-small cell lung cancer, adenocarcinoma histology, with metastatic disease to bone. Molecular profiling is positive for an EGFR exon 20 insertion mutation and high PD-L1 expression (TPS ≥50%).

### Proposed Ground Truth

**Recommended treatment:** amivantamab + carboplatin + pemetrexed

**Also NCCN-acceptable:** amivantamab + carboplatin + pemetrexed

### Your Assessment

| Field | Your answer |
|---|---|
| Label agreement (Agree / Acceptable-not-preferred / Disagree) |  |
| Preferred treatment (if disagree) |  |
| Note sufficiency (Yes / Partial / No) |  |
| Confidence (1–3) |  |
| Case complexity (Easy / Moderate / Complex) |  |
| Comments |  |

---

## Case 14

**Stage:** IV  |  **Histology:** adenocarcinoma

### Clinical Note

**HPI:**
This is a 73-year-old with a past medical history of bladder cancer and a former smoking history (quit >1 year ago), who presents for an initial medical oncology consultation for a new diagnosis of non-small cell lung cancer.

The patient was in their usual state of health until approximately two months prior to diagnosis, when they developed a persistent, non-productive cough and new-onset mid-back pain. The pain was initially attributed to musculoskeletal strain but did not improve with conservative measures. Due to the persistence of symptoms, a chest X-ray was obtained which revealed a suspicious opacity in the right upper lung.

A subsequent contrast-enhanced CT of the chest, abdomen, and pelvis was performed. This confirmed the presence of a primary lung mass and also identified a suspicious lytic lesion in the thoracic spine, raising concern for metastatic disease. The patient was referred for a CT-guided core needle biopsy of the lung mass. Pathology from this procedure established the diagnosis. A dedicated MRI of the brain was performed as part of the staging workup and showed no evidence of intracranial metastases.

The patient reports mild fatigue and intermittent back pain, which is managed with over-the-counter analgesics. They remain fully ambulatory and independent with all activities of daily living, with an ECOG performance status of 1. They deny significant weight loss, shortness of breath at rest, or hemoptysis. The patient is here today to discuss the diagnosis and establish care.

**Diagnostic Workup:**
- **CT Chest/Abdomen/Pelvis [De-identified Date]:** Revealed a 4.2 cm spiculated mass in the right upper lobe of the lung with associated mediastinal lymphadenopathy. A lytic lesion was noted in the T8 vertebral body, highly suspicious for a bone metastasis. No other distant visceral metastases were identified in the liver or adrenal glands.
- **MRI Brain [De-identified Date]:** Negative for intracranial metastatic disease.
- **CT-Guided Core Biopsy, Right Upper Lobe Lung Mass [De-identified Date]:** Pathology confirmed invasive adenocarcinoma. Immunohistochemical stains were consistent with a lung primary.

**Molecular Studies:**
Next-generation sequencing (NGS) performed on the tumor biopsy specimen revealed the following:
- **Actionable Driver Mutation:** KRAS G12C mutation detected.
- **Immunotherapy Resistance Marker:** STK11 loss-of-function mutation detected.
- **Tumor Mutational Burden (TMB):** Intermediate (2–16 mut/Mb).
- **PD-L1 Expression:** Not tested.
- **Additional Testing:** Negative for pathogenic mutations or rearrangements in EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, and ERBB2.

**Problem Summary:**
This is a 73-year-old with a new diagnosis of Stage IV non-small cell lung cancer, adenocarcinoma subtype, metastatic to bone. The patient is treatment-naive. Molecular profiling of the tumor is notable for a KRAS G12C mutation and a co-occurring STK11 loss-of-function mutation. The patient has a good performance status and is presenting today to discuss the implications of this diagnosis.

### Proposed Ground Truth

**Recommended treatment:** carboplatin + pemetrexed + pembrolizumab

**Also NCCN-acceptable:** carboplatin + pemetrexed + pembrolizumab; carboplatin + pemetrexed + atezolizumab + bevacizumab; pembrolizumab; testing_first

### Your Assessment

| Field | Your answer |
|---|---|
| Label agreement (Agree / Acceptable-not-preferred / Disagree) |  |
| Preferred treatment (if disagree) |  |
| Note sufficiency (Yes / Partial / No) |  |
| Confidence (1–3) |  |
| Case complexity (Easy / Moderate / Complex) |  |
| Comments |  |

---

## Case 15

**Stage:** IV  |  **Histology:** adenocarcinoma

### Clinical Note

**HPI:**
This is a 52-year-old individual referred for initial oncology consultation regarding a new diagnosis of metastatic non-small cell lung cancer. The patient reports a several-month history of progressive dyspnea on exertion and a persistent, non-productive cough. These symptoms prompted a visit to an outpatient clinic, where a chest radiograph revealed a right-sided lung mass and a pleural effusion. The patient was subsequently referred for further evaluation.

The patient is a current smoker. Functionally, the patient is able to perform all activities of daily living but is limited by shortness of breath when climbing stairs or walking for extended periods. The ECOG performance status is estimated to be 1. The patient is otherwise feeling well and denies fevers, chills, or significant weight loss.

**Diagnostic Workup:**
A contrast-enhanced CT of the chest, abdomen, and pelvis was performed for initial staging. This demonstrated a 4.1 cm spiculated mass in the right upper lobe. There was an associated moderate right-sided pleural effusion with nodular pleural thickening, consistent with pleural metastasis (M1a). No other distant metastatic disease was identified in the contralateral lung, liver, adrenal glands, or bones. A dedicated MRI of the brain with and without contrast was performed as part of the staging workup and was negative for intracranial metastases.

A CT-guided core needle biopsy of the right upper lobe lung mass was performed on [De-identified]. Pathology was consistent with adenocarcinoma. A diagnostic and therapeutic thoracentesis was also performed, and cytologic analysis of the pleural fluid confirmed the presence of malignant cells, consistent with metastatic adenocarcinoma.

**Molecular Studies:**
Next-generation sequencing (NGS) and immunohistochemistry were performed on the tumor tissue with the following results:
-   An actionable somatic mutation was identified in the **BRAF** gene, specifically a **V600E** mutation.
-   No pathogenic mutations were detected in **EGFR, ALK, ROS1, MET exon 14, RET, NTRK, KRAS,** or **ERBB2**.
-   Immunohistochemistry for PD-L1 expression revealed a Tumor Proportion Score (TPS) of **≥50%**.
-   Tumor Mutational Burden (TMB) was determined to be **intermediate (2–16 mut/Mb)**.

**Problem Summary:**
In summary, this is a 52-year-old individual with a new diagnosis of Stage IV non-small cell lung cancer, adenocarcinoma histology, metastatic to the pleura. The patient is a current smoker with an ECOG performance status of 1. Molecular profiling of the tumor is notable for a BRAF V600E mutation and high PD-L1 expression (TPS ≥50%). The patient is treatment-naive and is seen today for initial consultation to discuss the diagnosis and establish care.

### Proposed Ground Truth

**Recommended treatment:** dabrafenib + trametinib

**Also NCCN-acceptable:** dabrafenib + trametinib

### Your Assessment

| Field | Your answer |
|---|---|
| Label agreement (Agree / Acceptable-not-preferred / Disagree) |  |
| Preferred treatment (if disagree) |  |
| Note sufficiency (Yes / Partial / No) |  |
| Confidence (1–3) |  |
| Case complexity (Easy / Moderate / Complex) |  |
| Comments |  |

---

## Case 16

**Stage:** IV  |  **Histology:** adenocarcinoma

### Clinical Note

**HPI:**
This is a 42-year-old individual with a history of former tobacco use (quit >1 year ago) who presents for initial medical oncology consultation for a new diagnosis of non-small cell lung cancer. The patient was in their usual state of health until approximately six weeks ago, when they began to experience a persistent dry cough and progressive shortness of breath with exertion. These symptoms worsened to the point of limiting their ability to walk more than one block without resting. This prompted an evaluation in an urgent care setting, where a chest X-ray revealed a large right-sided lung mass with an associated pleural effusion. The patient was subsequently referred for further diagnostic workup. The patient denies fevers, chills, or significant weight loss. Performance status is ECOG 1; the patient is fully ambulatory and capable of all self-care but is restricted in physically strenuous activity.

**Diagnostic Workup:**
Following the initial chest radiograph, a contrast-enhanced CT of the chest, abdomen, and pelvis was performed. This study confirmed the presence of a 5.2 cm spiculated mass in the right upper lobe, associated with extensive ipsilateral mediastinal and hilar lymphadenopathy. A large, complex right-sided pleural effusion was also noted. No suspicious lesions were identified in the liver, adrenal glands, or other solid abdominal organs.

A CT-guided core needle biopsy of the right upper lobe mass was performed on [De-identified date]. Pathology confirmed a diagnosis of poorly differentiated adenocarcinoma, consistent with a lung primary.

For definitive staging, a whole-body PET/CT scan was obtained. This demonstrated intense FDG-avidity in the primary right upper lobe mass, the mediastinal lymphadenopathy, and diffuse nodular uptake throughout the right pleura, confirming malignant pleural disease. No other sites of FDG-avid metastatic disease were identified. A staging MRI of the brain with contrast was performed and was negative for intracranial metastases.

The cumulative findings are consistent with a diagnosis of AJCC 8th Edition Stage IV non-small cell lung cancer, clinical stage cT3 N2 M1a.

**Molecular Studies:**
Next-generation sequencing was performed on the tumor tissue obtained from the core biopsy. Results are as follows:
- **Actionable Driver Mutation:** BRAF V600E mutation was DETECTED.
- **Other Markers:** Testing was NEGATIVE for pathogenic mutations or rearrangements in EGFR, ALK, ROS1, MET exon 14, RET, NTRK, KRAS, and ERBB2.
- **Tumor Mutational Burden (TMB):** Intermediate (9 mut/Mb).
- **PD-L1:** Not tested.

**Problem Summary:**
In summary, this is a 42-year-old who presents with a new diagnosis of Stage IV (M1a) non-small cell lung adenocarcinoma, metastatic to the pleura. The patient is treatment-naive with an ECOG performance status of 1. Molecular profiling of the tumor is notable for an activating BRAF V600E mutation.

### Proposed Ground Truth

**Recommended treatment:** dabrafenib + trametinib

**Also NCCN-acceptable:** dabrafenib + trametinib

### Your Assessment

| Field | Your answer |
|---|---|
| Label agreement (Agree / Acceptable-not-preferred / Disagree) |  |
| Preferred treatment (if disagree) |  |
| Note sufficiency (Yes / Partial / No) |  |
| Confidence (1–3) |  |
| Case complexity (Easy / Moderate / Complex) |  |
| Comments |  |

---

## Case 17

**Stage:** IV  |  **Histology:** adenocarcinoma

### Clinical Note

**MEDICAL ONCOLOGY INITIAL CONSULTATION**
**DATE OF SERVICE:** [De-identified]
**PATIENT:** [De-identified]
**MRN:** [De-identified]

**HPI:**
This is a 67-year-old individual referred for initial oncology consultation regarding a new diagnosis of metastatic non-small cell lung cancer. The patient is a former smoker, having quit less than one year ago.

The patient was in their usual state of health until approximately two months prior to presentation, when they developed a persistent, dry cough and progressive dyspnea on exertion. This was associated with an unintentional 15-pound weight loss and increasing fatigue. An initial evaluation with a primary care provider led to a chest radiograph which was abnormal, prompting further investigation. The patient remains fully ambulatory and independent in all activities of daily living, though notes a decline in overall energy. Performance status is ECOG 1.

**Diagnostic Workup:**
A contrast-enhanced CT of the chest, abdomen, and pelvis was performed. This identified a 5.2 cm spiculated mass in the right upper lobe of the lung with associated mediastinal and hilar lymphadenopathy.

For staging, a whole-body PET/CT scan was subsequently obtained. This demonstrated high FDG-avidity in the primary right upper lobe mass and the mediastinal lymph nodes. In addition, the scan revealed hypermetabolic contralateral supraclavicular lymphadenopathy, consistent with distant metastatic disease. A dedicated MRI of the brain was performed and showed no evidence of intracranial metastases.

To establish a tissue diagnosis, the patient underwent a CT-guided core needle biopsy of the primary lung mass. Pathologic examination of the specimen confirmed a diagnosis of poorly differentiated adenocarcinoma.

**Molecular Studies:**
Next-generation sequencing (NGS) and immunohistochemistry were performed on the tumor biopsy specimen.

The results revealed an actionable KRAS G12C mutation. An STK11 loss-of-function mutation was also identified. Testing for other driver mutations was negative, including EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, and ERBB2.

Immunohistochemistry for PD-L1 expression showed a Tumor Proportion Score (TPS) of ≥50%. The tumor mutational burden (TMB) was reported as intermediate (2–16 mutations/megabase).

**Problem Summary:**
In summary, this is a 67-year-old with a new diagnosis of Stage IV (AJCC 8th edition) non-small cell lung cancer, adenocarcinoma histology. The disease is metastatic to distant lymph nodes, with no evidence of brain metastases. The patient is treatment-naive with an ECOG 1 performance status. Molecular profiling is notable for a KRAS G12C mutation, a co-occurring STK11 loss-of-function mutation, and high PD-L1 expression (TPS ≥50%).

### Proposed Ground Truth

**Recommended treatment:** pembrolizumab

**Also NCCN-acceptable:** pembrolizumab; carboplatin + pemetrexed + pembrolizumab

### Your Assessment

| Field | Your answer |
|---|---|
| Label agreement (Agree / Acceptable-not-preferred / Disagree) |  |
| Preferred treatment (if disagree) |  |
| Note sufficiency (Yes / Partial / No) |  |
| Confidence (1–3) |  |
| Case complexity (Easy / Moderate / Complex) |  |
| Comments |  |

---

## Case 18

**Stage:** IV  |  **Histology:** squamous

### Clinical Note

**REASON FOR CONSULTATION:** New diagnosis of metastatic non-small cell lung cancer.

**HISTORY OF PRESENT ILLNESS:**
This is a 78-year-old former smoker who presents for initial oncology consultation to discuss a new diagnosis of metastatic squamous cell lung cancer.

The patient was in their usual state of health until approximately six weeks prior to presentation, when they began experiencing persistent headaches and a sense of gait imbalance. These symptoms progressively worsened, prompting a visit to the emergency department at an outside hospital on [De-identified Date]. An initial neurologic evaluation led to a brain MRI, which revealed several enhancing intracranial lesions consistent with metastatic disease.

Given the findings on brain imaging, a staging workup was initiated to identify a primary malignancy. A contrast-enhanced CT of the chest, abdomen, and pelvis was performed. This study demonstrated a large, irregular mass in the right upper lobe of the lung with associated mediastinal lymphadenopathy. No other sites of distant metastatic disease were identified in the chest, abdomen, or pelvis. The patient was subsequently referred for a tissue diagnosis. They are now seen in clinic for evaluation and to establish care. The patient remains ambulatory with a good performance status, though they note some fatigue and ongoing mild headaches.

**DIAGNOSTIC WORKUP:**
*   **Brain MRI (with and without contrast), [De-identified Date]:** Revealed multiple, scattered ring-enhancing lesions in the cerebral hemispheres, consistent with metastatic deposits.
*   **CT Chest/Abdomen/Pelvis (with contrast), [De-identified Date]:** Identified a 4.5 cm spiculated mass in the right upper lobe. Mediastinal and hilar adenopathy was noted. No definitive evidence of metastatic disease in the liver, adrenal glands, or bones.
*   **CT-Guided Core Needle Biopsy, Right Lung Mass, [De-identified Date]:** Pathology confirmed a diagnosis of poorly differentiated non-small cell carcinoma with features most consistent with squamous cell carcinoma.

**MOLECULAR STUDIES:**
Next-generation sequencing was performed on the tumor biopsy specimen.
*   **Driver Mutations:** No actionable driver alterations were identified. Testing was negative for mutations or rearrangements in EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2.
*   **PD-L1:** Expression was not tested on this specimen.
*   **Tumor Mutational Burden (TMB):** Intermediate (reported as 2–16 mutations/megabase).

**PROBLEM SUMMARY:**
This is a 78-year-old former smoker with a new diagnosis of AJCC Stage IV non-small cell lung cancer, squamous cell histology, metastatic to the brain. Molecular profiling of the tumor did not identify any actionable driver alterations.

### Proposed Ground Truth

**Recommended treatment:** carboplatin + paclitaxel + pembrolizumab

**Also NCCN-acceptable:** carboplatin + paclitaxel + pembrolizumab; carboplatin + nab-paclitaxel + pembrolizumab; pembrolizumab; testing_first

### Your Assessment

| Field | Your answer |
|---|---|
| Label agreement (Agree / Acceptable-not-preferred / Disagree) |  |
| Preferred treatment (if disagree) |  |
| Note sufficiency (Yes / Partial / No) |  |
| Confidence (1–3) |  |
| Case complexity (Easy / Moderate / Complex) |  |
| Comments |  |

---

## Case 19

**Stage:** IV  |  **Histology:** adenocarcinoma

### Clinical Note

**HPI:**
This is a 67-year-old individual with a history of smoking (quit >1 year ago) who presents for initial medical oncology consultation regarding a new diagnosis of metastatic non-small cell lung cancer. The patient was in a usual state of health until approximately one month prior to presentation, when new-onset headaches and intermittent dizziness developed. These symptoms prompted an evaluation with a brain MRI, which revealed multiple intracranial lesions concerning for metastatic disease. A subsequent staging workup was initiated to identify a primary malignancy. The patient reports mild fatigue but is otherwise active and fully ambulatory, with an ECOG performance status of 1. There is no significant cough, hemoptysis, or dyspnea. Appetite is stable and there has been no unintentional weight loss.

**Diagnostic Workup:**
The diagnostic evaluation was prompted by neurological symptoms.

A brain MRI performed on [De-identified Date] demonstrated multiple enhancing parenchymal lesions in the cerebral hemispheres, consistent with metastatic disease.

Subsequent staging with a contrast-enhanced CT of the chest, abdomen, and pelvis on [De-identified Date] revealed a 4.1 cm spiculated mass in the right upper lobe of the lung, with associated mediastinal and hilar lymphadenopathy. No other sites of distant metastatic disease were identified in the chest, abdomen, or pelvis.

On [De-identified Date], the patient underwent a CT-guided core needle biopsy of the right upper lobe lung mass. Pathologic examination of the tissue confirmed a diagnosis of invasive adenocarcinoma, consistent with a non-small cell lung primary.

The cumulative findings of a primary lung adenocarcinoma with confirmed brain metastases establish a diagnosis of AJCC Stage IV disease.

**Molecular Studies:**
Next-generation sequencing was performed on the tumor tissue obtained from the lung biopsy.
- An actionable driver mutation was detected in KRAS (G12C).
- Testing was negative for pathogenic alterations in EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, and ERBB2.
- Tumor Mutational Burden (TMB) was determined to be intermediate (2–16 mutations/megabase).
- PD-L1 expression was not tested as part of this panel.

**Problem Summary:**
In summary, this is a 67-year-old former smoker presenting with newly diagnosed, treatment-naive Stage IV non-small cell lung cancer, adenocarcinoma histology, with metastatic disease to the brain. Molecular profiling of the tumor is notable for a KRAS G12C mutation. The patient is seen today for initial evaluation and discussion of the diagnosis.

### Proposed Ground Truth

**Recommended treatment:** carboplatin + pemetrexed + pembrolizumab

**Also NCCN-acceptable:** carboplatin + pemetrexed + pembrolizumab; carboplatin + pemetrexed + atezolizumab + bevacizumab; pembrolizumab; testing_first

### Your Assessment

| Field | Your answer |
|---|---|
| Label agreement (Agree / Acceptable-not-preferred / Disagree) |  |
| Preferred treatment (if disagree) |  |
| Note sufficiency (Yes / Partial / No) |  |
| Confidence (1–3) |  |
| Case complexity (Easy / Moderate / Complex) |  |
| Comments |  |

---

## Case 20

**Stage:** IV  |  **Histology:** nos

### Clinical Note

**HPI:**
This is an 87-year-old individual with a history of smoking (quit over one year ago) who presents for an initial oncology consultation regarding a new diagnosis of metastatic non-small cell lung cancer. The patient was in their usual state of health until approximately two months prior to presentation, when they developed a persistent, non-productive cough and mild exertional dyspnea. These symptoms prompted an evaluation by their primary care physician. Despite the new symptoms, the patient maintains a good performance status, remains ambulatory, and is independent with all activities of daily living.

**Diagnostic Workup:**
The diagnostic evaluation began with a chest X-ray, which demonstrated a suspicious opacity in the right lung. This led to a staging CT of the chest, abdomen, and pelvis with contrast. Imaging confirmed a 4.5 cm primary mass in the right upper lobe with associated mediastinal lymphadenopathy. The abdominal portion of the scan revealed a 3.2 cm enhancing mass in the left adrenal gland, highly suspicious for a solitary site of metastatic disease.

To complete staging and evaluate for central nervous system involvement, a contrast-enhanced MRI of the brain was performed, which was negative for any intracranial metastases.

Subsequently, the patient underwent a CT-guided core needle biopsy of the right upper lobe lung mass on [De-identified]. Pathologic analysis of the tissue confirmed a diagnosis of non-small cell lung cancer, not otherwise specified (NOS) histology.

**Molecular Studies:**
The biopsy specimen was submitted for next-generation sequencing to identify potential therapeutic targets. The key findings are as follows:
- Actionable driver detected: High-level MET amplification.
- Negative for other common driver mutations/fusions: EGFR, ALK, ROS1, BRAF, MET exon 14 skipping mutation, RET, NTRK, KRAS, and ERBB2 (HER2).
- Tumor Mutational Burden (TMB) was determined to be low (<2 mutations/megabase).
- PD-L1 expression was not tested, consistent with the standard of care at the time of initial tissue sequencing.

**Problem Summary:**
In summary, this is an 87-year-old former smoker who presents as treatment-naive with a new diagnosis of AJCC Stage IV non-small cell lung cancer, NOS histology. The disease is metastatic to a solitary site in the left adrenal gland, with no evidence of brain metastases. Molecular profiling of the tumor is notable for a high-level MET amplification. The patient is here for initial consultation to discuss the diagnosis.

### Proposed Ground Truth

**Recommended treatment:** carboplatin + pemetrexed + pembrolizumab

**Also NCCN-acceptable:** carboplatin + pemetrexed + pembrolizumab; carboplatin + pemetrexed + atezolizumab + bevacizumab; pembrolizumab; testing_first

### Your Assessment

| Field | Your answer |
|---|---|
| Label agreement (Agree / Acceptable-not-preferred / Disagree) |  |
| Preferred treatment (if disagree) |  |
| Note sufficiency (Yes / Partial / No) |  |
| Confidence (1–3) |  |
| Case complexity (Easy / Moderate / Complex) |  |
| Comments |  |

---

## Case 21

**Stage:** IIIA  |  **Histology:** adenocarcinoma

### Clinical Note

**HPI:**
This is a 62-year-old individual with a history of former tobacco use (quit >1 year ago) who is referred for initial oncologic consultation regarding a new diagnosis of non-small cell lung cancer. The patient was in their usual state of health until approximately two months prior to presentation when they developed a persistent, non-productive cough. This prompted a visit to their primary care provider. An initial chest radiograph showed a right-sided lung opacity, leading to further imaging. The patient denies fevers, chills, or significant weight loss but does endorse some mild fatigue. Performance status is excellent; the patient remains fully ambulatory and capable of all self-care.

**Diagnostic Workup:**
Following the abnormal chest x-ray, a contrast-enhanced CT of the chest, abdomen, and pelvis was obtained. This study characterized a 3.5 cm spiculated mass in the right upper lobe. It also demonstrated bulky ipsilateral mediastinal and hilar lymphadenopathy, concerning for locoregional nodal involvement. No suspicious lesions were identified in the liver, adrenal glands, or other visceral organs.

For definitive staging, a whole-body PET/CT was performed. This confirmed high metabolic activity within the primary right upper lobe mass and the associated right-sided mediastinal lymph nodes. There was no evidence of FDG-avid disease at any distant site. A dedicated MRI of the brain with and without contrast was subsequently performed and revealed no evidence of intracranial metastases.

To establish a tissue diagnosis, the patient underwent bronchoscopy with endobronchial ultrasound (EBUS) and fine-needle aspiration of a subcarinal lymph node. Pathologic analysis of the specimen confirmed the diagnosis of adenocarcinoma.

**Molecular Studies:**
Pathology from the EBUS-guided biopsy confirmed adenocarcinoma histology. Comprehensive next-generation sequencing and immunohistochemical analysis were performed on the tissue specimen.
- Actionable driver mutation detected: EGFR uncommon sensitizing mutation.
- Testing was negative for genomic alterations in ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2.
- PD-L1 expression by immunohistochemistry demonstrated a Tumor Proportion Score (TPS) of 1-49%.
- Tumor Mutational Burden (TMB) was found to be intermediate (2–16 mut/Mb).

**Problem Summary:**
In summary, this is a 62-year-old former smoker presenting for initial evaluation of a newly diagnosed, locally advanced lung cancer. The patient is treatment-naive with a good performance status.

1.  **Non-Small Cell Lung Cancer (NSCLC), Adenocarcinoma Histology, AJCC Stage IIIA.** The disease is localized to the right hemithorax with mediastinal nodal involvement, with no evidence of distant metastatic disease.
2.  **Molecular Profile:** Positive for an EGFR uncommon sensitizing mutation.
3.  **Immune Profile:** PD-L1 TPS is 1-49%.

### Proposed Ground Truth

**Recommended treatment:** concurrent chemoradiation + durvalumab (consolidation)

**Also NCCN-acceptable:** concurrent chemoradiation + durvalumab (consolidation)

### Your Assessment

| Field | Your answer |
|---|---|
| Label agreement (Agree / Acceptable-not-preferred / Disagree) |  |
| Preferred treatment (if disagree) |  |
| Note sufficiency (Yes / Partial / No) |  |
| Confidence (1–3) |  |
| Case complexity (Easy / Moderate / Complex) |  |
| Comments |  |

---

## Case 22

**Stage:** IV  |  **Histology:** adenocarcinoma

### Clinical Note

INITIAL MEDICAL ONCOLOGY CONSULTATION
Patient Name: [De-identified]
MRN: [De-identified]
Date of Service: [De-identified]

**History of Present Illness:**
This is a 79-year-old who presents for an initial oncology consultation regarding a new diagnosis of metastatic non-small cell lung cancer. The patient was in a usual state of health until approximately six weeks prior to presentation, when they began to experience a persistent, dry cough and progressive right-sided chest wall pain. The pain was initially managed with over-the-counter analgesics with minimal relief. Due to the persistence of symptoms, the patient presented to their primary care provider, who ordered a chest radiograph.

The chest X-ray revealed a suspicious opacity in the right upper lung field, prompting further evaluation with staging imaging. The patient reports a good functional status, estimated at an ECOG performance status of 1, remaining fully ambulatory and independent in all activities of daily living, though they have curtailed more strenuous activities due to discomfort. The patient is a former smoker with a remote history of tobacco use, having quit over a decade ago.

**Diagnostic Workup:**
A PET/CT scan was performed on [De-identified date] for staging. This study demonstrated a large, intensely hypermetabolic mass in the right upper lobe. There was also evidence of FDG-avid mediastinal and hilar lymphadenopathy. The scan identified distant metastatic disease, including a lytic, FDG-avid lesion in a right-sided rib corresponding to the patient's area of pain, as well as a hypermetabolic nodule in the left adrenal gland. To complete staging, a contrast-enhanced MRI of the brain was obtained, which was negative for any evidence of intracranial metastases.

On [De-identified date], the patient underwent a CT-guided core needle biopsy of the right upper lobe lung mass. Pathologic examination of the tissue confirmed the diagnosis of invasive adenocarcinoma, consistent with a lung primary.

**Molecular Studies:**
Comprehensive molecular profiling via next-generation sequencing (NGS) was performed on the tumor tissue. No actionable driver alterations were identified. Specifically, the tumor was found to be negative for mutations or fusions involving EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2.

Immunohistochemistry for PD-L1 was performed, and the tumor was found to be negative, with a Tumor Proportion Score (TPS) of <1%. Tumor Mutational Burden (TMB) was assessed and found to be in the intermediate range (14 mutations/megabase). Genomic analysis also identified a pathogenic loss-of-function mutation in the STK11 gene.

**Problem Summary:**
In summary, this is a 79-year-old with a new diagnosis of AJCC Stage IV non-small cell lung cancer, adenocarcinoma histology. Staging studies confirm metastatic disease involving bone and the left adrenal gland, with no evidence of brain metastases. The patient is treatment-naive with an excellent performance status. Molecular studies are notable for the absence of targetable driver mutations, negative PD-L1 expression, an intermediate TMB, and the presence of an STK11 loss-of-function mutation, which is a biomarker associated with primary resistance to PD-1/PD-L1 inhibitors. The patient is seen today to discuss the diagnosis and establish care.

### Proposed Ground Truth

**Recommended treatment:** carboplatin + pemetrexed + pembrolizumab

**Also NCCN-acceptable:** carboplatin + pemetrexed + pembrolizumab; carboplatin + pemetrexed + atezolizumab + bevacizumab; pembrolizumab; testing_first

### Your Assessment

| Field | Your answer |
|---|---|
| Label agreement (Agree / Acceptable-not-preferred / Disagree) |  |
| Preferred treatment (if disagree) |  |
| Note sufficiency (Yes / Partial / No) |  |
| Confidence (1–3) |  |
| Case complexity (Easy / Moderate / Complex) |  |
| Comments |  |

---

## Case 23

**Stage:** IV  |  **Histology:** adenocarcinoma

### Clinical Note

**INITIAL MEDICAL ONCOLOGY CONSULTATION**

**Patient Name:** [De-identified]
**MRN:** [De-identified]
**Date of Service:** [De-identified]

**History of Present Illness:**
This is an 82-year-old with a past medical history notable for breast cancer, who is seen in consultation for a new diagnosis of non-small cell lung cancer. The patient was in their usual state of health until approximately one month ago when they began experiencing intermittent headaches and mild word-finding difficulty. These symptoms prompted an evaluation in an outside emergency department.

An initial non-contrast head CT was concerning for intracranial masses, which led to a formal brain MRI with contrast. This study confirmed the presence of multiple enhancing lesions consistent with metastatic disease. A subsequent staging workup was initiated to identify a primary malignancy, including a contrast-enhanced CT of the chest, abdomen, and pelvis. This imaging revealed a suspicious 4.1 cm spiculated mass in the upper lobe of the left lung with associated mediastinal lymphadenopathy. No other sites of extracranial metastatic disease were identified.

The patient was referred to interventional radiology and underwent a CT-guided core needle biopsy of the left lung mass. Pathology confirmed the diagnosis of adenocarcinoma. The patient has remained functional, with an ECOG performance status of 1, but reports ongoing mild fatigue. They present today to discuss the diagnosis and establish care.

**Diagnostic Workup:**
*   **Brain MRI ([De-identified Date]):** Revealed multiple, scattered enhancing parenchymal lesions in the bilateral cerebral hemispheres, consistent with metastatic deposits.
*   **CT Chest/Abdomen/Pelvis ([De-identified Date]):** Identified a 4.1 cm spiculated mass in the left upper lobe. Prominent mediastinal and left hilar lymph nodes were noted. No suspicious hepatic, adrenal, or osseous lesions were seen.
*   **Pathology, Left Lung Mass Biopsy ([De-identified Date]):** Invasive adenocarcinoma, moderately differentiated. Immunohistochemical stains are consistent with a lung primary.

**Molecular Studies:**
Next-generation sequencing (NGS) performed on the tumor tissue demonstrated the following:
*   **Actionable Driver:** An EGFR uncommon sensitizing mutation was detected.
*   **Negative for:** Alterations in ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2.
*   **Tumor Mutational Burden (TMB):** Intermediate (2–16 mut/Mb).
*   **PD-L1:** Not tested.

**Problem Summary:**
In summary, this is an 82-year-old never-smoker who presents with a new diagnosis of Stage IV (AJCC 8th Edition) non-small cell lung cancer, adenocarcinoma histology, with metastases to the brain. Molecular testing of the tumor is significant for the presence of an EGFR uncommon sensitizing mutation. The patient is treatment-naive and is here for initial consultation to review the findings.

### Proposed Ground Truth

**Recommended treatment:** carboplatin + pemetrexed + pembrolizumab

**Also NCCN-acceptable:** carboplatin + pemetrexed + pembrolizumab; carboplatin + pemetrexed + atezolizumab + bevacizumab; pembrolizumab; testing_first

### Your Assessment

| Field | Your answer |
|---|---|
| Label agreement (Agree / Acceptable-not-preferred / Disagree) |  |
| Preferred treatment (if disagree) |  |
| Note sufficiency (Yes / Partial / No) |  |
| Confidence (1–3) |  |
| Case complexity (Easy / Moderate / Complex) |  |
| Comments |  |

---

## Case 24

**Stage:** IV  |  **Histology:** adenocarcinoma

### Clinical Note

**HPI:**
This is an initial oncology consultation for a 62-year-old with a recent diagnosis of metastatic non-small cell lung cancer. The patient was in their usual state of good health until approximately three months ago, when they began to experience a persistent non-productive cough and progressive shortness of breath with exertion. Over the subsequent weeks, these symptoms were accompanied by the development of right-sided chest wall pain and an unintentional 10-pound weight loss. An initial evaluation with their primary care provider prompted a chest X-ray, which was abnormal. The patient has a remote history of tobacco use, having quit more than one year ago. They are active and ambulatory, with an ECOG performance status of 1.

**Diagnostic Workup:**
Following the abnormal chest radiograph, a contrast-enhanced CT scan of the chest, abdomen, and pelvis was performed. This study revealed a 3.8 cm spiculated mass in the right upper lobe of the lung, with associated mediastinal and hilar adenopathy. The scan also demonstrated a moderate right-sided pleural effusion and a lytic lesion in the thoracic spine, concerning for metastatic disease.

A subsequent whole-body PET/CT scan was obtained for staging purposes. This confirmed high metabolic activity in the primary right upper lobe mass, multiple mediastinal lymph nodes, and nodular pleural thickening consistent with pleural metastases. Avid uptake was also noted in a skeletal lesion in the T8 vertebral body, confirming osseous metastatic disease. A dedicated MRI of the brain was performed and showed no evidence of intracranial metastases.

A CT-guided core needle biopsy of the right upper lobe lung mass was performed on [De-identified date]. Pathology confirmed the diagnosis of non-small cell lung cancer.

**Molecular Studies:**
Pathology from the lung mass biopsy confirmed adenocarcinoma histology. Comprehensive next-generation sequencing was performed on the tissue specimen.
- **Driver Mutations:** An actionable mutation was detected in **KRAS (G12C)**.
- **Other Markers:** Testing was negative for targetable alterations in EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, and ERBB2.
- **PD-L1 Expression:** Not tested.
- **Tumor Mutational Burden (TMB):** Intermediate (2-16 mut/Mb).

**Problem Summary:**
In summary, this is a 62-year-old who presents for evaluation of a new diagnosis of treatment-naive, AJCC Stage IV non-small cell lung cancer of adenocarcinoma histology. The diagnostic workup confirms metastatic disease involving the pleura and bone. Molecular analysis of the tumor is notable for a KRAS G12C mutation. The patient is here today to discuss the diagnosis and establish care.

### Proposed Ground Truth

**Recommended treatment:** carboplatin + pemetrexed + pembrolizumab

**Also NCCN-acceptable:** carboplatin + pemetrexed + pembrolizumab; carboplatin + pemetrexed + atezolizumab + bevacizumab; pembrolizumab; testing_first

### Your Assessment

| Field | Your answer |
|---|---|
| Label agreement (Agree / Acceptable-not-preferred / Disagree) |  |
| Preferred treatment (if disagree) |  |
| Note sufficiency (Yes / Partial / No) |  |
| Confidence (1–3) |  |
| Case complexity (Easy / Moderate / Complex) |  |
| Comments |  |

---

## Case 25

**Stage:** IIIB  |  **Histology:** adenocarcinoma

### Clinical Note

**HPI:**
This is the initial oncology consultation for a 55-year-old with a new diagnosis of non-small cell lung cancer. The patient is a former smoker, having quit over one year ago. They were in their usual state of health until approximately three months prior to presentation, when they developed a persistent, non-productive cough and progressive dyspnea on exertion. This was later accompanied by mild right-sided chest discomfort and an unintentional weight loss of approximately 10 pounds over two months. These symptoms prompted a visit to their primary care provider, who ordered initial imaging.

**Diagnostic Workup:**
A chest X-ray revealed a right upper lobe opacity, which led to a contrast-enhanced CT of the chest. The CT scan demonstrated a 5.5 cm spiculated mass in the right upper lobe. Additionally, there was extensive ipsilateral mediastinal and supraclavicular lymphadenopathy, with the largest node measuring 3.2 cm.

For definitive staging, a PET/CT was performed on [De-identified Date]. This study confirmed high FDG-avidity in the primary right upper lobe mass and in the extensive right-sided mediastinal, hilar, and supraclavicular lymph nodes. Importantly, there was no evidence of distant metastatic disease in the contralateral lung, liver, adrenal glands, or bones. A subsequent MRI of the brain with contrast was also performed, which was negative for any evidence of intracranial metastases.

On [De-identified Date], the patient underwent bronchoscopy with endobronchial ultrasound (EBUS) for tissue diagnosis and staging. A fine-needle aspiration (FNA) was performed on a subcarinal lymph node. Pathologic review of the specimen confirmed invasive adenocarcinoma, consistent with a lung primary.

**Molecular Studies:**
Tissue from the biopsy specimen was sent for next-generation sequencing. The results are as follows:
- No actionable driver alteration was identified. The tumor was negative for mutations or rearrangements in EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2.
- PD-L1 expression was not tested on this specimen.
- Tumor Mutational Burden (TMB) was found to be intermediate (2–16 mutations/megabase).

**Problem Summary:**
In summary, this is a 55-year-old former smoker who presents as treatment-naive with a new diagnosis of Stage IIIB non-small cell lung cancer, adenocarcinoma histology. The diagnostic workup confirms locally advanced, non-metastatic disease. Comprehensive molecular profiling did not identify any actionable oncogenic drivers. The patient is seen today for initial consultation to discuss the diagnosis in detail and review the clinical situation.

### Proposed Ground Truth

**Recommended treatment:** concurrent chemoradiation + durvalumab (consolidation)

**Also NCCN-acceptable:** concurrent chemoradiation + durvalumab (consolidation)

### Your Assessment

| Field | Your answer |
|---|---|
| Label agreement (Agree / Acceptable-not-preferred / Disagree) |  |
| Preferred treatment (if disagree) |  |
| Note sufficiency (Yes / Partial / No) |  |
| Confidence (1–3) |  |
| Case complexity (Easy / Moderate / Complex) |  |
| Comments |  |

---

## Case 26

**Stage:** IV  |  **Histology:** squamous

### Clinical Note

**HPI:**
This is a 58-year-old former smoker (quit over one year ago) who presents for initial oncology consultation for a new diagnosis of non-small cell lung cancer. The patient was in their usual state of health until approximately two months ago when they developed a persistent cough and mild shortness of breath with exertion. This prompted an evaluation by their primary care provider, which led to chest imaging. The patient reports good energy levels and maintains an excellent performance status, remaining fully active and able to carry on all pre-illness activities without restriction (ECOG 0). The patient is here today to discuss the comprehensive diagnostic findings and establish care.

**Diagnostic Workup:**
An initial chest CT scan revealed a 4.5 cm mass in the right upper lobe. The scan also demonstrated a distinct 1.2 cm nodule in the contralateral left lower lobe, concerning for metastatic disease. For comprehensive staging, a PET/CT was performed, which showed intense FDG-avidity in the primary right upper lobe mass as well as in the contralateral lung nodule. No other distant sites of FDG-avid disease were identified in the neck, abdomen, or pelvis. A dedicated MRI of the brain was performed and was negative for any intracranial metastases.

The patient subsequently underwent a CT-guided core needle biopsy of the right upper lobe mass on [De-identified Date]. Pathologic review confirmed the diagnosis of non-small cell lung cancer with squamous cell carcinoma histology.

**Molecular Studies:**
Next-generation sequencing performed on the tumor tissue revealed the following:
-   **Actionable Driver:** An ALK gene rearrangement was detected.
-   **Negative for:** EGFR, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, ERBB2.
-   **Tumor Mutational Burden (TMB):** Intermediate (2–16 mut/Mb).
-   **PD-L1:** Testing was not performed on this specimen.

**Problem Summary:**
This is a 58-year-old with newly diagnosed, treatment-naive Stage IV non-small cell lung cancer, squamous histology. The disease is metastatic to the contralateral lung. Molecular profiling is notable for an ALK rearrangement.

### Proposed Ground Truth

**Recommended treatment:** alectinib

**Also NCCN-acceptable:** alectinib; brigatinib; lorlatinib

### Your Assessment

| Field | Your answer |
|---|---|
| Label agreement (Agree / Acceptable-not-preferred / Disagree) |  |
| Preferred treatment (if disagree) |  |
| Note sufficiency (Yes / Partial / No) |  |
| Confidence (1–3) |  |
| Case complexity (Easy / Moderate / Complex) |  |
| Comments |  |

---

## Case 27

**Stage:** IIIA  |  **Histology:** adenocarcinoma

### Clinical Note

**MEDICAL ONCOLOGY - INITIAL CONSULTATION**
**DATE OF SERVICE:** [De-identified]
**PATIENT:** [De-identified]
**MRN:** [De-identified]

**HISTORY OF PRESENT ILLNESS:**
This is a 59-year-old with a recent diagnosis of non-small cell lung cancer. The patient is a former smoker, having quit within the past year. The patient initially presented to an outside facility with a persistent, non-productive cough and mild dyspnea on exertion, which prompted an initial workup. The patient remains active with an excellent performance status (ECOG 1) and is here today for initial consultation to discuss the diagnosis and management options.

**DIAGNOSTIC WORKUP:**
Initial evaluation included a chest CT scan which revealed a primary mass in the right upper lobe, measuring approximately 4 cm. The scan also demonstrated ipsilateral mediastinal lymphadenopathy.

To complete staging, a PET/CT scan was performed. This study confirmed FDG-avidity within the primary right upper lobe mass and in the mediastinal nodal stations, consistent with locoregionally advanced disease. Importantly, there was no evidence of FDG-avid disease elsewhere in the body to suggest distant metastases. A dedicated MRI of the brain was also negative for intracranial metastatic disease.

The patient subsequently underwent a bronchoscopy with endobronchial ultrasound (EBUS) for tissue acquisition. Biopsies of the primary lung mass were obtained. Pathology from this procedure confirmed a diagnosis of adenocarcinoma, consistent with a lung primary.

**MOLECULAR STUDIES:**
Next-generation sequencing was performed on the tumor tissue.
- No actionable driver alteration was identified. The tumor was negative for alterations in EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2.
- Tumor Mutational Burden (TMB) was intermediate (2–16 mut/Mb).
- PD-L1 expression by immunohistochemistry was not tested, as this was not standard of care at the time of the initial tissue analysis.

**PROBLEM SUMMARY:**
In summary, this is a 59-year-old former smoker who presents for initial evaluation of a new diagnosis of Stage IIIA non-small cell lung cancer, adenocarcinoma histology. The patient is treatment-naive. Staging workup is negative for distant metastatic disease. Molecular profiling of the tumor did not identify any targetable driver mutations. The patient has an excellent performance status and is here to discuss the findings.

### Proposed Ground Truth

**Recommended treatment:** concurrent chemoradiation + durvalumab (consolidation)

**Also NCCN-acceptable:** concurrent chemoradiation + durvalumab (consolidation)

### Your Assessment

| Field | Your answer |
|---|---|
| Label agreement (Agree / Acceptable-not-preferred / Disagree) |  |
| Preferred treatment (if disagree) |  |
| Note sufficiency (Yes / Partial / No) |  |
| Confidence (1–3) |  |
| Case complexity (Easy / Moderate / Complex) |  |
| Comments |  |

---

## Case 28

**Stage:** IIA  |  **Histology:** adenocarcinoma

### Clinical Note

**HPI:**
This is an 80-year-old individual with a history of smoking (quit >1 year ago) who is referred for an initial medical oncology consultation for a new diagnosis of non-small cell lung cancer. The patient initially presented to primary care with a persistent, non-productive cough. A chest X-ray was obtained which showed a right upper lobe opacity, prompting further investigation. A subsequent contrast-enhanced chest CT confirmed the presence of a spiculated mass in the right lung. The patient is otherwise feeling well, reporting no significant fatigue, weight loss, or hemoptysis. Performance status is excellent, ECOG 0-1, with the patient maintaining all activities of daily living without restriction.

**Diagnostic Workup:**
A comprehensive staging workup has been completed.

CT of the Chest, Abdomen, and Pelvis with contrast, performed on [De-identified Date], demonstrated a 4.2 cm spiculated solid mass in the posterior segment of the right upper lobe. There was no evidence of mediastinal, hilar, or supraclavicular lymphadenopathy. The visualized liver, adrenal glands, and kidneys were unremarkable, with no lesions suspicious for metastatic disease.

PET/CT scan, performed on [De-identified Date], showed intense FDG-avidity corresponding to the known right upper lobe mass. No other sites of abnormal FDG uptake were identified in the thorax or elsewhere to suggest nodal or distant metastatic disease.

MRI of the Brain with and without contrast, performed on [De-identified Date] for staging, was negative for any evidence of intracranial metastases.

CT-guided core needle biopsy of the right upper lobe mass was performed on [De-identified Date]. Pathology confirmed invasive adenocarcinoma, moderately differentiated.

**Molecular Studies:**
Next-generation sequencing (NGS) was performed on the tumor tissue. The key findings are as follows:
- Actionable driver mutation detected: KRAS G12C
- Co-mutation detected: STK11 loss-of-function mutation
- PD-L1 Tumor Proportion Score (TPS): 0% (Negative)
- Tumor Mutational Burden (TMB): Intermediate (14 mut/Mb)
- No pathogenic mutations were detected in EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, or ERBB2.

**Problem Summary:**
In summary, this is an 80-year-old with a new diagnosis of clinical Stage IIA (cT2bN0M0) non-small cell lung cancer of adenocarcinoma histology, confined to the right upper lobe. Staging workup including PET/CT and brain MRI is negative for regional or distant metastatic disease. Molecular profiling reveals a KRAS G12C mutation, a co-occurring STK11 loss-of-function mutation, and negative PD-L1 expression. The patient is treatment-naive and presents today for initial evaluation and discussion.

### Proposed Ground Truth

**Recommended treatment:** lobectomy + mediastinal lymph node dissection/sampling

**Also NCCN-acceptable:** lobectomy + mediastinal lymph node dissection/sampling; neoadjuvant nivolumab + platinum-doublet chemotherapy (CheckMate 816) then surgery; perioperative pembrolizumab + chemotherapy (KEYNOTE-671): neoadjuvant pembrolizumab + chemo → surgery → adjuvant pembrolizumab; perioperative durvalumab + chemotherapy (AEGEAN): neoadjuvant → surgery → adjuvant durvalumab

### Your Assessment

| Field | Your answer |
|---|---|
| Label agreement (Agree / Acceptable-not-preferred / Disagree) |  |
| Preferred treatment (if disagree) |  |
| Note sufficiency (Yes / Partial / No) |  |
| Confidence (1–3) |  |
| Case complexity (Easy / Moderate / Complex) |  |
| Comments |  |

---

## Case 29

**Stage:** IIIA  |  **Histology:** adenocarcinoma

### Clinical Note

**HPI:**
This is a 69-year-old individual with a history of former tobacco use who is seen in our oncology clinic for an initial consultation regarding a new diagnosis of non-small cell lung cancer. The patient was in their usual state of good health until approximately three months prior to presentation, when they developed a new, persistent, non-productive cough. This was initially treated as bronchitis without resolution, which prompted further investigation. An initial chest X-ray revealed a right upper lobe opacity, leading to a more detailed diagnostic workup.

The patient reports some mild fatigue but denies fevers, chills, night sweats, or significant unintentional weight loss. They remain fully ambulatory and independent in all activities of daily living, with an ECOG performance status of 0-1. They have no hemoptysis, chest pain, or bone pain. A review of systems is negative for headaches, visual changes, or other focal neurologic deficits.

**Diagnostic Workup:**
A contrast-enhanced CT of the chest confirmed the presence of a 4.2 cm spiculated mass in the right upper lobe. The scan also identified several enlarged ipsilateral mediastinal lymph nodes, concerning for locoregional involvement.

A subsequent whole-body PET/CT scan was performed for staging. This study demonstrated intense FDG uptake within the primary right upper lobe mass and confirmed hypermetabolic activity in right-sided mediastinal lymph nodes, consistent with nodal metastases. Crucially, there was no evidence of FDG-avid disease in the contralateral lung, liver, adrenal glands, bones, or other distant sites.

Given the findings of locally advanced disease, a staging MRI of the brain with contrast was obtained, which was negative for any evidence of intracranial metastases.

A CT-guided core needle biopsy of the right upper lobe mass was performed on [De-identified Date]. Histopathologic examination of the tissue confirmed a diagnosis of invasive adenocarcinoma, consistent with a primary lung origin.

**Molecular Studies:**
Next-generation sequencing was performed on the tumor specimen. No actionable driver alteration was identified; the tumor was negative for mutations or rearrangements in EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2. PD-L1 expression was not tested. The tumor mutational burden (TMB) was reported as intermediate (2–16 mut/Mb).

**Problem Summary:**
In summary, this is a 69-year-old former smoker with a new diagnosis of non-metastatic, Stage IIIA non-small cell lung cancer of adenocarcinoma histology. Molecular profiling did not identify an actionable driver mutation. The patient has an excellent performance status and is here to discuss the diagnosis and potential management options.

### Proposed Ground Truth

**Recommended treatment:** concurrent chemoradiation + durvalumab (consolidation)

**Also NCCN-acceptable:** concurrent chemoradiation + durvalumab (consolidation)

### Your Assessment

| Field | Your answer |
|---|---|
| Label agreement (Agree / Acceptable-not-preferred / Disagree) |  |
| Preferred treatment (if disagree) |  |
| Note sufficiency (Yes / Partial / No) |  |
| Confidence (1–3) |  |
| Case complexity (Easy / Moderate / Complex) |  |
| Comments |  |

---

## Case 30

**Stage:** IIIB  |  **Histology:** adenocarcinoma

### Clinical Note

**HPI:**
This is a 72-year-old with a history of smoking (quit over one year ago) who presents for an initial medical oncology consultation for a new diagnosis of non-small cell lung cancer. The patient was in their usual state of health until approximately two months prior to presentation, when they began to develop a persistent, non-productive cough and progressive exertional dyspnea. This was associated with mild fatigue and an unintentional weight loss of approximately 10 pounds over the preceding three months. These symptoms prompted a visit to their primary care provider, who ordered a chest radiograph that revealed a right upper lobe opacity and mediastinal fullness, prompting further diagnostic evaluation. The patient reports a good performance status (ECOG 1), remaining ambulatory and capable of all self-care, but is limited in strenuous activity by dyspnea.

**Diagnostic Workup:**
A contrast-enhanced CT of the chest, abdomen, and pelvis was performed, which confirmed the presence of a 4.5 cm spiculated mass in the right upper lobe. The scan also demonstrated extensive mediastinal and right-sided supraclavicular lymphadenopathy, with the largest conglomerate of nodes in the subcarinal region measuring up to 3.8 cm. No suspicious hepatic, adrenal, or osseous lesions were identified.

To complete staging, a PET/CT scan was obtained. This demonstrated intense FDG-avidity in the primary right upper lobe mass and in the extensive mediastinal and supraclavicular nodal stations, consistent with the CT findings. Importantly, the PET scan did not reveal any evidence of FDG-avid disease elsewhere, confirming the absence of distant metastases. A staging MRI of the brain was also performed and was negative for any intracranial metastatic disease.

The patient subsequently underwent bronchoscopy with endobronchial ultrasound (EBUS) for tissue diagnosis and pathologic staging. A fine-needle aspiration (FNA) was performed on a subcarinal lymph node (station 7). Pathology from this specimen confirmed the diagnosis of non-small cell lung cancer with adenocarcinoma histology.

Based on the combination of a primary tumor with extensive contralateral mediastinal and supraclavicular nodal involvement (T2bN3M0), the patient is diagnosed with AJCC Stage IIIB disease.

**Molecular Studies:**
Comprehensive next-generation sequencing was performed on the tumor tissue obtained from the EBUS-FNA. No actionable driver alteration was identified; testing was negative for mutations or fusions involving EGFR, ALK, ROS1, BRAF, MET exon 14, RET, KRAS, and ERBB2. Consistent with the standard of care at the time of tissue acquisition, PD-L1 immunohistochemistry was not performed. Tumor mutational burden (TMB) analysis was completed and was found to be high, at >16 mutations/megabase.

**Problem Summary:**
In summary, this is a 72-year-old former smoker with a new diagnosis of treatment-naive, locally advanced, unresectable Stage IIIB non-small cell lung cancer, adenocarcinoma subtype. The disease is characterized by a high tumor mutational burden (TMB) and is negative for common actionable driver mutations. Staging workup is complete and confirms no evidence of distant metastatic disease. The patient is here for initial consultation to discuss the diagnosis in detail.

### Proposed Ground Truth

**Recommended treatment:** concurrent chemoradiation + durvalumab (consolidation)

**Also NCCN-acceptable:** concurrent chemoradiation + durvalumab (consolidation)

### Your Assessment

| Field | Your answer |
|---|---|
| Label agreement (Agree / Acceptable-not-preferred / Disagree) |  |
| Preferred treatment (if disagree) |  |
| Note sufficiency (Yes / Partial / No) |  |
| Confidence (1–3) |  |
| Case complexity (Easy / Moderate / Complex) |  |
| Comments |  |

---

## Case 31

**Stage:** IV  |  **Histology:** adenocarcinoma

### Clinical Note

**INITIAL MEDICAL ONCOLOGY CONSULTATION**

**Patient Name:** [De-identified]
**MRN:** [De-identified]
**Date of Consultation:** [De-identified]

**HISTORY OF PRESENT ILLNESS**
This is a 46-year-old individual referred for evaluation and management of newly diagnosed metastatic non-small cell lung cancer.

The patient was in their usual state of good health until approximately one month prior to presentation, when they began experiencing intermittent, dull headaches and occasional episodes of blurred vision. These symptoms gradually increased in frequency and severity, prompting a visit to an outside emergency department. An initial CT of the head was performed, which was suspicious for intracranial pathology. This was followed by a brain MRI that confirmed the presence of multiple lesions.

Given the imaging findings concerning for metastatic disease, a search for a primary malignancy was initiated. A contrast-enhanced CT of the chest, abdomen, and pelvis was performed, which revealed a primary mass in the right lung. The patient subsequently underwent a CT-guided biopsy of this lung mass, which established the diagnosis.

The patient reports some mild fatigue but is otherwise asymptomatic from a pulmonary standpoint, with no cough, dyspnea, or chest pain. They have had no significant weight loss. They remain fully ambulatory and engaged in all activities of daily living. Performance status is excellent, ECOG 1. The patient is a lifetime never-smoker.

**DIAGNOSTIC WORKUP**
**Brain MRI with and without contrast ([De-identified Date]):** Revealed multiple, well-circumscribed, enhancing lesions within the bilateral cerebral hemispheres, consistent with metastatic deposits.

**CT of Chest, Abdomen, and Pelvis with contrast ([De-identified Date]):** Identified a 3.2 cm spiculated mass in the right upper lobe. Several enlarged mediastinal lymph nodes were also noted. No suspicious metastatic lesions were identified in the liver, adrenal glands, or osseous structures within the field of view.

**CT-guided Core Needle Biopsy, Right Upper Lobe Mass ([De-identified Date]):** Pathologic examination of the tissue specimen revealed invasive adenocarcinoma. Immunohistochemical staining was positive for TTF-1 and Napsin-A, supporting a lung primary origin.

**AJCC Staging (8th Edition):** Stage IV non-small cell lung cancer.

**MOLECULAR STUDIES**
Next-generation sequencing (NGS) was performed on the tumor tissue obtained from the lung biopsy.
- **Actionable driver mutation:** An **ALK gene rearrangement** was detected.
- **Other markers:** The tumor was found to be negative for pathogenic alterations in EGFR, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2.
- **PD-L1 Expression:** Testing was not performed.
- **Tumor Mutational Burden (TMB):** Low (<2 mutations/megabase).

**PROBLEM SUMMARY**
This is a 46-year-old never-smoker with a new diagnosis of Stage IV non-small cell lung cancer, adenocarcinoma histology. Staging studies confirmed a primary right upper lobe lung mass with metastatic disease to the brain. Comprehensive molecular profiling of the tumor is notable for the presence of an ALK gene rearrangement. The patient is treatment-naive and presents for initial oncology consultation.

### Proposed Ground Truth

**Recommended treatment:** alectinib

**Also NCCN-acceptable:** alectinib; brigatinib; lorlatinib

### Your Assessment

| Field | Your answer |
|---|---|
| Label agreement (Agree / Acceptable-not-preferred / Disagree) |  |
| Preferred treatment (if disagree) |  |
| Note sufficiency (Yes / Partial / No) |  |
| Confidence (1–3) |  |
| Case complexity (Easy / Moderate / Complex) |  |
| Comments |  |

---

## Case 32

**Stage:** IIIB  |  **Histology:** adenocarcinoma

### Clinical Note

**HPI:**
This is a 71-year-old with a history of tobacco use (former smoker, quit over one year ago) who presents for an initial medical oncology consultation to discuss management of a new diagnosis of non-small cell lung cancer. The patient was in their usual state of health until approximately two months prior to presentation, when they developed a persistent, non-productive cough and progressive dyspnea on exertion. This was initially attributed to a respiratory infection, but symptoms persisted despite a course of antibiotics. Due to worsening shortness of breath and new-onset right-sided chest discomfort, a chest X-ray was obtained, which revealed a large right upper lobe opacity. The patient was subsequently referred for further diagnostic evaluation. The patient is here today to understand the diagnosis and discuss the implications of the findings. The patient maintains a good functional status, able to perform all activities of daily living without significant limitation.

**Diagnostic Workup:**
A contrast-enhanced CT of the chest, abdomen, and pelvis was performed on [De-identified], which demonstrated a 5.8 cm spiculated mass in the right upper lobe. The mass was associated with extensive ipsilateral mediastinal and right supraclavicular lymphadenopathy, with the largest node measuring 3.2 cm in the right paratracheal station. No suspicious hepatic, adrenal, or osseous lesions were identified.

A PET/CT was subsequently performed for staging on [De-identified]. This confirmed intense FDG-avidity in the primary right upper lobe mass (SUVmax 14.2) and in the extensive mediastinal and supraclavicular nodal stations, consistent with the chest CT findings. Importantly, the PET/CT did not demonstrate any evidence of distant metastatic disease.

A brain MRI with and without contrast was completed for central nervous system staging on [De-identified] and was negative for intracranial metastases.

An endobronchial ultrasound (EBUS) with fine-needle aspiration of a subcarinal lymph node was performed by Pulmonology on [De-identified]. Pathology from this procedure confirmed metastatic adenocarcinoma, consistent with a lung primary.

Based on this comprehensive workup, the patient is diagnosed with AJCC Stage IIIB non-small cell lung cancer.

**Molecular Studies:**
Tissue from the EBUS biopsy was sent for next-generation sequencing. Molecular profiling did not identify any actionable driver alterations. Specifically, the tumor was negative for mutations or rearrangements in EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2.

Immunohistochemistry for PD-L1 was negative (Tumor Proportion Score <1%). Tumor Mutational Burden (TMB) was assessed and found to be high at >16 mutations/megabase.

**Problem Summary:**
In summary, this is a 71-year-old with a new diagnosis of treatment-naive, non-metastatic, unresectable Stage IIIB non-small cell lung cancer, adenocarcinoma histology. The patient has a good performance status. Molecular testing reveals no targetable driver mutations, a PD-L1 expression of <1%, and a high Tumor Mutational Burden.

### Proposed Ground Truth

**Recommended treatment:** concurrent chemoradiation + durvalumab (consolidation)

**Also NCCN-acceptable:** concurrent chemoradiation + durvalumab (consolidation)

### Your Assessment

| Field | Your answer |
|---|---|
| Label agreement (Agree / Acceptable-not-preferred / Disagree) |  |
| Preferred treatment (if disagree) |  |
| Note sufficiency (Yes / Partial / No) |  |
| Confidence (1–3) |  |
| Case complexity (Easy / Moderate / Complex) |  |
| Comments |  |

---

## Case 33

**Stage:** IV  |  **Histology:** adenocarcinoma

### Clinical Note

**HPI:**
This is a 77-year-old individual with a history of smoking who presents for an initial oncology consultation regarding a new diagnosis of metastatic non-small cell lung cancer. The patient was in their usual state of health until approximately two months prior to presentation, when they began to develop a persistent, non-productive cough and progressive dyspnea on exertion. This was associated with generalized fatigue and an unintentional weight loss of approximately 15 pounds over the past three months. More recently, the patient noted the onset of intermittent headaches and a dull ache in the right hip, which prompted a visit to their primary care physician.

An initial chest radiograph revealed a suspicious opacity in the right upper lung field. This led to a staging CT scan of the chest, abdomen, and pelvis, which confirmed the presence of a large right upper lobe mass with associated mediastinal and supraclavicular lymphadenopathy. The scan also identified multiple suspicious osseous lesions. Given the report of headaches, a brain MRI was obtained, which demonstrated evidence of intracranial metastases. The patient subsequently underwent a CT-guided core needle biopsy of the lung mass, which established the diagnosis of adenocarcinoma. The patient is currently treatment-naive. They remain ambulatory and are managing self-care but are limited in more strenuous activities. ECOG performance status is 1.

**Past Medical History:**
- Melanoma, diagnosed [De-identified Year], treated with wide local excision. No known recurrence.
- Hypertension

**Social History:**
- Former smoker with a significant pack-year history, quit over one year ago.

**Diagnostic Workup:**
- **CT Chest/Abdomen/Pelvis with contrast ([De-identified Date]):** Revealed a 4.8 cm spiculated mass in the right upper lobe. Extensive mediastinal and right supraclavicular lymphadenopathy was noted. Multiple lytic and blastic lesions were identified in the thoracic spine and right iliac bone, consistent with metastatic disease.
- **MRI Brain with and without contrast ([De-identified Date]):** Demonstrated three enhancing lesions in the cerebral and cerebellar hemispheres consistent with metastases, the largest measuring 1.2 cm. There was minimal surrounding vasogenic edema.
- **Pathology ([De-identified Date]):** CT-guided core biopsy of the right lung mass confirmed invasive, poorly differentiated adenocarcinoma.

**Molecular Studies:**
Next-generation sequencing performed on the tumor tissue revealed the following:
- **Actionable Driver:** KRAS G12C mutation detected.
- **Other Markers:** Negative for pathogenic mutations or rearrangements in EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, and ERBB2.
- **PD-L1 Immunohistochemistry:** Negative (Tumor Proportion Score < 1%).
- **Tumor Mutational Burden (TMB):** Intermediate (9 mutations/Mb).

**Problem Summary:**
1.  Metastatic Non-Small Cell Lung Cancer (NSCLC), Adenocarcinoma histology.
2.  AJCC Clinical Stage IV, with metastases to brain, bone, and distant lymph nodes.
3.  Molecular profile notable for a KRAS G12C mutation.
4.  PD-L1 negative, Tumor Mutational Burden (TMB) intermediate.
5.  ECOG Performance Status 1.
6.  History of resected melanoma.

### Proposed Ground Truth

**Recommended treatment:** carboplatin + pemetrexed + pembrolizumab

**Also NCCN-acceptable:** carboplatin + pemetrexed + pembrolizumab; carboplatin + pemetrexed + atezolizumab + bevacizumab; pembrolizumab; testing_first

### Your Assessment

| Field | Your answer |
|---|---|
| Label agreement (Agree / Acceptable-not-preferred / Disagree) |  |
| Preferred treatment (if disagree) |  |
| Note sufficiency (Yes / Partial / No) |  |
| Confidence (1–3) |  |
| Case complexity (Easy / Moderate / Complex) |  |
| Comments |  |

---

## Case 34

**Stage:** IV  |  **Histology:** squamous

### Clinical Note

INITIAL MEDICAL ONCOLOGY CONSULTATION

**Patient Name:** [De-identified]
**MRN:** [De-identified]
**Date of Service:** [De-identified]
**Referring Provider:** [De-identified]

**History of Present Illness:**
This is a 61-year-old who presents for initial oncology consultation regarding a new diagnosis of non-small cell lung cancer. The patient was in their usual state of good health until approximately two months prior to presentation, when they developed a persistent, non-productive cough and progressive exertional dyspnea. An initial evaluation with their primary care provider led to a chest radiograph which revealed a right-sided lung mass. The patient is a lifetime never-smoker and maintains an excellent performance status, continuing with daily activities without significant limitation.

**Diagnostic Workup:**
Following the abnormal chest X-ray, a contrast-enhanced CT of the chest, abdomen, and pelvis was obtained for staging. This imaging confirmed a large primary mass in the right lung. The scan also revealed multiple suspicious nodules in the contralateral (left) lung and nodular pleural thickening, concerning for metastatic disease. A subsequent PET/CT scan demonstrated intense FDG-avidity in the primary right lung mass, the contralateral lung nodules, and in the pleura, confirming the suspicion of widespread disease. A staging MRI of the brain was performed and was negative for any evidence of intracranial metastases.

To establish a tissue diagnosis, the patient underwent a CT-guided core needle biopsy of the primary right lung mass. The procedure was well-tolerated. Pathology from this specimen confirmed a diagnosis of poorly differentiated squamous cell carcinoma.

Based on the combination of imaging and pathology, the patient is diagnosed with AJCC Stage IV disease.

**Molecular Studies:**
Next-generation sequencing (NGS) was performed on the tumor tissue to evaluate for targetable mutations. No actionable driver alteration was identified. The tumor was found to be negative for mutations or fusions involving EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2.

Immunohistochemistry for PD-L1 expression was positive, with a Tumor Proportion Score (TPS) in the 1–49% range. The Tumor Mutational Burden (TMB) was determined to be intermediate (2–16 mutations/megabase).

**Problem Summary:**
In summary, this is a 61-year-old never-smoker with a new diagnosis of Stage IV non-small cell lung cancer, squamous cell histology. Staging studies confirm metastatic disease involving the contralateral lung and the pleura, without evidence of brain metastases. Molecular profiling is notable for the absence of any identified actionable driver mutations and a PD-L1 TPS of 1-49%. The patient has an excellent performance status and is treatment-naive.

### Proposed Ground Truth

**Recommended treatment:** carboplatin + paclitaxel + pembrolizumab

**Also NCCN-acceptable:** carboplatin + paclitaxel + pembrolizumab; carboplatin + nab-paclitaxel + pembrolizumab

### Your Assessment

| Field | Your answer |
|---|---|
| Label agreement (Agree / Acceptable-not-preferred / Disagree) |  |
| Preferred treatment (if disagree) |  |
| Note sufficiency (Yes / Partial / No) |  |
| Confidence (1–3) |  |
| Case complexity (Easy / Moderate / Complex) |  |
| Comments |  |

---

## Case 35

**Stage:** IV  |  **Histology:** adenocarcinoma

### Clinical Note

**HPI:**
This is an 80-year-old individual who presents for an initial oncology consultation. The patient was in a usual state of good health until approximately six weeks ago, when they began to experience a persistent, non-productive cough and progressive fatigue. These symptoms prompted a visit to their primary care provider. The patient reports a mild decrease in appetite but denies significant weight loss, hemoptysis, or chest pain. Performance status is excellent; the patient remains fully ambulatory and independent with all activities of daily living. Notably, there is no history of tobacco use.

**Diagnostic Workup:**
An initial chest X-ray revealed a right-sided pulmonary opacity, leading to further evaluation with a CT of the chest, abdomen, and pelvis with intravenous contrast. This study confirmed the presence of a 4 cm spiculated mass in the right upper lobe with associated mediastinal adenopathy. The scan also identified multiple hypoattenuating lesions throughout the liver, consistent with metastatic deposits. A subsequent MRI of the brain was performed for staging and showed no evidence of intracranial metastases.

To establish a tissue diagnosis, the patient underwent a CT-guided core needle biopsy of a dominant liver lesion. Pathological analysis of the specimen confirmed metastatic adenocarcinoma. The immunohistochemical staining profile was consistent with a lung primary origin.

**Molecular Studies:**
Next-generation sequencing (NGS) was performed on the tumor tissue.
- An actionable RET fusion was identified.
- Tumor mutational burden (TMB) was intermediate (2–16 mut/Mb).
- A loss-of-function mutation was detected in the KEAP1 gene.
- The panel was negative for alterations in EGFR, ALK, ROS1, BRAF, MET exon 14, NTRK, KRAS, and ERBB2.
- PD-L1 expression was not tested.

**Problem Summary:**
In summary, this is an 80-year-old never-smoker with a new diagnosis of Stage IV non-small cell lung cancer, adenocarcinoma histology, with metastases to the liver. Molecular profiling is notable for a RET fusion and a co-occurring KEAP1 loss-of-function mutation. The patient is treatment-naive and presents today to discuss the diagnosis and potential management options.

### Proposed Ground Truth

**Recommended treatment:** selpercatinib

**Also NCCN-acceptable:** selpercatinib; pralsetinib

### Your Assessment

| Field | Your answer |
|---|---|
| Label agreement (Agree / Acceptable-not-preferred / Disagree) |  |
| Preferred treatment (if disagree) |  |
| Note sufficiency (Yes / Partial / No) |  |
| Confidence (1–3) |  |
| Case complexity (Easy / Moderate / Complex) |  |
| Comments |  |

---

## Case 36

**Stage:** IA  |  **Histology:** squamous

### Clinical Note

**HPI:**
This is a 64-year-old who presents for initial oncology consultation for a new diagnosis of non-small cell lung cancer. The patient was asymptomatic and the diagnosis was made after a lung nodule was incidentally discovered on imaging performed for an unrelated reason. The patient denies cough, dyspnea, hemoptysis, chest pain, or constitutional symptoms such as fevers or unintentional weight loss. The patient is a former smoker with a significant pack-year history, having quit less than one year ago. Performance status is excellent; the patient is fully active and continues to work and engage in all usual activities without restriction (ECOG 0).

**Diagnostic Workup:**
A chest CT performed on [De-identified Date] revealed a 2.4 cm solid, spiculated nodule in the periphery of the right upper lobe. There was no associated mediastinal or hilar lymphadenopathy.

For purposes of staging, a PET/CT was performed on [De-identified Date]. This demonstrated intense FDG avidity isolated to the right upper lobe pulmonary nodule, consistent with the known malignancy. Crucially, there was no evidence of FDG-avid disease in the mediastinal lymph nodes or at any distant sites.

A staging brain MRI with and without contrast was performed on [De-identified Date] and was negative for any evidence of intracranial metastases.

A CT-guided core needle biopsy of the right upper lobe nodule was performed on [De-identified Date]. The pathology returned as squamous cell carcinoma.

**Molecular Studies:**
Next-generation sequencing was performed on the tumor biopsy specimen. No actionable driver alteration was identified on the molecular profiling panel, with results negative for EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2. PD-L1 expression was not tested. Tumor Mutational Burden (TMB) was reported as intermediate (2–16 mut/Mb).

**Problem Summary:**
In summary, this is a 64-year-old with an excellent performance status who is treatment-naive and presents with a new diagnosis of clinical Stage IA (cT1bN0M0) non-small cell lung cancer of squamous cell histology, localized to the right upper lobe. Molecular testing did not reveal any targetable driver mutations. The patient is here today to discuss the diagnosis and establish care.

### Proposed Ground Truth

**Recommended treatment:** lung-sparing resection (segmentectomy preferred) or wedge

**Also NCCN-acceptable:** lung-sparing resection (segmentectomy preferred) or wedge; lobectomy + mediastinal lymph node dissection/sampling

### Your Assessment

| Field | Your answer |
|---|---|
| Label agreement (Agree / Acceptable-not-preferred / Disagree) |  |
| Preferred treatment (if disagree) |  |
| Note sufficiency (Yes / Partial / No) |  |
| Confidence (1–3) |  |
| Case complexity (Easy / Moderate / Complex) |  |
| Comments |  |

---

## Case 37

**Stage:** IV  |  **Histology:** adenocarcinoma

### Clinical Note

**HPI:**
This is an initial oncology consultation for a 68-year-old former smoker who presents for evaluation of newly diagnosed metastatic non-small cell lung cancer. The patient was in their usual state of health until approximately two months prior to presentation, when they developed a persistent, dry cough. This was associated with mild fatigue and an unintentional 10-pound weight loss over the preceding three months. They were evaluated by their primary care provider, and an initial chest X-ray revealed a right-sided lung mass, which prompted referral for further diagnostic workup. The patient has a remote smoking history but quit over a decade ago. They maintain an excellent performance status (ECOG 0), with no significant comorbidities.

**Diagnostic Workup:**
Following the abnormal chest X-ray, a staging CT of the chest, abdomen, and pelvis with contrast was performed on [De-identified Date]. This imaging confirmed a 4.8 cm spiculated mass in the right upper lobe. The scan also demonstrated a 1.5 cm nodule in the contralateral left lower lobe and a 2.1 cm enhancing nodule in the left adrenal gland, both highly suspicious for metastatic disease.

A subsequent PET/CT scan on [De-identified Date] demonstrated intense FDG-avidity in the primary right upper lobe mass, the contralateral lung nodule, and the left adrenal nodule. No other sites of FDG-avid disease were identified. A staging MRI of the brain with and without contrast was performed and was negative for intracranial metastases.

On [De-identified Date], the patient underwent a CT-guided core needle biopsy of the right upper lobe lung mass. Pathologic analysis of the tissue confirmed the diagnosis.

**Molecular Studies:**
Pathology from the lung biopsy confirmed poorly differentiated adenocarcinoma. Comprehensive next-generation sequencing (NGS) was performed on the tumor tissue.
- **Actionable driver mutation:** A KRAS G12C mutation was detected.
- **Negative markers:** The panel was negative for other common driver mutations, including EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, and ERBB2.
- **PD-L1 Expression:** Immunohistochemistry for PD-L1 showed a Tumor Proportion Score (TPS) of 35% (in the 1-49% range).
- **Tumor Mutational Burden (TMB):** TMB was intermediate at 12 mutations/megabase.

**Problem Summary:**
In summary, this is a 68-year-old individual with a new diagnosis of Stage IV non-small cell lung adenocarcinoma, metastatic to the contralateral lung and left adrenal gland. Staging imaging of the brain is negative for metastatic disease. The patient is treatment-naive with an excellent performance status. Molecular profiling of the tumor is notable for a KRAS G12C mutation and a PD-L1 TPS of 35%. The patient is here today to discuss the diagnosis and establish care.

### Proposed Ground Truth

**Recommended treatment:** carboplatin + pemetrexed + pembrolizumab

**Also NCCN-acceptable:** carboplatin + pemetrexed + pembrolizumab; carboplatin + pemetrexed + atezolizumab + bevacizumab

### Your Assessment

| Field | Your answer |
|---|---|
| Label agreement (Agree / Acceptable-not-preferred / Disagree) |  |
| Preferred treatment (if disagree) |  |
| Note sufficiency (Yes / Partial / No) |  |
| Confidence (1–3) |  |
| Case complexity (Easy / Moderate / Complex) |  |
| Comments |  |

---

## Case 38

**Stage:** IV  |  **Histology:** adenocarcinoma

### Clinical Note

**HISTORY OF PRESENT ILLNESS:**
This is a 67-year-old individual with a history of smoking (quit >1 year ago) who presents for initial oncology consultation to discuss a new diagnosis of metastatic non-small cell lung cancer. The patient was in their usual state of health until approximately two months prior to presentation, when they developed a persistent, non-productive cough and new-onset, nagging mid-back pain. The pain was initially managed with over-the-counter analgesics with minimal relief. Due to the persistence of symptoms, the patient presented to their primary care provider.

An initial chest X-ray revealed a right-sided lung opacity, prompting a follow-up CT scan of the chest. This study confirmed a spiculated mass in the right upper lobe and also noted a suspicious lytic lesion in the thoracic spine. The patient has remained ambulatory and is managing activities of daily living, though is limited by the back pain. They report a mild decrease in appetite but deny significant weight loss, fevers, or night sweats. Performance status is good, estimated at ECOG 1. The patient is here today to establish care and discuss the findings of the diagnostic workup.

**DIAGNOSTIC WORKUP:**
Staging evaluation has been completed.

**Imaging:**
A PET/CT scan performed on [De-identified Date] demonstrated a hypermetabolic 4.5 cm mass in the right upper lobe. There was associated FDG-avid mediastinal lymphadenopathy. Distant metastatic disease was identified, most notably a focus of intense FDG uptake corresponding to a lytic lesion in the T8 vertebral body. No other sites of distant metastatic disease were identified in the chest, abdomen, or pelvis. An MRI of the brain with and without contrast was performed and was negative for intracranial metastases.

**Pathology:**
A CT-guided core needle biopsy of the right upper lobe lung mass was performed on [De-identified Date]. Histopathologic examination confirmed invasive adenocarcinoma, consistent with a lung primary.

**MOLECULAR STUDIES:**
Next-generation sequencing and immunohistochemistry were performed on the tumor tissue. No actionable driver alteration was identified; testing was negative for mutations or rearrangements in EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2.

Immunohistochemistry for PD-L1 was strongly positive, with a Tumor Proportion Score (TPS) of ≥50%.

Tumor Mutational Burden (TMB) was found to be intermediate (2–16 mut/Mb).

**PROBLEM SUMMARY:**
This is a 67-year-old former smoker presenting with a new diagnosis of metastatic lung cancer. The key findings are:
1.  **Metastatic Non-Small Cell Lung Cancer (NSCLC), Adenocarcinoma Histology.**
2.  **AJCC Stage IV disease**, based on a primary right upper lobe lung tumor with metastatic disease to bone.
3.  **Molecular Profile:** Notable for high PD-L1 expression (TPS ≥50%) with no identified actionable driver mutations.

### Proposed Ground Truth

**Recommended treatment:** pembrolizumab

**Also NCCN-acceptable:** pembrolizumab; carboplatin + pemetrexed + pembrolizumab

### Your Assessment

| Field | Your answer |
|---|---|
| Label agreement (Agree / Acceptable-not-preferred / Disagree) |  |
| Preferred treatment (if disagree) |  |
| Note sufficiency (Yes / Partial / No) |  |
| Confidence (1–3) |  |
| Case complexity (Easy / Moderate / Complex) |  |
| Comments |  |

---

## Case 39

**Stage:** IV  |  **Histology:** adenocarcinoma

### Clinical Note

**HPI:**
This is a 73-year-old individual with a history of smoking (quit >1 year ago) who presents for initial medical oncology consultation regarding a new diagnosis of non-small cell lung cancer. The patient initially presented to their primary care provider several weeks ago with a persistent non-productive cough, progressive dyspnea on exertion, and new-onset headaches. Due to the constellation of symptoms, the patient was sent for imaging. The patient reports increasing fatigue but remains ambulatory and able to perform most activities of daily living.

**Diagnostic Workup:**
An initial chest CT scan revealed a large primary mass in the right upper lobe, accompanied by malignant-appearing pleural thickening and a moderate right-sided pleural effusion. The scan also incidentally noted suspicious lytic lesions in the thoracic spine and a rib, concerning for osseous metastases.

Given the presenting complaint of headaches, a contrast-enhanced MRI of the brain was performed. This study confirmed the presence of multiple intraparenchymal metastatic deposits.

To establish a tissue diagnosis, the patient underwent a CT-guided core needle biopsy of the right upper lobe lung mass at [De-identified] Hospital on [De-identified Date]. Pathologic analysis of the specimen confirmed a diagnosis of lung adenocarcinoma.

The cumulative findings from imaging and pathology are consistent with Stage IV non-small cell lung cancer with metastases to the brain, bone, and pleura.

**Molecular Studies:**
Next-generation sequencing (NGS) was performed on the tumor tissue obtained from the biopsy. An actionable driver mutation was detected, specifically a MET exon 14 skipping mutation. Testing was negative for alterations in EGFR, ALK, ROS1, BRAF, RET, NTRK, KRAS, and ERBB2.

Immunohistochemistry for PD-L1 expression was also performed, which showed a Tumor Proportion Score (TPS) of ≥50%. Tumor Mutational Burden (TMB) was reported as intermediate (2–16 mut/Mb).

**Problem Summary:**
In summary, this is a 73-year-old former smoker with a new diagnosis of treatment-naive, Stage IV non-small cell lung adenocarcinoma with metastatic disease involving the brain, bone, and pleura. Molecular profiling is notable for a MET exon 14 skipping mutation and high PD-L1 expression (TPS ≥50%).

### Proposed Ground Truth

**Recommended treatment:** capmatinib

**Also NCCN-acceptable:** capmatinib; tepotinib

### Your Assessment

| Field | Your answer |
|---|---|
| Label agreement (Agree / Acceptable-not-preferred / Disagree) |  |
| Preferred treatment (if disagree) |  |
| Note sufficiency (Yes / Partial / No) |  |
| Confidence (1–3) |  |
| Case complexity (Easy / Moderate / Complex) |  |
| Comments |  |

---

## Case 40

**Stage:** IV  |  **Histology:** adenocarcinoma

### Clinical Note

**MEDICAL ONCOLOGY INITIAL CONSULTATION**

**Patient:** [De-identified]
**MRN:** [De-identified]
**Date of Consultation:** [De-identified]

**HISTORY OF PRESENT ILLNESS:**
This is a 70-year-old individual with a history of smoking (quit >1 year ago) who presents for an initial medical oncology consultation for a new diagnosis of metastatic non-small cell lung cancer.

The patient was in their usual state of health until approximately two months prior to presentation, when they developed a persistent, non-productive cough and progressive dyspnea on exertion. This was initially attributed to a seasonal illness, but symptoms worsened, accompanied by new-onset right-sided chest wall pain and an unintentional 10-pound weight loss. They presented to an outside emergency department for evaluation.

Initial workup included a chest X-ray which revealed a large right-sided lung mass and a pleural effusion. A subsequent contrast-enhanced CT of the chest, abdomen, and pelvis was performed for staging purposes. The patient has since undergone a diagnostic biopsy. They report manageable pain with over-the-counter analgesics and fatigue, but are otherwise able to perform all activities of daily living with some effort. Their ECOG performance status is 1.

**DIAGNOSTIC WORKUP:**
**Imaging:**
- Staging CT of the chest, abdomen, and pelvis revealed a large, spiculated 5.8 cm mass in the right upper lobe. There was evidence of widespread metastatic disease, including multiple bilateral pulmonary nodules in the contralateral lung, a moderate-to-large right-sided malignant pleural effusion, and extensive mediastinal and supraclavicular lymphadenopathy. The scan also demonstrated multiple lytic and blastic osseous lesions consistent with skeletal metastases. An indeterminate lesion was noted in the left adrenal gland, suspicious for an additional site of metastasis.
- A dedicated MRI of the brain with and without contrast was performed as part of the staging workup and was negative for intracranial metastases.

**Pathology:**
- A CT-guided core needle biopsy of the right upper lobe lung mass was performed.
- Histopathologic examination confirmed the diagnosis of invasive adenocarcinoma, consistent with a primary lung origin.

Based on the findings of a primary lung mass with metastases to the contralateral lung, pleura, distant lymph nodes, and bone, the patient is diagnosed with Stage IV non-small cell lung cancer (NSCLC).

**MOLECULAR STUDIES:**
Next-generation sequencing (NGS) was performed on the tumor biopsy specimen.
- No actionable driver alterations were identified. The tumor was negative for mutations or fusions involving EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2.
- PD-L1 expression analysis was not performed.
- Tumor Mutational Burden (TMB) was reported as intermediate (2–16 mutations/megabase).

**PROBLEM SUMMARY:**
In summary, this is a 70-year-old former smoker presenting with a new diagnosis of Stage IV non-small cell lung cancer, adenocarcinoma subtype. The diagnostic workup has confirmed widespread metastatic disease involving the contralateral lung, pleura, bone, and distant lymph nodes, with no evidence of central nervous system involvement. Molecular profiling of the tumor is notable for an intermediate tumor mutational burden and the absence of any identified actionable driver mutations. The case is discussed in detail with the patient.

### Proposed Ground Truth

**Recommended treatment:** carboplatin + pemetrexed + pembrolizumab

**Also NCCN-acceptable:** carboplatin + pemetrexed + pembrolizumab; carboplatin + pemetrexed + atezolizumab + bevacizumab; pembrolizumab; testing_first

### Your Assessment

| Field | Your answer |
|---|---|
| Label agreement (Agree / Acceptable-not-preferred / Disagree) |  |
| Preferred treatment (if disagree) |  |
| Note sufficiency (Yes / Partial / No) |  |
| Confidence (1–3) |  |
| Case complexity (Easy / Moderate / Complex) |  |
| Comments |  |

---

## Case 41

**Stage:** IV  |  **Histology:** adenocarcinoma

### Clinical Note

**HPI:**
This is an initial oncology consultation for a 65-year-old with a new diagnosis of metastatic non-small cell lung cancer. The patient was in their usual state of good health until approximately two months prior to presentation, when they developed a persistent, dry cough and progressive dyspnea on exertion. An initial evaluation with their primary care provider included a chest X-ray which revealed a right-sided pulmonary opacity. The patient is a lifetime never-smoker. Past medical history is significant for a remote history of breast cancer and melanoma, both treated with local modalities and with no evidence of recurrence. The patient maintains a good performance status (ECOG 1), continuing with most daily activities but is limited in strenuous activity by respiratory symptoms.

**Diagnostic Workup:**
Following the abnormal chest X-ray, a contrast-enhanced CT of the chest, abdomen, and pelvis was performed. This demonstrated a 4.2 cm spiculated mass in the right upper lobe with associated mediastinal and hilar lymphadenopathy. Multiple hepatic lesions were also identified, the largest being a 2.5 cm lesion in the right hepatic lobe, consistent with metastatic disease. A dedicated MRI of the brain with contrast was subsequently performed and was negative for any intracranial metastases.

The patient underwent a CT-guided core needle biopsy of the right upper lobe lung mass. Histopathologic analysis confirmed poorly differentiated non-small cell lung cancer, with an immunoprofile consistent with adenocarcinoma. The diagnosis is therefore Stage IV NSCLC.

**Molecular Studies:**
Next-generation sequencing performed on the tumor tissue revealed the following:
-   **Actionable driver detected:** EGFR exon 20 insertion
-   **Negative for pathogenic alterations in:** ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, ERBB2
-   **Tumor Mutational Burden (TMB):** Intermediate (2–16 mut/Mb)
-   **PD-L1:** Not tested

**Problem Summary:**
This is a 65-year-old, treatment-naive patient with a new diagnosis of Stage IV non-small cell lung cancer, adenocarcinoma histology. The patient is a never-smoker, and molecular profiling of the tumor is notable for the presence of an EGFR exon 20 insertion.

### Proposed Ground Truth

**Recommended treatment:** amivantamab + carboplatin + pemetrexed

**Also NCCN-acceptable:** amivantamab + carboplatin + pemetrexed

### Your Assessment

| Field | Your answer |
|---|---|
| Label agreement (Agree / Acceptable-not-preferred / Disagree) |  |
| Preferred treatment (if disagree) |  |
| Note sufficiency (Yes / Partial / No) |  |
| Confidence (1–3) |  |
| Case complexity (Easy / Moderate / Complex) |  |
| Comments |  |

---

## Case 42

**Stage:** IIIA  |  **Histology:** adenocarcinoma

### Clinical Note

INITIAL MEDICAL ONCOLOGY CONSULTATION

Patient Name: [De-identified]
MRN: [De-identified]
Date of Service: [De-identified]

**History of Present Illness:**
This is a 70-year-old who presents for an initial oncology consultation for a new diagnosis of non-small cell lung cancer. The patient was in a usual state of health until approximately two months prior to presentation, when they developed a persistent, non-productive cough and mild exertional dyspnea. Initial evaluation with a primary care provider led to a course of antibiotics without improvement. Given the persistence of symptoms and a history as a former smoker (having quit within the past year), a chest X-ray was obtained which revealed a right-sided pulmonary opacity. This prompted further investigation with cross-sectional imaging. The patient is otherwise active and independent with daily activities.

**Diagnostic Workup:**
A contrast-enhanced CT of the chest confirmed the presence of a 4.5 cm spiculated mass in the right upper lobe. The scan also demonstrated enlarged ipsilateral mediastinal and hilar lymph nodes, concerning for locoregional involvement.

A subsequent PET/CT scan was performed for staging purposes. This study showed intense FDG-avidity corresponding to the known right upper lobe primary mass as well as in multiple ipsilateral mediastinal lymph node stations. Importantly, there was no evidence of FDG-avid disease in the contralateral hemithorax, or at any distant sites in the abdomen, pelvis, or skeleton to suggest metastatic disease.

A CT-guided core needle biopsy of the right upper lobe mass was performed. Pathology from this specimen confirmed the diagnosis of non-small cell lung cancer, with features consistent with adenocarcinoma histology.

To complete staging, a contrast-enhanced MRI of the brain was obtained and was negative for any evidence of intracranial metastases.

**Molecular Studies:**
Next-generation sequencing was performed on the tumor tissue obtained from the lung biopsy.
-   An actionable driver mutation was identified: an EGFR uncommon sensitizing mutation.
-   Testing was negative for mutations or rearrangements in ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2.
-   Tumor Mutational Burden (TMB) was reported as intermediate (2–16 mut/Mb).
-   PD-L1 expression was not tested, as this was not standard practice at the time of tissue acquisition.

**Problem Summary:**
In summary, this is a 70-year-old former smoker with a new diagnosis of treatment-naive, non-metastatic Stage IIIA (AJCC 8th Edition) non-small cell lung adenocarcinoma of the right upper lobe. The tumor is characterized by an uncommon sensitizing EGFR mutation. The patient maintains a good performance status and is here today to discuss the diagnosis.

### Proposed Ground Truth

**Recommended treatment:** concurrent chemoradiation + durvalumab (consolidation)

**Also NCCN-acceptable:** concurrent chemoradiation + durvalumab (consolidation)

### Your Assessment

| Field | Your answer |
|---|---|
| Label agreement (Agree / Acceptable-not-preferred / Disagree) |  |
| Preferred treatment (if disagree) |  |
| Note sufficiency (Yes / Partial / No) |  |
| Confidence (1–3) |  |
| Case complexity (Easy / Moderate / Complex) |  |
| Comments |  |

---

## Case 43

**Stage:** IIIB  |  **Histology:** adenocarcinoma

### Clinical Note

**HPI:**
This is a 69-year-old who presents for initial oncology consultation for a new diagnosis of non-small cell lung cancer. The patient was in their usual state of health until approximately two months prior, when they developed a persistent dry cough and progressive shortness of breath with exertion. These symptoms did not resolve with a course of antibiotics. Due to the persistence of symptoms, a chest X-ray was performed, which demonstrated a right-sided lung mass. The patient is a former smoker, having quit more than one year ago. Performance status is good, though symptoms have become more limiting over the past several weeks. The patient is here today to discuss the diagnosis and establish care.

**Diagnostic Workup:**
Following the abnormal chest X-ray, a staging contrast-enhanced CT of the chest, abdomen, and pelvis was performed. This identified a 5 cm mass in the right upper lobe with extensive ipsilateral mediastinal and hilar lymphadenopathy. A subsequent PET/CT scan confirmed high FDG avidity in the primary right lung mass as well as in multiple mediastinal lymph node stations, consistent with locoregional nodal involvement. Critically, there was no evidence of distant metastatic disease on the PET/CT. A dedicated MRI of the brain was also performed and was negative for intracranial metastases.

A CT-guided core needle biopsy of the right upper lobe mass was performed on [De-identified]. Pathological review of the specimen confirmed invasive, poorly differentiated adenocarcinoma of the lung. Based on the combination of imaging and pathology, the patient carries a diagnosis of AJCC Stage IIIB non-small cell lung cancer.

**Molecular Studies:**
Next-generation sequencing was performed on the tumor tissue. No actionable driver alterations were identified; testing was negative for mutations or rearrangements involving EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2.

Immunohistochemistry for PD-L1 was negative, with a Tumor Proportion Score (TPS) of <1%. Tumor Mutational Burden (TMB) was determined to be intermediate (2–16 mutations/megabase). The molecular report also noted the presence of a loss-of-function mutation in STK11 as well as a loss-of-function mutation in KEAP1.

**Problem Summary:**
This is a 69-year-old with a new diagnosis of treatment-naive, non-metastatic Stage IIIB non-small cell lung cancer of adenocarcinoma histology. Molecular profiling is notable for PD-L1 negative disease (TPS <1%) with the presence of STK11 and KEAP1 loss-of-function mutations, and an absence of other targetable driver alterations. The patient presents for initial consultation to discuss the diagnosis and review potential management strategies.

### Proposed Ground Truth

**Recommended treatment:** concurrent chemoradiation + durvalumab (consolidation)

**Also NCCN-acceptable:** concurrent chemoradiation + durvalumab (consolidation)

### Your Assessment

| Field | Your answer |
|---|---|
| Label agreement (Agree / Acceptable-not-preferred / Disagree) |  |
| Preferred treatment (if disagree) |  |
| Note sufficiency (Yes / Partial / No) |  |
| Confidence (1–3) |  |
| Case complexity (Easy / Moderate / Complex) |  |
| Comments |  |

---

## Case 44

**Stage:** IV  |  **Histology:** adenocarcinoma

### Clinical Note

**REASON FOR VISIT:** Initial consultation for a new diagnosis of non-small cell lung cancer.
**MRN:** [De-identified]
**DATE OF VISIT:** [De-identified]

**HISTORY OF PRESENT ILLNESS:**
This is a 67-year-old former smoker (quit >1 year ago) who presents for an initial oncology evaluation following a new diagnosis of non-small cell lung cancer.

The patient was in their usual state of health until approximately three months prior to presentation, when they developed a persistent, dry cough. Over the subsequent weeks, they also noted the onset of new, persistent mid-thoracic back pain, which was unrelated to exertion. This prompted an evaluation with their primary care provider. An initial chest X-ray was obtained which demonstrated a right upper lobe opacity.

The patient was subsequently referred for further diagnostic imaging.

**DIAGNOSTIC WORKUP:**
A contrast-enhanced CT of the chest, abdomen, and pelvis was performed. This study confirmed the presence of a 3.5 cm spiculated mass in the right upper lobe of the lung with associated mediastinal lymphadenopathy. The scan also identified a destructive lytic lesion within the T7 vertebral body, suspicious for a metastasis.

For definitive staging, a PET/CT scan was obtained. This demonstrated intense FDG-avidity corresponding to the right upper lobe lung mass, several mediastinal lymph nodes, and the lytic lesion in the T7 vertebra. No other distant hypermetabolic sites were identified. A dedicated MRI of the brain was performed as part of the staging workup and was negative for intracranial metastases.

A CT-guided core needle biopsy of the right upper lobe lung mass was performed. Pathology from this procedure confirmed the diagnosis of invasive adenocarcinoma, consistent with a primary lung malignancy.

The combined findings are consistent with Stage IV disease. The patient has an ECOG performance status of 1.

**MOLECULAR STUDIES:**
Tumor tissue from the lung biopsy was sent for next-generation sequencing to assess for targetable alterations.
- No actionable driver alteration was identified.
- The tumor was negative for mutations or fusions involving EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2.
- Tumor Mutational Burden (TMB) was reported as intermediate (2–16 mut/Mb).
- PD-L1 expression was not tested on this specimen.

**PROBLEM SUMMARY:**
In summary, this is a 67-year-old individual with a new diagnosis of Stage IV non-small cell lung cancer, adenocarcinoma histology, with metastatic disease to bone. Molecular profiling is notable for an absence of an actionable oncogenic driver mutation and intermediate tumor mutational burden. The patient is treatment-naive and is seen today for initial consultation and discussion.

### Proposed Ground Truth

**Recommended treatment:** carboplatin + pemetrexed + pembrolizumab

**Also NCCN-acceptable:** carboplatin + pemetrexed + pembrolizumab; carboplatin + pemetrexed + atezolizumab + bevacizumab; pembrolizumab; testing_first

### Your Assessment

| Field | Your answer |
|---|---|
| Label agreement (Agree / Acceptable-not-preferred / Disagree) |  |
| Preferred treatment (if disagree) |  |
| Note sufficiency (Yes / Partial / No) |  |
| Confidence (1–3) |  |
| Case complexity (Easy / Moderate / Complex) |  |
| Comments |  |

---

## Case 45

**Stage:** IV  |  **Histology:** adenocarcinoma

### Clinical Note

**HPI:**
This is a 58-year-old individual referred for initial oncology consultation regarding a new diagnosis of metastatic non-small cell lung cancer. The patient was in their usual state of health until approximately two months prior to presentation, when they developed a persistent, non-productive cough and new-onset, nagging pain in the upper back. The symptoms did not resolve with conservative measures, prompting an evaluation with their primary care provider.

An initial chest radiograph revealed a right upper lobe opacity, leading to a follow-up contrast-enhanced CT of the chest, abdomen, and pelvis. This study confirmed the presence of a large mass in the right upper lobe with extensive mediastinal lymphadenopathy. Critically, the scan also identified multiple lytic lesions in the thoracic spine and ribs, as well as an enlarged left supraclavicular lymph node, concerning for metastatic disease. The patient reports the back pain has been manageable with non-prescription analgesics but is constant. They note mild fatigue but otherwise maintain a good performance status, continuing with all activities of daily living. The patient is a lifetime never-smoker.

**Diagnostic Workup:**
A PET/CT scan performed on [De-identified] confirmed a hypermetabolic primary mass in the right upper lobe measuring approximately 5 cm, with intense FDG uptake in right hilar and mediastinal lymph nodes. Widespread metastatic disease was confirmed, with avid uptake corresponding to the known osseous lesions in the thoracic spine and in a left supraclavicular lymph node, confirming M1 disease. A contrast-enhanced MRI of the brain was performed and was negative for intracranial metastases.

The patient subsequently underwent a CT-guided core needle biopsy of the right lung mass. Pathology review confirmed invasive adenocarcinoma, consistent with a primary lung malignancy.

**Molecular Studies:**
Next-generation sequencing performed on the tumor tissue revealed the following:
- Actionable driver mutations: EGFR exon 19 deletion (sensitizing) and high-level MET amplification.
- Negative for pathogenic alterations in: ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2.
- PD-L1 expression was not tested.
- Tumor Mutational Burden (TMB) was intermediate (2–16 mut/Mb).

**Problem Summary:**
Newly diagnosed, treatment-naive Stage IV non-small cell lung cancer, adenocarcinoma histology, with bone and distant lymph node metastases. The tumor is characterized by an EGFR exon 19 deletion and high-level MET amplification.

### Proposed Ground Truth

**Recommended treatment:** osimertinib

**Also NCCN-acceptable:** osimertinib; osimertinib + carboplatin + pemetrexed; amivantamab + lazertinib

### Your Assessment

| Field | Your answer |
|---|---|
| Label agreement (Agree / Acceptable-not-preferred / Disagree) |  |
| Preferred treatment (if disagree) |  |
| Note sufficiency (Yes / Partial / No) |  |
| Confidence (1–3) |  |
| Case complexity (Easy / Moderate / Complex) |  |
| Comments |  |

---

## Case 46

**Stage:** IV  |  **Histology:** adenocarcinoma

### Clinical Note

INITIAL MEDICAL ONCOLOGY CONSULTATION
Patient Name: [De-identified]
MRN: [De-identified]
Date of Service: [De-identified]
Referring Provider: [De-identified]

**History of Present Illness:**
This is a 63-year-old who presents for an initial medical oncology consultation regarding a new diagnosis of metastatic non-small cell lung cancer. The patient has a history of a persistent, non-productive cough for approximately three months, which was initially attributed to seasonal allergies. Over the past month, the patient developed worsening fatigue, a 15-pound unintentional weight loss, and new-onset right upper quadrant abdominal discomfort. This prompted an evaluation with a primary care provider.

The patient is a former smoker, having quit over one year ago after a significant pack-year history. Current performance status is ECOG 1; the patient is fully ambulatory and capable of all self-care but is restricted in physically strenuous activity. Review of systems is otherwise notable for decreased appetite but negative for fevers, chills, shortness of breath at rest, or hemoptysis.

**Diagnostic Workup:**
The initial workup began with a chest radiograph which revealed a large right upper lobe mass. This was followed by a contrast-enhanced CT of the chest, abdomen, and pelvis. Imaging demonstrated a 5.2 cm speculated mass in the right upper lobe with associated mediastinal lymphadenopathy. Additionally, multiple hypoattenuating lesions were identified throughout the liver, the largest measuring 3.4 cm, and a 2.1 cm left adrenal nodule, all suspicious for metastatic disease.

A subsequent whole-body PET/CT scan was performed for staging. This confirmed intense FDG-avidity in the primary right upper lobe lung mass and mediastinal nodes. It further demonstrated multiple hypermetabolic metastatic lesions in the liver, the left adrenal gland, and several osseous sites, including the T7 vertebral body and the right iliac crest. An MRI of the brain with and without contrast was performed as part of the standard staging workup and was negative for intracranial metastases.

A CT-guided core needle biopsy of the right upper lobe lung mass was performed. Pathology confirmed the diagnosis of adenocarcinoma, consistent with a lung primary.

**Molecular Studies:**
Next-generation sequencing (NGS) was performed on the tumor tissue.
- **Actionable Driver Mutation:** An activating ERBB2 (HER2) exon 20 insertion was detected.
- **Other Drivers:** The tumor was negative for mutations or rearrangements in EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, and KRAS.
- **Immunohistochemistry:** PD-L1 expression was negative.
- **Tumor Mutational Burden (TMB):** TMB was determined to be intermediate (2–16 mut/Mb).

**Problem Summary:**
In summary, this is a 63-year-old with a new diagnosis of Stage IV non-small cell lung cancer, adenocarcinoma histology, with metastatic disease to the bone, liver, and adrenal gland. The patient is treatment-naive. Molecular profiling of the tumor is notable for an activating ERBB2 exon 20 insertion mutation and negative PD-L1 expression. The patient presents for initial evaluation and discussion of the diagnosis.

### Proposed Ground Truth

**Recommended treatment:** carboplatin + pemetrexed + pembrolizumab

**Also NCCN-acceptable:** carboplatin + pemetrexed + pembrolizumab; carboplatin + pemetrexed + atezolizumab + bevacizumab; pembrolizumab; testing_first

### Your Assessment

| Field | Your answer |
|---|---|
| Label agreement (Agree / Acceptable-not-preferred / Disagree) |  |
| Preferred treatment (if disagree) |  |
| Note sufficiency (Yes / Partial / No) |  |
| Confidence (1–3) |  |
| Case complexity (Easy / Moderate / Complex) |  |
| Comments |  |

---

## Case 47

**Stage:** IA  |  **Histology:** adenocarcinoma

### Clinical Note

**HPI:**
This is an initial consultation for a 59-year-old with a new diagnosis of non-small cell lung cancer. The patient is a lifetime never-smoker and was in their usual state of good health until approximately two months ago when they developed a mild, persistent, non-productive cough. This prompted a visit to their primary care provider, who obtained a chest X-ray revealing a right upper lobe opacity. The patient was otherwise asymptomatic, denying fever, chills, weight loss, hemoptysis, or chest pain. They maintain an excellent performance status, fully active and able to carry on all pre-illness activities without restriction (ECOG 0). Following the abnormal chest X-ray, further diagnostic evaluation was pursued, leading to the current referral to medical oncology for discussion of management.

**Diagnostic Workup:**
A CT scan of the chest confirmed the presence of a 1.9 cm spiculated solid nodule in the right upper lobe. There was no evidence of mediastinal, hilar, or supraclavicular lymphadenopathy.

A subsequent PET/CT scan was performed for staging purposes. This demonstrated intense FDG avidity within the known 1.9 cm right upper lobe nodule. Importantly, there was no evidence of FDG-avid lymphadenopathy in the mediastinum or hila, and no findings concerning for distant metastatic disease in the chest, abdomen, or pelvis.

A staging MRI of the brain was performed and was negative for any evidence of intracranial metastatic disease.

The patient underwent a CT-guided core needle biopsy of the right upper lobe pulmonary nodule. Pathology from this procedure confirmed a diagnosis of lung adenocarcinoma.

**Molecular Studies:**
Next-generation sequencing (NGS) was performed on the tumor tissue.
- An activating EGFR point mutation, L858R, was detected.
- Further molecular testing was negative for ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2 rearrangements or mutations.
- PD-L1 expression by immunohistochemistry (IHC) was positive, with a Tumor Proportion Score (TPS) in the 1–49% range.
- Tumor Mutational Burden (TMB) was found to be intermediate (2–16 mut/Mb).

**Problem Summary:**
This is a 59-year-old never-smoker who presents for initial consultation regarding a new diagnosis of treatment-naive, non-metastatic non-small cell lung cancer. The diagnosis is specifically a Stage IA (T1b N0 M0) lung adenocarcinoma, confirmed by a comprehensive staging workup that was negative for nodal or distant metastatic disease. The patient has an excellent performance status. Molecular analysis of the tumor is notable for a sensitizing EGFR L858R mutation and PD-L1 expression of 1-49%.

### Proposed Ground Truth

**Recommended treatment:** lung-sparing resection (segmentectomy preferred) or wedge

**Also NCCN-acceptable:** lung-sparing resection (segmentectomy preferred) or wedge; lobectomy + mediastinal lymph node dissection/sampling

### Your Assessment

| Field | Your answer |
|---|---|
| Label agreement (Agree / Acceptable-not-preferred / Disagree) |  |
| Preferred treatment (if disagree) |  |
| Note sufficiency (Yes / Partial / No) |  |
| Confidence (1–3) |  |
| Case complexity (Easy / Moderate / Complex) |  |
| Comments |  |

---

## Case 48

**Stage:** IIA  |  **Histology:** adenocarcinoma

### Clinical Note

**HPI:**
This is a 56-year-old individual with a history of former tobacco use (quit >1 year ago) who is referred for an initial medical oncology consultation regarding a new diagnosis of non-small cell lung cancer. The patient initially presented to an outside provider several weeks ago with a persistent, non-productive cough. An initial chest X-ray was concerning for a lung mass, which prompted further investigation. The patient is otherwise feeling well, reporting good energy levels and no significant weight loss, shortness of breath, or chest pain at present. Performance status is excellent, consistent with an ECOG of 0.

**Diagnostic Workup:**
Following the abnormal chest X-ray, a contrast-enhanced CT of the chest, abdomen, and pelvis was performed. This confirmed the presence of a spiculated mass in the right upper lobe. There was no evidence of mediastinal or hilar lymphadenopathy, nor were there any suspicious lesions in the visualized portions of the liver, adrenal glands, or bones.

To establish a tissue diagnosis, a CT-guided core needle biopsy of the right upper lobe mass was performed on [De-identified Date]. Pathologic review of the specimen confirmed a diagnosis of adenocarcinoma.

Staging evaluation was completed with a PET/CT scan, which demonstrated intense FDG-avidity localized to the primary right upper lobe tumor. The scan did not show any evidence of regional nodal involvement or distant metastatic disease. A dedicated MRI of the brain with and without contrast was also performed and was negative for intracranial metastases.

Collectively, this workup is consistent with non-metastatic, clinical Stage IIA non-small cell lung cancer.

**Molecular Studies:**
Next-generation sequencing (NGS) was performed on the tumor biopsy tissue to assess for targetable alterations. No actionable driver mutations were identified; testing was negative for alterations in EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2.

Immunohistochemistry for PD-L1 expression was positive, with a Tumor Proportion Score (TPS) in the 1-49% range. The Tumor Mutational Burden (TMB) was reported as intermediate (2–16 mut/Mb). The molecular report also noted the presence of an STK11 loss-of-function mutation.

**Problem Summary:**
This is a 56-year-old, treatment-naive individual with newly diagnosed, non-metastatic Stage IIA non-small cell lung cancer of adenocarcinoma histology. Molecular profiling is notable for the absence of common driver mutations, a PD-L1 TPS of 1-49%, and the presence of an STK11 loss-of-function mutation. The patient has an excellent performance status and is seen today for initial consultation to discuss the diagnosis.

### Proposed Ground Truth

**Recommended treatment:** lobectomy + mediastinal lymph node dissection/sampling

**Also NCCN-acceptable:** lobectomy + mediastinal lymph node dissection/sampling; neoadjuvant nivolumab + platinum-doublet chemotherapy (CheckMate 816) then surgery; perioperative pembrolizumab + chemotherapy (KEYNOTE-671): neoadjuvant pembrolizumab + chemo → surgery → adjuvant pembrolizumab; perioperative durvalumab + chemotherapy (AEGEAN): neoadjuvant → surgery → adjuvant durvalumab

### Your Assessment

| Field | Your answer |
|---|---|
| Label agreement (Agree / Acceptable-not-preferred / Disagree) |  |
| Preferred treatment (if disagree) |  |
| Note sufficiency (Yes / Partial / No) |  |
| Confidence (1–3) |  |
| Case complexity (Easy / Moderate / Complex) |  |
| Comments |  |

---

## Case 49

**Stage:** IV  |  **Histology:** adenocarcinoma

### Clinical Note

**HPI:**
This is a 37-year-old individual with a history of being a never-smoker, referred for initial medical oncology consultation regarding a new diagnosis of metastatic non-small cell lung cancer. The patient was in their usual state of good health until approximately two months prior to presentation, when they developed a persistent, non-productive cough and progressive right-sided pleuritic chest pain. Symptoms were initially attributed to a musculoskeletal strain. Over the subsequent weeks, the patient noted increasing fatigue, an unintentional weight loss of approximately 10 pounds, and new-onset dull pain in the mid-back. Due to worsening shortness of breath on exertion, the patient presented to an outside emergency department for evaluation.

**Diagnostic Workup:**
Initial workup in the emergency department included a chest X-ray which demonstrated a right-sided lung mass and a moderate pleural effusion. A subsequent contrast-enhanced CT of the chest, abdomen, and pelvis was performed for staging on [De-identified Date]. This study confirmed the presence of a spiculated mass in the right lower lobe, measuring approximately 5.2 cm. The scan revealed extensive metastatic disease, including multiple nodular densities in the contralateral (left) lung, several hypodense lesions throughout the liver consistent with metastases, and multiple lytic osseous lesions in the thoracic spine and ribs. A significant right-sided malignant pleural effusion was also noted.

A dedicated MRI of the brain with and without contrast was performed and showed no evidence of intracranial metastases.

On [De-identified Date], the patient underwent a CT-guided core needle biopsy of the primary right lung mass. The procedure was uncomplicated. Histopathologic examination of the tissue confirmed a diagnosis of poorly differentiated adenocarcinoma, with features consistent with a lung primary.

**Molecular Studies:**
Tumor tissue from the core biopsy was sent for comprehensive next-generation sequencing. The key findings are as follows:
-   **Actionable Driver Mutation:** An **NTRK fusion** was detected.
-   **Negative for other drivers:** The panel was explicitly negative for alterations in **EGFR, ALK, ROS1, BRAF, MET exon 14, RET, KRAS, and ERBB2**.
-   **Tumor Mutational Burden (TMB):** TMB was reported as **intermediate (2–16 mut/Mb)**.
-   **PD-L1 Expression:** PD-L1 immunohistochemistry was **not tested** on this specimen, consistent with the standard practice for the panel utilized (pre-2017).

**Problem Summary:**
In summary, this is a 37-year-old never-smoker presenting for initial oncologic evaluation of a newly diagnosed, treatment-naive, **Stage IV non-small cell lung cancer (NSCLC), adenocarcinoma histology**. Staging studies demonstrate widespread metastatic disease involving the bone, liver, contralateral lung, and pleura. Comprehensive molecular profiling of the tumor is notable for the identification of an actionable NTRK fusion. The patient has a good performance status and is here today to discuss the diagnosis and establish care.

### Proposed Ground Truth

**Recommended treatment:** larotrectinib

**Also NCCN-acceptable:** larotrectinib; entrectinib

### Your Assessment

| Field | Your answer |
|---|---|
| Label agreement (Agree / Acceptable-not-preferred / Disagree) |  |
| Preferred treatment (if disagree) |  |
| Note sufficiency (Yes / Partial / No) |  |
| Confidence (1–3) |  |
| Case complexity (Easy / Moderate / Complex) |  |
| Comments |  |

---

## Case 50

**Stage:** IIIB  |  **Histology:** adenocarcinoma

### Clinical Note

**History of Present Illness**

This is a 56-year-old individual with a history of smoking (quit >1 year ago) who presents for initial medical oncology consultation for a new diagnosis of non-small cell lung cancer. The patient was in their usual state of health until approximately two months prior to this evaluation, at which time they began to experience a persistent, dry cough and progressive shortness of breath with exertion. These symptoms prompted a visit to their primary care provider.

The initial workup included a chest X-ray which revealed a right-sided lung mass. The patient reports feeling fatigued but remains fully ambulatory and able to perform all activities of daily living, corresponding to an ECOG performance status of 1.

**Diagnostic Workup**

Following the abnormal chest X-ray, a diagnostic CT scan of the chest, abdomen, and pelvis with intravenous contrast was performed on [De-identified date]. This study characterized a 4.5 cm spiculated mass in the right upper lobe. It also demonstrated extensive and bulky mediastinal and right hilar lymphadenopathy. Notably, an enlarged contralateral supraclavicular lymph node was identified. No suspicious lesions were noted in the liver, adrenal glands, or other visceral organs.

To complete staging, a whole-body PET/CT scan was obtained. This showed intense FDG-avidity in the primary right upper lobe mass, as well as in the extensive mediastinal, hilar, and contralateral supraclavicular nodal stations, consistent with the CT findings. Crucially, no FDG-avid lesions suggestive of distant metastatic disease were identified. A subsequent MRI of the brain with and without contrast was also performed and was negative for any evidence of intracranial metastases.

To establish a tissue diagnosis, the patient underwent bronchoscopy with endobronchial ultrasound (EBUS)-guided fine-needle aspiration of a subcarinal lymph node. The pathology from this procedure confirmed the diagnosis.

**Molecular Studies**

Pathology from the EBUS-guided biopsy of the mediastinal lymph node was consistent with adenocarcinoma of the lung. The tissue specimen was sent for next-generation sequencing for comprehensive molecular profiling.

This analysis did not identify any actionable driver alterations. Specific testing was negative for mutations or rearrangements in EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2. Tumor mutational burden (TMB) was reported as intermediate (2–16 mut/Mb). PD-L1 immunohistochemistry was not performed on the specimen, as this was not yet standard of care at the time of the initial diagnosis.

**Problem Summary**

In summary, this is a 56-year-old former smoker who presents with a new diagnosis of Stage IIIB (cT2bN3M0) non-small cell lung adenocarcinoma. The diagnosis was confirmed via EBUS-guided biopsy of a mediastinal lymph node. A comprehensive staging workup, including PET/CT and brain MRI, has confirmed locoregionally advanced disease confined to the chest and supraclavicular region, with no evidence of distant metastatic spread. Molecular analysis of the tumor is notable for the absence of identified targetable driver mutations. The patient is here today for an initial consultation to discuss the diagnosis and its implications.

### Proposed Ground Truth

**Recommended treatment:** concurrent chemoradiation + durvalumab (consolidation)

**Also NCCN-acceptable:** concurrent chemoradiation + durvalumab (consolidation)

### Your Assessment

| Field | Your answer |
|---|---|
| Label agreement (Agree / Acceptable-not-preferred / Disagree) |  |
| Preferred treatment (if disagree) |  |
| Note sufficiency (Yes / Partial / No) |  |
| Confidence (1–3) |  |
| Case complexity (Easy / Moderate / Complex) |  |
| Comments |  |

---
