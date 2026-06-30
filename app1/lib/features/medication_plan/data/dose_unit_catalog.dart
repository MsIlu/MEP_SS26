/// Common dose units used by the medication form autocomplete.
class DoseUnitCatalog {
  static const units = [
    'mg',
    'g',
    'µg',
    'ml',
    'Tropfen',
    'Tablette(n)',
    'Kapsel(n)',
    'Beutel',
    'Pflaster',
  ];

  /// Returns matching units while keeping the suggestions intentionally short.
  static Iterable<String> search(String query) {
    final normalizedQuery = query.trim().toLowerCase();
    if (normalizedQuery.isEmpty) {
      return units.take(6);
    }

    return units
        .where((unit) => unit.toLowerCase().contains(normalizedQuery))
        .take(6);
  }
}
