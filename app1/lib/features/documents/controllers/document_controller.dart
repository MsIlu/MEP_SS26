import 'package:flutter/foundation.dart';

import '../data/document_repository.dart';
import '../data/models/document_entry.dart';

/// Controls profile, category, and search filtering for the document list.
class DocumentController extends ChangeNotifier {
  final DocumentRepository repository;

  /// Profile that owns documents newly imported through this controller.
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
  bool _isLoading = false;
  String? _errorMessage;

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
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

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

  /// Shows documents for every profile accessible through the current session.
  void showAllProfiles() {
    _showAllProfiles = true;
    notifyListeners();
  }

  Future<void> loadProfileDocuments(int profileId) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      await repository.loadProfileDocuments(profileId);
    } catch (_) {
      _errorMessage = 'Dokumente konnten nicht geladen werden.';
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> selectProfile(int profileId) async {
    _showAllProfiles = false;
    _selectedProfileId = profileId;
    notifyListeners();
    await loadProfileDocuments(profileId);
  }

  Future<void> syncActiveProfile(int? profileId) async {
    if (_selectedProfileId == profileId && !_showAllProfiles) return;

    _showAllProfiles = false;
    _selectedProfileId = profileId;
    notifyListeners();

    if (profileId != null) {
      await loadProfileDocuments(profileId);
    }
  }

  Future<void> addDocument({
    required String name,
    required DocumentCategory category,
    required Uint8List fileBytes,
    required String mimeType,
  }) async {
    final profileId = _selectedProfileId;
    if (profileId == null) {
      throw StateError('No active profile selected for document upload.');
    }

    await repository.addDocument(
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

  Future<void> renameDocument(String id, String name) async {
    final trimmedName = name.trim();
    if (trimmedName.isEmpty) return;

    await repository.renameDocument(id, trimmedName);
  }

  Future<void> deleteDocument(String id) async {
    await repository.deleteDocument(id);
  }

  Future<DocumentEntry> loadDocumentFile(DocumentEntry document) {
    return repository.loadDocumentFile(document);
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