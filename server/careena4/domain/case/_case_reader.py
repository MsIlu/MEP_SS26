from careena4.models.domain import MedicalCase, Observation


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
        return self.read_central_observations(medical_case=medical_case)

    @staticmethod
    def read_topic_label(*, medical_case: MedicalCase | None) -> str | None:
        if medical_case is None or medical_case.topic is None:
            return None
        label = medical_case.topic.label.strip()
        return label or None

    @staticmethod
    def read_topic_description(*, medical_case: MedicalCase | None) -> str | None:
        if medical_case is None or medical_case.topic is None:
            return None
        description = medical_case.topic.description.strip()
        return description or None

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

    @staticmethod
    def read_has_topic(*, medical_case: MedicalCase | None) -> bool:
        return bool(
            medical_case is not None
            and medical_case.topic is not None
            and (
                medical_case.topic.label.strip()
                or medical_case.topic.description.strip()
            )
        )

    def read_first_observation_label(self, *, medical_case: MedicalCase | None) -> str | None:
        if medical_case is None:
            return None
        observations = self.read_active_observations(medical_case=medical_case)
        if not observations:
            return None
        return observations[0].label

    @staticmethod
    def read_person_relation(*, medical_case: MedicalCase):
        return medical_case.person.relation

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
