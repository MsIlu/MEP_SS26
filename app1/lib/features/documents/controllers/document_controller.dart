import 'package:flutter/foundation.dart';

import '../data/document_repository.dart';
import '../data/models/document_entry.dart';

class DocumentController extends ChangeNotifier {
  final DocumentRepository repository;

  DocumentController({
    DocumentRepository? repository,
  }) : repository = repository ?? DocumentRepository.instance {
    this.repository.documents.addListener(_notifyRepositoryChanged);
  }

  String _searchQuery = '';
  DocumentCategory? _selectedCategory;

  List<DocumentEntry> get documents =>
      List.unmodifiable(repository.documents.value);

  String get searchQuery => _searchQuery;

  DocumentCategory? get selectedCategory => _selectedCategory;

  List<DocumentEntry> get visibleDocuments {
    final normalizedQuery = _searchQuery.trim().toLowerCase();

    final filtered = repository.documents.value.where((document) {
      final matchesCategory =
          _selectedCategory == null ||
          document.category == _selectedCategory;

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

  void addDocument({
    required String name,
    required DocumentCategory category,
  }) {
    final normalizedName = name.trim().toLowerCase().endsWith('.pdf')
        ? name.trim()
        : '${name.trim()}.pdf';

    repository.addDocument(
      DocumentEntry(
        id: DateTime.now().microsecondsSinceEpoch.toString(),
        name: normalizedName,
        category: category,
        createdAt: DateTime.now(),
        sizeInBytes: 0,
        source: DocumentSource.uploaded,
      ),
    );
  }

  void renameDocument(String id, String name) {
    final trimmedName = name.trim();
    if (trimmedName.isEmpty) return;

    repository.renameDocument(id, trimmedName);
  }

  void deleteDocument(String id) {
    repository.deleteDocument(id);
  }

  void _notifyRepositoryChanged() {
    notifyListeners();
  }

  @override
  void dispose() {
    repository.documents.removeListener(_notifyRepositoryChanged);
    super.dispose();
  }
}
