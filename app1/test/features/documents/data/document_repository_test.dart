import 'package:app1/features/documents/data/document_repository.dart';
import 'package:app1/features/documents/data/models/document_entry.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  late DocumentRepository repository;

  setUp(() {
    repository = DocumentRepository.instance;

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

  test('adds a document', () {
    final document = createDocument(id: '1', profileId: 10);

    repository.addDocument(document);

    expect(repository.documents.value, hasLength(1));
    expect(repository.documents.value.first, same(document));
  });

  test('deletes a document by id', () {
    repository.addDocument(
      createDocument(id: '1', profileId: 10),
    );

    repository.deleteDocument('1');

    expect(repository.documents.value, isEmpty);
  });

  test('prevents duplicate recommendation for the same profile', () {
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

    expect(repository.addRecommendationIfMissing(first), isTrue);
    expect(repository.addRecommendationIfMissing(duplicate), isFalse);
    expect(repository.documents.value, hasLength(1));
  });

  test('allows the same recommendation for different profiles', () {
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
      repository.addRecommendationIfMissing(firstProfileDocument),
      isTrue,
    );
    expect(
      repository.addRecommendationIfMissing(secondProfileDocument),
      isTrue,
    );
    expect(repository.documents.value, hasLength(2));
  });

  test('tracks and clears unread count per profile', () {
    repository.addRecommendationIfMissing(
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
}