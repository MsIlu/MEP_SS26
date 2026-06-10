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
}