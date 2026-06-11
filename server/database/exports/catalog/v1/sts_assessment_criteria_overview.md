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
| 1101 | Bewusstlosigkeit / Bewusstseinsdefizit ohne offensichtliche Ursache | consciousness_level_observed | observed_sign | choice_buttons | True | conditional / self_report_or_observed | ask_if_context_relevant | primary | True | True | structured_safety_validator |
| 1101 | Bewusstlosigkeit / Bewusstseinsdefizit ohne offensichtliche Ursache | breathing_and_responsiveness_observed | observed_sign | yes_no_buttons | True | conditional / observer_report | ask_if_context_relevant | supporting | True | True | structured_safety_validator |
| 1101 | Bewusstlosigkeit / Bewusstseinsdefizit ohne offensichtliche Ursache | glasgow_coma_scale_observer_assisted | observed_sign | observed_sign_input | True | conditional / observer_assisted_scale | ask_if_context_relevant | supporting | True | False | supporting_context |
| 1102 | Erregungszustand, Aggressivitaet | agitation_or_aggression_observed | observed_sign | yes_no_buttons | True | usable / self_report_or_observed | ask_if_context_relevant | primary | True | True | structured_safety_validator |
| 1102 | Erregungszustand, Aggressivitaet | confusion_or_disorientation_observed | observed_sign | yes_no_buttons | True | usable / self_report_or_observed | ask_if_context_relevant | supporting | True | True | structured_safety_validator |
| 1103 | Verwirrtheit, Verhaltensauffaelligkeiten, kognitive Stoerungen | confusion_or_disorientation_observed | observed_sign | yes_no_buttons | True | usable / self_report_or_observed | ask_if_context_relevant | primary | True | True | structured_safety_validator |
| 1103 | Verwirrtheit, Verhaltensauffaelligkeiten, kognitive Stoerungen | consciousness_level_observed | observed_sign | choice_buttons | True | conditional / self_report_or_observed | ask_if_context_relevant | supporting | True | True | structured_safety_validator |
| 1103 | Verwirrtheit, Verhaltensauffaelligkeiten, kognitive Stoerungen | symptom_onset_or_duration | duration | duration_input | True | usable / self_report | ask_if_context_relevant | supporting | True | False | supporting_context |
| 1104 | Krampfereignis / unwillkuerliche Bewegungen akut bestehend oder kuerzlich geschehen | seizure_event_reported | boolean | yes_no_buttons | True | usable / self_report_or_observed | ask_if_context_relevant | primary | True | True | structured_safety_validator |
| 1104 | Krampfereignis / unwillkuerliche Bewegungen akut bestehend oder kuerzlich geschehen | breathing_and_responsiveness_observed | observed_sign | yes_no_buttons | True | conditional / observer_report | ask_if_context_relevant | supporting | True | True | structured_safety_validator |
| 1104 | Krampfereignis / unwillkuerliche Bewegungen akut bestehend oder kuerzlich geschehen | consciousness_level_observed | observed_sign | choice_buttons | True | conditional / self_report_or_observed | ask_if_context_relevant | supporting | True | True | structured_safety_validator |
| 1105 | Stoerung von Sprache, Gedaechtnis, Sehen, Gleichgewicht; Einschraenkung / Ausfall von Motorik, Sensibilitaet, Gesichtsfeld | focal_neurological_deficit_self_reported_or_observed | observed_sign | yes_no_buttons | True | usable / self_report_or_observed | ask_if_context_relevant | primary | True | True | structured_safety_validator |
| 1105 | Stoerung von Sprache, Gedaechtnis, Sehen, Gleichgewicht; Einschraenkung / Ausfall von Motorik, Sensibilitaet, Gesichtsfeld | dizziness_or_near_syncope_self_reported | boolean | yes_no_buttons | True | usable / self_report | ask_if_context_relevant | supporting | True | False | supporting_context |
| 1105 | Stoerung von Sprache, Gedaechtnis, Sehen, Gleichgewicht; Einschraenkung / Ausfall von Motorik, Sensibilitaet, Gesichtsfeld | symptom_onset_or_duration | duration | duration_input | True | usable / self_report | ask_if_context_relevant | supporting | True | False | supporting_context |
| 1106 | Kopfschmerzen heftig oder ungewohnt | headache_severe_or_unusual_self_reported | boolean | yes_no_buttons | True | usable / self_report | ask_if_context_relevant | primary | True | True | structured_safety_validator |
| 1106 | Kopfschmerzen heftig oder ungewohnt | focal_neurological_deficit_self_reported_or_observed | observed_sign | yes_no_buttons | True | usable / self_report_or_observed | ask_if_context_relevant | supporting | True | True | structured_safety_validator |
| 1106 | Kopfschmerzen heftig oder ungewohnt | pain_intensity_0_10 | number | scale_0_10 | True | usable / self_report | ask_if_context_relevant | supporting | True | False | supporting_context |
| 1106 | Kopfschmerzen heftig oder ungewohnt | symptom_onset_or_duration | duration | duration_input | True | usable / self_report | ask_if_context_relevant | supporting | True | False | supporting_context |
| 1107 | Kopfschmerzen leichtgradig oder ueber einen laengeren Zeitraum bestehend | headache_duration_or_recurrent_self_reported | free_text | free_text | True | usable / self_report | ask_if_context_relevant | primary | False | False | readiness_requirement |
| 1107 | Kopfschmerzen leichtgradig oder ueber einen laengeren Zeitraum bestehend | pain_intensity_0_10 | number | scale_0_10 | True | usable / self_report | ask_if_context_relevant | supporting | False | False | supporting_context |
| 1107 | Kopfschmerzen leichtgradig oder ueber einen laengeren Zeitraum bestehend | symptom_onset_or_duration | duration | duration_input | True | usable / self_report | ask_if_context_relevant | supporting | False | False | supporting_context |
| 1108 | Unwohlsein mit oder ohne Bewusstlosigkeit (Synkope / Praesynkope) | loss_of_consciousness_episode_reported | boolean | yes_no_buttons | True | usable / self_report_or_observed | ask_if_context_relevant | primary | True | True | structured_safety_validator |
| 1108 | Unwohlsein mit oder ohne Bewusstlosigkeit (Synkope / Praesynkope) | dizziness_or_near_syncope_self_reported | boolean | yes_no_buttons | True | usable / self_report | ask_if_context_relevant | supporting | True | False | supporting_context |
| 1108 | Unwohlsein mit oder ohne Bewusstlosigkeit (Synkope / Praesynkope) | symptom_onset_or_duration | duration | duration_input | True | usable / self_report | ask_if_context_relevant | supporting | True | False | supporting_context |
| 1109 | Akuter Angstzustand, Suizidgedanken, Mutismus | acute_psychiatric_crisis_self_reported_or_observed | boolean | yes_no_buttons | True | usable / self_report_or_observed | ask_if_context_relevant | primary | True | True | structured_safety_validator |
| 1109 | Akuter Angstzustand, Suizidgedanken, Mutismus | anxiety_or_panic_self_reported | boolean | yes_no_buttons | True | usable / self_report | ask_if_context_relevant | supporting | True | False | supporting_context |
| 1109 | Akuter Angstzustand, Suizidgedanken, Mutismus | suicidal_ideation_self_reported | boolean | yes_no_buttons | True | usable / self_report | ask_if_context_relevant | supporting | True | True | structured_safety_validator |
| 1110 | Angst / Aengstlichkeit / Unruhe, depressive Symptomatik | anxiety_or_panic_self_reported | boolean | yes_no_buttons | True | usable / self_report | ask_if_context_relevant | primary | False | False | readiness_requirement |
| 1110 | Angst / Aengstlichkeit / Unruhe, depressive Symptomatik | depressive_symptoms_self_reported | boolean | yes_no_buttons | True | usable / self_report | ask_if_context_relevant | supporting | True | False | supporting_context |
| 1110 | Angst / Aengstlichkeit / Unruhe, depressive Symptomatik | suicidal_ideation_self_reported | boolean | yes_no_buttons | True | usable / self_report | ask_if_context_relevant | supporting | True | True | structured_safety_validator |
| 1111 | Missbrauch / Intoxikation Medikamente, Drogen | medication_or_drug_intoxication_self_reported_or_observed | boolean | yes_no_buttons | True | usable / self_report_or_observed | ask_if_context_relevant | primary | True | True | structured_safety_validator |
| 1111 | Missbrauch / Intoxikation Medikamente, Drogen | confusion_or_disorientation_observed | observed_sign | yes_no_buttons | True | usable / self_report_or_observed | ask_if_context_relevant | supporting | True | True | structured_safety_validator |
| 1111 | Missbrauch / Intoxikation Medikamente, Drogen | consciousness_level_observed | observed_sign | choice_buttons | True | conditional / self_report_or_observed | ask_if_context_relevant | supporting | True | True | structured_safety_validator |
| 1112 | Missbrauch / Intoxikation Alkohol | alcohol_intoxication_self_reported_or_observed | boolean | yes_no_buttons | True | usable / self_report_or_observed | ask_if_context_relevant | primary | True | True | structured_safety_validator |
| 1112 | Missbrauch / Intoxikation Alkohol | confusion_or_disorientation_observed | observed_sign | yes_no_buttons | True | usable / self_report_or_observed | ask_if_context_relevant | supporting | True | True | structured_safety_validator |
| 1112 | Missbrauch / Intoxikation Alkohol | consciousness_level_observed | observed_sign | choice_buttons | True | conditional / self_report_or_observed | ask_if_context_relevant | supporting | True | True | structured_safety_validator |
| 1113 | Entzugssymptome, Entzugswunsch | withdrawal_symptoms_self_reported | boolean | yes_no_buttons | True | usable / self_report | ask_if_context_relevant | primary | True | False | readiness_requirement |
| 1113 | Entzugssymptome, Entzugswunsch | agitation_or_aggression_observed | observed_sign | yes_no_buttons | True | usable / self_report_or_observed | ask_if_context_relevant | supporting | True | True | structured_safety_validator |
| 1113 | Entzugssymptome, Entzugswunsch | confusion_or_disorientation_observed | observed_sign | yes_no_buttons | True | usable / self_report_or_observed | ask_if_context_relevant | supporting | True | True | structured_safety_validator |
| 1114 | Halluzinationen | hallucinations_self_reported_or_observed | boolean | yes_no_buttons | True | usable / self_report_or_observed | ask_if_context_relevant | primary | True | True | structured_safety_validator |
| 1114 | Halluzinationen | confusion_or_disorientation_observed | observed_sign | yes_no_buttons | True | usable / self_report_or_observed | ask_if_context_relevant | supporting | True | True | structured_safety_validator |
| 1114 | Halluzinationen | suicidal_ideation_self_reported | boolean | yes_no_buttons | True | usable / self_report | ask_if_context_relevant | supporting | True | True | structured_safety_validator |
| 1115 | Muedigkeit, Schlaflosigkeit | fatigue_or_sleep_disturbance_self_reported | boolean | yes_no_buttons | True | usable / self_report | ask_if_context_relevant | primary | False | False | readiness_requirement |
| 1115 | Muedigkeit, Schlaflosigkeit | depressive_symptoms_self_reported | boolean | yes_no_buttons | True | usable / self_report | ask_if_context_relevant | supporting | True | False | supporting_context |

## Review Notes

- `1001 Herzstillstand, Atemstillstand` now uses `breathing_and_responsiveness_observed` as primary lay-observable safety criterion.
- `glasgow_coma_scale_observer_assisted` remains conditional/supporting and must not be used as the primary criterion for STS 1001.
- GCS is more suitable for neurologic, trauma, intoxication, or reduced-consciousness contexts.
- Further criteria links should be reviewed iteratively before being treated as stable.
