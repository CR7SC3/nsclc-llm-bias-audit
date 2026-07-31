# GENIE BPC NSCLC - Generated Note Review

Total cases: 50
Faithfulness + neutrality PASS: 48/50 (96%)
Cases with soft warnings: 13/50

---

## genie_NSCLC_GENIE-DFCI-010239_2  [PASS]

**Structured profile (ground truth):**
- Stage IA, adenocarcinoma, brain_mets=False
- EGFR=negative ALK=negative ROS1=negative BRAF=negative MET=negative RET=negative NTRK=negative PD-L1=low
- biomarkers_available=True
- actual_treatment (held out): Carboplatin, Paclitaxel

**Generated note:**
```
**HPI:**
This is a [De-identified] 69-year-old individual who presents for an initial oncology consultation regarding a new diagnosis of non-small cell lung cancer. The patient is a never smoker. The diagnosis was initially suspected following a routine chest X-ray that revealed a suspicious lung nodule. This finding prompted further evaluation with a CT scan of the chest, which identified a 2.5 cm solid nodule in the right upper lobe. The patient reports mild, intermittent cough for the past few weeks, but otherwise denies significant constitutional symptoms, hemoptysis, or dyspnea. Performance status is excellent, ECOG 0.

**Diagnostic Workup:**
Following the CT chest, a CT-guided needle biopsy of the right upper lobe lesion was performed, which confirmed the diagnosis of non-small cell lung cancer, adenocarcinoma histology. Subsequent comprehensive staging workup included a whole-body PET/CT scan and a brain MRI. The PET/CT demonstrated uptake confined to the primary lung lesion, with no evidence of regional lymph node involvement or distant metastatic disease. The brain MRI showed no evidence of intracranial metastases. Based on these findings, the patient is diagnosed with clinical Stage IA non-small cell lung cancer.

**Molecular Studies:**
Molecular profiling of the tumor tissue was performed and revealed no actionable driver alterations, specifically negative for EGFR mutations, ALK rearrangements, ROS1 rearrangements, BRAF V600E mutations, MET exon 14 skipping mutations, RET fusions, NTRK fusions, KRAS mutations, and ERBB2 (HER2) mutations. Programmed death-ligand 1 (PD-L1) expression was negative, with a tumor proportion score (TPS) of <1%. Tumor mutational burden (TMB) was found to be intermediate, ranging from 2-16 mut/Mb.

**Problem Summary:**
[De-identified] is a 69-year-old individual with newly diagnosed, treatment-naive non-small cell lung cancer, adenocarcinoma histology, Stage IA. Staging workup confirms localized disease without evidence of regional lymph node involvement or distant metastases, including no brain metastases. Molecular profiling indicates no targetable driver alterations, negative PD-L1 expression (TPS <1%), and intermediate tumor mutational burden. The patient is here today to discuss management options for this diagnosis.
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
[De-identified] Medical Oncology
Consultation Note

Patient: [De-identified]
DOB: [De-identified]
MRN: [De-identified]
Date of Visit: [De-identified]
Attending: [De-identified]

HISTORY OF PRESENT ILLNESS:
The 72-year-old patient presents for initial oncology consultation following a recent diagnosis of non-small cell lung cancer. The patient initially presented to their primary care physician approximately [De-identified] months ago with a persistent, non-productive cough. A chest X-ray was performed, which revealed a suspicious right upper lobe nodule. This finding prompted further investigation with a CT scan of the chest. The patient reports generally good health prior to this presentation, with no significant weight loss, fevers, chills, or hemoptysis. Performance status is excellent, with the patient maintaining full activity levels and performing all activities of daily living without restriction. The patient is a never smoker.

DIAGNOSTIC WORKUP:
The CT chest performed on [De-identified] revealed a solid, spiculated nodule measuring approximately [De-identified] cm in the right upper lobe, without evidence of significant mediastinal or hilar lymphadenopathy. Subsequent PET/CT scan on [De-identified] demonstrated avid uptake within the right upper lobe lesion, with no evidence of hypermetabolic activity in regional lymph nodes or distant sites. A brain MRI was also performed to exclude intracranial metastatic disease, which was negative.
A CT-guided biopsy of the right upper lobe lesion was performed on [De-identified]. Pathology confirmed adenocarcinoma of the lung.
Based on the comprehensive imaging and pathological findings, the patient is diagnosed with Non-Small Cell Lung Cancer, Adenocarcinoma histology, AJCC Stage IB (cT1b N0 M0).

MOLECULAR STUDIES:
Molecular testing was performed on the tumor biopsy specimen. Results demonstrated an EGFR exon 19 deletion (sensitizing mutation). The tumor was negative for ALK rearrangement, ROS1 rearrangement, BRAF V600E mutation, MET exon 14 skipping mutation, RET fusion, NTRK fusion, KRAS mutation, and ERBB2 amplification. PD-L1 expression was not tested at the time of initial sequencing, consistent with practices prior to [De-identified] (pre-2017 sequencing). Tumor mutational burden (TMB) was reported as low (<2 mut/Mb).

PROBLEM SUMMARY:
This is a 72-year-old patient with newly diagnosed, treatment-naive Non-Small Cell Lung Cancer, Adenocarcinoma histology, AJCC Stage IB (cT1b N0 M0). The patient's tumor harbors an EGFR exon 19 deletion. The patient maintains an excellent performance status. The immediate focus is to discuss treatment options for this localized, molecularly-defined lung cancer.

[De-identified], MD
Medical Oncologist
```

---

## genie_NSCLC_GENIE-MSK-P-0014506_0  [PASS]

**Structured profile (ground truth):**
- Stage IV, adenocarcinoma, brain_mets=False
- EGFR=negative ALK=negative ROS1=positive BRAF=negative MET=negative RET=negative NTRK=negative PD-L1=high
- biomarkers_available=True
- actual_treatment (held out): Bevacizumab, Carboplatin, Pemetrexed Disodium

**Generated note:**
```
[Clinic Name] Medical Oncology Program
[Clinic Address]
Phone: [Phone Number] | Fax: [Fax Number]

Initial Consultation [Date]
Patient: [De-identified Patient Name], 67-year-old
MRN: [De-identified MRN]

**HPI:**
I had the pleasure of seeing a 67-year-old patient in initial consultation today for recently diagnosed non-small cell lung cancer (NSCLC). The patient initially presented several weeks ago with a constellation of symptoms including a persistent, dry cough, progressively worsening dyspnea on exertion, and a reported 10-pound unintentional weight loss over the past two months. These symptoms prompted an evaluation by their primary care physician, which led to a chest X-ray demonstrating a suspicious pulmonary mass. The patient has a medical history notable only for well-controlled hypertension and reports being a never smoker. At the time of this consultation, the patient maintains an ECOG performance status of 1, indicating they are ambulatory and able to carry out light work.

**Diagnostic Workup:**
Following the initial chest X-ray, a comprehensive staging workup was initiated. This included a contrast-enhanced CT scan of the chest, abdomen, and pelvis, which identified a dominant mass in the right upper lobe of the lung. Critically, this imaging also revealed multiple, discrete pulmonary nodules within the contralateral (left) lung, consistent with metastatic disease. Furthermore, a moderate right pleural effusion with associated nodular pleural thickening was noted, along with a solitary, enhancing lesion in the liver, highly suspicious for metastasis. A subsequent whole-body PET/CT scan confirmed these findings, demonstrating intense hypermetabolic activity in the primary right upper lobe mass, the contralateral lung nodules, the pleural lesions, and the hepatic lesion, thereby confirming widespread distant metastatic disease. Based on these findings, the patient was formally diagnosed with AJCC Stage IV NSCLC. Tissue acquisition was performed via CT-guided core needle biopsy of the right upper lobe mass, which histopathologically confirmed adenocarcinoma.

**Molecular Studies:**
Comprehensive genomic profiling was performed on the tumor tissue obtained from the biopsy. The results of this analysis revealed the presence of a ROS1 rearrangement, identifying an actionable driver alteration. Further testing demonstrated that the tumor was negative for other commonly encountered driver mutations, including EGFR, ALK, BRAF, MET exon 14 skipping, RET, NTRK, KRAS, and ERBB2 (HER2) amplifications. Programmed death-ligand 1 (PD-L1) expression was assessed by immunohistochemistry, yielding a tumor proportion score (TPS) of ≥50%. Tumor mutational burden (TMB) analysis indicated an intermediate value, falling within the range of 2 to 16 mutations per megabase (mut/Mb).

**Problem Summary:**
This 67-year-old patient presents as treatment-naive with newly diagnosed AJCC Stage IV non-small cell lung cancer of adenocarcinoma histology. The disease is characterized by a primary right upper lobe mass with metastatic involvement of the contralateral lung, pleura, and liver. The patient maintains an ECOG performance status of 1. Molecular profiling has identified a ROS1 rearrangement, high PD-L1 expression (TPS ≥50%), and intermediate tumor mutational burden.
```

---

## genie_NSCLC_GENIE-MSK-P-0010681_0  [PASS]

**Structured profile (ground truth):**
- Stage IV, nos, brain_mets=False
- EGFR=negative ALK=negative ROS1=negative BRAF=negative MET=negative RET=negative NTRK=negative PD-L1=unknown
- biomarkers_available=True
- actual_treatment (held out): Carboplatin, Pemetrexed Disodium

**Generated note:**
```
**HPI:**
The patient is a 66-year-old individual presenting for initial oncology consultation following a recent diagnosis of non-small cell lung cancer. The patient is a current smoker. Initial symptoms included a persistent cough, exertional dyspnea, and generalized fatigue, which prompted evaluation by their primary care provider. Over the past several weeks, the patient also noted increasing localized pain in the thoracic spine and a newly palpable, non-tender nodule in the left supraclavicular region. These symptoms led to further investigations.

**Diagnostic Workup:**
Initial imaging, including a chest X-ray, revealed a suspicious mass in the right upper lobe of the lung. This was followed by a comprehensive staging workup, including a CT scan of the chest, abdomen, and pelvis, as well as a PET/CT scan. These studies confirmed a primary lung mass in the right upper lobe and demonstrated distant metastatic disease. Specifically, osseous metastases were identified in the thoracic spine, consistent with the patient's reported pain, and a biopsy of the palpable left supraclavicular nodule confirmed it to be a subcutaneous metastasis. A core needle biopsy of the right upper lobe lung mass was performed, which confirmed the diagnosis of non-small cell lung cancer (NSCLC), nos histology. No evidence of brain metastases was identified on dedicated brain imaging. Based on these findings, the patient was diagnosed with AJCC Stage IV NSCLC. The patient maintains a good performance status, with an ECOG PS of 1.

**Molecular Studies:**
Molecular profiling was performed on the tumor tissue. Results indicated no actionable driver alteration, with testing negative for EGFR, ALK, ROS1, BRAF, MET exon 14 skipping, RET fusions, NTRK fusions, KRAS mutations, and ERBB2 (HER2) alterations. PD-L1 expression was not assessed, which is consistent with the pre-2017 sequencing timeframe when this testing was not yet standard of care. Tumor mutational burden (TMB) was reported as intermediate (2–16 mut/Mb).

**Problem Summary:**
This is a 66-year-old current smoker with newly diagnosed, treatment-naive AJCC Stage IV non-small cell lung cancer, nos histology, with metastatic disease involving bone and subcutaneous tissue. Molecular profiling revealed no actionable driver alterations, and TMB was reported as intermediate. PD-L1 status is unknown. The patient is presenting for discussion of systemic therapy options.
```

---

## genie_NSCLC_GENIE-MSK-P-0008261_0  [FAIL]

**Structured profile (ground truth):**
- Stage IV, adenocarcinoma, brain_mets=True
- EGFR=negative ALK=negative ROS1=negative BRAF=negative MET=negative RET=negative NTRK=negative PD-L1=unknown
- biomarkers_available=True
- actual_treatment (held out): Bevacizumab, Carboplatin, Pemetrexed Disodium

**FAILURES:**
- brain_mets=True but no brain metastasis stated

**Generated note:**
```
[De-identified] Patient, 58-year-old
DOB: [De-identified]
MRN: [De-identified]
Date of Service: [De-identified]
Referring Provider: [De-identified]

**History of Present Illness:**
The patient is a 58-year-old who presents for initial oncology evaluation following a recent diagnosis of non-small cell lung cancer (NSCLC). Approximately three months prior to presentation, the patient began experiencing a persistent, dry cough, increasing exertional dyspnea, and significant fatigue. Over the past two months, the patient noted an unintentional weight loss of approximately 15 pounds. More recently, the patient reported intermittent headaches and occasional episodes of dizziness, which prompted further medical attention. The patient is a former smoker, having quit less than one year ago. The patient reports a generally active lifestyle prior to the onset of symptoms and currently maintains a good performance status despite the symptoms.

**Diagnostic Workup:**
Initial evaluation by the primary care physician included a chest X-ray, which revealed a suspicious mass in the right upper lobe. This finding was further characterized by a subsequent CT scan of the chest, abdomen, and pelvis, which identified a 4.0 cm spiculated mass in the right upper lung, suspicious mediastinal lymphadenopathy, and a 2.5 cm nodule in the right adrenal gland. A CT-guided core needle biopsy of the right upper lobe lung mass was performed, confirming adenocarcinoma histology.

To complete staging, a whole-body PET-CT scan was performed, demonstrating intense hypermetabolic activity in the primary right upper lobe lung mass, multiple mediastinal lymph nodes, and the right adrenal gland nodule, consistent with metastatic disease. Due to the patient's reported neurological symptoms, an MRI of the brain with contrast was obtained, which revealed multiple enhancing lesions in the cerebral hemispheres, consistent with metastatic brain disease.

Based on these comprehensive findings, the patient is diagnosed with Stage IV (cT2b N2 M1c) non-small cell lung cancer, adenocarcinoma histology, metastatic to the brain and right adrenal gland.

**Molecular Studies:**
Tumor tissue obtained from the lung biopsy underwent comprehensive genomic profiling. The results identified an actionable driver mutation: KRAS G12C. Further analysis for other common driver mutations was negative, including EGFR, ALK, ROS1, BRAF, MET exon 14 skipping, RET fusions, NTRK fusions, and ERBB2 (HER2) mutations. PD-L1 expression was not assessed, consistent with the pre-2017 sequencing timeframe when this testing was not yet standard of care. Tumor mutational burden (TMB) was reported as intermediate (2-16 mutations/Mb).

**Problem Summary:**
This is a 58-year-old patient with newly diagnosed, treatment-naive Stage IV non-small cell lung cancer, adenocarcinoma histology, metastatic to the brain and right adrenal gland. Molecular profiling revealed an actionable KRAS G12C mutation, with other common driver alterations negative. Tumor mutational burden is intermediate. The patient presents for initial oncology consultation to discuss management strategies.
```

---

## genie_NSCLC_GENIE-MSK-P-0009154_0  [PASS]

**Structured profile (ground truth):**
- Stage IIB, adenocarcinoma, brain_mets=False
- EGFR=unknown ALK=unknown ROS1=unknown BRAF=unknown MET=unknown RET=unknown NTRK=unknown PD-L1=unknown
- biomarkers_available=False
- actual_treatment (held out): Cisplatin, Pemetrexed Disodium

**warnings:**
- brain_mets=False but note appears to mention brain metastasis

**Generated note:**
```
**HPI:** The 48-year-old patient presents for initial oncology evaluation following a recent diagnosis of non-small cell lung cancer. The patient reports a persistent cough and increasing shortness of breath over the past few months, accompanied by some fatigue and unintentional weight loss. The patient is a former smoker, having quit less than one year ago. This visit marks the first oncology consultation following the cancer diagnosis.

**Diagnostic Workup:** Initial evaluation began with a chest X-ray, which revealed a suspicious mass in the lung. This finding prompted a contrast-enhanced CT scan of the chest, abdomen, and pelvis, which confirmed a primary lung lesion and demonstrated regional lymphadenopathy. A CT-guided biopsy of the lung mass was subsequently performed, and histological examination confirmed adenocarcinoma. Further staging with a PET/CT scan demonstrated FDG-avid disease confined to the primary lung tumor and ipsilateral hilar and mediastinal lymph nodes, with no evidence of distant metastatic disease. An MRI of the brain was also performed as part of the staging workup, which was negative for intracranial metastases. Based on these comprehensive findings, the patient is diagnosed with Non-Small Cell Lung Cancer, adenocarcinoma histology, AJCC Stage IIB.

**Molecular Studies:** Comprehensive molecular profiling on the tumor tissue is currently not yet available, with no sequencing panel on record at this time. PD-L1 expression was not tested, consistent with diagnostic practices prior to 2017 when such testing was not yet standard of care. Tumor mutational burden (TMB) was assessed and found to be low (<2 mut/Mb).

**Problem Summary:** The patient is a 48-year-old with newly diagnosed, treatment-naive Non-Small Cell Lung Cancer, adenocarcinoma histology, AJCC Stage IIB. The diagnostic workup confirms locoregional disease without distant metastases. Molecular findings include pending comprehensive profiling, untested PD-L1 expression, and a low tumor mutational burden.
```

---

## genie_NSCLC_GENIE-MSK-P-0025642_0  [PASS]

**Structured profile (ground truth):**
- Stage IV, adenocarcinoma, brain_mets=False
- EGFR=negative ALK=negative ROS1=negative BRAF=negative MET=exon_14 RET=negative NTRK=negative PD-L1=high
- biomarkers_available=True
- actual_treatment (held out): Pembrolizumab

**Generated note:**
```
**DATE:** [De-identified Date]
**PATIENT:** [De-identified Patient]
**MRN:** [De-identified MRN]

**HPI:**
This is a 73-year-old never-smoker presenting for an initial oncology consultation following a recent diagnosis of non-small cell lung cancer. The patient initially presented to their primary care physician approximately two months ago with a persistent cough, increasing fatigue, and recent onset of dull, aching pain in the lower back. A chest X-ray was performed, which revealed a suspicious lung mass. Subsequent imaging and biopsy confirmed the diagnosis and staging. The patient reports an ECOG performance status of 1, able to perform all self-care activities and light work, but unable to perform more strenuous activities. They deny any significant weight loss or hemoptysis.

**Diagnostic Workup:**
Following the initial chest X-ray, a contrast-enhanced CT scan of the chest, abdomen, and pelvis was performed, revealing a primary mass in the right upper lobe of the lung, along with multiple suspicious lesions in the liver, lytic lesions in the lumbar spine, and enlarged mediastinal and supraclavicular lymph nodes. An FDG PET/CT scan was subsequently performed, confirming hypermetabolic activity in the right upper lobe lung mass, multiple liver lesions, several bone lesions in the spine and pelvis, and multiple distant lymph nodes (supraclavicular, retroperitoneal). A brain MRI with contrast was also performed, which showed no evidence of intracranial metastatic disease. A CT-guided biopsy of the right upper lobe lung mass was performed, confirming adenocarcinoma histology. The overall staging, based on these findings, is AJCC Stage IV.

**Molecular Studies:**
Comprehensive genomic profiling was performed on the tumor tissue, revealing the presence of a MET exon 14 skipping mutation, which is considered an actionable driver alteration. The tumor was found to be negative for other common driver mutations, including EGFR, ALK, ROS1, BRAF, RET, NTRK, KRAS, and ERBB2. Immunohistochemistry for PD-L1 expression showed a tumor proportion score (TPS) of ≥50%, indicating high expression. Tumor mutational burden (TMB) analysis reported an intermediate score of 2–16 mutations per megabase (mut/Mb).

**Problem Summary:**
This 73-year-old patient has newly diagnosed, treatment-naive, metastatic non-small cell lung cancer, adenocarcinoma histology, AJCC Stage IV. Metastatic disease involves the bone, liver, and distant lymph nodes, with no evidence of brain metastases. Molecular testing identified an actionable MET exon 14 skipping mutation, high PD-L1 expression (TPS ≥50%), and intermediate tumor mutational burden. The patient presents for discussion of systemic treatment options.
```

