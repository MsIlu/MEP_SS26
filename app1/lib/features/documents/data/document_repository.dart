import 'package:flutter/foundation.dart';

import 'models/document_entry.dart';

class DocumentRepository {
  DocumentRepository._();

  static final DocumentRepository instance = DocumentRepository._();

  final ValueNotifier<List<DocumentEntry>> documents = ValueNotifier([]);
  final ValueNotifier<int> unreadCount = ValueNotifier(0);

  bool addRecommendationIfMissing(DocumentEntry document) {
    final alreadyExists = documents.value.any(
      (entry) =>
          entry.source == DocumentSource.careena &&
          entry.name.trim().toLowerCase() ==
              document.name.trim().toLowerCase(),
    );

    if (alreadyExists) {
      return false;
    }

    documents.value = [document, ...documents.value];
    unreadCount.value++;
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

  void markAllAsSeen() {
    unreadCount.value = 0;
  }
}