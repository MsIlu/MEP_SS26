from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """
    Baseschema für die Audit- und Protokoll-Metadaten 
    """

    model_config = ConfigDict(
        # Überprüft Datentypen auch bei nachträglichen Änderungen im Code
        validate_assignment=True,
        
        # Blockiert unbekannte JSON-Felder sofort (Schutz vor fehlerhaften API-Anfragen)
        extra="forbid",
        
        # Wandelt Enums (z. B. Versorgungsebenen) automatisch in Werte (Strings/ints) um
        use_enum_values=True,

        # Zwingt Pydantic, verschachtelte Modelle über absolute Pfade im Hintergrund neu aufzubauen
        rebuild_instance_models=True
    )