---

## genie_NSCLC_GENIE-DFCI-010089_0  [PASS]

**Structured profile (ground truth):**
- Stage IIIB, adenocarcinoma, brain_mets=False
- EGFR=negative ALK=negative ROS1=negative BRAF=negative MET=negative RET=negative NTRK=negative PD-L1=unknown
- biomarkers_available=True
- actual_treatment (held out): Carboplatin, Paclitaxel

**Generated note:**
```
[De-identified]
[De-identified], [De-identified]
[De-identified]

**HPI:**
[De-identified] is a 61-year-old patient presenting for initial oncology consultation regarding a recent diagnosis of non-small cell lung cancer. The patient initially sought medical attention several weeks prior due to the onset of a persistent, non-productive cough and increasing shortness of breath with exertion. They also reported mild, intermittent chest discomfort. The patient has a history of current smoking. Their performance status is estimated at ECOG 1.

**Diagnostic Workup:**
Initial evaluation included a chest X-ray, which identified a suspicious mass in the right upper lobe. This finding prompted further comprehensive imaging, including a contrast-enhanced CT scan of the chest, abdomen, and pelvis. The CT confirmed a primary lung mass measuring approximately 4.8 cm in the right upper lobe, along with prominent mediastinal and hilar lymphadenopathy. There was no radiological evidence of distant metastatic disease in the abdomen or pelvis. A subsequent PET/CT scan demonstrated intense hypermetabolic activity within the primary lung lesion and confirmed uptake in multiple mediastinal lymph nodes, but no other sites of active disease were identified. To further characterize the extent of disease, an MRI of the brain was performed, which revealed no intracranial metastases. A bronchoscopy with endobronchial ultrasound (EBUS) guided biopsy of the mediastinal lymph nodes and a transbronchial biopsy of the lung mass were performed. Pathology confirmed non-small cell lung cancer, specifically adenocarcinoma histology. Based on the comprehensive staging workup, the patient's cancer is classified as AJCC Stage IIIB, reflecting locoregional disease with significant nodal involvement but no distant spread.

**Molecular Studies:**
Molecular profiling was performed on the tumor tissue. The analysis revealed no actionable driver alterations, with specific testing negative for EGFR mutations, ALK rearrangements, ROS1 rearrangements, BRAF mutations, MET exon 14 skipping mutations, RET fusions, NTRK fusions, KRAS mutations, and ERBB2 (HER2) amplification/mutations. PD-L1 expression was not assessed, which is consistent with the sequencing having been performed prior to PD-L1 testing becoming a standard of care biomarker. Tumor mutational burden (TMB) was determined to be intermediate, ranging from 2–16 mutations/megabase (mut/Mb).

**Problem Summary:**
This 61-year-old patient presents with newly diagnosed, treatment-naive non-small cell lung cancer of adenocarcinoma histology, staged as AJCC Stage IIIB. The disease is locoregional, involving mediastinal lymph nodes, without evidence of distant metastasis, including no brain involvement. Molecular testing indicates no actionable driver mutations, intermediate tumor mutational burden, and PD-L1 status is unknown as it was not tested. The patient has a history of current smoking.
```

---

## genie_NSCLC_GENIE-DFCI-112084_0  [PASS]

**Structured profile (ground truth):**
- Stage IIB, adenocarcinoma, brain_mets=False
- EGFR=negative ALK=negative ROS1=negative BRAF=negative MET=negative RET=negative NTRK=negative PD-L1=high
- biomarkers_available=True
- actual_treatment (held out): Carboplatin, Paclitaxel

**Generated note:**
```
**HPI:**
This is a 64-year-old patient presenting for initial oncology consultation regarding a recent diagnosis of non-small cell lung cancer. The patient first experienced a persistent cough and mild exertional dyspnea approximately three months prior to presentation, accompanied by some fatigue and an unintentional weight loss of 8 pounds. These symptoms prompted evaluation by their primary care physician, who ordered a chest X-ray.

**Diagnostic Workup:**
The initial chest X-ray demonstrated a suspicious mass in the right lung. Subsequent contrast-enhanced computed tomography (CT) of the chest confirmed a primary lung mass measuring approximately [e.g., 4.5 cm] in the right upper lobe, along with several enlarged right hilar and mediastinal lymph nodes. A positron emission tomography (PET)/CT scan was performed for comprehensive staging, which showed avid fluorodeoxyglucose (FDG) uptake in the primary right lung mass and the aforementioned regional mediastinal lymph nodes, but no evidence of distant metastatic disease elsewhere in the body. Magnetic resonance imaging (MRI) of the brain was also performed and was negative for intracranial metastases. A bronchoscopy with endobronchial ultrasound-guided transbronchial needle aspiration (EBUS-TBNA) of the lung mass and mediastinal lymph nodes was performed, which confirmed the diagnosis of adenocarcinoma. Based on the imaging and biopsy findings, the patient is staged as AJCC Stage IIB (T2b N1 M0). The patient reports an ECOG Performance Status of 0-1, feeling generally well with minimal limitations to daily activities. The patient has a history of smoking, having quit less than one year ago.

**Molecular Studies:**
Comprehensive genomic profiling was performed on the tumor tissue. Results indicated no actionable driver alterations, specifically negative for EGFR mutations, ALK rearrangements, ROS1 rearrangements, BRAF V600E mutations, MET exon 14 skipping alterations, RET fusions, NTRK fusions, and KRAS mutations, as well as ERBB2 (HER2) alterations. Immunohistochemistry (IHC) for PD-L1 expression demonstrated a Tumor Proportion Score (TPS) of ≥50%. Tumor Mutational Burden (TMB) was reported as intermediate, in the range of 2–16 mutations/megabase (mut/Mb).

**Problem Summary:**
64-year-old patient with newly diagnosed, treatment-naive non-small cell lung cancer, adenocarcinoma histology, AJCC Stage IIB. Diagnostic workup confirms localized disease with regional lymph node involvement and no evidence of distant metastasis, including no brain metastases. Molecular profiling reveals no actionable driver alterations, PD-L1 TPS ≥50%, and intermediate TMB. The patient is a former smoker.
```

---

## genie_NSCLC_GENIE-VICC-203874_0  [PASS]

**Structured profile (ground truth):**
- Stage IB, adenocarcinoma, brain_mets=False
- EGFR=unknown ALK=unknown ROS1=unknown BRAF=unknown MET=unknown RET=unknown NTRK=unknown PD-L1=unknown
- biomarkers_available=False
- actual_treatment (held out): Bevacizumab, Carboplatin, Pemetrexed Disodium

**Generated note:**
```
[De-identified]
[De-identified]
[De-identified]

**HPI:**
This 60-year-old patient presents for an initial oncology consultation regarding a new diagnosis of non-small cell lung cancer (NSCLC). The patient reports a several-month history of a persistent cough, which prompted evaluation by their primary care provider. Initial workup included a chest X-ray, which revealed a suspicious pulmonary nodule. The patient has a significant smoking history and is a current smoker. The patient is treatment-naive, and this consultation is for further management planning. The patient reports generally good functional status with no significant weight loss, fevers, or night sweats.

**Diagnostic Workup:**
Following the abnormal chest X-ray, a CT scan of the chest was performed, which identified a solitary, well-circumscribed mass in the right upper lobe, measuring approximately [De-identified] cm. Subsequent PET/CT imaging confirmed avid uptake within this pulmonary mass but demonstrated no evidence of distant metastatic disease or significant mediastinal lymphadenopathy. A CT-guided core needle biopsy of the lung mass was performed, and pathology confirmed the diagnosis of adenocarcinoma. Based on the imaging and pathology findings, the patient's disease is staged as AJCC Stage IB. There is no evidence of brain metastases on dedicated brain imaging.

**Molecular Studies:**
Comprehensive molecular profiling for actionable alterations is currently not available and pending. PD-L1 expression was not tested, consistent with the diagnostic timeline (pre-2017 sequencing, when testing was not yet standard of care). Tumor mutational burden (TMB) testing was performed and found to be low (<2 mut/Mb).

**Problem Summary:**
60-year-old patient with newly diagnosed, treatment-naive non-small cell lung cancer, adenocarcinoma histology, AJCC Stage IB. The patient has a history of current smoking. Molecular profiling is pending, PD-L1 was not tested, and TMB is low.
```

---

## genie_NSCLC_GENIE-MSK-P-0016994_0  [PASS]

**Structured profile (ground truth):**
- Stage IIA, squamous, brain_mets=False
- EGFR=negative ALK=negative ROS1=negative BRAF=negative MET=negative RET=negative NTRK=negative PD-L1=unknown
- biomarkers_available=True
- actual_treatment (held out): Gemcitabine Hydrochloride

**Generated note:**
```
The patient is a 75-year-old individual referred for initial oncology consultation regarding newly diagnosed non-small cell lung cancer. The history was obtained from the patient and review of available medical records.

**HPI:**
This 75-year-old individual presented to their primary care physician approximately two months ago with a persistent cough, mild dyspnea on exertion, and occasional pleuritic chest pain. An initial chest X-ray revealed an abnormality, prompting further investigation with a CT scan of the chest. This imaging identified a mass in the right upper lobe. The patient has a remote history of smoking, having quit over one year ago. The patient reports a good functional status, with an ECOG performance status of 0-1, and denies any significant weight loss or other B symptoms.

**Diagnostic Workup:**
*   **Imaging:** A dedicated CT scan of the chest confirmed a solid, enhancing mass in the right upper lobe, measuring approximately 4.2 x 3.8 cm, with associated ipsilateral hilar lymphadenopathy. A comprehensive whole-body PET/CT scan, performed on [De-identified Date], demonstrated avid uptake within the primary lung mass and the ipsilateral hilar lymph nodes, but crucially, no evidence of distant metastatic disease. An MRI of the brain, performed on [De-identified Date], was negative for intracranial metastases. The overall staging workup is consistent with localized disease without distant spread.
*   **Pathology:** A biopsy of the right upper lobe lung mass, obtained via bronchoscopy with transbronchial biopsy on [De-identified Date], confirmed the diagnosis of non-small cell lung cancer. Histological analysis was consistent with squamous cell carcinoma.
*   **Staging:** Based on the comprehensive diagnostic workup, the patient's cancer is formally staged as AJCC Stage IIA.

**Molecular Studies:**
Tumor tissue underwent molecular profiling for common driver alterations. Results indicated no actionable driver alterations, with testing negative for EGFR mutations, ALK rearrangements, ROS1 rearrangements, BRAF V600E mutations, MET exon 14 skipping mutations, RET fusions, NTRK fusions, and KRAS mutations, as well as ERBB2 (HER2) alterations. PD-L1 expression was not tested, consistent with the standard of care at the time of initial sequencing (pre-2017). Tumor mutational burden (TMB) was reported as intermediate (2–16 mut/Mb).

**Problem Summary:**
This 75-year-old individual presents with newly diagnosed, treatment-naive non-small cell lung cancer, squamous cell carcinoma histology, AJCC Stage IIA. Molecular profiling revealed no actionable driver alterations, PD-L1 was not tested, and TMB was intermediate. There is no evidence of distant metastatic disease, including no brain metastases. The patient is here for initial oncology evaluation to discuss management options.
```

---

## genie_NSCLC_GENIE-DFCI-001163_0  [PASS]

**Structured profile (ground truth):**
- Stage IB, adenocarcinoma, brain_mets=False
- EGFR=negative ALK=negative ROS1=negative BRAF=negative MET=negative RET=negative NTRK=negative PD-L1=unknown
- biomarkers_available=True
- actual_treatment (held out): Carboplatin, Paclitaxel

**warnings:**
- brain_mets=False but note appears to mention brain metastasis

**Generated note:**
```
[De-identified] Cancer Center
Medical Oncology Program
[De-identified]
[De-identified]
Phone: [De-identified] | Fax: [De-identified]

Initial Consultation [De-identified]
Patient: [De-identified]

**HPI:**
A 60-year-old patient presents for an initial oncology consultation following a recent diagnosis of non-small cell lung cancer (NSCLC). The patient reports a history of former smoking, having quit less than one year ago. The diagnosis was established as adenocarcinoma histology. The patient initially presented with a persistent cough and mild dyspnea, prompting further investigation. Performance status is excellent (ECOG 0-1).

**Diagnostic Workup:**
Initial evaluation for the presenting symptoms included a chest X-ray, which revealed a suspicious pulmonary nodule. A subsequent computed tomography (CT) scan of the chest confirmed the presence of a primary lung mass. Bronchoscopy with biopsy of the lesion confirmed the diagnosis of adenocarcinoma. Comprehensive staging workup included a whole-body PET/CT scan, which demonstrated metabolic activity confined to the primary lung lesion, with no evidence of regional lymph node involvement or distant metastatic disease. A magnetic resonance imaging (MRI) of the brain was also performed and was negative for intracranial metastases. Based on these findings, the patient was staged as AJCC Stage IB non-small cell lung cancer.

**Molecular Studies:**
Tumor tissue underwent comprehensive molecular profiling. Results indicated no actionable driver alterations, with testing negative for EGFR mutations, ALK rearrangements, ROS1 rearrangements, BRAF mutations, MET exon 14 skipping alterations, RET fusions, NTRK fusions, KRAS mutations, and ERBB2 (HER2) mutations. PD-L1 expression was not assessed, consistent with sequencing performed prior to 2017 when PD-L1 testing was not yet standard of care. Tumor mutational burden (TMB) was reported as intermediate (2–16 mut/Mb).

**Problem Summary:**
This is a 60-year-old patient with newly diagnosed, treatment-naive non-small cell lung cancer, adenocarcinoma histology, staged as AJCC IB. The tumor exhibits no identified actionable driver alterations on comprehensive molecular profiling, and tumor mutational burden is intermediate. The patient has a history of former smoking. Further discussion is warranted to determine the optimal management strategy for this localized disease.
```

---

## genie_NSCLC_GENIE-MSK-P-0010554_0  [PASS]

**Structured profile (ground truth):**
- Stage IV, adenocarcinoma, brain_mets=False
- EGFR=l858r ALK=negative ROS1=negative BRAF=negative MET=negative RET=negative NTRK=negative PD-L1=unknown
- biomarkers_available=True
- actual_treatment (held out): Investigational Drug

**Generated note:**
```
**HPI:**
[De-identified] is a 47-year-old patient presenting for initial oncology consultation following a recent diagnosis of non-small cell lung cancer. The patient reports a several-month history of persistent cough, progressive dyspnea on exertion, and a recent 10-pound unintentional weight loss over the past two months. Approximately one month prior to presentation, the patient also noted a new, non-tender nodule developing on the anterior chest wall. These symptoms prompted evaluation by their primary care physician, leading to initial imaging studies. The patient has a history of current tobacco use. Performance status is estimated at ECOG 1, with the patient largely independent but experiencing some fatigue and shortness of breath with moderate activity. This is the patient's first presentation to oncology, and they are treatment-naive for their lung cancer.

**Diagnostic Workup:**
Initial diagnostic evaluation included a CT scan of the chest, abdomen, and pelvis, which revealed a dominant mass in the right upper lobe of the lung, along with nodular pleural thickening and a small pleural effusion. The scan also identified a subcutaneous nodule on the chest wall. A subsequent PET-CT scan confirmed hypermetabolic activity within the right upper lobe lung mass, pleural lesions, and the subcutaneous nodule, with no other sites of distant metastatic disease noted. An MRI of the brain was performed and demonstrated no evidence of intracranial metastases. Biopsy of the right upper lobe lung mass and the subcutaneous chest wall nodule both confirmed adenocarcinoma histology. Based on these findings, the patient was staged as Stage IV non-small cell lung cancer (NSCLC) due to involvement of the pleura and subcutaneous tissue.

**Molecular Studies:**
Comprehensive genomic profiling was performed on the tumor tissue. Results indicated the presence of an EGFR L858R point mutation, which is a known sensitizing actionable driver. Testing for other common oncogenic drivers was negative, including ALK rearrangement, ROS1 rearrangement, BRAF V600E mutation, MET exon 14 skipping mutation, RET rearrangement, NTRK fusions, KRAS mutation, and ERBB2 (HER2) mutation. PD-L1 expression was not assessed, as this testing was not standard of care at the time of initial sequencing. Tumor mutational burden (TMB) was reported as intermediate (2–16 mut/Mb).

**Problem Summary:**
This 47-year-old patient presents with newly diagnosed, treatment-naive Stage IV non-small cell lung cancer of adenocarcinoma histology. The disease is characterized by a primary lung mass with metastatic involvement of the pleura and a subcutaneous chest wall nodule. Molecular testing revealed an EGFR L858R sensitizing mutation, with all other common actionable drivers negative. PD-L1 status is unknown, and TMB is intermediate. The patient is a current smoker. This consultation is for the discussion of systemic therapy options.
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
**CONSULTATION NOTE**

**DATE:** [De-identified Date]
**PATIENT:** [De-identified Patient Name]
**DOB:** [De-identified Date of Birth]
**MRN:** [De-identified MRN]

**HPI:**
The patient is a pleasant 75-year-old individual referred for initial oncology evaluation following a recent diagnosis of non-small cell lung cancer (NSCLC), adenocarcinoma histology. The patient initially presented to their primary care physician several weeks ago complaining of a persistent, non-productive cough and mild exertional dyspnea that had been worsening over the preceding few months. A chest X-ray was performed, which revealed a suspicious lung mass. Subsequent imaging and biopsy confirmed the diagnosis. The patient reports generally feeling well, with good energy levels and maintaining their usual activities of daily living. They are a former smoker, having quit over one year ago. Performance status is estimated to be ECOG 0-1.

**Diagnostic Workup:**
Initial diagnostic imaging included a CT scan of the chest, which demonstrated a primary mass in the right upper lobe measuring approximately 3.5 cm, with associated enlarged hilar lymph nodes. A subsequent PET/CT scan was performed, confirming avid FDG uptake in the right upper lobe mass and the ipsilateral hilar lymph nodes, but crucially, no evidence of distant metastatic disease. To complete staging, an MRI of the brain was also performed, which was negative for any intracranial metastases. A CT-guided core needle biopsy of the right upper lobe mass confirmed adenocarcinoma. Based on the comprehensive imaging and pathological findings, the patient is staged as AJCC Stage IIA (T2a N1 M0).

**Molecular Studies:**
Molecular profiling was performed on the tumor biopsy specimen. Results indicate the presence of an **ALK rearrangement**, which is an actionable driver mutation. The tumor was found to be negative for other common driver mutations, including EGFR, ROS1, BRAF, MET exon 14 skipping, RET, NTRK, KRAS, and ERBB2 (HER2). PD-L1 expression was not tested, consistent with the standard of care for molecular sequencing performed prior to 2017. Tumor mutational burden (TMB) was reported as low (<2 mut/Mb).

**Problem Summary:**
This 75-year-old patient presents with newly diagnosed, treatment-naive non-small cell lung cancer, adenocarcinoma histology, staged as AJCC Stage IIA. Molecular testing has identified an ALK rearrangement. The patient maintains a good performance status. Further discussion regarding appropriate treatment strategies for this localized, ALK-rearranged NSCLC is required.
```

