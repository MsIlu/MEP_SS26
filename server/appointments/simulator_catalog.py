from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SimulatorProvider:
    name: str
    specialty: str
    street: str
    city: str
    postal_prefixes: tuple[str, ...]
    base_distance_km: float
    supports_video: bool = False


SPECIALTY_LABELS = {
    "general_practice": "Allgemeinmedizin",
    "cardiology": "Kardiologie",
    "dermatology": "Dermatologie",
    "gastroenterology": "Gastroenterologie",
    "orthopedics": "Orthopädie",
    "neurology": "Neurologie",
    "ent": "HNO",
    "dentistry": "Zahnmedizin",
    "ophthalmology": "Augenheilkunde",
    "gynecology": "Gynäkologie",
    "pediatrics": "Kinder- und Jugendmedizin",
    "psychiatry": "Psychiatrie",
    "urology": "Urologie",
    "emergency_medicine": "Notfallmedizin",
    "unknown": "Allgemeinmedizin",
}


# Synthetic provider data for the local 116117 simulator. Names and addresses
# are deliberately fictional and must never be presented as productive data.
PROVIDERS: tuple[SimulatorProvider, ...] = (
    SimulatorProvider("Hausarztzentrum am Markt", "general_practice", "Marktweg 12", "Mannheim", ("68",), 1.8, True),
    SimulatorProvider("Praxis Dr. Lena Sommer", "general_practice", "Rheinallee 44", "Mannheim", ("68",), 4.3),
    SimulatorProvider("Hausärztliche Gemeinschaftspraxis Neckar", "general_practice", "Neckarstraße 7", "Heidelberg", ("69",), 2.1, True),
    SimulatorProvider("Praxis am Schloss", "general_practice", "Schlossweg 18", "Stuttgart", ("70", "71"), 3.5),
    SimulatorProvider("Hausarztpraxis Mitte", "general_practice", "Luisenstraße 23", "Berlin", ("10", "12", "13"), 2.7, True),
    SimulatorProvider("Kardiologie am Wasserturm", "cardiology", "Friedrichsring 20", "Mannheim", ("68",), 2.7),
    SimulatorProvider("Herzpraxis Neckarstadt", "cardiology", "Käfertaler Straße 88", "Mannheim", ("68",), 4.6, True),
    SimulatorProvider("Kardiologie Heidelberg-West", "cardiology", "Kurfürsten-Anlage 32", "Heidelberg", ("69",), 3.3),
    SimulatorProvider("Herzzentrum Berlin-Mitte", "cardiology", "Luisenstraße 9", "Berlin", ("10", "12", "13"), 3.5),
    SimulatorProvider("Dermatologie Quadrat", "dermatology", "Q 4, 9", "Mannheim", ("68",), 3.2, True),
    SimulatorProvider("Hautzentrum Heidelberg", "dermatology", "Bergheimer Straße 51", "Heidelberg", ("69",), 2.9),
    SimulatorProvider("Hautärzte am Park", "dermatology", "Parkstraße 31", "Stuttgart", ("70", "71"), 5.1, True),
    SimulatorProvider("Dermatologie Spreebogen", "dermatology", "Spreeufer 8", "Berlin", ("10", "12", "13"), 4.0),
    SimulatorProvider("Gastroenterologie Rhein-Neckar", "gastroenterology", "Collinistraße 11", "Mannheim", ("68",), 3.9, True),
    SimulatorProvider("Magen-Darm-Praxis Heidelberg", "gastroenterology", "Sofienstraße 28", "Heidelberg", ("69",), 2.8),
    SimulatorProvider("Gastroenterologie Königstraße", "gastroenterology", "Königstraße 74", "Stuttgart", ("70", "71"), 3.6),
    SimulatorProvider("Gastro-Praxis Spreebogen", "gastroenterology", "Invalidenstraße 21", "Berlin", ("10", "12", "13"), 4.2),
    SimulatorProvider("Orthopädie Rhein-Neckar", "orthopedics", "Augustaanlage 16", "Mannheim", ("68",), 2.6),
    SimulatorProvider("Orthopädisches Zentrum Altstadt", "orthopedics", "Hauptstraße 88", "Heidelberg", ("69",), 3.8),
    SimulatorProvider("Orthopädie Königstraße", "orthopedics", "Königstraße 61", "Stuttgart", ("70", "71"), 1.9),
    SimulatorProvider("Orthopädie Berlin-Mitte", "orthopedics", "Invalidenstraße 42", "Berlin", ("10", "12", "13"), 3.4),
    SimulatorProvider("Neurologie am Wasserturm", "neurology", "Friedrichsplatz 5", "Mannheim", ("68",), 2.2, True),
    SimulatorProvider("Neurozentrum Heidelberg", "neurology", "Rohrbacher Straße 27", "Heidelberg", ("69",), 4.4),
    SimulatorProvider("Neurologische Praxis Stuttgart", "neurology", "Hegelstraße 14", "Stuttgart", ("70", "71"), 3.1, True),
    SimulatorProvider("Neurologie Charitébogen", "neurology", "Chausseestraße 19", "Berlin", ("10", "12", "13"), 2.5),
    SimulatorProvider("HNO-Zentrum Rhein", "ent", "Rheingoldstraße 22", "Mannheim", ("68",), 3.0),
    SimulatorProvider("HNO-Praxis Altstadt", "ent", "Plöck 35", "Heidelberg", ("69",), 2.4, True),
    SimulatorProvider("HNO am Schlossplatz", "ent", "Planie 3", "Stuttgart", ("70", "71"), 2.8),
    SimulatorProvider("HNO-Zentrum Alexanderplatz", "ent", "Alexanderstraße 11", "Berlin", ("10", "12", "13"), 3.7, True),
    SimulatorProvider("Zahnarztzentrum am Wasserturm", "dentistry", "Seckenheimer Straße 18", "Mannheim", ("68",), 2.0),
    SimulatorProvider("Zahnärzte Altstadt", "dentistry", "Sofienstraße 12", "Heidelberg", ("69",), 2.6),
    SimulatorProvider("Zahnmedizin Königstraße", "dentistry", "Königstraße 33", "Stuttgart", ("70", "71"), 1.7),
    SimulatorProvider("Zahnarztpraxis Spree", "dentistry", "Friedrichstraße 84", "Berlin", ("10", "12", "13"), 3.1),
    SimulatorProvider("Augenärzte Rhein-Neckar", "ophthalmology", "Tattersallstraße 9", "Mannheim", ("68",), 2.4),
    SimulatorProvider("Augenpraxis am Bismarckplatz", "ophthalmology", "Bismarckplatz 4", "Heidelberg", ("69",), 1.5),
    SimulatorProvider("Gynäkologie am Park", "gynecology", "Parkring 21", "Mannheim", ("68",), 3.6),
    SimulatorProvider("Frauenärzte Mitte", "gynecology", "Torstraße 40", "Berlin", ("10", "12", "13"), 2.8),
    SimulatorProvider("Kinderarztpraxis Neckar", "pediatrics", "Neckarauer Straße 30", "Mannheim", ("68",), 2.9),
    SimulatorProvider("Kinderärzte am Schloss", "pediatrics", "Schlossstraße 16", "Stuttgart", ("70", "71"), 2.2),
    SimulatorProvider("Psychiatrische Praxis am Luisenpark", "psychiatry", "Lameystraße 17", "Mannheim", ("68",), 3.7, True),
    SimulatorProvider("Praxis für Psychiatrie Heidelberg", "psychiatry", "Bergheimer Straße 19", "Heidelberg", ("69",), 2.6),
    SimulatorProvider("Psychiatrie Stuttgart-Mitte", "psychiatry", "Hauptstätter Straße 45", "Stuttgart", ("70", "71"), 3.8),
    SimulatorProvider("Psychiatrische Praxis Prenzlauer Berg", "psychiatry", "Schönhauser Allee 63", "Berlin", ("10", "12", "13"), 3.4, True),
    SimulatorProvider("Urologie Rhein", "urology", "Rheinhäuser Straße 15", "Mannheim", ("68",), 4.1),
    SimulatorProvider("Urologie Berlin-Mitte", "urology", "Leipziger Straße 55", "Berlin", ("10", "12", "13"), 3.0),
)


def providers_for(postal_code: str, specialty: str) -> list[SimulatorProvider]:
    normalized_specialty = specialty if specialty in SPECIALTY_LABELS else "general_practice"
    if normalized_specialty in {"unknown", "emergency_medicine"}:
        normalized_specialty = "general_practice"

    regional = [
        provider
        for provider in PROVIDERS
        if provider.specialty == normalized_specialty
        and any(postal_code.startswith(prefix) for prefix in provider.postal_prefixes)
    ]
    all_specialists = [
        provider for provider in PROVIDERS if provider.specialty == normalized_specialty
    ]
    # Return several different practices even in sparsely populated simulator
    # regions. Non-regional entries are presented as branches in the requested
    # test region when resources are generated.
    return (regional + [p for p in all_specialists if p not in regional])[:4]


def simulated_location(postal_code: str) -> str:
    mappings = {
        "68": "Mannheim",
        "69": "Heidelberg",
        "70": "Stuttgart",
        "71": "Region Stuttgart",
        "10": "Berlin",
        "12": "Berlin",
        "13": "Berlin",
    }
    return next(
        (city for prefix, city in mappings.items() if postal_code.startswith(prefix)),
        f"Testregion {postal_code}",
    )
