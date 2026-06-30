import 'package:flutter/foundation.dart';

import 'document_api_service.dart';
import 'models/document_entry.dart';

/// Shared document store used by chat, home, and document screens.
class DocumentRepository {
  DocumentRepository._();

  DocumentRepository({DocumentApiService? apiService})
    : _apiService = apiService;

  static final DocumentRepository instance = DocumentRepository._();

  DocumentApiService? _apiService;

  final ValueNotifier<List<DocumentEntry>> documents = ValueNotifier([]);

  /// Number of unseen Careena documents grouped by profile id.
  final ValueNotifier<Map<int?, int>> unreadCounts = ValueNotifier({});

  void configure({DocumentApiService? apiService}) {
    _apiService = apiService;
  }

  Future<void> loadProfileDocuments(int profileId) async {
    final apiService = _apiService;
    if (apiService == null) return;

    final remoteDocuments = await apiService.getDocuments(profileId);
    documents.value = [
      ...remoteDocuments,
      ...documents.value.where((document) => document.profileId != profileId),
    ];
  }

  /// Adds a Careena recommendation unless the same profile already owns one
  /// with the same normalized document name.
  Future<bool> addRecommendationIfMissing(DocumentEntry document) async {
    final alreadyExists = documents.value.any(
      (entry) =>
          entry.profileId == document.profileId &&
          entry.source == DocumentSource.careena &&
          entry.name.trim().toLowerCase() == document.name.trim().toLowerCase(),
    );

    if (alreadyExists) {
      return false;
    }

    await addDocument(document);
    final profileId = document.profileId;

    unreadCounts.value = {
      ...unreadCounts.value,
      profileId: (unreadCounts.value[profileId] ?? 0) + 1,
    };
    return true;
  }

  Future<DocumentEntry> addDocument(DocumentEntry document) async {
    final savedDocument = await _persistCreatedDocument(document);
    documents.value = [savedDocument, ...documents.value];
    return savedDocument;
  }

  Future<void> renameDocument(String id, String name) async {
    final currentDocument = _findById(id);
    if (currentDocument == null) return;

    final savedDocument = await _persistUpdatedDocument(
      currentDocument.copyWith(name: name.trim()),
    );

    documents.value = documents.value.map((document) {
      return document.id == id ? savedDocument : document;
    }).toList();
  }

  Future<void> deleteDocument(String id) async {
    final currentDocument = _findById(id);
    final profileId = currentDocument?.profileId;

    if (profileId != null) {
      await _apiService?.deleteDocument(profileId, id);
    }

    documents.value = documents.value
        .where((document) => document.id != id)
        .toList();
  }

  int unreadCountForProfile(int? profileId) {
    return unreadCounts.value[profileId] ?? 0;
  }

  void markAllAsSeen(int? profileId) {
    unreadCounts.value = {...unreadCounts.value, profileId: 0};
  }

  DocumentEntry? _findById(String id) {
    for (final document in documents.value) {
      if (document.id == id) return document;
    }

    return null;
  }

  Future<DocumentEntry> _persistCreatedDocument(DocumentEntry document) async {
    final profileId = document.profileId;
    final apiService = _apiService;

    if (profileId == null || apiService == null) {
      return document;
    }

    return apiService.createDocument(profileId, document);
  }

  Future<DocumentEntry> _persistUpdatedDocument(DocumentEntry document) async {
    final profileId = document.profileId;
    final apiService = _apiService;

    if (profileId == null || apiService == null) {
      return document;
    }

    return apiService.updateDocument(profileId, document);
  }
}