---

## genie_NSCLC_GENIE-MSK-P-0014075_1  [PASS]

**Structured profile (ground truth):**
- Stage IV, adenocarcinoma, brain_mets=False
- EGFR=negative ALK=negative ROS1=negative BRAF=negative MET=exon_14 RET=negative NTRK=negative PD-L1=unknown
- biomarkers_available=True
- actual_treatment (held out): Crizotinib

**Generated note:**
```
**HPI:** This is a new 79-year-old patient presenting for initial oncology consultation following a recent diagnosis of non-small cell lung cancer. The patient initially presented with a persistent cough, increasing dyspnea on exertion, and new-onset back pain. An initial chest X-ray revealed a right upper lobe mass, prompting further diagnostic evaluation. The patient is a former smoker, having quit over one year ago. Performance status is estimated at ECOG 1, with the patient able to perform daily activities and light work, though experiencing some generalized fatigue.

**Diagnostic Workup:** A contrast-enhanced CT scan of the chest, abdomen, and pelvis confirmed a primary mass in the right upper lobe of the lung, measuring approximately 4.5 x 3.2 cm, with associated mediastinal lymphadenopathy. A CT-guided core needle biopsy of the lung mass was performed, confirming adenocarcinoma histology. Subsequent full body staging with PET/CT demonstrated hypermetabolic activity in the right upper lobe mass and mediastinal lymph nodes, as well as an intensely avid lesion in the lumbar spine, consistent with osseous metastasis. An MRI of the brain was performed and showed no evidence of intracranial metastatic disease. Based on these findings, the patient is diagnosed with Stage IV (cT2a N2 M1b) non-small cell lung cancer, with distant metastasis to bone.

**Molecular Studies:** Comprehensive genomic profiling was performed on the tumor biopsy specimen. Results revealed an actionable MET exon 14 skipping mutation. Testing for other common driver mutations was negative, including EGFR, ALK, ROS1, BRAF, RET, NTRK, KRAS, and ERBB2. PD-L1 expression was negative. Tumor mutational burden (TMB) was reported as intermediate (2–16 mut/Mb).

**Problem Summary:**
1.  Newly diagnosed Stage IV non-small cell lung cancer, adenocarcinoma histology, with osseous metastases.
2.  Actionable MET exon 14 skipping mutation detected.
3.  PD-L1 negative, TMB intermediate.
4.  Treatment-naive status.
```

---

## genie_NSCLC_GENIE-DFCI-081731_0  [PASS]

**Structured profile (ground truth):**
- Stage IV, adenocarcinoma, brain_mets=True
- EGFR=negative ALK=negative ROS1=negative BRAF=negative MET=negative RET=negative NTRK=negative PD-L1=unknown
- biomarkers_available=True
- actual_treatment (held out): Erlotinib Hydrochloride

**Generated note:**
```
Patient Name: [De-identified]
DOB: [De-identified]
MRN: [De-identified]
Date of Service: [De-identified]
Attending Physician: [De-identified] MD
Consultation Type: Initial Oncology Consultation

**HISTORY OF PRESENT ILLNESS:**
This 79-year-old patient presents for initial oncology consultation regarding recently diagnosed Stage IV non-small cell lung cancer (NSCLC), adenocarcinoma histology. Patient reports a several-month history of progressive fatigue, unintentional weight loss, and a persistent cough. More recently, patient has experienced new onset headaches and some mild gait instability, prompting further evaluation and leading to the current diagnosis. The patient is treatment-naive, having received no prior systemic therapy for this malignancy.

**DIAGNOSTIC WORKUP:**
Initial evaluation included a chest X-ray which revealed a dominant left upper lobe mass. This was followed by a contrast-enhanced CT scan of the chest, abdomen, and pelvis which confirmed a primary lung mass measuring approximately 4.5 cm in the left upper lobe, with associated mediastinal and hilar lymphadenopathy. The CT also identified suspicious lesions in the liver, left adrenal gland, and several osseous lesions concerning for metastatic disease. Further staging with a whole-body PET/CT scan demonstrated hypermetabolic activity corresponding to the primary lung lesion, involved lymph nodes, liver lesions, adrenal lesion, and multiple bone lesions, confirming widespread metastatic disease. Given the patient's neurological symptoms and the extent of metastatic disease, a brain MRI was performed, which revealed multiple enhancing lesions consistent with brain metastases. Biopsy of the left upper lobe lung mass, performed via CT-guided core needle biopsy, confirmed adenocarcinoma histology. Overall, the diagnostic workup confirms AJCC Stage IV NSCLC, adenocarcinoma histology, with metastatic disease to the brain, bone, liver, adrenal gland, and distant lymph nodes.

**MOLECULAR STUDIES:**
Molecular profiling was performed on the tumor biopsy specimen. Testing for common driver alterations, including EGFR, ALK, ROS1, BRAF, MET exon 14 skipping, RET, NTRK, KRAS, and ERBB2 (HER2) amplification or mutations, did not identify any actionable alterations. PD-L1 expression was not assessed, as this testing was not standard of care at the time of initial sequencing (pre-2017 sequencing). Tumor mutational burden (TMB) was reported as intermediate (2–16 mut/Mb).

**PROBLEM SUMMARY:**
This 79-year-old patient presents with newly diagnosed, treatment-naive Stage IV non-small cell lung cancer, adenocarcinoma histology. The disease is widely metastatic to the brain, bone, liver, adrenal gland, and distant lymph nodes. Molecular profiling did not reveal any actionable driver alterations (negative for EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, ERBB2). PD-L1 expression was not tested. Tumor mutational burden is intermediate (2–16 mut/Mb). Further discussion regarding management strategies for this advanced disease is warranted.
```

---

## genie_NSCLC_GENIE-MSK-P-0018573_0  [PASS]

**Structured profile (ground truth):**
- Stage IV, adenocarcinoma, brain_mets=True
- EGFR=negative ALK=positive ROS1=negative BRAF=negative MET=negative RET=negative NTRK=negative PD-L1=unknown
- biomarkers_available=True
- actual_treatment (held out): Alectinib, Bevacizumab

**Generated note:**
```
[De-identified] Clinic
[De-identified] Oncology
[De-identified], [De-identified]

PATIENT: [De-identified]
DOB: [De-identified]
MRN: [De-identified]
DATE OF VISIT: [De-identified]

**HPI:**
This is an initial oncology consultation for a 43-year-old patient with newly diagnosed Stage IV non-small cell lung cancer (NSCLC), adenocarcinoma histology. The patient initially presented to their primary care physician several weeks ago with a persistent cough, increasing dyspnea on exertion, and new-onset headaches associated with occasional dizziness. The patient is a former smoker, having quit over one year ago. Despite these symptoms, the patient maintains a good functional status, with an ECOG performance status of 1. This visit represents the first oncology evaluation for this diagnosis, and the patient is treatment-naive, having received no prior systemic therapy.

**Diagnostic Workup:**
Initial investigations included a chest X-ray, which revealed a left upper lobe mass. Subsequent contrast-enhanced CT of the chest, abdomen, and pelvis confirmed a primary lung mass measuring approximately 4.5 cm in the left upper lobe, with associated mediastinal lymphadenopathy. Additionally, the CT identified multiple suspicious lesions in the liver and a small pleural effusion. Brain MRI was performed due to the patient's neurological symptoms, which demonstrated several enhancing lesions consistent with brain metastases. A PET/CT scan further delineated the extent of disease, confirming hypermetabolic activity in the primary lung lesion, mediastinal lymph nodes, liver lesions, and pleural involvement. A palpable subcutaneous nodule was noted during physical examination and biopsied, confirming metastatic adenocarcinoma. A core needle biopsy of the primary lung mass confirmed the histology as adenocarcinoma. The overall findings are consistent with AJCC Stage IV non-small cell lung cancer with metastases to the brain, liver, pleura, and subcutaneous tissue.

**Molecular Studies:**
Comprehensive genomic profiling was performed on the tumor biopsy specimen. Results demonstrated the presence of an ALK rearrangement, identified as an actionable driver mutation. Testing for other common oncogenic drivers was negative, including EGFR, ROS1, BRAF, MET exon 14 skipping, RET fusion, NTRK fusion, KRAS, and ERBB2 (HER2) mutations. PD-L1 expression was negative. Tumor mutational burden (TMB) was reported as low (<2 mut/Mb).

**Problem Summary:**
This 43-year-old patient presents with newly diagnosed Stage IV non-small cell lung cancer, adenocarcinoma histology, with metastatic disease involving the brain, liver, pleura, and subcutaneous tissue. Molecular testing revealed an ALK rearrangement, with negative PD-L1 expression and low tumor mutational burden. The patient is treatment-naive and is seeking evaluation for management options.
```

---

## genie_NSCLC_GENIE-VICC-588847_1  [PASS]

**Structured profile (ground truth):**
- Stage IV, adenocarcinoma, brain_mets=False
- EGFR=negative ALK=positive ROS1=negative BRAF=negative MET=negative RET=negative NTRK=negative PD-L1=unknown
- biomarkers_available=True
- actual_treatment (held out): Crizotinib

**Generated note:**
```
**HPI:**
The patient is a 44-year-old who presents for an initial oncology consultation following a recent diagnosis of non-small cell lung cancer. The patient first sought medical attention several weeks prior due to a persistent cough, progressive shortness of breath, and mild exertional fatigue. They also reported a recent unintentional weight loss of approximately 5 pounds over the past two months. The patient has a remote history of smoking cessation but identifies as a never smoker. Performance status is currently estimated at ECOG 1, with the patient maintaining most daily activities despite symptoms.

**Diagnostic Workup:**
Initial evaluation included a chest X-ray, which revealed a suspicious right upper lobe mass and diffuse interstitial opacities. This prompted a contrast-enhanced CT scan of the chest, abdomen, and pelvis. The CT chest confirmed a primary mass in the right upper lobe, along with multiple pulmonary nodules in the contralateral (left) lung, and evidence of extensive pleural thickening and effusions. A subsequent PET-CT scan demonstrated hypermetabolic activity corresponding to the right upper lobe mass, the contralateral lung nodules, and the pleural involvement. No other distant hypermetabolic foci were identified. To further characterize the disease, a CT-guided biopsy of the right upper lobe mass was performed. Histopathologic examination confirmed adenocarcinoma of the lung. Given the findings on imaging, particularly the contralateral lung and pleural involvement, the patient was diagnosed with AJCC Stage IV non-small cell lung cancer. An MRI of the brain was performed as part of the staging workup and showed no evidence of intracranial metastatic disease.

**Molecular Studies:**
Molecular profiling was performed on the tumor tissue obtained from the biopsy. Next-generation sequencing (NGS) identified an ALK rearrangement. Further testing for common driver mutations revealed the tumor to be negative for EGFR mutations, ROS1 rearrangement, BRAF mutations, MET exon 14 skipping, RET rearrangement, NTRK fusions, KRAS mutations, and ERBB2 (HER2) mutations. PD-L1 expression was not tested at the time of sequencing, consistent with pre-2017 sequencing practices. Tumor mutational burden (TMB) analysis indicated an intermediate TMB of 2–16 mut/Mb.

**Problem Summary:**
This 44-year-old patient has newly diagnosed, treatment-naive non-small cell lung cancer, adenocarcinoma histology, AJCC Stage IV, with metastatic disease involving the contralateral lung and pleura. Molecular testing revealed an actionable ALK rearrangement, with other common driver mutations being negative. PD-L1 was not tested, and TMB was intermediate. The patient's performance status is ECOG 1. We will proceed with a comprehensive discussion of treatment options tailored to these findings.
```

---

## genie_NSCLC_GENIE-VICC-289285_0  [PASS]

**Structured profile (ground truth):**
- Stage IV, squamous, brain_mets=False
- EGFR=negative ALK=negative ROS1=negative BRAF=negative MET=negative RET=negative NTRK=not_on_panel PD-L1=intermediate
- biomarkers_available=True
- actual_treatment (held out): Carboplatin, Nabpaclitaxel

**warnings:**
- brain_mets=False but note appears to mention brain metastasis

**Generated note:**
```
**HPI:**
[De-identified] is a 76-year-old who presents for initial oncology evaluation of newly diagnosed non-small cell lung cancer. The patient first noted symptoms approximately three months ago, including a persistent cough, mild dyspnea on exertion, and generalized fatigue. Concurrently, the patient developed a new, slowly enlarging subcutaneous nodule on the left anterior chest wall, which prompted medical attention. The patient has a history of controlled hypertension but otherwise reports good health prior to these recent symptoms. Notably, the patient is a never smoker.

**Diagnostic Workup:**
Initial evaluation included a chest X-ray demonstrating a suspicious lung mass. This was followed by a CT scan of the chest, abdomen, and pelvis which confirmed a primary lesion measuring approximately 4.5 cm in the right upper lobe and identified the subcutaneous nodule as a potential metastatic site. A subsequent PET/CT scan confirmed hypermetabolic activity in both the primary lung lesion and the subcutaneous nodule, with no other sites of distant metastatic disease noted. A brain MRI was performed as part of the staging workup and was negative for intracranial metastases. Biopsy of the primary lung lesion, performed via bronchoscopy, revealed non-small cell lung cancer, squamous cell carcinoma histology. A concurrent excisional biopsy of the subcutaneous nodule confirmed metastatic squamous cell carcinoma, consistent with the lung primary. Based on these findings, the patient is diagnosed with AJCC Stage IV non-small cell lung cancer (M1b, due to subcutaneous metastasis). The patient's performance status is estimated at ECOG 1, with mild symptoms and able to carry out light work.

**Molecular Studies:**
Molecular profiling was performed on the tumor tissue. Results indicate no actionable driver alterations, with comprehensive testing negative for EGFR, ALK, ROS1, BRAF, MET exon 14 skipping, RET fusions, KRAS mutations, and ERBB2 (HER2) alterations. Programmed death-ligand 1 (PD-L1) expression was positive, with a tumor proportion score (TPS) of 1–49%. Tumor mutational burden (TMB) was reported as high, at >16 mutations/megabase (mut/Mb).

**Problem Summary:**
[De-identified] is a 76-year-old with newly diagnosed, treatment-naive non-small cell lung cancer, squamous cell carcinoma histology, AJCC Stage IV, with metastatic disease involving subcutaneous tissue. The patient is a never smoker. Molecular testing revealed no actionable driver mutations. PD-L1 expression is positive (TPS 1-49%), and tumor mutational burden is high (>16 mut/Mb). This initial consultation serves to establish care and discuss potential systemic therapy options.
```

---

## genie_NSCLC_GENIE-DFCI-091175_0  [PASS]

**Structured profile (ground truth):**
- Stage IV, adenocarcinoma, brain_mets=False
- EGFR=negative ALK=negative ROS1=negative BRAF=negative MET=negative RET=negative NTRK=negative PD-L1=high
- biomarkers_available=True
- actual_treatment (held out): Pembrolizumab

**Generated note:**
```
**HPI:**
The patient is a 72-year-old individual presenting for an initial oncology consultation following a recent diagnosis of non-small cell lung cancer. The patient initially presented to their primary care physician approximately three months ago with a several-week history of persistent, non-productive cough, progressive dyspnea on exertion, and occasional dull, right-sided pleuritic chest pain. These symptoms prompted initial investigations, including a chest X-ray, which revealed a suspicious right lung mass and a moderate right pleural effusion. Subsequent contrast-enhanced computed tomography (CT) of the chest, abdomen, and pelvis confirmed the presence of a primary lung lesion in the right lower lobe, extensive nodular pleural thickening, and a large right-sided pleural effusion. Additionally, a suspicious enhancing lesion was noted in the right adrenal gland, concerning for metastatic disease. A PET-CT scan was performed and demonstrated avid uptake in the primary lung mass, the diffuse pleural disease, and the right adrenal lesion. Biopsy of the primary lung mass, guided by CT, confirmed adenocarcinoma histology. The patient's performance status is currently ECOG 1, with the patient largely independent in activities of daily living but experiencing some fatigue and mild exertional dyspnea.

**Diagnostic Workup:**
*   **Imaging:**
    *   [De-identified Date]: Chest X-ray: Revealed a right lower lobe mass and a moderate right pleural effusion.
    *   [De-identified Date]: CT Chest/Abdomen/Pelvis with contrast: Demonstrated a 3.5 cm mass in the right lower lobe, extensive nodular pleural thickening, and a large right-sided pleural effusion. Additionally, a 2.1 cm enhancing lesion was noted in the right adrenal gland, highly suspicious for metastatic disease. No evidence of obstructive uropathy or significant lymphadenopathy beyond the chest was observed.
    *   [De-identified Date]: PET-CT scan: Confirmed hypermetabolic activity in the right lower lobe lung mass (SUVmax 12.5), diffuse pleural disease (SUVmax 8.2), and the right adrenal lesion (SUVmax 7.8). No other sites of distant metastatic disease were identified.
    *   [De-identified Date]: Brain MRI with contrast: Performed to complete staging, demonstrated no evidence of intracranial metastatic disease.
*   **Pathology:**
    *   [De-identified Date]: CT-guided biopsy of the right lower lobe lung mass: Histology confirmed invasive adenocarcinoma of the lung.
    *   AJCC Stage: Stage IV (cT2b cN2 cM1b, based on pleural metastases and distant adrenal metastasis).
*   **Smoking History:** The patient is a former smoker, having quit greater than one year ago.

**Molecular Studies:**
Comprehensive molecular profiling was performed on the tumor tissue from the lung biopsy.
*   **Actionable Driver Alterations:** No actionable driver alterations were identified. Specifically, testing was negative for mutations in *EGFR*, *ALK* rearrangements, *ROS1* rearrangements, *BRAF* V600E, *MET* exon 14 skipping mutations, *RET* fusions, *NTRK* fusions, *KRAS* mutations, and *ERBB2* (HER2) mutations.
*   **PD-L1 Expression:** Programmed death-ligand 1 (PD-L1) expression by immunohistochemistry (IHC) was positive with a tumor proportion score (TPS) of ≥50%.
*   **Tumor Mutational Burden (TMB):** Tumor mutational burden was intermediate, reported as 2–16 mutations/megabase (mut/Mb).

**Problem Summary:**
The patient is a 72-year-old individual with newly diagnosed, treatment-naive Stage IV non-small cell lung cancer, adenocarcinoma histology, with metastatic disease involving the pleura and right adrenal gland. Molecular testing revealed no identifiable actionable driver alterations, a PD-L1 TPS ≥50%, and intermediate tumor mutational burden. The patient maintains a good performance status (ECOG 1).
```

