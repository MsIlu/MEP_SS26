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
| 1001 | Herzstillstand, Atemstillstand | glasgow_coma_scale_observer_assisted | observed_sign | observed_sign_input | True | conditional / observer_assisted_scale | ask_if_context_relevant | supporting | True | True | structured_safety_validator |
| 1002 | Thoraxschmerzen | pain_intensity_0_10 | number | scale_0_10 | True | usable / self_report | ask_if_context_relevant | primary | True | False | supporting_context |
| 1002 | Thoraxschmerzen | symptom_onset_or_duration | duration | duration_input | True | usable / self_report | ask_if_context_relevant | primary | True | False | supporting_context |
| 1002 | Thoraxschmerzen | dyspnea_self_reported | boolean | yes_no_buttons | True | usable / self_report | ask_if_context_relevant | supporting | True | True | safety_clarification_trigger |
| 1005 | Hypertonie | blood_pressure_user_provided | measurement | measurement_input | True | conditional / user_provided_measurement | accept_if_user_provided | primary | True | False | supporting_context |
| 1005 | Hypertonie | symptom_onset_or_duration | duration | duration_input | True | usable / self_report | ask_if_context_relevant | supporting | False | False | supporting_context |
| 1008 | Atemsymptome (Dyspnoe, Tachypnoe, Bradypnoe, ungenuegende O2-Saettigung) | dyspnea_self_reported | boolean | yes_no_buttons | True | usable / self_report | ask_if_context_relevant | primary | True | True | safety_clarification_trigger |
| 1008 | Atemsymptome (Dyspnoe, Tachypnoe, Bradypnoe, ungenuegende O2-Saettigung) | speaking_full_sentences_difficulty | boolean | yes_no_buttons | True | usable / self_report_or_observed | ask_if_context_relevant | primary | True | True | structured_safety_validator |
| 1008 | Atemsymptome (Dyspnoe, Tachypnoe, Bradypnoe, ungenuegende O2-Saettigung) | pupil_response | not_collectable | none | True | not_usable / clinician_assessment | do_not_ask | source_only | True | False | not_used_for_product_decision |
| 1008 | Atemsymptome (Dyspnoe, Tachypnoe, Bradypnoe, ungenuegende O2-Saettigung) | cyanosis_observed | boolean | yes_no_buttons | True | conditional / observer_report | ask_if_context_relevant | supporting | True | True | structured_safety_validator |
| 1008 | Atemsymptome (Dyspnoe, Tachypnoe, Bradypnoe, ungenuegende O2-Saettigung) | glasgow_coma_scale_observer_assisted | observed_sign | observed_sign_input | True | conditional / observer_assisted_scale | ask_if_context_relevant | supporting | True | True | structured_safety_validator |
| 1008 | Atemsymptome (Dyspnoe, Tachypnoe, Bradypnoe, ungenuegende O2-Saettigung) | oxygen_saturation_user_provided | measurement | measurement_input | True | conditional / user_provided_measurement | accept_if_user_provided | supporting | True | False | supporting_context |

## Review Notes

- `1001 Herzstillstand, Atemstillstand -> glasgow_coma_scale_observer_assisted` is a known review finding.
- It should later be replaced or supplemented with a lay-observable criterion such as `breathing_and_responsiveness_observed`.
- GCS should remain conditional/observer-assisted and is more suitable for neurologic, trauma, intoxication, or reduced-consciousness contexts.
- Further criteria links should be reviewed iteratively before being treated as stable.
