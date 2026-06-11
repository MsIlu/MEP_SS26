# STS Assessment Criteria Overview

Generated review export for Careena Pipeline3 catalog work.

This export shows how STS consultation reasons are linked to reusable assessment criteria.
It is intended for medical/product review, not as runtime case state.

## Columns

- `expected_value_type`: structured value Pipeline3 should extract
- `suggested_input_mode`: optional UI/input helper
- `free_text_allowed`: whether users may still answer freely
- `capture_status`: whether Careena can responsibly capture the criterion
- `use_policy`: whether Careena may ask actively or only accept user-provided information
- `decision_role`: possible later Pipeline3 role; not a direct emergency decision

## Review Table

| STS ID | STS reason | Criterion | Value type | Input mode | Free text | Capture | Use policy | Relevance | Safety | Red flag candidate | Decision role |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1001 | Herzstillstand, Atemstillstand | breathing_and_responsiveness_observed | observed_sign | yes_no_buttons | True | conditional / observer_report | ask_if_context_relevant | primary | True | True | structured_safety_validator |
| 1001 | Herzstillstand, Atemstillstand | glasgow_coma_scale_observer_assisted | observed_sign | observed_sign_input | True | conditional / observer_assisted_scale | ask_if_context_relevant | supporting | True | False | supporting_context |
| 1002 | Thoraxschmerzen | chest_pain_character_or_radiation_self_reported | free_text | free_text | True | usable / self_report | ask_if_context_relevant | primary | True | True | structured_safety_validator |
| 1002 | Thoraxschmerzen | dyspnea_self_reported | boolean | yes_no_buttons | True | usable / self_report | ask_if_context_relevant | supporting | True | True | structured_safety_validator |
| 1002 | Thoraxschmerzen | pain_intensity_0_10 | number | scale_0_10 | True | usable / self_report | ask_if_context_relevant | supporting | True | False | supporting_context |
| 1002 | Thoraxschmerzen | symptom_onset_or_duration | duration | duration_input | True | usable / self_report | ask_if_context_relevant | supporting | True | False | supporting_context |
| 1003 | Tachykardie, Rhythmusstoerung, Palpitationen | palpitations_self_reported | boolean | yes_no_buttons | True | usable / self_report | ask_if_context_relevant | primary | True | False | readiness_requirement |
| 1003 | Tachykardie, Rhythmusstoerung, Palpitationen | dizziness_or_near_syncope_self_reported | boolean | yes_no_buttons | True | usable / self_report | ask_if_context_relevant | supporting | True | True | structured_safety_validator |
| 1003 | Tachykardie, Rhythmusstoerung, Palpitationen | dyspnea_self_reported | boolean | yes_no_buttons | True | usable / self_report | ask_if_context_relevant | supporting | True | True | structured_safety_validator |
| 1003 | Tachykardie, Rhythmusstoerung, Palpitationen | pulse_or_heart_rate_user_provided | measurement | measurement_input | True | conditional / user_provided_measurement | accept_if_user_provided | supporting | True | False | supporting_context |
| 1003 | Tachykardie, Rhythmusstoerung, Palpitationen | symptom_onset_or_duration | duration | duration_input | True | usable / self_report | ask_if_context_relevant | supporting | True | False | supporting_context |
| 1004 | Bradykardie | pulse_or_heart_rate_user_provided | measurement | measurement_input | True | conditional / user_provided_measurement | accept_if_user_provided | primary | True | False | readiness_requirement |
| 1004 | Bradykardie | dizziness_or_near_syncope_self_reported | boolean | yes_no_buttons | True | usable / self_report | ask_if_context_relevant | supporting | True | True | structured_safety_validator |
| 1004 | Bradykardie | dyspnea_self_reported | boolean | yes_no_buttons | True | usable / self_report | ask_if_context_relevant | supporting | True | True | structured_safety_validator |
| 1004 | Bradykardie | symptom_onset_or_duration | duration | duration_input | True | usable / self_report | ask_if_context_relevant | supporting | True | False | supporting_context |
| 1005 | Hypertonie | blood_pressure_user_provided | measurement | measurement_input | True | conditional / user_provided_measurement | accept_if_user_provided | primary | True | False | readiness_requirement |
| 1005 | Hypertonie | dizziness_or_near_syncope_self_reported | boolean | yes_no_buttons | True | usable / self_report | ask_if_context_relevant | supporting | True | True | structured_safety_validator |
| 1005 | Hypertonie | dyspnea_self_reported | boolean | yes_no_buttons | True | usable / self_report | ask_if_context_relevant | supporting | True | True | structured_safety_validator |
| 1005 | Hypertonie | symptom_onset_or_duration | duration | duration_input | True | usable / self_report | ask_if_context_relevant | supporting | True | False | supporting_context |
| 1006 | Hypotonie | blood_pressure_user_provided | measurement | measurement_input | True | conditional / user_provided_measurement | accept_if_user_provided | primary | True | False | readiness_requirement |
| 1006 | Hypotonie | dizziness_or_near_syncope_self_reported | boolean | yes_no_buttons | True | usable / self_report | ask_if_context_relevant | supporting | True | True | structured_safety_validator |
| 1006 | Hypotonie | symptom_onset_or_duration | duration | duration_input | True | usable / self_report | ask_if_context_relevant | supporting | True | False | supporting_context |
| 1007 | Extremitaet, Schmerzen und / oder Oedem | limb_pain_or_swelling_self_reported | boolean | yes_no_buttons | True | usable / self_report_or_observed | ask_if_context_relevant | primary | True | False | readiness_requirement |
| 1007 | Extremitaet, Schmerzen und / oder Oedem | dyspnea_self_reported | boolean | yes_no_buttons | True | usable / self_report | ask_if_context_relevant | supporting | True | True | structured_safety_validator |
| 1007 | Extremitaet, Schmerzen und / oder Oedem | symptom_onset_or_duration | duration | duration_input | True | usable / self_report | ask_if_context_relevant | supporting | True | False | supporting_context |
| 1008 | Atemsymptome (Dyspnoe, Tachypnoe, Bradypnoe, ungenuegende O2-Saettigung) | dyspnea_self_reported | boolean | yes_no_buttons | True | usable / self_report | ask_if_context_relevant | primary | True | True | structured_safety_validator |
| 1008 | Atemsymptome (Dyspnoe, Tachypnoe, Bradypnoe, ungenuegende O2-Saettigung) | pupil_response | not_collectable | none | True | not_usable / clinician_assessment | do_not_ask | source_only | True | False | not_used_for_product_decision |
| 1008 | Atemsymptome (Dyspnoe, Tachypnoe, Bradypnoe, ungenuegende O2-Saettigung) | cyanosis_observed | boolean | yes_no_buttons | True | conditional / observer_report | ask_if_context_relevant | supporting | True | True | structured_safety_validator |
| 1008 | Atemsymptome (Dyspnoe, Tachypnoe, Bradypnoe, ungenuegende O2-Saettigung) | glasgow_coma_scale_observer_assisted | observed_sign | observed_sign_input | True | conditional / observer_assisted_scale | ask_if_context_relevant | supporting | True | False | supporting_context |
| 1008 | Atemsymptome (Dyspnoe, Tachypnoe, Bradypnoe, ungenuegende O2-Saettigung) | oxygen_saturation_user_provided | measurement | measurement_input | True | conditional / user_provided_measurement | accept_if_user_provided | supporting | True | False | supporting_context |
| 1008 | Atemsymptome (Dyspnoe, Tachypnoe, Bradypnoe, ungenuegende O2-Saettigung) | speaking_full_sentences_difficulty | boolean | yes_no_buttons | True | usable / self_report_or_observed | ask_if_context_relevant | supporting | True | True | structured_safety_validator |
| 1009 | Husten, Auswurf | cough_self_reported | boolean | yes_no_buttons | True | usable / self_report | ask_if_context_relevant | primary | False | False | readiness_requirement |
| 1009 | Husten, Auswurf | dyspnea_self_reported | boolean | yes_no_buttons | True | usable / self_report | ask_if_context_relevant | supporting | True | True | structured_safety_validator |
| 1009 | Husten, Auswurf | fever_self_reported | boolean | yes_no_buttons | True | usable / self_report | ask_if_context_relevant | supporting | True | False | supporting_context |
| 1009 | Husten, Auswurf | productive_cough_or_sputum_self_reported | boolean | yes_no_buttons | True | usable / self_report | ask_if_context_relevant | supporting | False | False | supporting_context |
| 1009 | Husten, Auswurf | symptom_onset_or_duration | duration | duration_input | True | usable / self_report | ask_if_context_relevant | supporting | False | False | supporting_context |
| 1010 | Bluthusten (Haemoptyse) | hemoptysis_self_reported | boolean | yes_no_buttons | True | usable / self_report | ask_if_context_relevant | primary | True | True | structured_safety_validator |
| 1010 | Bluthusten (Haemoptyse) | dyspnea_self_reported | boolean | yes_no_buttons | True | usable / self_report | ask_if_context_relevant | supporting | True | True | structured_safety_validator |
| 1010 | Bluthusten (Haemoptyse) | symptom_onset_or_duration | duration | duration_input | True | usable / self_report | ask_if_context_relevant | supporting | True | False | supporting_context |

## Review Notes

- `1001 Herzstillstand, Atemstillstand` now uses `breathing_and_responsiveness_observed` as primary lay-observable safety criterion.
- `glasgow_coma_scale_observer_assisted` remains conditional/supporting and must not be used as the primary criterion for STS 1001.
- GCS is more suitable for neurologic, trauma, intoxication, or reduced-consciousness contexts.
- Further criteria links should be reviewed iteratively before being treated as stable.
