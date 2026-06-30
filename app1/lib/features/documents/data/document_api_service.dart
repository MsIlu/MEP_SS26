import 'package:app1/core/network/api_client.dart';

import 'models/document_entry.dart';

/// Provides API methods for profile-scoped document entries.
class DocumentApiService {
  final ApiClient _apiClient;

  const DocumentApiService(this._apiClient);

  Future<List<DocumentEntry>> getDocuments(int profileId) async {
    final response = await _apiClient.getList(_path(profileId));

    return response
        .map((item) => DocumentEntry.fromApiJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<DocumentEntry> createDocument(
    int profileId,
    DocumentEntry document,
  ) async {
    final response = await _apiClient.post(
      _path(profileId),
      document.toCreateApiJson(),
    );

    return DocumentEntry.fromApiJson(response);
  }

  Future<DocumentEntry> updateDocument(
    int profileId,
    DocumentEntry document,
  ) async {
    final response = await _apiClient.patch(
      '${_path(profileId)}/${document.id}',
      document.toUpdateApiJson(),
    );

    return DocumentEntry.fromApiJson(response);
  }

  Future<void> deleteDocument(int profileId, String documentId) async {
    await _apiClient.delete('${_path(profileId)}/$documentId');
  }

  String _path(int profileId) => '/profiles/$profileId/documents';
}