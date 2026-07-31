# GENIE BPC NSCLC - Generated Note Review

Total cases: 5
Faithfulness + neutrality PASS: 5/5 (100%)
Cases with soft warnings: 5/5

---

## genie_NSCLC_GENIE-MSK-P-0013483_0  [PASS]

**Structured profile (ground truth):**
- Stage IIIA, adenocarcinoma, brain_mets=False
- EGFR=unknown ALK=unknown ROS1=unknown BRAF=unknown MET=unknown RET=unknown NTRK=unknown PD-L1=unknown
- biomarkers_available=False
- actual_treatment (held out): Crizotinib

**warnings:**
- brain_mets=False but note appears to mention brain metastasis

**Generated note:**
```
**HPI:**
This is a 58-year-old individual with a history of being a never-smoker who presents for an initial medical oncology consultation regarding a new diagnosis of non-small cell lung cancer. The patient was in their usual state of health until approximately two months prior to presentation, when they developed a persistent, non-productive cough and mild shortness of breath with exertion. These symptoms prompted a visit to their primary care provider, which led to an initial chest X-ray that was concerning for a right-sided lung mass. The patient reports good functional status, remaining fully ambulatory and capable of self-care, consistent with an ECOG performance status of 1.

**Diagnostic Workup:**
Following the abnormal chest X-ray, a contrast-enhanced CT of the chest, abdomen, and pelvis was obtained. This study identified a 4.2 cm spiculated mass in the right upper lobe. Additionally, the scan revealed enlarged right paratracheal and subcarinal lymph nodes, raising suspicion for mediastinal nodal involvement. No definitive evidence of distant metastatic disease was identified in the visualized portions of the liver, adrenal glands, or osseous structures.

To complete staging, a whole-body PET/CT scan was performed. This demonstrated high FDG-avidity in the primary right upper lobe mass and in the right paratracheal (4R) and subcarinal (7) nodal stations, confirming suspected locoregional disease. No other sites of abnormal hypermetabolism were seen to suggest distant metastatic disease. A dedicated MRI of the brain with and without contrast was also performed as part of the staging evaluation and was negative for intracranial metastases.

The patient subsequently underwent bronchoscopy with endobronchial ultrasound (EBUS) for tissue diagnosis. A fine-needle aspiration biopsy was performed on the right upper lobe mass and the subcarinal lymph node. Pathology from both sites returned as invasive adenocarcinoma, confirming the diagnosis and the presence of nodal metastasis.

**Molecular Studies:**
Immunohistochemistry for PD-L1 was performed on the biopsy specimen and showed a Tumor Proportion Score (TPS) of 0%, which is considered negative. Tumor Mutational Burden (TMB) was assessed and found to be low at <2 mut/Mb. Tissue has been sent for comprehensive next-generation sequencing, and these results are pending at the time of this consultation.

**Problem Summary:**
In summary, this is a 58-year-old never-smoker with a new diagnosis of treatment-naive, Stage IIIA non-small cell lung cancer, adenocarcinoma histology. The diagnosis was established by EBUS-guided biopsy of a right upper lobe mass and a positive subcarinal lymph node. Staging workup is notable for locoregionally advanced disease without evidence of distant metastases. Initial biomarker analysis is significant for PD-L1 negative and TMB-low disease. The patient is seen today for initial consultation to review these findings.
```

---

## genie_NSCLC_GENIE-MSK-P-0009102_0  [PASS]

**Structured profile (ground truth):**
- Stage IIA, adenocarcinoma, brain_mets=False
- EGFR=negative ALK=positive ROS1=negative BRAF=negative MET=negative RET=negative NTRK=negative PD-L1=unknown
- biomarkers_available=True
- actual_treatment (held out): Cisplatin, Vinorelbine Tartrate

**warnings:**
- brain_mets=False but note appears to mention brain metastasis

**Generated note:**
```
**HPI:**
This is a 75-year-old who presents for an initial medical oncology consultation for a new diagnosis of non-small cell lung cancer. The patient has a history of being a former smoker, having quit over one year ago. The patient was in their usual state of health until approximately three months prior to presentation, when they developed a persistent, non-productive cough. After a course of antibiotics prescribed by their primary care provider failed to resolve the symptoms, a chest X-ray was obtained which showed a right upper lobe opacity. This prompted further diagnostic evaluation. The patient reports mild fatigue but is fully ambulatory and managing all self-care, with an ECOG performance status of 1. They deny fevers, chills, night sweats, or significant unintentional weight loss.

**Diagnostic Workup:**
A contrast-enhanced CT of the chest, abdomen, and pelvis was performed on [De-identified], which confirmed a 4.5 cm spiculated mass in the right upper lobe. There was no evidence of mediastinal or hilar lymphadenopathy. No suspicious lesions were identified in the liver, adrenal glands, or other visualized portions of the abdomen and pelvis.

For staging purposes, a PET/CT was performed on [De-identified]. This demonstrated intense FDG-avidity within the known right upper lobe mass. There was no evidence of hypermetabolic activity in the regional lymph nodes or in any distant sites to suggest metastatic disease. A staging MRI of the brain was also performed and was negative for intracranial metastases.

On [De-identified], the patient underwent a CT-guided core needle biopsy of the right upper lobe mass. Pathological analysis of the tissue confirmed the diagnosis of non-small cell lung cancer with adenocarcinoma histology.

Based on this workup, the patient is diagnosed with AJCC Stage IIA disease.

**Molecular Studies:**
Tissue from the biopsy was sent for next-generation sequencing. The results are as follows:
- Actionable driver mutation detected: ALK rearrangement.
- No pathogenic mutations detected in: EGFR, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, ERBB2.
- PD-L1: Not tested.
- Tumor Mutational Burden (TMB): Low (<2 mut/Mb).

**Problem Summary:**
This is a 75-year-old with an excellent performance status who presents for an initial consultation to discuss a new diagnosis of treatment-naive, non-metastatic Stage IIA non-small cell lung cancer, adenocarcinoma histology. Molecular profiling of the tumor is notable for the presence of an ALK rearrangement.
```

