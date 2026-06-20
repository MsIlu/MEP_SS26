enum DocumentCategory {
  findings('Befunde'),
  laboratory('Labor'),
  recommendations('Empfehlungen'),
  other('Sonstige');

  final String label;

  const DocumentCategory(this.label);
}

enum DocumentSource { uploaded, careena }

class DocumentEntry {
  final String id;
  final String name;
  final DocumentCategory category;
  final DateTime createdAt;
  final int sizeInBytes;
  final DocumentSource source;

  const DocumentEntry({
    required this.id,
    required this.name,
    required this.category,
    required this.createdAt,
    required this.sizeInBytes,
    required this.source,
  });

  DocumentEntry copyWith({
    String? name,
    DocumentCategory? category,
    DateTime? createdAt,
    int? sizeInBytes,
    DocumentSource? source,
  }) {
    return DocumentEntry(
      id: id,
      name: name ?? this.name,
      category: category ?? this.category,
      createdAt: createdAt ?? this.createdAt,
      sizeInBytes: sizeInBytes ?? this.sizeInBytes,
      source: source ?? this.source,
    );
  }
}