---

## genie_NSCLC_GENIE-MSK-P-0017253_0  [PASS]

**Structured profile (ground truth):**
- Stage IV, adenocarcinoma, brain_mets=False
- EGFR=negative ALK=negative ROS1=negative BRAF=negative MET=negative RET=negative NTRK=negative PD-L1=unknown
- biomarkers_available=True
- actual_treatment (held out): Bevacizumab, Carboplatin, Pemetrexed Disodium

**Generated note:**
```
HPI:
The patient is a 66-year-old individual presenting for an initial oncology consultation following a recent diagnosis of non-small cell lung cancer. The patient reports a several-month history of persistent cough, progressive dyspnea on exertion, and approximately 10-pound unintentional weight loss over the past three months. More recently, [De-identified] developed new-onset, dull aching pain in the lower back and ribs, prompting further medical evaluation. The patient is a former smoker, having successfully quit less than one year ago. Currently, [De-identified] reports an ECOG performance status of 1, able to carry out light work and ambulate independently but experiencing some symptomatic limitations.

Diagnostic Workup:
The diagnostic evaluation commenced with the patient's presenting symptoms. An initial chest X-ray revealed a suspicious right upper lobe mass, which was further characterized by a subsequent CT scan of the chest, abdomen, and pelvis. This imaging confirmed a primary lung lesion and identified multiple sclerotic and lytic lesions within the axial skeleton, highly concerning for osseous metastases. Additionally, several hypodense lesions were noted within the liver parenchyma, suspicious for hepatic metastases. A whole-body PET-CT scan demonstrated avid uptake in the primary lung mass, the aforementioned bony lesions, and the hepatic lesions, consistent with widespread metastatic disease. A CT-guided biopsy of the primary lung mass confirmed the diagnosis of non-small cell lung cancer with adenocarcinoma histology. Further staging workup, including a dedicated bone scan, corroborated the extent of bone metastases. Given the presence of distant metastases to bone and liver, the patient was diagnosed with AJCC Stage IV non-small cell lung cancer. An MRI of the brain was performed and showed no evidence of intracranial metastatic disease.

Molecular Studies:
Molecular profiling was performed on the tumor tissue using next-generation sequencing. The analysis identified an actionable KRAS G12C mutation. The tumor was found to be negative for other common oncogenic drivers, including EGFR mutations, ALK rearrangements, ROS1 rearrangements, BRAF V600E mutations, MET exon 14 skipping alterations, RET fusions, NTRK fusions, and ERBB2 (HER2) mutations. PD-L1 expression was not assessed, consistent with standard practice for tumor sequencing prior to [De-identified Year]. Tumor mutational burden (TMB) was reported as intermediate, falling within the range of 2–16 mutations per megabase (mut/Mb).

Problem Summary:
This is a 66-year-old patient with newly diagnosed, treatment-naive AJCC Stage IV non-small cell lung cancer, adenocarcinoma histology, metastatic to bone and liver. Molecular testing revealed an actionable KRAS G12C mutation, with no other common driver alterations detected, and an intermediate tumor mutational burden. PD-L1 status is unknown. The patient presents for discussion of initial systemic therapy options.
```

---

## genie_NSCLC_GENIE-MSK-P-0022777_0  [PASS]

**Structured profile (ground truth):**
- Stage IIIA, adenocarcinoma, brain_mets=False
- EGFR=exon_19_del ALK=negative ROS1=negative BRAF=negative MET=negative RET=negative NTRK=negative PD-L1=intermediate
- biomarkers_available=True
- actual_treatment (held out): Investigational Drug

**Generated note:**
```
[De-identified] Medical Oncology Consultation Note

**DATE OF CONSULTATION:** [De-identified Date]

**PATIENT IDENTIFICATION:** The patient is a 54-year-old individual presenting for initial oncology evaluation for newly diagnosed non-small cell lung cancer. This patient is treatment-naive.

**HPI:**
The patient is a 54-year-old individual who was in their usual state of health until approximately [De-identified number] months ago, when they developed a persistent cough, occasionally productive, and some exertional dyspnea. They also report mild fatigue but deny significant weight loss, fevers, or night sweats. Due to worsening symptoms, they sought evaluation by their primary care provider, which led to a chest X-ray revealing a suspicious lung mass. The patient has a remote history of smoking but quit many years ago, and is a never smoker for the purposes of this diagnosis. Their ECOG performance status is currently 0-1, indicating they are fully ambulatory and able to carry out all normal activities with minimal to mild symptoms.

**Diagnostic Workup:**
Following the suspicious chest X-ray, a contrast-enhanced CT scan of the chest, abdomen, and pelvis was performed. This imaging demonstrated a primary mass measuring approximately [De-identified size] cm in the [De-identified lobe, e.g., right upper lobe], along with several enlarged mediastinal and hilar lymph nodes. Critically, no evidence of distant metastatic disease was identified on this scan. A subsequent PET/CT scan confirmed hypermetabolic activity within the primary lung lesion and the involved mediastinal lymph nodes, without uptake in any other distant sites. An MRI of the brain was also performed to rule out intracranial metastases, which revealed no evidence of brain involvement.
Tissue biopsy, obtained via [De-identified biopsy method, e.g., bronchoscopy with transbronchial biopsy], confirmed the diagnosis of non-small cell lung cancer, specifically adenocarcinoma histology. Based on the imaging findings of a primary tumor with regional nodal involvement but no distant metastases, the patient is staged as AJCC Stage IIIA.

**Molecular Studies:**
Comprehensive molecular profiling was performed on the tumor tissue. Key findings include:
*   **Actionable driver mutations:** An EGFR exon 19 deletion was detected, which is a sensitizing mutation.
*   **Other common mutations:** The tumor was negative for ALK rearrangement, ROS1 rearrangement, BRAF V600E mutation, MET exon 14 skipping, RET fusion, NTRK fusion, KRAS mutations, and ERBB2 (HER2) mutations.
*   **PD-L1 expression:** Programmed death-ligand 1 (PD-L1) expression was positive, with a tumor proportion score (TPS) of 1-49%.
*   **Tumor Mutational Burden (TMB):** Tumor mutational burden was low (<2 mut/Mb).

**Problem Summary:**
This is a 54-year-old patient with newly diagnosed, treatment-naive non-small cell lung cancer, adenocarcinoma histology, staged as AJCC Stage IIIA. The diagnostic workup consistently showed locoregional disease without evidence of distant metastases, including no brain metastases. Molecular profiling revealed an EGFR exon 19 deletion, with negative results for other common driver mutations. PD-L1 expression was positive (TPS 1-49%), and tumor mutational burden was low. The patient maintains a good performance status (ECOG 0-1). Further discussion regarding optimal management strategies given these findings is warranted.
```

---

## genie_NSCLC_GENIE-VICC-235319_0  [PASS]

**Structured profile (ground truth):**
- Stage IIIB, adenocarcinoma, brain_mets=False
- EGFR=negative ALK=negative ROS1=negative BRAF=negative MET=negative RET=negative NTRK=not_on_panel PD-L1=intermediate
- biomarkers_available=True
- actual_treatment (held out): Carboplatin, Paclitaxel

**warnings:**
- brain_mets=False but note appears to mention brain metastasis

**Generated note:**
```
[De-identified] is a 62-year-old individual presenting for initial consultation regarding a recent diagnosis of non-small cell lung cancer (NSCLC). The history was obtained from the patient and review of available medical records.

**History of Present Illness**
This generally healthy 62-year-old began experiencing a persistent cough and mild shortness of breath approximately three months prior to presentation. Initially attributed to a viral illness, symptoms gradually worsened, prompting a visit to their primary care physician. A chest X-ray revealed a suspicious mass in the lung, leading to further investigation with a CT scan of the chest. The CT confirmed a primary lung mass and also identified enlarged mediastinal lymph nodes. Subsequent bronchoscopy with transbronchial biopsy of the lung lesion and endobronchial ultrasound-guided transbronchial needle aspiration (EBUS-TBNA) of the mediastinal lymph nodes confirmed the diagnosis of adenocarcinoma. The patient reports maintaining a good performance status, with occasional fatigue but no significant weight loss or other systemic symptoms. They are a former smoker, having quit several years ago. This is the patient's first oncology evaluation, and they are treatment-naive.

**Diagnostic Workup**
Following the biopsy confirmation of adenocarcinoma, comprehensive staging was performed. A whole-body PET-CT scan identified a hypermetabolic primary lung lesion and metabolically active mediastinal lymph nodes, consistent with locoregional disease. Importantly, no evidence of distant metastatic disease was found on the PET-CT. An MRI of the brain was also performed to evaluate for intracranial metastases, which was negative. Based on these findings, the patient's cancer is staged as AJCC Stage IIIB non-small cell lung cancer. The patient's functional status is excellent, with an ECOG performance status of 0-1.

**Molecular Studies**
Molecular profiling of the tumor tissue was performed and revealed no actionable driver alterations, with testing negative for EGFR, ALK, ROS1, BRAF, MET exon 14 skipping, RET fusions, KRAS mutations, and ERBB2 (HER2) alterations. Programmed death-ligand 1 (PD-L1) expression was positive, with a tumor proportion score (TPS) of 1–49%. Tumor mutational burden (TMB) was reported as high, at >16 mut/Mb.

**Problem Summary**
The patient is a 62-year-old with newly diagnosed, treatment-naive non-small cell lung cancer, adenocarcinoma histology, AJCC Stage IIIB. Molecular testing indicates no actionable driver alterations, PD-L1 expression of 1–49%, and a high tumor mutational burden (>16 mut/Mb). There is no evidence of distant metastatic disease, including to the brain.
```

---

## genie_NSCLC_GENIE-MSK-P-0007345_2  [PASS]

**Structured profile (ground truth):**
- Stage IIIA, adenocarcinoma, brain_mets=False
- EGFR=negative ALK=negative ROS1=negative BRAF=negative MET=negative RET=negative NTRK=negative PD-L1=unknown
- biomarkers_available=True
- actual_treatment (held out): Carboplatin, Pemetrexed Disodium

**Generated note:**
```
**HPI:**
The patient is an 82-year-old individual presenting for initial oncology consultation regarding a recent diagnosis of non-small cell lung cancer. The patient reports a history of persistent cough and increasing dyspnea on exertion over the past several months, which prompted evaluation by their primary care physician. A chest X-ray performed on [De-identified Date] revealed a suspicious mass in the left upper lobe, leading to further diagnostic workup. The patient is a former smoker, having quit over one year ago. They report good functional status prior to the onset of these symptoms, with an ECOG performance status of 1, primarily due to mild fatigue.

**Diagnostic Workup:**
Following the abnormal chest X-ray, a contrast-enhanced CT scan of the chest, abdomen, and pelvis was performed on [De-identified Date]. This imaging confirmed a 4.5 cm spiculated mass in the left upper lobe. It also demonstrated several enlarged mediastinal lymph nodes, with the largest measuring 2.2 cm in the subcarinal station. No evidence of pleural effusion, pericardial effusion, or distant metastatic disease was identified on this scan. Subsequent PET/CT scan on [De-identified Date] showed avid FDG uptake in the primary left upper lobe mass (SUVmax 12.5) and in multiple mediastinal lymph node stations (SUVmax up to 8.9), consistent with locoregional disease. A brain MRI with contrast on [De-identified Date] was negative for intracranial metastatic disease.
A CT-guided biopsy of the left upper lobe mass was performed on [De-identified Date]. Pathology review confirmed non-small cell lung cancer, adenocarcinoma histology. Based on these findings, the patient's cancer is staged as AJCC Stage IIIA (cT2a N2 M0).

**Molecular Studies:**
Molecular profiling was performed on the tumor biopsy specimen. Testing for common driver alterations including EGFR mutations, ALK rearrangements, ROS1 rearrangements, BRAF V600E mutations, MET exon 14 skipping mutations, RET fusions, NTRK fusions, KRAS mutations, and ERBB2 mutations did not identify any actionable alterations. PD-L1 expression was not assessed, as this testing was not standard of care at the time of initial sequencing in [De-identified Year, prior to 2017]. Tumor mutational burden (TMB) was reported as intermediate, ranging from 2–16 mut/Mb.

**Problem Summary:**
The patient is an 82-year-old individual with newly diagnosed, treatment-naive non-small cell lung cancer, adenocarcinoma histology, AJCC Stage IIIA. Diagnostic workup has confirmed locoregional lymph node involvement without evidence of distant metastasis, including no brain metastases. Molecular profiling revealed no actionable driver alterations, and TMB was intermediate. The patient has a history of prostate cancer, which is currently stable and under surveillance.
```

---

## genie_NSCLC_GENIE-MSK-P-0019128_0  [PASS]

**Structured profile (ground truth):**
- Stage IV, adenocarcinoma, brain_mets=False
- EGFR=l858r ALK=negative ROS1=negative BRAF=negative MET=negative RET=negative NTRK=negative PD-L1=intermediate
- biomarkers_available=True
- actual_treatment (held out): Erlotinib Hydrochloride

**Generated note:**
```
[De-identified Date]

**HPI:**
This is an 83-year-old patient presenting for an initial oncology consultation regarding a new diagnosis of non-small cell lung cancer (NSCLC). The patient initially sought medical attention several months ago due to a persistent cough, progressive dyspnea on exertion, and some unintentional weight loss. Initial evaluation by their primary care provider included a chest X-ray, which revealed an abnormality prompting further imaging. The patient reports an ECOG Performance Status of 1, able to perform all self-care activities and light work, but unable to carry out more strenuous activities. They deny significant pain, hemoptysis, or neurological symptoms. The patient is a never smoker.

**Diagnostic Workup:**
A subsequent chest CT scan identified a suspicious mass in the left lung and a moderate left-sided pleural effusion. To further characterize and stage the disease, a PET/CT scan was performed. This confirmed the primary lung lesion and demonstrated FDG-avid pleural implants, consistent with distant metastatic disease. A dedicated brain MRI was obtained, which showed no evidence of intracranial metastases. A diagnostic thoracentesis was performed, and cytology of the pleural fluid confirmed the presence of adenocarcinoma. Based on these findings, the patient was diagnosed with AJCC Stage IV non-small cell lung cancer.

**Molecular Studies:**
Tumor tissue obtained from the pleural fluid cytology block underwent comprehensive molecular profiling. This revealed an **EGFR L858R point mutation**, which is a known sensitizing driver mutation. Testing for other common oncogenic drivers was negative, including **ALK, ROS1, BRAF, MET exon 14 skipping, RET, NTRK, KRAS, and ERBB2** alterations. Programmed death-ligand 1 (PD-L1) expression by immunohistochemistry (IHC) was **positive with a Tumor Proportion Score (TPS) of 1–49%**. Tumor Mutational Burden (TMB) was **low (<2 mut/Mb)**.

**PAST MEDICAL HISTORY:**
Reviewed and notable for well-controlled hypertension and hyperlipidemia. No other significant medical comorbidities.

**MEDICATIONS:**
Current medication list reviewed and up-to-date. No medications of specific oncologic relevance.

**ALLERGIES:**
No known drug allergies.

**SOCIAL HISTORY:**
The patient lives independently and has a good support system. As noted, they are a never smoker. No history of alcohol or illicit drug use.

**FAMILY HISTORY:**
Non-contributory for early-onset cancers.

**PHYSICAL EXAM:**
General: Well-appearing, conversant, and in no acute distress.
Vitals: Within normal limits for age.
Lungs: Decreased breath sounds at the left lung base.
Cardiovascular: Regular rate and rhythm, no murmurs.
Abdomen: Soft, non-tender, non-distended.
Extremities: No clubbing, cyanosis, or edema.
Neurologic: Alert and oriented x3, no focal deficits.
ECOG Performance Status: 1.

**RELEVANT DIAGNOSTIC STUDIES:**
All relevant laboratory and imaging studies have been reviewed and are incorporated into the HPI and Diagnostic Workup sections above.

**Problem Summary:**
This is an 83-year-old patient with newly diagnosed, treatment-naive non-small cell lung cancer, adenocarcinoma histology, AJCC Stage IV, with metastatic disease to the pleura. Molecular profiling reveals an EGFR L858R sensitizing mutation, PD-L1 TPS 1-49%, and low TMB. The patient is currently seeking initial oncology evaluation for management recommendations.
```

---

## genie_NSCLC_GENIE-VICC-529086_0  [PASS]

**Structured profile (ground truth):**
- Stage IIB, adenocarcinoma, brain_mets=False
- EGFR=negative ALK=negative ROS1=negative BRAF=negative MET=negative RET=negative NTRK=not_on_panel PD-L1=low
- biomarkers_available=True
- actual_treatment (held out): Carboplatin, Pemetrexed Disodium