---

## genie_NSCLC_GENIE-MSK-P-0009293_3  [PASS]

**Structured profile (ground truth):**
- Stage IA, adenocarcinoma, brain_mets=False
- EGFR=negative ALK=negative ROS1=negative BRAF=negative MET=negative RET=negative NTRK=negative PD-L1=unknown
- biomarkers_available=True
- actual_treatment (held out): Gemcitabine Hydrochloride, Vinorelbine Tartrate

**warnings:**
- brain_mets=False but note appears to mention brain metastasis

**Generated note:**
```
**HPI:**
This is an initial oncology consultation for a 76-year-old individual referred for a new diagnosis of non-small cell lung cancer. The patient is a former smoker, having quit over a year ago. The patient initially presented to their primary care provider several weeks ago with a mild, persistent, non-productive cough. An initial chest radiograph was performed which revealed a right upper lobe pulmonary nodule, prompting further evaluation. The patient reports a stable energy level and denies fevers, chills, night sweats, or significant unintentional weight loss. Performance status is excellent, ECOG 0.

**Diagnostic Workup:**
Following the abnormal chest X-ray, a contrast-enhanced chest CT was performed on [De-identified]. This confirmed the presence of a 1.9 cm solid, spiculated nodule in the apical segment of the right upper lobe. No other suspicious pulmonary nodules were identified. There was no mediastinal or hilar lymphadenopathy.

For definitive staging, a PET/CT was obtained on [De-identified]. This demonstrated intense FDG avidity corresponding to the right upper lobe nodule (SUVmax 8.1). Importantly, there was no evidence of hypermetabolic activity in any mediastinal or hilar lymph nodes, nor were there any findings concerning for distant metastatic disease in the chest, abdomen, or pelvis.

Given the diagnosis of adenocarcinoma, a brain MRI with and without contrast was performed on [De-identified] to complete staging, which was negative for any intracranial metastases.

On [De-identified], the patient underwent a CT-guided core needle biopsy of the right upper lobe nodule. The procedure was well-tolerated. Pathologic examination of the tissue confirmed the diagnosis of invasive adenocarcinoma.

**Molecular Studies:**
Tumor tissue from the biopsy was sent for comprehensive next-generation sequencing and biomarker analysis.
- **Driver Mutations:** No actionable driver alteration was identified. Testing was negative for mutations or rearrangements in EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2.
- **PD-L1:** Immunohistochemistry for PD-L1 was negative, with a Tumor Proportion Score (TPS) of 0%.
- **Tumor Mutational Burden (TMB):** TMB was found to be high at >16 mutations/megabase.

**Problem Summary:**
In summary, this is a 76-year-old with a new diagnosis of clinical Stage IA (AJCC 8th Edition) non-small cell lung cancer, adenocarcinoma histology, confined to the right upper lobe. Staging workup including PET/CT and brain MRI is negative for regional nodal involvement or distant metastatic disease. Molecular profiling of the tumor demonstrates a high Tumor Mutational Burden (TMB-high) and is negative for PD-L1 expression and common targetable driver mutations.
```

---

## genie_NSCLC_GENIE-MSK-P-0011234_2  [PASS]

**Structured profile (ground truth):**
- Stage IB, adenocarcinoma, brain_mets=False
- EGFR=exon_19_del ALK=negative ROS1=negative BRAF=negative MET=negative RET=negative NTRK=negative PD-L1=unknown
- biomarkers_available=True
- actual_treatment (held out): Carboplatin, Paclitaxel

**warnings:**
- brain_mets=False but note appears to mention brain metastasis

