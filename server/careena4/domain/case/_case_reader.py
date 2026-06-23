from careena4.models.domain import CaseTopic, MedicalCase, Observation


class _CaseReader:
    def read_observation(
        self,
        *,
        medical_case: MedicalCase,
        observation_id: str,
    ) -> Observation | None:
        return self._find_observation(
            medical_case=medical_case,
            observation_id=observation_id,
        )

    @staticmethod
    def read_observations(*, medical_case: MedicalCase) -> list[Observation]:
        return list(medical_case.observations)

    @staticmethod
    def read_active_observations(*, medical_case: MedicalCase) -> list[Observation]:
        return list(medical_case.active_observations())

    @staticmethod
    def read_central_observations(*, medical_case: MedicalCase) -> list[Observation]:
        return list(medical_case.central_observations())

    def read_central_non_negated_observations(
        self,
        *,
        medical_case: MedicalCase,
    ) -> list[Observation]:
        return [
            observation
            for observation in self.read_central_observations(medical_case=medical_case)
            if not observation.negated
        ]

    def read_topic_id(self, *, case_topic: CaseTopic | None) -> str | None:
        if case_topic is None:
            return None
        return case_topic.topic_id

    def read_topic_label(self, *, case_topic: CaseTopic | None) -> str | None:
        if case_topic is None:
            return None
        return case_topic.current_label

    def read_topic_tokens(self, *, case_topic: CaseTopic | None) -> set[str]:
        if case_topic is None:
            return set()
        return case_topic.search_tokens()

    @staticmethod
    def read_topic_extension_kinds(*, case_topic: CaseTopic | None) -> set[str]:
        if case_topic is None:
            return set()
        return {extension.kind for extension in case_topic.extensions}

    @staticmethod
    def read_topic_extensions(*, case_topic: CaseTopic | None):
        if case_topic is None:
            return []
        return list(case_topic.extensions)

    @staticmethod
    def read_topic_initial_label(*, case_topic: CaseTopic | None) -> str | None:
        if case_topic is None:
            return None
        return case_topic.initial_label

    @staticmethod
    def read_topic_type(*, case_topic: CaseTopic | None):
        if case_topic is None:
            return None
        return case_topic.topic_type

    def read_observation_label(
        self,
        *,
        medical_case: MedicalCase,
        observation_id: str,
    ) -> str | None:
        observation = self.read_observation(
            medical_case=medical_case,
            observation_id=observation_id,
        )
        if observation is None:
            return None
        return observation.label

    @staticmethod
    def read_has_active_observations(*, medical_case: MedicalCase) -> bool:
        return bool(_CaseReader.read_active_observations(medical_case=medical_case))

    @staticmethod
    def read_has_observations(*, medical_case: MedicalCase) -> bool:
        return bool(medical_case.observations)

    def read_first_observation_label(self, *, medical_case: MedicalCase | None) -> str | None:
        if medical_case is None:
            return None
        observations = self.read_active_observations(medical_case=medical_case)
        if not observations:
            return None
        return observations[0].label

    @staticmethod
    def read_person_relation(*, medical_case: MedicalCase):
        return medical_case.subject.relation

    @staticmethod
    def _find_observation(
        *,
        medical_case: MedicalCase,
        observation_id: str,
    ) -> Observation | None:
        return next(
            (
                observation
                for observation in medical_case.observations
                if observation.observation_id == observation_id
            ),
            None,
        )
