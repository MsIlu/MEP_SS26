from __future__ import annotations

from careena_pipeline3.domain.case_update import DialogueConsequence
from careena_pipeline3.models.domain import DialogueState, MedicalCase, PendingFollowup


MODULE_REQUIREMENTS: dict[str, tuple[str, ...]] = {
    "subject": ("subject.subject_relation",),
    "symptom": ("symptom.duration_or_onset",),
    "injury": ("injury.duration_or_onset", "injury.injury_context"),
    "measurement": ("measurement.kind", "measurement.value"),
    "medication": ("medication.name",),
    "risk_factor": ("risk_factor.kind",),
    "concern": ("concern.main_concern",),
    "administrative": (),
}

OBSERVATION_TYPE_TO_MODULE: dict[str, str] = {
    "symptom": "symptom",
    "injury": "injury",
    "measurement": "measurement",
    "medication": "medication",
    "risk_factor": "risk_factor",
    "concern": "concern",
    "administrative": "administrative",
}

FOLLOWUP_SLOT_ALIASES: dict[str, str] = {
    "subject.subject_relation": "subject",
    "subject.age": "subject_age",
    "symptom.duration_or_onset": "duration_or_onset",
    "injury.duration_or_onset": "duration_or_onset",
    "injury.injury_context": "injury_context",
    "injury.functional_limitation": "functional_limitation",
    "symptom.severity": "severity",
    "injury.severity": "severity",
}


