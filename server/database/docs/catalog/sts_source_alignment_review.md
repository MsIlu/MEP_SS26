# STS Source Alignment Review

## Purpose

This document explains how the Careena catalog is checked against the Swiss Triage System (STS) source.

The review is intentionally split into two layers:

1. **Automated structural tests**: verify that review samples exist, reference valid STS reasons, match the seed labels/categories, and have primary criterion links.
2. **Manual medical/source review**: verifies whether the selected database mapping is medically and source-wise plausible against the STS document.

This is not runtime triage logic and does not make medical decisions.

## Sampling Strategy

The review uses risk-based sampling instead of random sampling.

- Minimum: two STS consultation reasons per category.
- Selection: one high-risk or safety-sensitive sample plus one common/routine sample where possible.
- The category `Verschiedene Konsultationsmotive` receives four samples because it contains heterogeneous and sensitive reasons.

## Current Review Status

The initial sample set is marked as `pending_source_review`.

A sample may only be changed to `reviewed_ok` after a reviewer checks:

- STS ID
- STS label
- STS category
- STS urgency levels/source level metadata
- primary criterion mapping
- supporting safety mapping
- lay capture feasibility
- limitations for criteria that are not safely collectable from lay users

If a mismatch is found, set `review_status` to `needs_revision` and fix the seed before merging.

## What the Automated Tests Prove

- The review sample file is structurally valid.
- Every sampled STS ID exists in the consultation reason seed.
- Review labels/categories still match the current seed.
- Every sampled reason has at least one active primary criterion link.
- Every category has enough review samples.
- A reviewed sample cannot be marked `reviewed_ok` unless all checklist items are true.

## What the Automated Tests Do Not Prove

The tests do not prove medical correctness. Medical/source alignment still requires human review against the STS document.

## Review Samples

| Category | STS ID | Label | Type | Status | Selection reason |
|---|---:|---|---|---|---|
| Dermatologie | 1701 | Allergische Reaktion | high_risk_sample | pending_source_review | Allergic reaction sample with possible airway safety relevance. |
| Dermatologie | 1703 | Haut, Weichteile; Beschwerden / Infekt | routine_sample | pending_source_review | Skin/soft tissue complaint sample. |
| HNO | 1602 | HNO-Beschwerden | routine_sample | pending_source_review | Common ENT complaint sample. |
| HNO | 1603 | Nasenbluten (Epistaxis) | high_risk_sample | pending_source_review | Epistaxis sample with bleeding safety relevance. |
| Infektsymptome | 1501 | Fieber | high_risk_sample | pending_source_review | Fever/systemic infection sample. |
| Infektsymptome | 1503 | Hypothermie | routine_sample | pending_source_review | Rash/exanthem sample. |
| Kardiovaskulaer und respiratorisch | 1001 | Herzstillstand, Atemstillstand | high_risk_sample | pending_source_review | Critical cardiac/respiratory arrest sample; also covers the GCS review finding. |
| Kardiovaskulaer und respiratorisch | 1009 | Husten, Auswurf | routine_sample | pending_source_review | Frequent respiratory complaint sample. |
| Magen - Darm - Gynaekologie | 1307 | Diarrhoe | routine_sample | pending_source_review | Diarrhea sample. |
| Magen - Darm - Gynaekologie | 1317 | Nabelschnurvorfall | high_risk_sample | pending_source_review | Umbilical cord prolapse sample with high obstetric safety relevance. |
| Neurologie - Psychiatrie | 1105 | Stoerung von Sprache, Gedaechtnis, Sehen, Gleichgewicht; Einschraenkung / Ausfall von Motorik, Sensibilitaet, Gesichtsfeld | high_risk_sample | pending_source_review | Stroke-like focal neurological deficit sample. |
| Neurologie - Psychiatrie | 1107 | Kopfschmerzen leichtgradig oder ueber einen laengeren Zeitraum bestehend | routine_sample | pending_source_review | Lower-acuity headache sample. |
| Rheumatologie | 1801 | Rueckenschmerzen, Nackenschmerzen | safety_sensitive_sample | pending_source_review | Back/neck pain sample with neurological red-flag supporting criteria. |
| Rheumatologie | 1802 | Gelenkschmerzen (Arthralgie), Muskelschmerzen (Myalgie), Nervenschmerzen (Neuralgie) | routine_sample | pending_source_review | Joint/muscle/nerve pain sample. |
| Traumatologie | 1201 | Polytrauma | high_risk_sample | pending_source_review | Polytrauma sample with high safety relevance. |
| Traumatologie | 1213 | Oberflaechliche Wunde | routine_sample | pending_source_review | Superficial wound sample. |
| Urologie - Nephrologie | 1403 | Anurie / Urinretention | high_risk_sample | pending_source_review | Anuria/urinary retention sample. |
| Urologie - Nephrologie | 1404 | Brennen beim Urinieren / Pollakisurie | routine_sample | pending_source_review | Dysuria/pollakisuria sample. |
| Verschiedene Konsultationsmotive | 1903 | Toxische Substanz; Einnahme, Inhalation, Exposition | high_risk_sample | pending_source_review | Toxic substance exposure sample. |
| Verschiedene Konsultationsmotive | 1914 | Beratung, Arztzeugnis, Rezept | routine_sample | pending_source_review | Administrative medical request sample. |
| Verschiedene Konsultationsmotive | 1916 | Sexuelle Aggression | sensitive_sample | pending_source_review | Sexual assault sample; safeguarding and trauma-informed handling. |
| Verschiedene Konsultationsmotive | 1920 | Geplante Konsultation | routine_sample | pending_source_review | Planned consultation sample. |

## How to Run the Tests

From the `server` directory:

```powershell
python -m pytest tests/test_sts_source_alignment_review.py
```

For the full backend test suite:

```powershell
python -m pytest
```
