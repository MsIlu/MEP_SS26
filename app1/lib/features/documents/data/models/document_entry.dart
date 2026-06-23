import 'dart:typed_data';

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
  final int? profileId;
  final String name;
  final DocumentCategory category;
  final DateTime createdAt;
  final int sizeInBytes;
  final DocumentSource source;
  final Uint8List? fileBytes;
  final String mimeType;

  const DocumentEntry({
    required this.id,
    this.profileId,
    required this.name,
    required this.category,
    required this.createdAt,
    required this.sizeInBytes,
    required this.source,
    this.fileBytes,
    this.mimeType = 'application/pdf',
  });

  DocumentEntry copyWith({
    int? profileId,
    String? name,
    DocumentCategory? category,
    DateTime? createdAt,
    int? sizeInBytes,
    DocumentSource? source,
    Uint8List? fileBytes,
    String? mimeType,
  }) {
    return DocumentEntry(
      id: id,
      profileId: profileId ?? this.profileId,
      name: name ?? this.name,
      category: category ?? this.category,
      createdAt: createdAt ?? this.createdAt,
      sizeInBytes: sizeInBytes ?? this.sizeInBytes,
      source: source ?? this.source,
      fileBytes: fileBytes ?? this.fileBytes,
      mimeType: mimeType ?? this.mimeType,
    );
  }
}
