import 'package:flutter/foundation.dart';

import 'models/document_entry.dart';

class DocumentRepository {
  DocumentRepository._();

  static final DocumentRepository instance = DocumentRepository._();

  final ValueNotifier<List<DocumentEntry>> documents = ValueNotifier([]);
  final ValueNotifier<Map<int?, int>> unreadCounts = ValueNotifier({});

  bool addRecommendationIfMissing(DocumentEntry document) {
    final alreadyExists = documents.value.any(
      (entry) =>
          entry.profileId == document.profileId &&
          entry.source == DocumentSource.careena &&
          entry.name.trim().toLowerCase() == document.name.trim().toLowerCase(),
    );

    if (alreadyExists) {
      return false;
    }

    documents.value = [document, ...documents.value];
    final profileId = document.profileId;

unreadCounts.value = {
  ...unreadCounts.value,
  profileId: (unreadCounts.value[profileId] ?? 0) + 1,
};
    return true;
  }

  void addDocument(DocumentEntry document) {
    documents.value = [document, ...documents.value];
  }

  void renameDocument(String id, String name) {
    documents.value = documents.value.map((document) {
      return document.id == id
          ? document.copyWith(name: name.trim())
          : document;
    }).toList();
  }

  void deleteDocument(String id) {
    documents.value = documents.value
        .where((document) => document.id != id)
        .toList();
  }

  int unreadCountForProfile(int? profileId) {
  return unreadCounts.value[profileId] ?? 0;
}

void markAllAsSeen(int? profileId) {
  unreadCounts.value = {
    ...unreadCounts.value,
    profileId: 0,
  };
}
}