**Generated note:**
```
[De-identified Clinic Name]
[De-identified Address]
[De-identified Phone Number]

**PATIENT:** [De-identified Patient Name]
**DOB:** [De-identified Date of Birth]
**MRN:** [De-identified Medical Record Number]
**DATE OF CONSULTATION:** [De-identified Date]

**ATTENDING PHYSICIAN:** [De-identified Physician Name], MD
**SERVICE:** Medical Oncology

**REASON FOR CONSULTATION:** Initial oncology evaluation for newly diagnosed non-small cell lung cancer.

**HPI:**
This is a 58-year-old patient presenting for initial oncology consultation regarding a recent diagnosis of non-small cell lung cancer (NSCLC). The patient reports a history of being a former smoker, having quit over one year ago. Approximately three months prior to presentation, the patient began experiencing a persistent, non-productive cough, which was initially attributed to seasonal allergies. Over the subsequent weeks, the cough worsened, and the patient noted mild exertional dyspnea and occasional dull, right-sided chest discomfort. There was also a reported unintentional weight loss of approximately 10 pounds over the past two months and increased fatigue. These symptoms prompted a visit to the primary care physician. The patient maintains an excellent performance status, ambulating independently and engaging in all usual activities without limitation (ECOG PS 0).

**Diagnostic Workup:**
Initial evaluation by the primary care physician included a chest X-ray, which revealed a suspicious right upper lobe mass. This finding prompted a subsequent contrast-enhanced CT scan of the chest, abdomen, and pelvis on [De-identified Date]. The CT confirmed a 4.5 cm solid mass in the right upper lobe, along with several enlarged hilar and mediastinal lymph nodes. There was no evidence of distant metastatic disease in the abdomen or pelvis. A CT-guided core needle biopsy of the right upper lobe mass was performed on [De-identified Date], which confirmed the diagnosis of adenocarcinoma. Subsequent comprehensive staging included a PET/CT scan on [De-identified Date], demonstrating hypermetabolic activity corresponding to the right upper lobe mass and the aforementioned hilar and mediastinal lymph nodes, but no evidence of hypermetabolic lesions elsewhere in the body suggestive of distant metastasis. An MRI of the brain with contrast was performed on [De-identified Date] and was negative for intracranial metastatic disease. Based on these findings, the patient's disease is staged as AJCC Stage IIB non-small cell lung cancer, adenocarcinoma histology.

**Molecular Studies:**
Tissue obtained from the biopsy was submitted for comprehensive molecular profiling. Results indicate no actionable driver alterations, with testing negative for EGFR mutations, ALK rearrangements, ROS1 rearrangements, BRAF mutations, MET exon 14 skipping alterations, RET rearrangements, KRAS mutations, and ERBB2 (HER2) mutations. Programmed death-ligand 1 (PD-L1) expression was assessed by immunohistochemistry and was found to be negative, with a tumor proportion score (TPS) of less than 1%. Tumor mutational burden (TMB) analysis was also performed and revealed a high TMB, quantified at >16 mutations/megabase (mut/Mb).

**Problem Summary:**
This is a 58-year-old patient with newly diagnosed, treatment-naive non-small cell lung cancer, adenocarcinoma histology, AJCC Stage IIB. Staging workup confirmed localized disease without evidence of distant metastasis, including no brain metastases. Molecular profiling revealed no actionable driver alterations, a PD-L1 TPS <1%, and high tumor mutational burden (>16 mut/Mb). The patient is presenting for initial oncology evaluation to discuss management options for their lung cancer.
```

---

## genie_NSCLC_GENIE-DFCI-011107_0  [PASS]

**Structured profile (ground truth):**
- Stage IIIB, adenocarcinoma, brain_mets=False
- EGFR=negative ALK=negative ROS1=negative BRAF=negative MET=negative RET=negative NTRK=negative PD-L1=unknown
- biomarkers_available=True
- actual_treatment (held out): Cisplatin, Pemetrexed Disodium

**warnings:**
- brain_mets=False but note appears to mention brain metastasis

**Generated note:**
```
REASON FOR VISIT/CC: Chief Complaint: Patient presents with non-small cell lung cancer for initial oncology consultation.

HISTORY OF PRESENT ILLNESS:
[De-identified] is a 47-year-old individual presenting for initial oncology consultation regarding recently diagnosed non-small cell lung cancer. The patient reports a several-month history of persistent, dry cough and increasing fatigue, which prompted evaluation by their primary care provider. Initial workup included a chest X-ray, which revealed a suspicious lung mass. The patient is a never smoker. Performance status is excellent, estimated at ECOG 0.

DIAGNOSTIC WORKUP:
Following the abnormal chest X-ray, the patient underwent a comprehensive diagnostic evaluation. A CT scan of the chest, abdomen, and pelvis confirmed a primary mass in the lung and identified enlarged ipsilateral mediastinal lymph nodes. A subsequent PET/CT scan demonstrated hypermetabolic activity in the primary lung mass and the involved mediastinal lymph nodes, without evidence of distant metastatic disease. Brain MRI was performed and was negative for intracranial metastases. A CT-guided biopsy of the lung mass confirmed the diagnosis of non-small cell lung cancer (NSCLC) with adenocarcinoma histology. Based on these findings, the patient was staged as AJCC Stage IIIB.

MOLECULAR STUDIES:
Molecular profiling on the tumor tissue was performed and revealed no actionable driver alterations, testing negative for EGFR, ALK, ROS1, BRAF, MET exon 14 skipping, RET, NTRK, KRAS, and ERBB2 mutations. PD-L1 expression was negative. Tumor mutational burden (TMB) was intermediate, measured at 2–16 mut/Mb.

PROBLEM SUMMARY:
This is a 47-year-old treatment-naive patient with newly diagnosed non-small cell lung cancer, adenocarcinoma histology, AJCC Stage IIIB. Molecular studies indicate no actionable driver alterations, negative PD-L1 expression, and intermediate tumor mutational burden. The patient is a never smoker with an excellent performance status.
```

---

## genie_NSCLC_GENIE-DFCI-027678_0  [PASS]

**Structured profile (ground truth):**
- Stage IV, adenocarcinoma, brain_mets=False
- EGFR=negative ALK=negative ROS1=negative BRAF=negative MET=negative RET=negative NTRK=negative PD-L1=unknown
- biomarkers_available=True
- actual_treatment (held out): Cisplatin, Pemetrexed Disodium

**Generated note:**
```
Patient name [De-identified] DOB [De-identified] Medical record number [De-identified] Date of service [De-identified] Referring Provider: Dr. [De-identified]

I am seeing a 45-year-old patient as a new patient for newly diagnosed non-small cell lung cancer. The history was obtained from the patient, along with my review of all available records.

**History of Present Illness (HPI):**
The patient presents for initial oncology evaluation following a recent diagnosis of non-small cell lung cancer. The patient initially presented to their primary care physician several weeks ago with a several-month history of persistent cough, increasing dyspnea on exertion, and recent onset of localized back pain. They also report some unintentional weight loss over the past few months. The patient is a former smoker, having quit over 1 year ago. Performance status is generally good, with the patient able to perform most activities of daily living independently, though activity levels have decreased due to fatigue and pain.

**Diagnostic Workup:**
Initial workup included a chest X-ray which showed a suspicious lung mass. This was followed by a CT scan of the chest, abdomen, and pelvis, which confirmed a primary lung mass and revealed suspicious lytic lesions in the lumbar spine. A subsequent biopsy of the lung mass confirmed adenocarcinoma histology. Further staging with a PET/CT scan demonstrated hypermetabolic activity in the primary lung lesion and confirmed metastatic disease to multiple osseous sites, including the lumbar spine and pelvis. A dedicated MRI of the brain was performed, which showed no evidence of intracranial metastatic disease. Based on this comprehensive workup, the patient is diagnosed with Stage IV non-small cell lung cancer (adenocarcinoma) with bone metastases.

**Molecular Studies:**
Molecular profiling was performed on the tumor tissue, revealing the following results:
*   An activating ERBB2 exon 20 insertion was detected.
*   The tumor was negative for mutations in EGFR, ALK rearrangements, ROS1 rearrangements, BRAF mutations, MET exon 14 skipping, RET fusions, NTRK fusions, and KRAS mutations.
*   PD-L1 expression was not tested, consistent with the timing of sequencing prior to its standard clinical utility.
*   Tumor Mutational Burden (TMB) was reported as intermediate (2–16 mut/Mb).

**Problem Summary:**
In summary, this is a 45-year-old patient with newly diagnosed, treatment-naive Stage IV non-small cell lung cancer, adenocarcinoma histology, with metastatic disease to bone. Molecular profiling identified an activating ERBB2 exon 20 insertion. Other common driver mutations (EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS) were negative. PD-L1 expression was not assessed, and Tumor Mutational Burden was intermediate. The patient is currently experiencing symptoms related to their disease, including cough, dyspnea, fatigue, and bone pain.
```

---

## genie_NSCLC_GENIE-VICC-539512_0  [PASS]

**Structured profile (ground truth):**
- Stage IV, adenocarcinoma, brain_mets=False
- EGFR=negative ALK=negative ROS1=negative BRAF=negative MET=negative RET=negative NTRK=not_on_panel PD-L1=intermediate
- biomarkers_available=True
- actual_treatment (held out): Carboplatin, Investigational Drug, Pemetrexed Disodium

**warnings:**
- brain_mets=False but note appears to mention brain metastasis

**Generated note:**
```
**CONSULTATION NOTE**

**Patient:** [De-identified Patient Name]
**DOB:** [De-identified Date of Birth]
**MRN:** [De-identified Medical Record Number]
**Date of Service:** [De-identified Date]

**HPI:**
This is a 66-year-old patient presenting for an initial oncology consultation regarding a new diagnosis of non-small cell lung cancer (NSCLC). The patient reports a several-month history of persistent, non-productive cough and increasing exertional dyspnea. Over the past few weeks, they also noted some mild, intermittent left-sided chest discomfort and generalized fatigue. The patient is a former smoker, having quit more than one year ago, with a prior smoking history of approximately [De-identified] pack-years. These symptoms prompted a visit to their primary care physician, who ordered an initial chest X-ray, revealing an abnormality in the left lung and a small pleural effusion.

**Diagnostic Workup:**
Following the abnormal chest X-ray, a CT scan of the chest, abdomen, and pelvis was performed, which confirmed a spiculated mass in the left upper lobe measuring approximately [De-identified] cm and a moderate left pleural effusion. Multiple mediastinal and hilar lymph nodes were also noted to be enlarged. A subsequent PET/CT scan demonstrated hypermetabolic activity within the left upper lobe mass, the enlarged mediastinal and hilar lymph nodes, and the left pleural effusion. No other distant sites of hypermetabolic disease were identified. A CT-guided core needle biopsy of the left upper lobe mass was performed, confirming adenocarcinoma histology. Thoracentesis was also performed, and cytology of the pleural fluid was positive for malignant cells. A brain MRI was performed as part of the staging workup and was negative for intracranial metastatic disease. Based on these findings, the patient's non-small cell lung cancer is staged as AJCC 8th Edition Stage IV (M1a).

**Molecular Studies:**
Molecular profiling was performed on the tumor tissue. Results indicate no actionable driver alteration identified, specifically negative for EGFR, ALK, ROS1, BRAF, MET exon 14 skipping, RET fusion, KRAS mutation, and ERBB2 (HER2) amplification. PD-L1 expression was positive, with a tumor proportion score (TPS) of 1-49%. Tumor mutational burden (TMB) was low (<2 mut/Mb).

**Past Medical History:**
Unremarkable, aside from presenting malignancy.

**Social History:**
Former smoker, quit >1 year ago.

**Review of Systems:**
Reviewed and largely negative except as described in HPI.

**Problem Summary:**
This 66-year-old patient has newly diagnosed non-small cell lung cancer, adenocarcinoma histology, AJCC Stage IV (M1a) due to malignant pleural effusion. The patient is treatment-naive. Molecular profiling shows no actionable driver alterations, PD-L1 TPS is 1-49%, and TMB is low. The patient requires initiation of systemic therapy.
```

---

## genie_NSCLC_GENIE-MSK-P-0022372_0  [PASS]

**Structured profile (ground truth):**
- Stage IV, adenocarcinoma, brain_mets=False
- EGFR=negative ALK=negative ROS1=positive BRAF=negative MET=negative RET=negative NTRK=negative PD-L1=high
- biomarkers_available=True
- actual_treatment (held out): Bevacizumab, Cisplatin, Pemetrexed Disodium

**Generated note:**
```
Patient name: [De-identified Patient Name]
DOB: [De-identified DOB]
Medical record number: [De-identified MRN]
Date of service: [De-identified Date]
Referring Provider: [De-identified Referring Provider]

**History of Present Illness (HPI):**
The patient is a 62-year-old individual presenting for initial oncology consultation regarding a recent diagnosis of non-small cell lung cancer. The patient initially sought medical attention several weeks prior due to the insidious onset of a persistent, non-productive cough and progressive dyspnea on exertion, which were accompanied by a several-month history of unintentional weight loss and generalized fatigue. An initial workup for these symptoms led to the discovery of a pulmonary mass. The patient is a never-smoker.

**Diagnostic Workup:**
Following the patient's presentation, a chest X-ray revealed a suspicious pulmonary lesion. Subsequent contrast-enhanced computed tomography (CT) of the chest, abdomen, and pelvis further characterized a primary lung mass, identified an associated pleural effusion, and demonstrated multiple enlarged lymph nodes in distant nodal basins, consistent with metastatic disease. A positron emission tomography (PET)/CT scan was performed, confirming hypermetabolic activity in the primary lung lesion, the pleura, and the involved distant lymph nodes, with no other sites of distant metastatic disease identified. A CT-guided core needle biopsy of the primary lung mass was performed, which yielded tissue confirming the diagnosis of non-small cell lung cancer, adenocarcinoma histology. The patient's Eastern Cooperative Oncology Group (ECOG) performance status is currently assessed as 1, indicating they are fully ambulatory and able to perform light work. Based on the comprehensive diagnostic imaging and pathologic findings, the patient is formally staged as AJCC Stage IV non-small cell lung cancer.

**Molecular Studies:**
Comprehensive genomic profiling was performed on the tumor tissue obtained from biopsy. This analysis identified an actionable driver alteration in the form of a ROS1 rearrangement. Further molecular testing specifically evaluated for other common oncogenic drivers and yielded negative results for EGFR mutations, ALK rearrangements, BRAF mutations, MET exon 14 skipping alterations, RET fusions, NTRK fusions, KRAS mutations, and ERBB2 (HER2) amplifications/mutations. Programmed death-ligand 1 (PD-L1) immunohistochemistry was performed, demonstrating a tumor proportion score (TPS) of ≥50%, indicative of high expression. Tumor mutational burden (TMB) analysis reported an intermediate value, falling within the range of 2–16 mutations per megabase (mut/Mb).

**Problem Summary:**
In summary, this 62-year-old patient presents with newly diagnosed, treatment-naive non-small cell lung cancer of adenocarcinoma histology. The disease is classified as AJCC Stage IV, with metastatic involvement identified in the pleura and distant lymph nodes. Key molecular findings include a ROS1 rearrangement, a PD-L1 tumor proportion score of ≥50%, and an intermediate tumor mutational burden. The patient's current functional status is ECOG 1.
```

---

## genie_NSCLC_GENIE-MSK-P-0015492_0  [PASS]

**Structured profile (ground truth):**
- Stage IV, adenocarcinoma, brain_mets=False
- EGFR=negative ALK=negative ROS1=negative BRAF=negative MET=negative RET=negative NTRK=negative PD-L1=intermediate
- biomarkers_available=True
- actual_treatment (held out): Bevacizumab, Cisplatin, Pemetrexed Disodium

**warnings:**
- brain_mets=False but note appears to mention brain metastasis

**Generated note:**
```
**HPI:**
[De-identified] is a 52-year-old patient presenting for initial oncology consultation regarding a recent diagnosis of non-small cell lung cancer. The patient initially sought medical attention several weeks ago for a persistent cough and mild exertional dyspnea. Initial evaluation by their primary care physician led to a chest X-ray, which revealed a suspicious lung mass. The patient reports a history of former smoking, having quit over one year ago. Performance status is currently excellent, with the patient maintaining full activity and independence in daily life. This is the patient's first encounter with medical oncology, and they are treatment-naive for this malignancy.

**Diagnostic Workup:**
Following the abnormal chest X-ray, a comprehensive diagnostic workup was initiated. A CT scan of the chest, abdomen, and pelvis confirmed a primary lung mass and identified enlarged distant lymph nodes, as well as a suspicious lesion in the left adrenal gland. A subsequent PET-CT scan demonstrated avid uptake in the primary lung mass, the distant lymph nodes, and the adrenal lesion, further supporting metastatic disease. To confirm the diagnosis, a CT-guided biopsy of the lung mass was performed, which revealed non-small cell lung cancer with adenocarcinoma histology. A brain MRI was also performed as part of the staging workup and was negative for any intracranial metastases. Based on these findings, the patient is diagnosed with AJCC Stage IV non-small cell lung cancer.

**Molecular Studies:**
Molecular profiling was performed on the tumor tissue. Results indicate no actionable driver alterations, with testing specifically negative for EGFR mutations, ALK rearrangements, ROS1 rearrangements, BRAF mutations, MET exon 14 skipping mutations, RET fusions, NTRK fusions, KRAS mutations, and ERBB2 mutations. PD-L1 expression was positive, with a tumor proportion score (TPS) of 1-49%. Tumor mutational burden (TMB) was found to be intermediate, ranging from 2–16 mutations per megabase (mut/Mb). Additionally, a STK11 loss-of-function mutation was identified.

**Problem Summary:**
In summary, this is a 52-year-old former smoker with newly diagnosed AJCC Stage IV non-small cell lung cancer, adenocarcinoma histology, presenting with metastatic disease involving distant lymph nodes and the adrenal gland. Molecular profiling demonstrates no actionable driver alterations, PD-L1 TPS 1-49%, intermediate TMB, and an STK11 loss-of-function mutation. The patient is treatment-naive and presents for discussion of management options.
```

---

## genie_NSCLC_GENIE-MSK-P-0006844_2  [PASS]

**Structured profile (ground truth):**
- Stage IIIA, adenocarcinoma, brain_mets=False
- EGFR=exon_19_del ALK=negative ROS1=negative BRAF=negative MET=negative RET=negative NTRK=negative PD-L1=high
- biomarkers_available=True
- actual_treatment (held out): Cisplatin, Pemetrexed Disodium

**warnings:**
- brain_mets=False but note appears to mention brain metastasis

**Generated note:**
```
**Patient:** [De-identified Name], 59-year-old
**MRN:** [De-identified MRN]
**Date of Visit:** [De-identified Date]
**Attending Physician:** [De-identified Physician Name], MD

**HISTORY OF PRESENT ILLNESS:**
The patient is a 59-year-old individual presenting for initial oncology consultation regarding a recent diagnosis of non-small cell lung cancer (NSCLC). The patient reports experiencing a persistent cough for the past several months, initially attributed to seasonal allergies, but which progressively worsened and became associated with mild dyspnea on exertion. There has been no reported hemoptysis, fevers, or chills. The patient denies significant unintended weight loss or night sweats. Due to the persistence of symptoms, the patient sought evaluation from their primary care physician, which initiated the diagnostic workup. The patient has a past medical history significant for a prior malignancy of melanoma, now resolved. The patient is a never smoker and reports a good functional status, with an ECOG performance status of 0-1, able to perform all usual activities without restriction or with only mild symptoms.

**DIAGNOSTIC WORKUP:**
Initial diagnostic evaluation included a chest X-ray that revealed a suspicious mass in the left upper lobe. This was followed by a contrast-enhanced CT scan of the chest, abdomen, and pelvis, which confirmed a primary lung mass measuring approximately 4.5 cm in the left upper lobe, along with several enlarged ipsilateral mediastinal and subcarinal lymph nodes. No evidence of distant metastatic disease was identified in the abdomen or pelvis. A subsequent PET/CT scan demonstrated hypermetabolic activity in the left upper lobe mass and the involved mediastinal/subcarinal lymph nodes, with no other sites of avid disease. Brain MRI was performed to complete staging and was negative for intracranial metastases. A CT-guided core biopsy of the left upper lobe mass was performed, confirming adenocarcinoma histology. Endobronchial ultrasound with transbronchial needle aspiration (EBUS-TBNA) of the enlarged mediastinal lymph nodes also confirmed metastatic adenocarcinoma. Based on these findings, the patient's cancer is staged as AJCC Stage IIIA.

**MOLECULAR STUDIES:**
Molecular profiling was performed on the tumor biopsy specimen. Key findings include:
*   **Actionable Driver Mutation:** EGFR exon 19 deletion (sensitizing).
*   **Negative for:** ALK rearrangement, ROS1 rearrangement, BRAF V600E mutation, MET exon 14 skipping mutation, RET fusion, NTRK fusion, KRAS mutation, ERBB2 (HER2) mutation.
*   **PD-L1 Expression:** Positive, with a tumor proportion score (TPS) of ≥50%.
*   **Tumor Mutational Burden (TMB):** Intermediate (2–16 mut/Mb).

**PROBLEM SUMMARY:**
This 59-year-old patient presents with newly diagnosed, treatment-naive non-small cell lung cancer, adenocarcinoma histology, AJCC Stage IIIA. The disease involves a primary left upper lobe mass with ipsilateral mediastinal and subcarinal lymph node involvement, without evidence of distant metastasis, including to the brain. Molecular testing revealed a sensitizing EGFR exon 19 deletion, high PD-L1 expression (TPS ≥50%), and intermediate TMB. The patient has a history of prior melanoma. This consultation is for the discussion of further management strategies.
```

