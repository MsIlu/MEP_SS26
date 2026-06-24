from careena4.domain.case._case_input_models import _LegacyCaseWritePayload, _ObservationPatch
from careena4.models.domain import Observation, Person, Source
from careena4.models.turn import ExtractedCaseInput, ExtractedObservationInput, ObservationPatch, PersonUpdate


class _LegacyCaseInputAdapter:
    def adapt_case_input(self, *, case_input: ExtractedCaseInput) -> _LegacyCaseWritePayload:
        return _LegacyCaseWritePayload(
            person_update=self._person_update(case_input=case_input),
            observations=[self._observation_from_input(observation_input=observation) for observation in case_input.observations],
        )

    def adapt_followup_patch(self, *, patch: ObservationPatch) -> _ObservationPatch:
        return _ObservationPatch(
            onset=patch.onset,
            onset_source=self._copy_source(patch.onset_source),
            body_site=patch.body_site,
            body_site_source=self._copy_source(patch.body_site_source),
            description=patch.description,
            description_source=self._copy_source(patch.description_source),
            severity=patch.severity,
            severity_source=self._copy_source(patch.severity_source),
            mechanism=patch.mechanism,
            mechanism_source=self._copy_source(patch.mechanism_source),
            functional_limitation=patch.functional_limitation,
            functional_limitation_source=self._copy_source(patch.functional_limitation_source),
            measurement_kind=patch.measurement_kind,
            measurement_kind_source=self._copy_source(patch.measurement_kind_source),
        )

    def adapt_person_update(self, *, person_update: PersonUpdate) -> Person | None:
        if person_update.relation not in {"self", "child", "other", "unclear"}:
            return None
        return Person(
            relation=person_update.relation,
            relation_source=self._copy_source(person_update.relation_source),
        )

    @staticmethod
    def _person_update(*, case_input: ExtractedCaseInput) -> Person | None:
        if case_input.person is None:
            return None
        if case_input.person.relation not in {"self", "child", "other", "unclear"}:
            return None
        return Person(
            relation=case_input.person.relation,
            relation_source=case_input.person.relation_source.model_copy(deep=True)
            if case_input.person.relation_source is not None
            else None,
        )

    def _observation_from_input(self, *, observation_input: ExtractedObservationInput) -> Observation:
        person_ref = observation_input.person_ref or "unclear"
        observation = Observation(
            type=observation_input.type,
            label=observation_input.label,
            label_source=self._copy_source(observation_input.label_source),
            status=observation_input.status,
            status_source=self._copy_source(observation_input.status_source),
            person_ref=person_ref,
            person_ref_source=self._copy_source(observation_input.person_ref_source),
            onset=observation_input.onset,
            onset_source=self._copy_source(observation_input.onset_source),
            body_site=observation_input.body_site,
            body_site_source=self._copy_source(observation_input.body_site_source),
            description=observation_input.description,
            description_sources=(
                [observation_input.description_source.model_copy(deep=True)]
                if observation_input.description_source is not None
                else []
            ),
            severity=observation_input.severity,
            severity_source=self._copy_source(observation_input.severity_source),
            mechanism=observation_input.mechanism,
            mechanism_source=self._copy_source(observation_input.mechanism_source),
            functional_limitation=observation_input.functional_limitation,
            functional_limitation_source=self._copy_source(observation_input.functional_limitation_source),
            measurement_kind=observation_input.measurement_kind,
            measurement_kind_source=self._copy_source(observation_input.measurement_kind_source),
        )
        return observation

    @staticmethod
    def _copy_source(source: Source | None) -> Source | None:
        if source is None:
            return None
        return source.model_copy(deep=True)
