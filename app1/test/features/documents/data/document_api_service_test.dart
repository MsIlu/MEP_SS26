import 'dart:convert';
import 'dart:typed_data';

import 'package:app1/core/network/api_client.dart';
import 'package:app1/features/documents/data/document_api_service.dart';
import 'package:app1/features/documents/data/models/document_entry.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

void main() {
  group('DocumentApiService', () {
    test('getDocuments parses metadata list and sends auth header', () async {
      String? authorizationHeader;

      final mockHttpClient = MockClient((request) async {
        expect(request.method, 'GET');
        expect(request.url.path, contains('/profiles/10/documents'));

        authorizationHeader = request.headers['Authorization'];

        return http.Response(
          jsonEncode([_apiDocumentMetadataJson()]),
          200,
          headers: {'content-type': 'application/json'},
        );
      });

      final apiClient = ApiClient(mockHttpClient);
      apiClient.setAccessToken('test-token');

      final service = DocumentApiService(apiClient);
      final documents = await service.getDocuments(10);

      expect(authorizationHeader, 'Bearer test-token');
      expect(documents, hasLength(1));
      expect(documents.first.id, '42');
      expect(documents.first.profileId, 10);
      expect(documents.first.category, DocumentCategory.findings);
      expect(documents.first.fileBytes, isNull);
    });

    test('getDocument parses full document with file data', () async {
      final mockHttpClient = MockClient((request) async {
        expect(request.method, 'GET');
        expect(request.url.path, contains('/profiles/10/documents/42'));

        return http.Response(
          jsonEncode(_apiDocumentJson()),
          200,
          headers: {'content-type': 'application/json'},
        );
      });

      final service = DocumentApiService(ApiClient(mockHttpClient));
      final document = await service.getDocument(10, '42');

      expect(document.id, '42');
      expect(document.profileId, 10);
      expect(document.fileBytes, Uint8List.fromList([1, 2, 3]));
    });

    test('metadata without file data keeps file bytes empty', () {
      final document = DocumentEntry.fromApiJson(_apiDocumentJson()
        ..remove('file_data_base64'));

      expect(document.fileBytes, isNull);
      expect(document.mimeType, 'application/pdf');
    });

    test('document with file data decodes bytes', () {
      final document = DocumentEntry.fromApiJson(_apiDocumentJson());

      expect(document.fileBytes, Uint8List.fromList([1, 2, 3]));
    });

    test('createDocument sends FastAPI document JSON', () async {
      Map<String, dynamic>? sentBody;

      final mockHttpClient = MockClient((request) async {
        expect(request.method, 'POST');
        expect(request.url.path, contains('/profiles/10/documents'));

        sentBody = jsonDecode(request.body) as Map<String, dynamic>;

        return http.Response(
          jsonEncode(_apiDocumentJson(id: 43)),
          200,
          headers: {'content-type': 'application/json'},
        );
      });

      final service = DocumentApiService(ApiClient(mockHttpClient));
      final created = await service.createDocument(10, _entry());

      expect(sentBody?['name'], 'Befund.pdf');
      expect(sentBody?['category'], 'findings');
      expect(sentBody?['source'], 'uploaded');
      expect(sentBody?['mime_type'], 'application/pdf');
      expect(sentBody?['file_data_base64'], 'AQID');
      expect(created.id, '43');
    });

    test('updateDocument sends patch JSON with editable metadata', () async {
      Map<String, dynamic>? sentBody;

      final mockHttpClient = MockClient((request) async {
        expect(request.method, 'PATCH');
        expect(request.url.path, contains('/profiles/10/documents/1'));

        sentBody = jsonDecode(request.body) as Map<String, dynamic>;

        return http.Response(
          jsonEncode(_apiDocumentJson()),
          200,
          headers: {'content-type': 'application/json'},
        );
      });

      final service = DocumentApiService(ApiClient(mockHttpClient));
      await service.updateDocument(10, _entry());

      expect(sentBody, isNot(contains('file_data_base64')));
      expect(sentBody?['name'], 'Befund.pdf');
      expect(sentBody?['category'], 'findings');
    });
  });
}

DocumentEntry _entry() {
  return DocumentEntry(
    id: '1',
    profileId: 10,
    name: 'Befund.pdf',
    category: DocumentCategory.findings,
    createdAt: DateTime(2026, 6, 23),
    sizeInBytes: 3,
    source: DocumentSource.uploaded,
    fileBytes: Uint8List.fromList([1, 2, 3]),
    mimeType: 'application/pdf',
  );
}

Map<String, dynamic> _apiDocumentJson({int id = 42}) {
  return {
    'id': id,
    'profile_id': 10,
    'name': 'Befund.pdf',
    'category': 'findings',
    'source': 'uploaded',
    'size_in_bytes': 3,
    'mime_type': 'application/pdf',
    'file_data_base64': 'AQID',
    'created_at': '2026-06-23T10:00:00',
    'updated_at': '2026-06-23T10:00:00',
  };
}

Map<String, dynamic> _apiDocumentMetadataJson({int id = 42}) {
  return _apiDocumentJson(id: id)..remove('file_data_base64');
}