class RequirementPolicy:
    """Derives centralized follow-up requirements from canonical case state."""

    def sync_dialogue_state(
        self,
        *,
        dialogue_state: DialogueState,
        medical_case: MedicalCase | None,
        active_modules: list[str],
        person_reference_present: bool = False,
        multi_person_context: bool = False,
        subject_relation_unclear: bool = False,
    ) -> DialogueState:
        normalized_modules = self.normalize_modules(active_modules)
        if not normalized_modules:
            normalized_modules = self.infer_active_modules(
                medical_case=medical_case,
                dialogue_state=dialogue_state,
            )
        resolved_requirements = self.resolved_requirements(
            medical_case=medical_case,
            dialogue_state=dialogue_state,
        )
        open_requirements = self.has_blocking_requirements(
            medical_case=medical_case,
            dialogue_state=dialogue_state,
            active_modules=normalized_modules,
            person_reference_present=person_reference_present,
            multi_person_context=multi_person_context,
            subject_relation_unclear=subject_relation_unclear,
        )

        dialogue_state.active_modules = normalized_modules
        dialogue_state.resolved_requirements = resolved_requirements
        dialogue_state.open_requirements = open_requirements
        dialogue_state.pending_followup = self.pending_followup_request(
            open_requirements=open_requirements,
            medical_case=medical_case,
            dialogue_state=dialogue_state,
        )
        return dialogue_state

    def normalize_modules(self, modules: list[str] | None) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for module in modules or []:
            if module not in MODULE_REQUIREMENTS or module in seen:
                continue
            seen.add(module)
            result.append(module)
        return result

    def required_requirements(
        self,
        *,
        medical_case: MedicalCase | None,
        dialogue_state: DialogueState,
        active_modules: list[str],
        person_reference_present: bool = False,
        multi_person_context: bool = False,
        subject_relation_unclear: bool = False,
    ) -> list[str]:
        normalized_modules = self.normalize_modules(active_modules)
        if not normalized_modules:
            normalized_modules = self.infer_active_modules(
                medical_case=medical_case,
                dialogue_state=dialogue_state,
            )
        requirements: list[str] = []

        for module in normalized_modules:
            for requirement in MODULE_REQUIREMENTS.get(module, ()):
                if requirement not in requirements:
                    requirements.append(requirement)

        if requirements and medical_case is not None and self.needs_subject_resolution(
            medical_case,
            person_reference_present=person_reference_present,
            multi_person_context=multi_person_context,
            subject_relation_unclear=subject_relation_unclear,
        ):
            if "subject.subject_relation" not in requirements:
                requirements.insert(0, "subject.subject_relation")

        return requirements

    def resolved_requirements(
        self,
        *,
        medical_case: MedicalCase | None,
        dialogue_state: DialogueState,
    ) -> list[str]:
        if medical_case is None:
            return []

        resolved: list[str] = []
        if medical_case.subject.relation != "unknown":
            resolved.append("subject.subject_relation")
        if medical_case.subject.age is not None:
            resolved.append("subject.age")

        for observation in medical_case.observations_of_type("symptom", include_negated=True):
            if observation.requirement_value("duration_or_onset"):
                self._append_unique(resolved, "symptom.duration_or_onset")
            if observation.requirement_value("body_site"):
                self._append_unique(resolved, "symptom.body_site")
            if observation.requirement_value("severity") is not None:
                self._append_unique(resolved, "symptom.severity")
            if observation.requirement_value("course"):
                self._append_unique(resolved, "symptom.course")

        for observation in medical_case.observations_of_type("injury", include_negated=True):
            if observation.requirement_value("duration_or_onset"):
                self._append_unique(resolved, "injury.duration_or_onset")
            if observation.requirement_value("body_site"):
                self._append_unique(resolved, "injury.body_site")
            if observation.requirement_value("severity") is not None:
                self._append_unique(resolved, "injury.severity")
            if observation.requirement_value("injury_context"):
                self._append_unique(resolved, "injury.injury_context")
            if observation.requirement_value("functional_limitation"):
                self._append_unique(resolved, "injury.functional_limitation")

        for observation in medical_case.observations_of_type("measurement", include_negated=True):
            if observation.requirement_value("kind"):
                self._append_unique(resolved, "measurement.kind")
            if observation.requirement_value("value"):
                self._append_unique(resolved, "measurement.value")

        for observation in medical_case.observations_of_type("medication", include_negated=True):
            if observation.requirement_value("name"):
                self._append_unique(resolved, "medication.name")

        for observation in medical_case.observations_of_type("risk_factor", include_negated=True):
            if observation.requirement_value("kind"):
                self._append_unique(resolved, "risk_factor.kind")

        for observation in medical_case.observations_of_type("concern", include_negated=True):
            if observation.requirement_value("main_concern"):
                self._append_unique(resolved, "concern.main_concern")

        return resolved

    def pending_followup_request(
        self,
        *,
        open_requirements: list[str],
        medical_case: MedicalCase | None,
        dialogue_state: DialogueState,
    ) -> PendingFollowup | None:
        if not open_requirements:
            return None
        first_requirement = open_requirements[0]
        focused = self.followup_target_observation(
            medical_case=medical_case,
            dialogue_state=dialogue_state,
            requirement_key=first_requirement,
        )
        return PendingFollowup(
            requirement_key=first_requirement,
            slot=FOLLOWUP_SLOT_ALIASES.get(first_requirement, first_requirement),
            kind="requirement",
            focus_observation_id=(focused.id if focused is not None else None),
            focus_label=(focused.patient_label if focused is not None else None),
        )

    def apply_dialogue_consequences(
        self,
        *,
        dialogue_state: DialogueState,
        medical_case: MedicalCase | None,
        dialogue_consequences: list[DialogueConsequence],
    ) -> DialogueState:
        if "ask_conflict_followup" in dialogue_consequences:
            dialogue_state.pending_followup = self._consequence_followup(
                medical_case=medical_case,
                dialogue_state=dialogue_state,
                kind="conflict",
                consequence="ask_conflict_followup",
                requirement_key="case.conflict_resolution",
                slot="case_conflict",
            )
            return dialogue_state

        if "ask_disambiguation_followup" in dialogue_consequences:
            dialogue_state.pending_followup = self._consequence_followup(
                medical_case=medical_case,
                dialogue_state=dialogue_state,
                kind="disambiguation",
                consequence="ask_disambiguation_followup",
                requirement_key="case.disambiguation",
                slot="case_disambiguation",
            )
        return dialogue_state

    def infer_active_modules(
        self,
        *,
        medical_case: MedicalCase | None,
        dialogue_state: DialogueState,
    ) -> list[str]:
        if medical_case is None:
            return []

        modules: list[str] = []
        if medical_case.subject.relation != "unknown" or medical_case.subject.age is not None:
            modules.append("subject")

        for observation in medical_case.active_observations(include_negated=True):
            module = OBSERVATION_TYPE_TO_MODULE.get(observation.type)
            if module is not None and module not in modules:
                modules.append(module)
        return modules

    def _consequence_followup(
        self,
        *,
        medical_case: MedicalCase | None,
        dialogue_state: DialogueState,
        kind: str,
        consequence: str,
        requirement_key: str,
        slot: str,
    ) -> PendingFollowup:
        focused = self.followup_target_observation(
            medical_case=medical_case,
            dialogue_state=dialogue_state,
            requirement_key=requirement_key,
        )
        return PendingFollowup(
            requirement_key=requirement_key,
            slot=slot,
            kind=kind,
            consequence=consequence,
            focus_observation_id=(focused.id if focused is not None else None),
            focus_label=(focused.patient_label if focused is not None else None),
        )

    def focused_observation(
        self,
        *,
        medical_case: MedicalCase | None,
        dialogue_state: DialogueState,
    ):
        if medical_case is None:
            return None

        focus_id = dialogue_state.focus_observation_id or medical_case.primary_problem_id
        if focus_id is not None:
            for observation in medical_case.active_observations(include_negated=True):
                if observation.id == focus_id:
                    return observation
        return medical_case.primary_observation()

    def followup_target_observation(
        self,
        *,
        medical_case: MedicalCase | None,
        dialogue_state: DialogueState,
        requirement_key: str,
    ):
        if medical_case is None:
            return None

        preferred = self.focused_observation(
            medical_case=medical_case,
            dialogue_state=dialogue_state,
        )
        if preferred is not None and self._observation_missing_requirement(
            preferred,
            requirement_key=requirement_key,
        ):
            return preferred

        for observation in medical_case.active_observations(include_negated=True):
            if self._observation_missing_requirement(
                observation,
                requirement_key=requirement_key,
            ):
                return observation
        return preferred

    def focused_observations(
        self,
        *,
        medical_case: MedicalCase | None,
        dialogue_state: DialogueState,
        types: tuple[str, ...] | None = None,
    ) -> list:
        if medical_case is None:
            return []

        focused = self.focused_observation(
            medical_case=medical_case,
            dialogue_state=dialogue_state,
        )
        if focused is not None and (types is None or focused.type in types):
            return [focused]
        if types is None:
            return medical_case.active_observations(include_negated=True)
        return medical_case.observations_of_type(*types, include_negated=True)

    def has_blocking_requirements(
        self,
        *,
        medical_case: MedicalCase | None,
        dialogue_state: DialogueState,
        active_modules: list[str],
        person_reference_present: bool = False,
        multi_person_context: bool = False,
        subject_relation_unclear: bool = False,
    ) -> list[str]:
        required = self.required_requirements(
            medical_case=medical_case,
            dialogue_state=dialogue_state,
            active_modules=active_modules,
            person_reference_present=person_reference_present,
            multi_person_context=multi_person_context,
            subject_relation_unclear=subject_relation_unclear,
        )
        if medical_case is None:
            return required

        blocking: list[str] = []
        for requirement in required:
            if self._requirement_missing_somewhere(
                medical_case=medical_case,
                dialogue_state=dialogue_state,
                requirement_key=requirement,
            ):
                blocking.append(requirement)
        return blocking

    @staticmethod
    def _append_unique(values: list[str], value: str) -> None:
        if value not in values:
            values.append(value)

    def _requirement_missing_somewhere(
        self,
        *,
        medical_case: MedicalCase,
        dialogue_state: DialogueState,
        requirement_key: str,
    ) -> bool:
        if requirement_key == "subject.subject_relation":
            return medical_case.subject.relation == "unknown"
        if requirement_key == "subject.age":
            return medical_case.subject.age is None

        observations = self._requirement_target_observations(
            medical_case=medical_case,
            dialogue_state=dialogue_state,
            requirement_key=requirement_key,
        )
        if not observations:
            return False
        return any(
            self._observation_missing_requirement(
                observation,
                requirement_key=requirement_key,
            )
            for observation in observations
        )

    def _requirement_target_observations(
        self,
        *,
        medical_case: MedicalCase,
        dialogue_state: DialogueState,
        requirement_key: str,
    ) -> list:
        if requirement_key.startswith("symptom."):
            return medical_case.observations_of_type("symptom", include_negated=True)
        if requirement_key.startswith("injury."):
            return medical_case.observations_of_type("injury", include_negated=True)
        if requirement_key.startswith("measurement."):
            return medical_case.observations_of_type("measurement", include_negated=True)
        if requirement_key.startswith("medication."):
            return medical_case.observations_of_type("medication", include_negated=True)
        if requirement_key.startswith("risk_factor."):
            return medical_case.observations_of_type("risk_factor", include_negated=True)
        if requirement_key.startswith("concern."):
            return medical_case.observations_of_type("concern", include_negated=True)
        focused = self.focused_observation(
            medical_case=medical_case,
            dialogue_state=dialogue_state,
        )
        return [focused] if focused is not None else []

    @staticmethod
    def _observation_missing_requirement(
        observation,
        *,
        requirement_key: str,
    ) -> bool:
        if "." not in requirement_key:
            return False
        observation_type, requirement_name = requirement_key.split(".", 1)
        if observation.type != observation_type:
            return False

        requirement_value = observation.requirement_value(requirement_name)
        if requirement_name == "severity":
            return requirement_value is None
        return requirement_value is None or requirement_value == "" or requirement_value == []

    @staticmethod
    def needs_subject_resolution(
        medical_case: MedicalCase,
        *,
        person_reference_present: bool = False,
        multi_person_context: bool = False,
        subject_relation_unclear: bool = False,
    ) -> bool:
        if multi_person_context or subject_relation_unclear:
            return True
        if not person_reference_present:
            return False
        if not medical_case.observations:
            return False

        subject_refs = {
            observation.subject_ref
            for observation in medical_case.observations
            if observation.subject_ref and observation.subject_ref != "unknown"
        }
        if len(subject_refs) > 1:
            return True
        if subject_refs and medical_case.subject.relation == "unknown":
            return True
        return False