---

## genie_NSCLC_GENIE-MSK-P-0013483_0  [PASS]

**Structured profile (ground truth):**
- Stage IIIA, adenocarcinoma, brain_mets=False
- EGFR=unknown ALK=unknown ROS1=unknown BRAF=unknown MET=unknown RET=unknown NTRK=unknown PD-L1=unknown
- biomarkers_available=False
- actual_treatment (held out): Crizotinib

**Generated note:**
```
[De-identified] [De-identified], 58-year-old, presents for initial oncology consultation regarding a recent diagnosis of non-small cell lung cancer. The history was obtained from the patient and review of available medical records.

**HPI:**
The patient is a 58-year-old never smoker who initially presented to their primary care physician several weeks ago with a persistent cough and mild, exertional dyspnea. Initial workup included a chest X-ray, which revealed a suspicious right upper lobe mass. Subsequent CT chest confirmed a primary lung mass with associated mediastinal lymphadenopathy. The patient reports an ECOG performance status of 1, indicating mild symptoms but fully ambulatory and able to perform light work. There has been no significant weight loss, fevers, or night sweats. No neurological symptoms were reported.

**Diagnostic Workup:**
Following the initial imaging, the patient underwent a bronchoscopy with endobronchial ultrasound (EBUS)-guided biopsy of the right upper lobe mass and mediastinal lymph nodes. Pathology confirmed adenocarcinoma of the lung. Further staging evaluation included a whole-body PET-CT scan, which demonstrated hypermetabolic activity in the primary right upper lobe lesion and in several ipsilateral mediastinal lymph nodes, consistent with locoregional disease. Importantly, no distant metastatic sites were identified on PET-CT. A brain MRI was also performed as part of the staging workup and showed no evidence of intracranial metastases. Based on these findings, the patient's cancer is staged as AJCC Stage IIIA.

**Molecular Studies:**
Tumor tissue obtained from the biopsy was submitted for comprehensive molecular profiling. At the time of this consultation, the full sequencing panel results are pending. However, preliminary testing has shown that the tumor is PD-L1 negative and has a low tumor mutational burden (TMB <2 mut/Mb).

**Problem Summary:**
The patient is a 58-year-old, treatment-naive individual with newly diagnosed non-small cell lung cancer, adenocarcinoma histology, AJCC Stage IIIA. The tumor is PD-L1 negative and has a low TMB, with comprehensive molecular profiling results pending. The patient is currently in good general condition with an ECOG PS of 1. We will now proceed to discuss potential treatment strategies for this locoregionally advanced disease.
```

---

## genie_NSCLC_GENIE-DFCI-108464_2  [PASS]

**Structured profile (ground truth):**
- Stage IV, adenocarcinoma, brain_mets=True
- EGFR=negative ALK=negative ROS1=negative BRAF=negative MET=negative RET=negative NTRK=negative PD-L1=unknown
- biomarkers_available=True
- actual_treatment (held out): Carboplatin, Pembrolizumab, Pemetrexed Disodium

**Generated note:**
```
**HPI:**
This 77-year-old patient presents for an initial oncology consultation regarding a new diagnosis of non-small cell lung cancer. The patient first noted symptoms approximately [De-identified Month] [De-identified Year], including a persistent cough, increasing shortness of breath with exertion, and generalized fatigue. They also reported new-onset headaches and a dull ache in the lower back, which prompted further evaluation. The patient has a history of melanoma and is a former smoker, having quit more than one year ago. Their current performance status is assessed as ECOG 1.

**Diagnostic Workup:**
The diagnostic workup initiated by the primary care provider included a chest X-ray demonstrating a right upper lobe mass. This was followed by a contrast-enhanced CT of the chest, abdomen, and pelvis, which revealed a primary lung lesion measuring approximately 4.5 cm in the right upper lobe, along with enlarged mediastinal and right supraclavicular lymph nodes. A subsequent PET/CT scan confirmed hypermetabolic activity in the primary lung lesion and these lymph nodes, as well as a focus of increased uptake in the T10 vertebral body concerning for osseous metastasis. A brain MRI was also performed, which identified multiple enhancing lesions in the frontal and parietal lobes, consistent with brain metastases. Biopsy of the right upper lobe lung mass, performed via CT-guided needle aspiration, confirmed the diagnosis of non-small cell lung cancer, adenocarcinoma type. Based on these findings, the patient's cancer is staged as AJCC Stage IV.

**Molecular Studies:**
Molecular profiling of the tumor tissue was performed and revealed a KRAS G12C mutation. Comprehensive genomic testing was negative for other common actionable alterations, including EGFR mutations, ALK rearrangements, ROS1 fusions, BRAF mutations, MET exon 14 skipping mutations, RET fusions, NTRK fusions, and ERBB2 (HER2) mutations. PD-L1 immunohistochemistry demonstrated negative expression. Tumor mutational burden (TMB) was reported as intermediate (2–16 mut/Mb).

**Problem Summary:**
This 77-year-old patient presents with newly diagnosed, treatment-naive non-small cell lung cancer, adenocarcinoma histology, AJCC Stage IV. The disease is metastatic to the brain, bone, and distant lymph nodes. Molecular studies revealed a KRAS G12C mutation, negative PD-L1 expression, and intermediate tumor mutational burden. The patient has a history of melanoma and is a former smoker.
```

---

## genie_NSCLC_GENIE-VICC-968402_0  [PASS]

**Structured profile (ground truth):**
- Stage IIIB, squamous, brain_mets=False
- EGFR=negative ALK=negative ROS1=negative BRAF=negative MET=negative RET=negative NTRK=negative PD-L1=unknown
- biomarkers_available=True
- actual_treatment (held out): Carboplatin, Paclitaxel

**warnings:**
- brain_mets=False but note appears to mention brain metastasis

**Generated note:**
```
REASON FOR VISIT: Initial oncology consultation for newly diagnosed non-small cell lung cancer.

IDENTIFICATION: [De-identified] is an 81-year-old patient presenting for initial oncology evaluation of newly diagnosed Stage IIIB non-small cell lung cancer.

HISTORY OF PRESENT ILLNESS:
The patient is an 81-year-old current smoker with a significant smoking history, who presents for initial oncology evaluation following a recent diagnosis of non-small cell lung cancer. Approximately three months prior to presentation, the patient began experiencing a persistent cough, which progressed to include increasing shortness of breath with exertion and a generalized sense of fatigue. There was also an unintentional weight loss of approximately 10 pounds over this period. These symptoms prompted a visit to their primary care physician.

Initial workup included a chest X-ray, which revealed a suspicious mass in the right upper lobe. This was followed by a contrast-enhanced CT scan of the chest, abdomen, and pelvis, which demonstrated a primary mass measuring approximately 4.5 cm in the right upper lobe, with extensive ipsilateral mediastinal and hilar lymphadenopathy. No distant metastatic disease was identified on this imaging. A subsequent MRI of the brain was performed, which was negative for any intracranial metastases.

A CT-guided biopsy of the lung mass was performed, and pathology confirmed the diagnosis of non-small cell lung cancer, specifically squamous cell carcinoma. Subsequent comprehensive genomic profiling was performed on the tumor tissue.

Molecular Studies:
Tumor molecular profiling revealed high-level MET amplification. Testing for other common driver mutations was negative, including EGFR, ALK, ROS1, BRAF, MET exon 14 skipping mutations, RET, NTRK, KRAS, and ERBB2. PD-L1 expression was not assessed, as this testing was not standard of care at the time of initial sequencing. Tumor mutational burden (TMB) was intermediate (2–16 mut/Mb).

Based on the imaging findings and pathology, the patient is diagnosed with AJCC Stage IIIB non-small cell lung cancer.

Review of Systems:
Constitutional: Positive for fatigue, unintentional weight loss. Negative for fevers, chills, night sweats.
Respiratory: Positive for persistent cough, dyspnea on exertion. Negative for hemoptysis, wheezing.
Cardiovascular: Negative for chest pain, palpitations, leg swelling.
Gastrointestinal: Negative for nausea, vomiting, diarrhea, constipation, abdominal pain.
Musculoskeletal: Negative for arthralgias, myalgias, bone pain.
Neurological: Negative for headache, dizziness, focal weakness, numbness, tingling.
All other systems reviewed and are negative.

Past Medical History:
Hypertension
Hyperlipidemia
Osteoarthritis

Past Surgical History:
Cholecystectomy (remote)
Appendectomy (remote)

Current Medications:
Lisinopril 10 mg daily
Atorvastatin 20 mg daily
Acetaminophen 500 mg as needed for pain

Allergies/Contraindications:
No known drug allergies.

Social History:
The patient has a significant smoking history and is a current smoker.

OBJECTIVE ASSESSMENT:
Physical Exam:
Vitals: BP 130/80, HR 78, RR 18, Temp 36.8 C, SpO2 96% on room air.
General: 81-year-old patient, appears somewhat fatigued but in no acute distress. Well-oriented. ECOG Performance Status 1.
HEENT: Normocephalic, atraumatic. Conjunctivae anicteric. Oropharynx clear.
Neck: Supple. No palpable lymphadenopathy. Trachea midline.
Lungs: Decreased breath sounds at the right upper lobe, otherwise clear to auscultation bilaterally. No wheezes, rales, or rhonchi.
Cardiac: Regular rate and rhythm, no murmurs, rubs, or gallops.
Abdomen: Soft, non-tender, non-distended. Normoactive bowel sounds. No hepatosplenomegaly.
Extremities: No clubbing, cyanosis, or edema. Pulses 2+ bilaterally.
Neurological: Alert and oriented x3. Cranial nerves intact. Motor and sensory intact. No focal deficits.

Diagnostic Workup Summary:
Imaging: Chest X-ray showed a right upper lobe mass. CT chest, abdomen, pelvis confirmed a primary right upper lobe mass with extensive ipsilateral mediastinal and hilar lymphadenopathy. No distant metastases were identified. MRI brain was negative for intracranial metastases.
Pathology: Biopsy of the lung mass confirmed squamous cell carcinoma.
Molecular: Comprehensive genomic profiling demonstrated high-level MET amplification. Negative for EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, ERBB2. PD-L1 was not tested. TMB was intermediate (2–16 mut/Mb).

Problem Summary:
[De-identified] is an 81-year-old current smoker with newly diagnosed AJCC Stage IIIB non-small cell lung cancer, squamous histology. The disease is characterized by a right upper lobe primary tumor with extensive ipsilateral mediastinal and hilar lymphadenopathy, without evidence of distant metastatic spread. Molecular testing revealed high-level MET amplification, with other common driver mutations being negative. PD-L1 expression was not assessed, and TMB is intermediate. The patient is treatment-naive and presents for initial oncology evaluation.
```

---

## genie_NSCLC_GENIE-VICC-535531_0  [PASS]

**Structured profile (ground truth):**
- Stage IV, adenocarcinoma, brain_mets=False
- EGFR=exon_19_del ALK=negative ROS1=negative BRAF=negative MET=negative RET=negative NTRK=not_on_panel PD-L1=intermediate
- biomarkers_available=True
- actual_treatment (held out): Afatinib Dimaleate

**Generated note:**
```
[De-identified Patient Name]
DOB: [De-identified DOB]
MRN: [De-identified MRN]
Date of Service: [De-identified Date]
Referring Provider: [De-identified Referring Provider]

This 52-year-old patient is seen today for an initial oncology consultation regarding newly diagnosed non-small cell lung cancer. The history was obtained from the patient, along with review of available medical records.

**HPI (History of Present Illness):**
The patient initially presented approximately three months ago with a persistent cough and increasing shortness of breath, accompanied by generalized fatigue and unintentional weight loss of approximately 10 pounds over several weeks. The patient is a never smoker. Initial evaluation included a chest X-ray, which revealed a suspicious lung mass. Subsequent imaging and biopsy confirmed the diagnosis of non-small cell lung cancer. The patient reports an ECOG performance status of 1, able to carry out light work and maintain independence in daily activities, though experiencing some fatigue and occasional mild discomfort attributed to the disease. No significant pain requiring regular analgesia is reported at this time.

**Diagnostic Workup:**
Initial diagnostic workup involved a CT scan of the chest, abdomen, and pelvis, which identified a primary mass in the right upper lobe of the lung, along with suspicious lesions in the liver, right adrenal gland, and a contralateral lung nodule. Enlarged mediastinal and hilar lymph nodes were also noted. A CT-guided biopsy of the right lung mass confirmed adenocarcinoma histology. Comprehensive staging with a PET-CT scan further delineated the extent of disease, showing avid uptake in the primary lung lesion, multiple bone lesions (e.g., in the thoracic spine), the known liver and adrenal lesions, a contralateral lung nodule, and distant lymphadenopathy (e.g., supraclavicular and abdominal nodes). Based on these findings, the patient is diagnosed with Stage IV non-small cell lung cancer, adenocarcinoma.

**Molecular Studies:**
Molecular profiling was performed on the tumor tissue, revealing the following results:
*   **Actionable Drivers:** EGFR exon 19 deletion (sensitizing) detected.
*   **Negative for:** ALK rearrangement, ROS1 rearrangement, BRAF V600E mutation, MET exon 14 skipping mutation, RET fusion, KRAS mutation, ERBB2 (HER2) mutation.
*   **PD-L1 Expression:** Positive, with a tumor proportion score (TPS) of 1–49%.
*   **Tumor Mutational Burden (TMB):** High (>16 mut/Mb).

**Problem Summary:**
This 52-year-old patient presents with newly diagnosed, treatment-naive Stage IV non-small cell lung cancer of adenocarcinoma histology. The disease is characterized by metastatic involvement of bone, liver, adrenal gland, contralateral lung, and distant lymph nodes. Molecular testing demonstrates an EGFR exon 19 deletion (sensitizing), PD-L1 expression of 1-49%, and high tumor mutational burden (>16 mut/Mb), with no other common actionable drivers detected. The patient is seeking initial oncology evaluation and discussion of systemic treatment options.
```

---

## genie_NSCLC_GENIE-DFCI-024726_1  [PASS]

**Structured profile (ground truth):**
- Stage IV, adenocarcinoma, brain_mets=False
- EGFR=unknown ALK=unknown ROS1=unknown BRAF=unknown MET=unknown RET=unknown NTRK=unknown PD-L1=unknown
- biomarkers_available=False
- actual_treatment (held out): Erlotinib Hydrochloride

**Generated note:**
```
[De-identified]
[De-identified], [De-identified]

**HPI:**
Mr./Ms. [De-identified] is a 68-year-old individual presenting for an initial oncology consultation regarding recently diagnosed non-small cell lung cancer (NSCLC). He/She initially presented to his/her primary care physician several months ago with a persistent, non-productive cough and progressive dyspnea on exertion. These symptoms were accompanied by generalized fatigue and a reported 10-pound unintentional weight loss over the past three months. His/Her performance status is currently Eastern Cooperative Oncology Group (ECOG) 1, indicating he/she is ambulatory and able to carry out light work. He/She has a past medical history significant for being a former smoker, having quit tobacco use over one year ago. The patient is treatment-naive, and this consultation is the initial oncology evaluation to discuss management options.

**Diagnostic Workup:**
The initial evaluation commenced with a chest X-ray, which demonstrated a suspicious mass in the lung and a moderate pleural effusion. This prompted a comprehensive staging workup, including a contrast-enhanced CT scan of the chest, abdomen, and pelvis, followed by a PET/CT scan. The CT chest confirmed a dominant lung mass and extensive nodular thickening of the pleura with a significant pleural effusion. The PET/CT scan demonstrated intense hypermetabolic activity within the primary lung lesion and diffuse uptake throughout the pleura, consistent with metastatic disease. A diagnostic thoracentesis was performed, and cytology of the pleural fluid confirmed the presence of adenocarcinoma. Subsequent biopsy of a pleural nodule further corroborated the diagnosis of non-small cell lung cancer, adenocarcinoma histology. Based on these findings, the patient was staged as AJCC Stage IV, with metastatic involvement of the pleura. Brain imaging (MRI brain) was performed and showed no evidence of intracranial metastatic disease.

**Molecular Studies:**
Comprehensive molecular profiling of the tumor tissue is not yet available and remains pending. PD-L1 expression was not tested, as the diagnostic workup occurred prior to the routine implementation of PD-L1 testing as standard of care in [De-identified]. Tumor mutational burden (TMB) analysis, when performed, revealed a low TMB, measured at less than 2 mutations/megabase.

**Problem Summary:**
Mr./Ms. [De-identified] is a 68-year-old former smoker with newly diagnosed, treatment-naive non-small cell lung cancer, adenocarcinoma histology, AJCC Stage IV, with metastatic disease limited to the pleura. Molecular profiling is pending, PD-L1 was not tested, and TMB is low. This is an initial consultation to establish a management plan.
```

---

## genie_NSCLC_GENIE-MSK-P-0015978_0  [PASS]

**Structured profile (ground truth):**
- Stage IV, nos, brain_mets=False
- EGFR=negative ALK=negative ROS1=negative BRAF=negative MET=negative RET=negative NTRK=negative PD-L1=unknown
- biomarkers_available=True
- actual_treatment (held out): Cisplatin, Pemetrexed Disodium