**Generated note:**
```
**HPI:**
This is a 72-year-old individual with a history of being a never-smoker who is seen today in the Thoracic Oncology clinic for an initial consultation regarding a new diagnosis of non-small cell lung cancer. The patient was in their usual state of excellent health and asymptomatic until a lung nodule was incidentally discovered on a chest CT scan performed for a non-pulmonary indication. The patient denies any cough, shortness of breath, hemoptysis, chest pain, or constitutional symptoms such as fevers, chills, or unintentional weight loss. They maintain a very active lifestyle with an ECOG performance status of 0. Following the discovery of the lung mass, the patient was referred for further diagnostic evaluation.

**Diagnostic Workup:**
The initial diagnostic chest CT revealed a 3.2 cm spiculated solid nodule in the superior segment of the right lower lobe. There was no associated mediastinal or hilar lymphadenopathy.

For purposes of staging, a whole-body PET/CT was performed on [De-identified date]. This study demonstrated intense FDG-avidity corresponding to the known right lower lobe primary tumor. Importantly, there was no evidence of FDG-avid disease in any regional lymph node stations or at any distant sites.

To complete staging, a brain MRI with and without contrast was obtained on [De-identified date], which was negative for any evidence of intracranial metastatic disease.

A CT-guided core needle biopsy of the right lower lobe mass was subsequently performed by Interventional Radiology on [De-identified date]. Pathologic review of the tissue specimen confirmed the diagnosis of invasive adenocarcinoma of the lung.

Based on this comprehensive workup, the tumor is a T2aN0M0, corresponding to AJCC 8th Edition Stage IB.

**Molecular Studies:**
Next-generation sequencing (NGS) was performed on the tumor tissue. The results are notable for the detection of an actionable sensitizing EGFR exon 19 deletion.

Further molecular analysis was negative for alterations in ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2.

PD-L1 expression was not tested. Tumor Mutational Burden (TMB) was low (<2 mut/Mb).

**Problem Summary:**
In summary, this is a 72-year-old never-smoker who presents for initial oncologic evaluation of a newly diagnosed, asymptomatic Stage IB (T2aN0M0) pulmonary adenocarcinoma of the right lower lobe. Molecular profiling of the tumor is positive for a sensitizing EGFR exon 19 deletion. The patient has an excellent performance status and is fully active and independent.
```

---

## genie_NSCLC_GENIE-MSK-P-0022777_0  [PASS]

**Structured profile (ground truth):**
- Stage IIIA, adenocarcinoma, brain_mets=False
- EGFR=exon_19_del ALK=negative ROS1=negative BRAF=negative MET=negative RET=negative NTRK=negative PD-L1=intermediate
- biomarkers_available=True
- actual_treatment (held out): Investigational Drug

**warnings:**
- brain_mets=False but note appears to mention brain metastasis

**Generated note:**
```
**HPI:**
This is a 54-year-old individual with a recent diagnosis of non-small cell lung cancer, referred for initial oncology consultation. The patient is treatment-naive. The history was obtained from the patient and a review of available medical records.

The patient was in their usual state of good health until approximately two months prior to presentation, when they developed a persistent, non-productive cough. This was followed by the gradual onset of mild dyspnea with strenuous activity. They initially sought evaluation with their primary care provider, who ordered a chest X-ray which revealed a right upper lobe opacity. The patient was subsequently referred to Pulmonology for further evaluation.

The patient is a lifetime never-smoker. They deny fevers, chills, night sweats, or significant weight loss. They remain fully active and independent in all activities of daily living, with an ECOG performance status of 0.

**Diagnostic Workup:**
A comprehensive staging workup was completed.

- **CT Chest/Abdomen/Pelvis with contrast:** Performed on [De-identified], this revealed a 3.8 cm spiculated mass in the posterior segment of the right upper lobe. There was associated bulky mediastinal and hilar lymphadenopathy, including enlarged subcarinal and right paratracheal nodes, with the largest node measuring 2.5 cm in short-axis dimension. No suspicious lesions were identified in the liver, adrenal glands, or other visualized portions of the abdomen and pelvis.
- **PET/CT:** Performed on [De-identified], this confirmed intense FDG-avidity within the right upper lobe primary mass (SUVmax 14.2) and in multiple ipsilateral mediastinal lymph node stations, including the subcarinal station (SUVmax 9.5). There was no evidence of FDG-avid disease below the diaphragm or elsewhere to suggest distant metastasis.
- **MRI Brain with and without contrast:** Performed on [De-identified], this was negative for intracranial metastatic disease.
- **Bronchoscopy with EBUS-TBNA:** The patient underwent bronchoscopy with endobronchial ultrasound-guided transbronchial needle aspiration of the primary mass and a subcarinal lymph node (station 7) on [De-identified]. Pathology from both sites was consistent with invasive adenocarcinoma of lung origin.

**Molecular Studies:**
Next-generation sequencing and PD-L1 immunohistochemistry were performed on the biopsy tissue. The results are as follows:
- **Actionable driver(s) detected:** EGFR exon 19 deletion (sensitizing)
- **Negative for:** ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, ERBB2
- **PD-L1 TPS:** 1-49%
- **Tumor Mutational Burden (TMB):** Low (<2 mut/Mb)

**Problem Summary:**
In summary, this is a 54-year-old never-smoker with a new diagnosis of treatment-naive, Stage IIIA (cT2aN2M0, AJCC 8th Edition) EGFR-mutated non-small cell lung adenocarcinoma.
```

---
