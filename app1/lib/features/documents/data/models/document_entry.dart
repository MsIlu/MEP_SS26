import 'dart:convert';
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

/// Frontend representation of an imported or Careena-generated document.
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
    String? id,
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
      id: id ?? this.id,
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

  factory DocumentEntry.fromApiJson(Map<String, dynamic> json) {
    final fileDataBase64 = json['file_data_base64']?.toString() ?? '';

    return DocumentEntry(
      id: json['id']?.toString() ?? '',
      profileId: _intFromJson(json['profile_id']),
      name: json['name']?.toString() ?? '',
      category: _categoryFromApi(json['category']?.toString()),
      createdAt:
          DateTime.tryParse(json['created_at']?.toString() ?? '') ??
          DateTime.now(),
      sizeInBytes: _intFromJson(json['size_in_bytes']) ?? 0,
      source: _sourceFromApi(json['source']?.toString()),
      fileBytes: fileDataBase64.isEmpty ? null : base64Decode(fileDataBase64),
      mimeType: json['mime_type']?.toString() ?? 'application/pdf',
    );
  }

  Map<String, dynamic> toCreateApiJson() {
    return {
      'name': name,
      'category': category.apiValue,
      'source': source.apiValue,
      'size_in_bytes': sizeInBytes,
      'mime_type': mimeType,
      'file_data_base64': fileBytes == null ? '' : base64Encode(fileBytes!),
      'created_at': createdAt.toIso8601String(),
    };
  }

  Map<String, dynamic> toUpdateApiJson() {
    return {
      'name': name,
      'category': category.apiValue,
    };
  }
}

extension DocumentCategoryApiValue on DocumentCategory {
  String get apiValue {
    switch (this) {
      case DocumentCategory.findings:
        return 'findings';
      case DocumentCategory.laboratory:
        return 'laboratory';
      case DocumentCategory.recommendations:
        return 'recommendations';
      case DocumentCategory.other:
        return 'other';
    }
  }
}

extension DocumentSourceApiValue on DocumentSource {
  String get apiValue {
    switch (this) {
      case DocumentSource.uploaded:
        return 'uploaded';
      case DocumentSource.careena:
        return 'careena';
    }
  }
}

DocumentCategory _categoryFromApi(String? value) {
  return DocumentCategory.values.firstWhere(
    (category) => category.apiValue == value,
    orElse: () => DocumentCategory.other,
  );
}

DocumentSource _sourceFromApi(String? value) {
  return DocumentSource.values.firstWhere(
    (source) => source.apiValue == value,
    orElse: () => DocumentSource.uploaded,
  );
}

int? _intFromJson(dynamic value) {
  if (value is int) return value;
  if (value is num) return value.toInt();
  return int.tryParse(value?.toString() ?? '');
}