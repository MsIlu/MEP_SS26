import 'package:flutter/foundation.dart';

import '../data/models/document_entry.dart';

class DocumentController extends ChangeNotifier {
  DocumentController({List<DocumentEntry>? initialDocuments})
    : _documents = initialDocuments ?? _demoDocuments;

  static final List<DocumentEntry> _demoDocuments = [
    DocumentEntry(
      id: 'recommendation-1',
      name: 'Handlungsempfehlung Kopfschmerzen.pdf',
      category: DocumentCategory.recommendations,
      createdAt: DateTime(2026, 6, 16),
      sizeInBytes: 284000,
      source: DocumentSource.careena,
    ),
    DocumentEntry(
      id: 'laboratory-1',
      name: 'Blutwerte Juni 2026.pdf',
      category: DocumentCategory.laboratory,
      createdAt: DateTime(2026, 6, 8),
      sizeInBytes: 1150000,
      source: DocumentSource.uploaded,
    ),
    DocumentEntry(
      id: 'findings-1',
      name: 'Befund Hausarzt.pdf',
      category: DocumentCategory.findings,
      createdAt: DateTime(2026, 5, 24),
      sizeInBytes: 692000,
      source: DocumentSource.uploaded,
    ),
  ];

  List<DocumentEntry> _documents;
  String _searchQuery = '';
  DocumentCategory? _selectedCategory;

  List<DocumentEntry> get documents => List.unmodifiable(_documents);
  String get searchQuery => _searchQuery;
  DocumentCategory? get selectedCategory => _selectedCategory;

  List<DocumentEntry> get visibleDocuments {
    final normalizedQuery = _searchQuery.trim().toLowerCase();
    final filtered = _documents.where((document) {
      final matchesCategory =
          _selectedCategory == null || document.category == _selectedCategory;
      final matchesSearch =
          normalizedQuery.isEmpty ||
          document.name.toLowerCase().contains(normalizedQuery) ||
          document.category.label.toLowerCase().contains(normalizedQuery);

      return matchesCategory && matchesSearch;
    }).toList();

    filtered.sort((a, b) => b.createdAt.compareTo(a.createdAt));
    return filtered;
  }

  void updateSearch(String query) {
    _searchQuery = query;
    notifyListeners();
  }

  void selectCategory(DocumentCategory? category) {
    _selectedCategory = category;
    notifyListeners();
  }

  void addDocument({required String name, required DocumentCategory category}) {
    final normalizedName = name.trim().toLowerCase().endsWith('.pdf')
        ? name.trim()
        : '${name.trim()}.pdf';

    _documents = [
      DocumentEntry(
        id: DateTime.now().microsecondsSinceEpoch.toString(),
        name: normalizedName,
        category: category,
        createdAt: DateTime.now(),
        sizeInBytes: 0,
        source: DocumentSource.uploaded,
      ),
      ..._documents,
    ];
    notifyListeners();
  }

  void renameDocument(String id, String name) {
    final trimmedName = name.trim();
    if (trimmedName.isEmpty) return;

    _documents = _documents
        .map(
          (document) => document.id == id
              ? document.copyWith(name: trimmedName)
              : document,
        )
        .toList();
    notifyListeners();
  }

  void deleteDocument(String id) {
    _documents = _documents.where((document) => document.id != id).toList();
    notifyListeners();
  }
}