**Generated note:**
```
**Patient Identification:**
[De-identified Name], a 49-year-old individual, presents for initial oncology consultation regarding a recent diagnosis of non-small cell lung cancer.

**History of Present Illness:**
This 49-year-old individual was referred to medical oncology for evaluation and management of newly diagnosed non-small cell lung cancer (NSCLC). The patient's initial presentation approximately two months prior involved a persistent dry cough and mild dyspnea on exertion. These symptoms prompted a visit to their primary care physician, leading to a chest X-ray that revealed a suspicious mass in the right lung. Subsequent imaging with a CT scan of the chest, abdomen, and pelvis confirmed a primary mass in the right upper lobe, along with a distinct, smaller nodule identified in the contralateral (left) lung. A PET/CT scan demonstrated FDG avidity in both lesions, consistent with malignancy. The diagnosis of NSCLC, not otherwise specified (NOS) histology, was confirmed via a CT-guided core needle biopsy of the right lung mass. Further staging workup, including a brain MRI, was negative for intracranial metastases. Given the presence of disease in the contralateral lung, the patient was staged as AJCC Stage IV. The patient is a former smoker, having quit less than one year ago. This is the patient's first oncology evaluation, and they are treatment-naive.

**Diagnostic Workup:**
Initial diagnostic evaluation included:
*   **Chest X-ray:** Revealed a right upper lobe mass.
*   **CT Chest/Abdomen/Pelvis:** Demonstrated a primary mass in the right upper lobe measuring approximately [plausible size, e.g., 4.5 cm], and a separate, distinct nodule in the left lower lobe measuring [plausible size, e.g., 1.2 cm]. No evidence of intra-abdominal metastases or significant lymphadenopathy was noted.
*   **PET/CT Scan:** Showed hypermetabolic activity corresponding to the right upper lobe mass and the left lower lobe nodule. No other hypermetabolic lesions suggestive of distant metastasis were identified.
*   **MRI Brain:** Performed for metastatic workup, revealed no evidence of brain metastases.
*   **Biopsy:** CT-guided core needle biopsy of the right upper lobe mass confirmed the diagnosis of non-small cell lung carcinoma, NOS histology.

Based on these findings, the patient is diagnosed with AJCC Stage IV NSCLC due to the presence of distant metastasis to the contralateral lung.

**Molecular Studies:**
Molecular profiling was performed on the tumor tissue, yielding the following results:
*   **Actionable Drivers:** High-level MET amplification was detected.
*   **Negative for:** EGFR mutations, ALK rearrangements, ROS1 rearrangements, BRAF mutations, MET exon 14 skipping mutations, RET rearrangements, NTRK fusions, KRAS mutations, and ERBB2 (HER2) alterations.
*   **PD-L1 Expression:** Negative.
*   **Tumor Mutational Burden (TMB):** Intermediate (2–16 mut/Mb).

**Problem Summary:**
[De-identified Name] is a 49-year-old individual with newly diagnosed, treatment-naive non-small cell lung cancer, NOS histology, AJCC Stage IV, with metastasis to the contralateral lung. Molecular studies revealed high-level MET amplification, negative PD-L1 expression, and intermediate tumor mutational burden. The patient is a former smoker.
```

---

## genie_NSCLC_GENIE-MSK-P-0018814_0  [PASS]

**Structured profile (ground truth):**
- Stage IV, adenocarcinoma, brain_mets=True
- EGFR=negative ALK=negative ROS1=negative BRAF=negative MET=negative RET=negative NTRK=negative PD-L1=intermediate
- biomarkers_available=True
- actual_treatment (held out): Bevacizumab, Carboplatin, Pemetrexed Disodium

**Generated note:**
```
**HPI:**
[De-identified] is a 64-year-old individual presenting for initial oncology consultation following a recent diagnosis of non-small cell lung cancer. The patient initially presented with a persistent cough, progressive shortness of breath, and unintentional weight loss over the past several months. Additionally, the patient reported new onset headaches and increasing lower back pain. The patient has a history of former smoking, having quit over one year ago.

**Diagnostic Workup:**
The initial diagnostic workup commenced with a chest X-ray, which prompted a CT scan of the chest, abdomen, and pelvis. This imaging revealed a primary lung mass, along with suspicious lesions in the contralateral lung, bone, and subcutaneous tissue. A subsequent PET/CT scan confirmed widespread metabolically active disease consistent with metastatic spread to these sites. Due to the reported headaches, a brain MRI was performed, which identified multiple enhancing lesions consistent with brain metastases. Histologic confirmation was obtained via CT-guided core biopsy of the primary lung lesion, which demonstrated adenocarcinoma. Biopsy of a subcutaneous nodule also confirmed metastatic adenocarcinoma. Based on these findings, the patient is diagnosed with Stage IV (M1) non-small cell lung cancer. The patient's current performance status is ECOG 1.

**Molecular Studies:**
Comprehensive molecular profiling was performed on the tumor tissue. Results indicated the presence of an actionable KRAS G12C mutation. Testing for other common oncogenic drivers was negative, specifically for EGFR mutations, ALK fusions, ROS1 fusions, BRAF mutations, MET exon 14 skipping, RET fusions, NTRK fusions, and ERBB2 (HER2) mutations. Programmed death-ligand 1 (PD-L1) immunohistochemistry was positive, with a tumor proportion score (TPS) of 1–49%. Tumor mutational burden (TMB) was assessed as intermediate, falling within the range of 2–16 mutations/megabase.

**Problem Summary:**
[De-identified] is a 64-year-old treatment-naive individual with newly diagnosed Stage IV (M1) non-small cell lung cancer, adenocarcinoma histology. The disease has metastasized to the brain, bone, contralateral lung, and subcutaneous tissue. Molecular analysis confirms an actionable KRAS G12C mutation, absence of other common driver alterations, positive PD-L1 expression (TPS 1–49%), and intermediate tumor mutational burden. The patient is here for initial discussion of therapeutic options.
```

---

## genie_NSCLC_GENIE-VICC-987046_0  [PASS]

**Structured profile (ground truth):**
- Stage IV, adenocarcinoma, brain_mets=False
- EGFR=exon_19_del ALK=negative ROS1=negative BRAF=negative MET=negative RET=negative NTRK=not_on_panel PD-L1=high
- biomarkers_available=True
- actual_treatment (held out): Erlotinib Hydrochloride

**Generated note:**
```
[De-identified] Medical Oncology Program
[De-identified] [De-identified], MD
[De-identified] [De-identified] [De-identified]
Phone: [De-identified] | Fax: [De-identified]

Initial Consultation [De-identified]
[De-identified]: [De-identified] [De-identified], MD, [De-identified]

[De-identified Date]

I had the pleasure of seeing [De-identified] [De-identified] for initial oncology consultation regarding recently diagnosed non-small cell lung cancer. The history was obtained from the patient, along with my review of all available medical records.

**History of Present Illness (HPI):**
This 72-year-old individual presents for initial oncology consultation following a recent diagnosis of non-small cell lung cancer (NSCLC). The patient, a never smoker, initially sought medical attention several weeks prior due to a persistent cough, increasing dyspnea on exertion, and generalized fatigue. A chest X-ray was performed, revealing a suspicious lung mass and a new right-sided pleural effusion. Subsequent diagnostic workup, including CT imaging, confirmed the presence of a primary lung lesion and a moderate-sized malignant pleural effusion. The patient reports an ECOG performance status of 1, maintaining independence in daily activities but experiencing some symptomatic limitations. No significant weight loss has been noted.

**Diagnostic Workup:**
Initial evaluation included a chest X-ray which demonstrated a right upper lobe mass and pleural effusion. This was followed by a contrast-enhanced CT scan of the chest, abdomen, and pelvis on [De-identified Date], which confirmed a [De-identified] cm spiculated mass in the right upper lobe, as well as a moderate right-sided pleural effusion. No other distant visceral metastases were identified on this staging scan. A brain MRI with contrast on [De-identified Date] revealed no evidence of intracranial metastatic disease.
Diagnostic confirmation was obtained via CT-guided biopsy of the right upper lobe lung mass on [De-identified Date]. Pathology review confirmed adenocarcinoma histology. Thoracentesis was performed on [De-identified Date], yielding cytology positive for malignant cells, consistent with metastatic adenocarcinoma. Based on these findings, the patient's cancer is staged as AJCC 8th Edition Stage IV (M1a).

**Molecular Studies:**
Comprehensive genomic profiling was performed on the tumor tissue obtained from the lung biopsy. Results indicate the presence of an **EGFR exon 19 deletion (sensitizing)**. Further analysis showed the tumor to be negative for ALK, ROS1, BRAF, MET exon 14 skipping, RET rearrangements, KRAS mutations, and ERBB2 (HER2) alterations.
Immunohistochemistry for PD-L1 expression was performed, demonstrating a **positive result with a Tumor Proportion Score (TPS) ≥50%**. Tumor Mutational Burden (TMB) analysis revealed a **high TMB, measured at >16 mutations/megabase (mut/Mb)**.

**Problem Summary:**
In summary, this is a 72-year-old never smoker recently diagnosed with treatment-naive, Stage IV (M1a) non-small cell lung cancer of adenocarcinoma histology. The disease is characterized by a primary lung mass and malignant pleural effusion. Molecular testing has identified an EGFR exon 19 deletion, a PD-L1 TPS ≥50%, and high tumor mutational burden (>16 mut/Mb). The patient maintains a good performance status. The primary concern is the management of advanced NSCLC with multiple actionable biomarkers.
```

---

## genie_NSCLC_GENIE-MSK-P-0022765_0  [PASS]

**Structured profile (ground truth):**
- Stage IIIA, adenocarcinoma, brain_mets=False
- EGFR=negative ALK=negative ROS1=negative BRAF=negative MET=negative RET=negative NTRK=negative PD-L1=unknown
- biomarkers_available=True
- actual_treatment (held out): Cisplatin, Pemetrexed Disodium

**warnings:**
- brain_mets=False but note appears to mention brain metastasis

**Generated note:**
```
**Date:** [De-identified Date]
**Patient:** [De-identified Patient Name], 55-year-old
**MRN:** [De-identified MRN]

**HPI:**
The patient is a 55-year-old individual presenting for initial oncology consultation regarding a new diagnosis of non-small cell lung cancer. The patient reports experiencing a persistent cough and mild exertional dyspnea for the past several months, which prompted an evaluation by their primary care provider. They also note some associated fatigue but deny significant weight loss or hemoptysis. Performance status is excellent, with the patient maintaining full activities of daily living and an ECOG performance status of 0-1. Past medical history is otherwise unremarkable. The patient is a former smoker, having quit more than one year ago, with a prior smoking history of approximately 20 pack-years.

**Diagnostic Workup:**
Initial chest X-ray revealed a suspicious left upper lobe mass, prompting a subsequent CT scan of the chest. This imaging confirmed a [plausible size, e.g., 4.5 cm] spiculated mass in the left upper lobe, along with several enlarged mediastinal lymph nodes. Further staging was performed with a PET/CT scan, which demonstrated hypermetabolic activity in the primary left upper lobe mass and in several ipsilateral mediastinal lymph nodes (e.g., stations 4L and 7). No distant metastatic disease was identified on the PET/CT scan. A brain MRI was also performed as part of the staging workup, which was negative for intracranial metastases. Percutaneous biopsy of the left upper lobe mass confirmed adenocarcinoma histology. Based on these findings, the patient was diagnosed with AJCC Stage IIIA Non-Small Cell Lung Cancer.

**Molecular Studies:**
Tissue obtained from the biopsy underwent comprehensive molecular profiling. Results indicate no actionable driver alterations were identified, with testing negative for EGFR mutations, ALK rearrangements, ROS1 rearrangements, BRAF V600E mutations, MET exon 14 skipping mutations, RET fusions, NTRK fusions, KRAS mutations, and ERBB2 mutations. PD-L1 expression was negative. Tumor mutational burden (TMB) was low (<2 mut/Mb).

**Problem Summary:**
This is a 55-year-old patient with newly diagnosed, treatment-naive Non-Small Cell Lung Cancer, adenocarcinoma histology, AJCC Stage IIIA. Staging workup confirms locoregional disease with mediastinal lymph node involvement and no evidence of distant metastases. Molecular profiling revealed no actionable driver alterations, negative PD-L1 expression, and low tumor mutational burden. The patient is currently asymptomatic apart from mild cough and dyspnea, with an excellent performance status. The purpose of this consultation is to discuss definitive management strategies.
```

---

## genie_NSCLC_GENIE-MSK-P-0009559_0  [FAIL]

**Structured profile (ground truth):**
- Stage IV, adenocarcinoma, brain_mets=True
- EGFR=negative ALK=negative ROS1=negative BRAF=negative MET=negative RET=negative NTRK=negative PD-L1=unknown
- biomarkers_available=True
- actual_treatment (held out): Carboplatin, Pemetrexed Disodium

**FAILURES:**
- brain_mets=True but no brain metastasis stated

**Generated note:**
```
[De-identified] Cancer Center
Medical Oncology Program
[De-identified]
Phone: [De-identified] | Fax: [De-identified]

Initial Consultation [De-identified]
Date: [De-identified]
Attending: [De-identified], MD

**HPI:**
Patient is a 78-year-old individual presenting for an initial oncology consultation regarding a recent diagnosis of non-small cell lung cancer. The patient reports a history of progressive cough, dyspnea, and generalized fatigue over the past several months, which prompted medical evaluation. He/she is a former smoker, having quit over 1 year ago. This is the patient's first oncology evaluation, and he/she is treatment-naive for this malignancy. The patient's performance status is estimated at ECOG 1, with mild symptoms limiting strenuous physical activity but able to carry out light work.

**Diagnostic Workup:**
Initial diagnostic imaging, including a chest X-ray and subsequent CT scan of the chest, revealed a suspicious mass in the right lung. Bronchoscopic biopsy of the lung mass confirmed the diagnosis of non-small cell lung cancer, specifically adenocarcinoma histology. Further staging workup, including a whole-body PET/CT scan and a dedicated brain MRI, demonstrated widespread metastatic disease. Metastatic sites identified include multiple lesions in the brain, osseous metastases in the axial skeleton, several nodules in the contralateral lung, numerous distant lymph nodes (e.g., supraclavicular, retroperitoneal), and a subcutaneous nodule on the anterior chest wall. Based on these findings, the patient is diagnosed with AJCC Stage IV NSCLC.

**Molecular Studies:**
Molecular profiling was performed on the tumor tissue. The comprehensive genomic analysis revealed no actionable driver alterations, testing negative for EGFR, ALK, ROS1, BRAF, MET exon 14 skipping mutations, RET fusions, NTRK fusions, KRAS mutations, and ERBB2 (HER2) alterations. PD-L1 expression was not tested, consistent with the standard of care for sequencing performed prior to 2017. Tumor mutational burden (TMB) was found to be intermediate, in the range of 2–16 mutations/Mb. Further analysis identified an STK11 loss-of-function mutation, which is recognized as a biomarker associated with primary resistance to PD-1 inhibitors.

**Problem Summary:**
This is an initial consultation for a 78-year-old treatment-naive individual with newly diagnosed AJCC Stage IV non-small cell lung cancer, adenocarcinoma histology. The disease is widespread, involving the brain, bone, contralateral lung, distant lymph nodes, and subcutaneous tissue. Molecular studies indicate no actionable driver mutations, intermediate tumor mutational burden, and the presence of an STK11 loss-of-function mutation, which has implications for immunotherapy response. PD-L1 status is unknown. The patient's current performance status is ECOG 1.
```

---

## genie_NSCLC_GENIE-MSK-P-0012890_2  [PASS]

**Structured profile (ground truth):**
- Stage IIIA, adenocarcinoma, brain_mets=False
- EGFR=negative ALK=negative ROS1=negative BRAF=negative MET=negative RET=negative NTRK=negative PD-L1=unknown
- biomarkers_available=True
- actual_treatment (held out): Carboplatin, Pemetrexed Disodium

**Generated note:**
```
[De-identified Clinic Name]
[De-identified Address]
[De-identified Phone]

**PATIENT NAME:** [De-identified Patient Name]
**DOB:** [De-identified Date of Birth]
**MRN:** [De-identified MRN]
**DATE OF VISIT:** [De-identified Date]

**HPI:**
This is a 79-year-old patient presenting for initial oncology consultation regarding a new diagnosis of non-small cell lung cancer. The patient first sought medical attention several months ago for persistent cough, progressive dyspnea, and a 10-pound unintentional weight loss over the past three months. Initial evaluation by their primary care physician included a chest X-ray which demonstrated a suspicious left upper lobe mass. The patient has a significant smoking history, currently smoking approximately one pack per day for 60 pack-years. They have a past medical history significant for bladder cancer, diagnosed several years prior and successfully treated with local therapy, currently in remission. This patient is treatment-naive for their current lung cancer diagnosis.

**Diagnostic Workup:**
Following the abnormal chest X-ray, a CT scan of the chest with contrast was performed, confirming a 4.5 cm spiculated mass in the left upper lobe with associated hilar and mediastinal lymphadenopathy. Subsequent CT-guided biopsy of the lung mass confirmed the diagnosis of non-small cell lung cancer, specifically adenocarcinoma histology. Comprehensive staging was then completed, including a PET/CT scan of the chest, abdomen, and pelvis, which showed hypermetabolic activity corresponding to the primary lung mass and several mediastinal lymph nodes (e.g., subcarinal, ipsilateral hilar), but no evidence of distant metastatic disease. A brain MRI with contrast was also performed and showed no intracranial metastases. Based on these findings, the patient's cancer is staged as AJCC Stage IIIA.

**Molecular Studies:**
Molecular profiling of the tumor tissue was performed and revealed no actionable driver alterations. Specifically, the tumor was negative for mutations or rearrangements in EGFR, ALK, ROS1, BRAF, MET exon 14 skipping, RET, NTRK, KRAS, and ERBB2. PD-L1 expression was not assessed, as the sequencing was performed prior to 2017 when PD-L1 testing was not yet standard of care for NSCLC. Tumor mutational burden (TMB) was reported as intermediate (2–16 mut/Mb).

**Problem Summary:**
This is a 79-year-old patient with newly diagnosed, treatment-naive non-small cell lung cancer, adenocarcinoma histology, AJCC Stage IIIA. The patient has a significant smoking history and a prior history of bladder cancer. Molecular profiling shows no actionable driver alterations, PD-L1 status is unknown, and tumor mutational burden is intermediate. The patient presents for discussion of further management options.
```

---

## genie_NSCLC_GENIE-MSK-P-0006950_0  [PASS]

**Structured profile (ground truth):**
- Stage IIIA, adenocarcinoma, brain_mets=False
- EGFR=negative ALK=positive ROS1=negative BRAF=negative MET=negative RET=negative NTRK=negative PD-L1=unknown
- biomarkers_available=True
- actual_treatment (held out): Cisplatin, Docetaxel, Investigational Drug

**warnings:**
- brain_mets=False but note appears to mention brain metastasis

