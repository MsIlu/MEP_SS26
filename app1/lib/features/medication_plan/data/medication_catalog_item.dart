/// Minimal medication metadata shown after selecting a demo catalog entry.
class MedicationCatalogItem {
  final String id;
  final String name;
  final String activeSubstance;
  final String strength;
  final String dosageForm;

  const MedicationCatalogItem({
    required this.id,
    required this.name,
    required this.activeSubstance,
    required this.strength,
    required this.dosageForm,
  });

  /// Compact description for autocomplete suggestions and detail rows.
  String get subtitle => '$activeSubstance • $strength • $dosageForm';

  /// Serializes the selected metadata together with the saved medication.
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'activeSubstance': activeSubstance,
      'strength': strength,
      'dosageForm': dosageForm,
    };
  }

  /// Serializes catalog metadata for the FastAPI medication endpoints.
  Map<String, dynamic> toApiJson() {
    return {
      'id': id,
      'name': name,
      'active_substance': activeSubstance,
      'strength': strength,
      'dosage_form': dosageForm,
    };
  }

  /// Restores catalog metadata from local medication storage.
  factory MedicationCatalogItem.fromJson(Map<String, dynamic> json) {
    return MedicationCatalogItem(
      id: json['id'] as String,
      name: json['name'] as String,
      activeSubstance: json['activeSubstance'] as String,
      strength: json['strength'] as String,
      dosageForm: json['dosageForm'] as String,
    );
  }

  /// Restores catalog metadata returned by the FastAPI medication endpoints.
  factory MedicationCatalogItem.fromApiJson(Map<String, dynamic> json) {
    return MedicationCatalogItem(
      id: json['id'] as String,
      name: json['name'] as String,
      activeSubstance: json['active_substance'] as String,
      strength: json['strength'] as String,
      dosageForm: json['dosage_form'] as String,
    );
  }
}
