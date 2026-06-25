import 'medication_catalog_item.dart';

/// Local sample catalog used until the official backend search is connected.
class DemoMedicationCatalog {
  static const List<MedicationCatalogItem> items = [
    MedicationCatalogItem(
      id: 'demo-ibuprofen-400',
      name: 'Ibuprofen 400 mg Filmtabletten',
      activeSubstance: 'Ibuprofen',
      strength: '400 mg',
      dosageForm: 'Filmtablette',
    ),
    MedicationCatalogItem(
      id: 'demo-paracetamol-500',
      name: 'Paracetamol 500 mg Tabletten',
      activeSubstance: 'Paracetamol',
      strength: '500 mg',
      dosageForm: 'Tablette',
    ),
    MedicationCatalogItem(
      id: 'demo-ass-100',
      name: 'ASS 100 mg Tabletten',
      activeSubstance: 'Acetylsalicylsäure',
      strength: '100 mg',
      dosageForm: 'Tablette',
    ),
    MedicationCatalogItem(
      id: 'demo-pantoprazol-20',
      name: 'Pantoprazol 20 mg magensaftresistente Tabletten',
      activeSubstance: 'Pantoprazol',
      strength: '20 mg',
      dosageForm: 'magensaftresistente Tablette',
    ),
    MedicationCatalogItem(
      id: 'demo-cetirizin-10',
      name: 'Cetirizin 10 mg Filmtabletten',
      activeSubstance: 'Cetirizin',
      strength: '10 mg',
      dosageForm: 'Filmtablette',
    ),
    MedicationCatalogItem(
      id: 'demo-novaminsulfon-500',
      name: 'Novaminsulfon 500 mg Tabletten',
      activeSubstance: 'Metamizol-Natrium',
      strength: '500 mg',
      dosageForm: 'Tablette',
    ),
  ];

  /// Searches the small demo catalog by product name and user-relevant metadata.
  static Iterable<MedicationCatalogItem> search(String query) {
    final normalizedQuery = query.trim().toLowerCase();
    if (normalizedQuery.isEmpty) {
      return items.take(4);
    }

    return items
        .where((item) {
          final haystack = [
            item.name,
            item.activeSubstance,
            item.strength,
            item.dosageForm,
          ].join(' ').toLowerCase();

          return haystack.contains(normalizedQuery);
        })
        .take(6);
  }
}