**Generated note:**
```
Date: [De-identified Date]
Patient: [De-identified Patient Name]
DOB: [De-identified DOB]
MRN: [De-identified MRN]

**HPI:**
Patient is a 61-year-old individual presenting for initial oncology evaluation of recently diagnosed non-small cell lung cancer. The patient reports a several-month history of a persistent, productive cough, progressive dyspnea on exertion, and some unintentional weight loss totaling approximately 10 pounds over the past 3 months. They are a former smoker, having quit less than one year ago. These symptoms prompted evaluation by their primary care provider, leading to initial imaging. The patient's current ECOG performance status is 1 due to mild fatigue and dyspnea with moderate activity.

**Diagnostic Workup:**
Initial chest X-ray revealed a suspicious mass in the lung, which was further characterized by a subsequent contrast-enhanced CT scan of the chest. This imaging confirmed a primary lung mass, along with mediastinal and hilar lymphadenopathy. A PET/CT scan was performed for comprehensive staging, demonstrating hypermetabolic activity in the primary lung lesion and involved regional lymph nodes, consistent with locoregional spread. No evidence of distant metastatic disease was identified on the PET/CT scan, including no suspicious lesions in the liver, bones, or adrenal glands. A brain MRI was also performed, which was negative for intracranial metastases. Diagnosis was confirmed via bronchoscopic biopsy of the lung mass, which revealed adenocarcinoma histology. Final AJCC staging based on these findings is Stage IIIA.

**Molecular Studies:**
Comprehensive molecular profiling was performed on the tumor tissue. This revealed an ALK rearrangement. Testing for other common driver mutations was negative, including EGFR, ROS1, BRAF, MET exon 14 skipping, RET, NTRK, KRAS, and ERBB2. PD-L1 expression by immunohistochemistry was negative. Tumor mutational burden (TMB) was reported as intermediate (2-16 mutations/megabase).

**Problem Summary:**
This 61-year-old individual presents with newly diagnosed, treatment-naive non-small cell lung cancer, adenocarcinoma histology, Stage IIIA. Molecular profiling demonstrates an ALK rearrangement, negative PD-L1, and intermediate TMB.
```

---

## genie_NSCLC_GENIE-DFCI-078202_0  [PASS]

**Structured profile (ground truth):**
- Stage IV, squamous, brain_mets=True
- EGFR=negative ALK=negative ROS1=negative BRAF=negative MET=negative RET=negative NTRK=negative PD-L1=high
- biomarkers_available=True
- actual_treatment (held out): Pembrolizumab

**Generated note:**
```
[De-identified Clinic Name]
[De-identified Address]
[De-identified Phone Number]

**Date:** [De-identified Date]
**Patient Name:** [De-identified Patient Name]
**DOB:** [De-identified DOB]
**MRN:** [De-identified MRN]

**REASON FOR VISIT/CC:** Initial consultation for newly diagnosed non-small cell lung cancer.

**HISTORY OF PRESENT ILLNESS:**
Patient is a 79-year-old individual presenting for initial oncology consultation regarding recently diagnosed non-small cell lung cancer. The patient's history is notable for having quit smoking over one year ago. They initially presented with new onset headaches and a gradually enlarging subcutaneous nodule, prompting further medical evaluation. The patient reports a generally stable performance status, though they note some mild fatigue. Subsequent imaging and biopsy confirmed the diagnosis of advanced lung cancer. The patient is treatment-naive and has not received any prior systemic therapy for this malignancy.

**DIAGNOSTIC WORKUP:**
Initial diagnostic imaging included a CT scan of the chest, abdomen, and pelvis, which revealed a primary lung mass. A subsequent MRI of the brain confirmed the presence of intracranial metastatic disease. Additionally, a biopsy of a subcutaneous lesion confirmed metastatic involvement. Histopathological review of the biopsied tissue confirmed non-small cell lung cancer with squamous histology. The patient's disease is staged as AJCC Stage IV, reflecting the presence of distant metastases to both the brain and subcutaneous tissue.

**MOLECULAR STUDIES:**
Molecular profiling was performed on the tumor tissue. Results indicated no actionable driver alterations, specifically negative for EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, and ERBB2 mutations/rearrangements. PD-L1 expression by immunohistochemistry was positive with a Tumor Proportion Score (TPS) of ≥50%. Tumor Mutational Burden (TMB) was found to be intermediate (2–16 mut/Mb). Additionally, a KEAP1 loss-of-function mutation was identified.

**PROBLEM SUMMARY:**
This 79-year-old patient presents with newly diagnosed, treatment-naive Stage IV non-small cell lung cancer of squamous histology, with metastatic involvement of the brain and subcutaneous tissue. Key molecular findings include high PD-L1 expression (TPS ≥50%) and intermediate TMB, alongside a KEAP1 loss-of-function mutation.

[De-identified Physician Name]
Medical Oncologist
```

---

## genie_NSCLC_GENIE-MSK-P-0010648_0  [PASS]

**Structured profile (ground truth):**
- Stage IV, adenocarcinoma, brain_mets=False
- EGFR=negative ALK=negative ROS1=negative BRAF=negative MET=negative RET=negative NTRK=negative PD-L1=unknown
- biomarkers_available=True
- actual_treatment (held out): Carboplatin, Pemetrexed Disodium

**Generated note:**
```
**DATE:** [De-identified Date]

**HPI:**
[De-identified] is a 73-year-old patient presenting for initial oncology consultation regarding a recent diagnosis of non-small cell lung cancer. The patient reports experiencing a persistent, non-productive cough and increasing exertional dyspnea over the past three months. This was accompanied by a noticeable decline in energy levels and a 10-pound unintentional weight loss. Approximately two months prior to presentation, the patient developed new-onset, dull, aching pain in the lower back, which has been progressively worsening and is only partially relieved by over-the-counter analgesics. This constellation of symptoms prompted evaluation by their primary care physician. The patient is a former smoker, having quit over one year ago.

**Diagnostic Workup:**
Initial workup commenced with a chest X-ray, which revealed a suspicious mass in the right upper lobe. This finding was further investigated with a contrast-enhanced CT scan of the chest, abdomen, and pelvis, which confirmed a 4.5 cm spiculated mass in the right upper lobe of the lung, associated with ipsilateral hilar and mediastinal lymphadenopathy. Of note, the CT also identified a lytic lesion within the L3 vertebral body, highly concerning for metastatic disease. A CT-guided core needle biopsy of the right upper lobe lung mass was subsequently performed, yielding pathology consistent with adenocarcinoma. To complete staging, a whole-body PET/CT scan was obtained, demonstrating hypermetabolic activity corresponding to the primary right upper lobe lung mass, the mediastinal lymph nodes, and the L3 vertebral body lesion, confirming distant metastatic disease. An MRI of the brain was also performed and showed no evidence of intracranial metastases. Based on these comprehensive studies, the patient is diagnosed with Stage IV non-small cell lung cancer, adenocarcinoma histology, with metastatic disease to bone. The patient's current Eastern Cooperative Oncology Group (ECOG) performance status is 1, indicating they are ambulatory and able to carry out light work, though experiencing some symptoms.

**Molecular Studies:**
Molecular profiling was performed on the tumor tissue obtained from the right upper lobe lung biopsy. Comprehensive genomic sequencing revealed no actionable driver alterations, with specific testing negative for mutations or rearrangements in EGFR, ALK, ROS1, BRAF, MET exon 14 skipping, RET, NTRK, KRAS, and ERBB2. PD-L1 expression was not tested, as this assay was not standard of care at the time of initial sequencing. Tumor mutational burden (TMB) was reported as low (<2 mut/Mb).

**Problem Summary:**
73-year-old patient with newly diagnosed, treatment-naive Stage IV non-small cell lung cancer, adenocarcinoma histology, with distant metastasis to bone. Molecular profiling demonstrates no actionable driver alterations (negative for EGFR, ALK, ROS1, BRAF, MET exon 14, RET, NTRK, KRAS, ERBB2), PD-L1 status is not available, and tumor mutational burden is low. The patient presents for initial oncology evaluation and discussion of systemic therapy options.
```

---

## genie_NSCLC_GENIE-MSK-P-0011517_0  [PASS]

**Structured profile (ground truth):**
- Stage IIIA, adenocarcinoma, brain_mets=False
- EGFR=negative ALK=negative ROS1=negative BRAF=negative MET=negative RET=negative NTRK=negative PD-L1=unknown
- biomarkers_available=True
- actual_treatment (held out): Carboplatin, Pemetrexed Disodium

**Generated note:**
```
**HPI:**
The patient, a 59-year-old individual, presents for an initial oncology consultation following a recent diagnosis of non-small cell lung cancer. The patient reports experiencing a persistent cough, some intermittent shortness of breath, and a general sense of fatigue over the past few months. They also noted an unintentional weight loss of approximately 10 pounds during this period. The patient is a former smoker, having quit less than one year ago. These symptoms prompted an initial evaluation with their primary care physician, leading to further diagnostic workup. The patient is currently treatment-naive, and this visit is to establish a comprehensive management plan.

**Diagnostic Workup:**
Initial imaging, including a chest X-ray and subsequent CT scan of the chest, revealed a spiculated mass in the right upper lobe of the lung, along with enlarged ipsilateral mediastinal lymph nodes. To further characterize the lesion and confirm the diagnosis, a CT-guided core needle biopsy of the lung mass was performed, which confirmed adenocarcinoma histology. A comprehensive staging workup was then completed, including a whole-body PET/CT scan and an MRI of the brain. The PET/CT demonstrated hypermetabolic activity corresponding to the primary lung mass and the ipsilateral mediastinal lymph nodes, but no evidence of distant metastatic disease was identified. The MRI of the brain was also unremarkable, showing no intracranial metastases. Based on these findings, the patient's disease is classified as AJCC Stage IIIA.

**Molecular Studies:**
Molecular profiling was performed on the tumor tissue. The results indicated no identifiable actionable driver alterations, with testing negative for EGFR, ALK, ROS1, BRAF, MET exon 14 skipping, RET fusion, NTRK fusion, KRAS mutations, and ERBB2 (HER2) alterations. PD-L1 expression was not assessed, as the sequencing was performed prior to 2017, when PD-L1 testing was not yet standard of care for NSCLC. Tumor mutational burden (TMB) analysis revealed an intermediate TMB, ranging between 2 and 16 mutations per megabase (mut/Mb).

**Problem Summary:**
This 59-year-old former smoker is a newly diagnosed, treatment-naive patient with non-small cell lung cancer, adenocarcinoma histology, AJCC Stage IIIA. Diagnostic workup confirms locoregionally advanced disease without evidence of distant metastases, including no brain involvement. Molecular testing showed no actionable driver mutations, intermediate tumor mutational burden, and PD-L1 status was not assessed. Further discussion is warranted to determine the optimal therapeutic approach.
```

---

## genie_NSCLC_GENIE-DFCI-029716_0  [PASS]

**Structured profile (ground truth):**
- Stage IIIA, adenocarcinoma, brain_mets=False
- EGFR=negative ALK=negative ROS1=negative BRAF=negative MET=negative RET=negative NTRK=negative PD-L1=unknown
- biomarkers_available=True
- actual_treatment (held out): Carboplatin, Paclitaxel

**Generated note:**
```
[De-identified] is a 70-year-old individual referred to our clinic for initial oncologic evaluation and management of newly diagnosed non-small cell lung cancer.

**HPI:**
The patient first presented to their primary care physician approximately three months ago with a persistent cough and increasing shortness of breath, accompanied by mild fatigue. They also reported an unintentional weight loss of 8 pounds over the past two months. Given a history of current smoking, a chest X-ray was performed, which revealed a suspicious right upper lobe mass. This finding prompted further diagnostic investigation.

**Diagnostic Workup:**
A subsequent CT scan of the chest confirmed a 4.5 cm mass in the right upper lobe with associated mediastinal lymphadenopathy. A CT-guided core needle biopsy of the lung mass was performed, which confirmed the diagnosis of non-small cell lung cancer, adenocarcinoma histology. For comprehensive staging, a PET/CT scan was conducted, demonstrating hypermetabolic activity within the primary right upper lobe mass and in several ipsilateral mediastinal lymph nodes (specifically stations 2R, 4R, and 7). There was no evidence of hypermetabolic activity indicative of distant metastatic disease in the abdomen or pelvis. An MRI of the brain was also performed as part of the staging workup, which showed no evidence of intracranial metastases. Based on these findings, the patient's disease is staged as AJCC Stage IIIA. The patient maintains a good performance status, ECOG 1, reporting mild symptoms but remaining fully ambulatory.

**Molecular Studies:**
Molecular profiling was performed on the tumor biopsy specimen. The results indicate no actionable driver alteration identified, with specific testing being negative for EGFR, ALK, ROS1, BRAF, MET exon 14 skipping, RET fusion, NTRK fusion, KRAS mutation, and ERBB2 (HER2) amplification. PD-L1 expression was not tested, consistent with the pre-2017 sequencing era when this particular assay was not yet standard of care. Tumor mutational burden (TMB) was reported as intermediate (2–16 mut/Mb).

**Problem Summary:**
[De-identified] is a 70-year-old individual with newly diagnosed, treatment-naive non-small cell lung cancer, adenocarcinoma histology, AJCC Stage IIIA. The patient has a history of current smoking. Staging workup confirmed locoregional disease involving ipsilateral mediastinal lymph nodes, with no evidence of distant metastases, including to the brain. Molecular studies revealed no actionable driver alterations, an untested PD-L1 status, and an intermediate tumor mutational burden. The patient presents with a good performance status.
```

---

## genie_NSCLC_GENIE-MSK-P-0009789_0  [PASS]

**Structured profile (ground truth):**
- Stage IV, adenocarcinoma, brain_mets=False
- EGFR=negative ALK=negative ROS1=negative BRAF=negative MET=negative RET=negative NTRK=negative PD-L1=intermediate
- biomarkers_available=True
- actual_treatment (held out): Carboplatin, Pemetrexed Disodium

**Generated note:**
```
**HPI:**
[De-identified] is a 71-year-old patient presenting for an initial oncology consultation regarding a recent diagnosis of non-small cell lung cancer. The patient initially presented to their primary care physician several weeks ago with a persistent cough and new-onset dyspnea on exertion. They also reported some associated fatigue and a mild, unintentional weight loss of approximately 5-7 pounds over the past 2-3 months. The patient has a past medical history significant for former smoking, having quit over one year ago. Performance status is currently estimated at ECOG 1.

**Diagnostic Workup:**
Initial evaluation included a chest X-ray which demonstrated a suspicious left upper lobe mass. This prompted further imaging with a CT scan of the chest, abdomen, and pelvis, which confirmed a dominant mass in the left upper lobe measuring approximately 4.5 x 3.8 cm with associated mediastinal lymphadenopathy. Additionally, a smaller, new nodule was identified in the contralateral (right) lung, concerning for metastatic disease. A subsequent PET/CT scan confirmed increased metabolic activity in the left upper lobe mass, mediastinal lymph nodes, and the right lung nodule. Given the findings, a biopsy of the left upper lobe mass was performed, which confirmed adenocarcinoma histology. An MRI of the brain was also performed as part of the staging workup and showed no evidence of intracranial metastases. Based on these findings, the patient is diagnosed with Stage IV non-small cell lung cancer, with metastatic disease to the contralateral lung.

**Molecular Studies:**
Molecular testing was performed on the biopsy specimen. Results indicate the presence of an actionable KRAS G12C mutation. Comprehensive genomic profiling was negative for other commonly tested oncogenic drivers, including EGFR, ALK, ROS1, BRAF, MET exon 14 skipping, RET fusion, NTRK fusion, and ERBB2 (HER2) mutations. PD-L1 immunohistochemistry revealed a tumor proportion score (TPS) of 1-49%. Tumor mutational burden (TMB) was reported as intermediate, in the range of 2-16 mutations/megabase.

**Problem Summary:**
[De-identified] is a 71-year-old patient with newly diagnosed, treatment-naive Stage IV non-small cell lung cancer of adenocarcinoma histology, presenting with metastatic disease to the contralateral lung. Molecular studies reveal a KRAS G12C mutation, negative status for other common drivers, PD-L1 TPS 1-49%, and intermediate TMB. The patient is currently seeking initial oncology evaluation for management recommendations.
```

---

## genie_NSCLC_GENIE-DFCI-011383_0  [PASS]

**Structured profile (ground truth):**
- Stage IV, adenocarcinoma, brain_mets=False
- EGFR=negative ALK=negative ROS1=negative BRAF=negative MET=negative RET=negative NTRK=negative PD-L1=unknown
- biomarkers_available=True
- actual_treatment (held out): Carboplatin, Pemetrexed Disodium

**Generated note:**
```
**Initial Consultation Note**

**Patient:** [De-identified Patient Name], 83-year-old
**Date of Service:** [De-identified Date]
**MRN:** [De-identified MRN]

**HPI:**
The patient is an 83-year-old, treatment-naive individual presenting for an initial oncology consultation regarding a recent diagnosis of non-small cell lung cancer. The patient is a former smoker, having quit more than one year prior to presentation. Approximately three months ago, the patient began experiencing a persistent, non-productive cough, coupled with progressive shortness of breath, particularly with exertion. This was accompanied by a dull, persistent left-sided chest discomfort and a reported unintentional weight loss of approximately 10 pounds over the past two months. Given these symptoms, the patient sought evaluation with their primary care physician.

**Diagnostic Workup:**
Initial evaluation included a chest X-ray, which revealed a left lung mass and a moderate left pleural effusion. Subsequent contrast-enhanced CT of the chest confirmed a spiculated mass in the left upper lobe, measuring approximately 4 cm, along with a significant left pleural effusion and diffuse pleural thickening and nodularity. To establish a diagnosis, a thoracentesis was performed, yielding exudative fluid. Cytological analysis of the pleural fluid was positive for adenocarcinoma. A CT-guided core needle biopsy of the left upper lobe mass was also performed, confirming invasive adenocarcinoma of the lung. Further staging workup included a PET/CT scan, which demonstrated hypermetabolic activity in the primary left upper lobe mass and extensive uptake within the left pleura, consistent with metastatic disease. There was no evidence of other distant metastatic sites on PET/CT. A dedicated MRI of the brain was performed, which showed no evidence of intracranial metastatic disease. Based on these findings, the patient was diagnosed with Stage IV (cT2a N0 M1a) non-small cell lung cancer, adenocarcinoma histology, with metastatic involvement of the pleura. The patient's performance status at the time of consultation is generally good, with mild limitations due to dyspnea on exertion.

**Molecular Studies:**
Comprehensive molecular profiling was performed on tumor tissue from the lung biopsy. Results revealed the presence of a KRAS G12C mutation, which is considered an actionable driver mutation. Testing for other common driver mutations was negative, including EGFR, ALK, ROS1, BRAF, MET exon 14 skipping, RET fusion, NTRK fusion, and ERBB2 (HER2) mutations. PD-L1 expression was not tested, as this diagnostic modality was not standard of care at the time of initial sequencing. Tumor mutational burden (TMB) was reported as intermediate, falling within the range of 2–16 mutations/megabase.

**Problem Summary:**
This 83-year-old former smoker presents with newly diagnosed Stage IV non-small cell lung cancer of adenocarcinoma histology. The disease is metastatic to the pleura, with no identified brain metastases. Molecular testing demonstrates a KRAS G12C mutation, with other common driver mutations being negative. PD-L1 status was not assessed, and TMB is intermediate. The patient is treatment-naive and now seeks discussion of therapeutic options.
```

---
