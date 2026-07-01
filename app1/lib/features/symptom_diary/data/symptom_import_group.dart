import 'symptom_import.dart';

class IndexedSymptomImport {
  final int index;
  final SymptomImport symptomImport;

  const IndexedSymptomImport({
    required this.index,
    required this.symptomImport,
  });
}

class SymptomImportGroup {
  final String id;
  final String name;
  final int? severity;
  final String? bodyArea;
  final List<IndexedSymptomImport> items;

  const SymptomImportGroup({
    required this.id,
    required this.name,
    required this.severity,
    required this.bodyArea,
    required this.items,
  });
}

List<SymptomImportGroup> groupSymptomImports(List<SymptomImport> imports) {
  final groupsByKey = <String, List<IndexedSymptomImport>>{};

  for (var i = 0; i < imports.length; i++) {
    final symptomImport = imports[i];
    // Dates stay selectable inside the group; only stable symptom properties group.
    final key = [
      symptomImport.name.trim().toLowerCase(),
      symptomImport.severity?.toString() ?? '',
      symptomImport.bodyArea ?? '',
    ].join('|');
    groupsByKey
        .putIfAbsent(key, () => [])
        .add(IndexedSymptomImport(index: i, symptomImport: symptomImport));
  }

  return groupsByKey.entries.map((entry) {
    final first = entry.value.first.symptomImport;
    return SymptomImportGroup(
      id: entry.key,
      name: first.name,
      severity: first.severity,
      bodyArea: first.bodyArea,
      items: entry.value,
    );
  }).toList();
}
