import 'dart:convert';

import 'package:app1/core/network/api_client.dart';
import 'package:app1/features/documents/data/document_api_service.dart';
import 'package:app1/features/documents/data/document_repository.dart';
import 'package:app1/features/documents/data/models/document_entry.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

void main() {
  late DocumentRepository repository;

  setUp(() {
    repository = DocumentRepository.instance;
    repository.configure(apiService: null);

    // Gemeinsamen Speicher vor jedem Test zurücksetzen.
    repository.documents.value = [];
    repository.unreadCounts.value = {};
  });

  DocumentEntry createDocument({
    required String id,
    required int profileId,
    String name = 'Befund.pdf',
    DocumentSource source = DocumentSource.uploaded,
  }) {
    return DocumentEntry(
      id: id,
      profileId: profileId,
      name: name,
      category: source == DocumentSource.careena
          ? DocumentCategory.recommendations
          : DocumentCategory.findings,
      createdAt: DateTime(2026, 6, 23),
      sizeInBytes: 1000,
      source: source,
    );
  }

  test('adds a document', () async {
    final document = createDocument(id: '1', profileId: 10);

    await repository.addDocument(document);

    expect(repository.documents.value, hasLength(1));
    expect(repository.documents.value.first, same(document));
  });

  test('deletes a document by id', () async {
    await repository.addDocument(
      createDocument(id: '1', profileId: 10),
    );

    await repository.deleteDocument('1');

    expect(repository.documents.value, isEmpty);
  });

  test('prevents duplicate recommendation for the same profile', () async {
    final first = createDocument(
      id: '1',
      profileId: 10,
      name: 'Hausarzt Empfehlung.pdf',
      source: DocumentSource.careena,
    );

    final duplicate = createDocument(
      id: '2',
      profileId: 10,
      name: 'hausarzt empfehlung.pdf',
      source: DocumentSource.careena,
    );

    expect(await repository.addRecommendationIfMissing(first), isTrue);
    expect(await repository.addRecommendationIfMissing(duplicate), isFalse);
    expect(repository.documents.value, hasLength(1));
  });

  test('allows the same recommendation for different profiles', () async {
    final firstProfileDocument = createDocument(
      id: '1',
      profileId: 10,
      name: 'Hausarzt Empfehlung.pdf',
      source: DocumentSource.careena,
    );

    final secondProfileDocument = createDocument(
      id: '2',
      profileId: 20,
      name: 'Hausarzt Empfehlung.pdf',
      source: DocumentSource.careena,
    );

    expect(
      await repository.addRecommendationIfMissing(firstProfileDocument),
      isTrue,
    );
    expect(
      await repository.addRecommendationIfMissing(secondProfileDocument),
      isTrue,
    );
    expect(repository.documents.value, hasLength(2));
  });

  test('tracks and clears unread count per profile', () async {
    await repository.addRecommendationIfMissing(
      createDocument(
        id: '1',
        profileId: 10,
        source: DocumentSource.careena,
      ),
    );

    expect(repository.unreadCountForProfile(10), 1);
    expect(repository.unreadCountForProfile(20), 0);

    repository.markAllAsSeen(10);

    expect(repository.unreadCountForProfile(10), 0);
  });

  test('loads file data for a metadata-only document', () async {
    final requestedPaths = <String>[];
    final apiService = DocumentApiService(
      ApiClient(
        MockClient((request) async {
          requestedPaths.add(request.url.path);
          return http.Response(
            jsonEncode({
              'id': 1,
              'profile_id': 10,
              'name': 'Befund.pdf',
              'category': 'findings',
              'source': 'uploaded',
              'size_in_bytes': 3,
              'mime_type': 'application/pdf',
              'file_data_base64': 'AQID',
              'created_at': '2026-06-23T10:00:00',
              'updated_at': '2026-06-23T10:00:00',
            }),
            200,
            headers: {'content-type': 'application/json'},
          );
        }),
      ),
    );
    repository.configure(apiService: apiService);
    repository.documents.value = [createDocument(id: '1', profileId: 10)];

    final loaded = await repository.loadDocumentFile(
      repository.documents.value.first,
    );

    expect(requestedPaths.single, contains('/profiles/10/documents/1'));
    expect(loaded.fileBytes, isNotNull);
    expect(repository.documents.value.single.fileBytes, isNotNull);
  });

  test('clear removes cached documents and unread counts', () async {
    await repository.addRecommendationIfMissing(
      createDocument(id: '1', profileId: 10, source: DocumentSource.careena),
    );

    repository.clear();

    expect(repository.documents.value, isEmpty);
    expect(repository.unreadCounts.value, isEmpty);
  });
}