from fhir_mapper.mapper import map_to_fhir_bundle
from fhir_mapper.validator import validate_fhir_bundle


def _sample_internal_data():
    return {
        "patient": {
            "id": "test-patient-1",
            "birthDate": "1998-05-12",
            "gender": "male",
        },
        "input": {
            "rawText": "Ich habe seit gestern Kopfschmerzen und Halsschmerzen.",
        },
        "analysis": {
            "observations": {
                "events": [
                    {
                        "id": "obs-1",
                        "type": "symptom",
                        "label": "Kopfschmerzen",
                        "source_span": "Kopfschmerzen",
                        "context": {
                            "negated": False,
                            "certainty": "confirmed",
                            "temporality": "seit gestern",
                        },
                    },
                    {
                        "id": "obs-2",
                        "type": "symptom",
                        "label": "Halsschmerzen",
                        "source_span": "Halsschmerzen",
                        "context": {
                            "negated": False,
                            "certainty": "confirmed",
                            "temporality": None,
                        },
                    },
                ]
            }
        },
        "recommendation": {
            "urgency": "non_urgent",
            "text": "Selbstbeobachtung. Bei Verschlechterung ärztliche Hilfe suchen.",
        },
    }


def test_map_to_fhir_bundle_creates_expected_resources():
    bundle = map_to_fhir_bundle(_sample_internal_data())

    assert bundle["resourceType"] == "Bundle"
    assert bundle["type"] == "collection"

    resources = [entry["resource"] for entry in bundle["entry"]]
    resource_types = [resource["resourceType"] for resource in resources]

    assert "Patient" in resource_types
    assert "QuestionnaireResponse" in resource_types
    assert "Observation" in resource_types
    assert "ServiceRequest" in resource_types

    observations = [
        resource
        for resource in resources
        if resource["resourceType"] == "Observation"
    ]

    assert len(observations) == 2
    assert observations[0]["code"]["text"] == "Kopfschmerzen"
    assert observations[1]["code"]["text"] == "Halsschmerzen"


def test_service_request_contains_urgency_extension():
    bundle = map_to_fhir_bundle(_sample_internal_data())

    resources = [entry["resource"] for entry in bundle["entry"]]
    service_request = next(
        resource
        for resource in resources
        if resource["resourceType"] == "ServiceRequest"
    )

    assert service_request["status"] == "draft"
    assert service_request["intent"] == "proposal"
    assert service_request["extension"][0]["valueCode"] == "non_urgent"


def test_generated_bundle_passes_fhir_resources_validation():
    bundle = map_to_fhir_bundle(_sample_internal_data())

    validated = validate_fhir_bundle(bundle)

    assert validated["resourceType"] == "Bundle"
    assert validated["type"] == "collection"