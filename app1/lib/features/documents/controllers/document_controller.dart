import 'package:flutter/foundation.dart';

import '../data/document_repository.dart';
import '../data/models/document_entry.dart';

class DocumentController extends ChangeNotifier {
  final DocumentRepository repository;
  final int? profileId;

  DocumentController({DocumentRepository? repository, this.profileId})
    : repository = repository ?? DocumentRepository.instance,
      _selectedProfileId = profileId {
    this.repository.documents.addListener(_notifyRepositoryChanged);
  }

  String _searchQuery = '';
  DocumentCategory? _selectedCategory;
  int? _selectedProfileId;
  bool _showAllProfiles = false;

  List<DocumentEntry> get documents {
    final allDocuments = repository.documents.value;

    if (_showAllProfiles) {
      return List.unmodifiable(allDocuments);
    }

    return List.unmodifiable(
      allDocuments.where(
        (document) => document.profileId == _selectedProfileId,
      ),
    );
  }

  String get searchQuery => _searchQuery;

  DocumentCategory? get selectedCategory => _selectedCategory;
  int? get selectedProfileId => _selectedProfileId;
  bool get isShowingAllProfiles => _showAllProfiles;

  List<DocumentEntry> get visibleDocuments {
    final normalizedQuery = _searchQuery.trim().toLowerCase();

    final filtered = documents.where((document) {
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

  void showAllProfiles() {
    _showAllProfiles = true;
    notifyListeners();
  }

  void selectProfile(int profileId) {
    _showAllProfiles = false;
    _selectedProfileId = profileId;
    notifyListeners();
  }

  void addDocument({
    required String name,
    required DocumentCategory category,
    required Uint8List fileBytes,
    required String mimeType,
  }) {
    repository.addDocument(
      DocumentEntry(
        id: DateTime.now().microsecondsSinceEpoch.toString(),
        profileId: profileId,
        name: name.trim(),
        category: category,
        createdAt: DateTime.now(),
        sizeInBytes: fileBytes.lengthInBytes,
        source: DocumentSource.uploaded,
        fileBytes: fileBytes,
        mimeType: mimeType,
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
