import 'dart:typed_data';

import 'package:app1/features/documents/controllers/document_controller.dart';
import 'package:app1/features/documents/data/document_repository.dart';
import 'package:app1/features/documents/data/models/document_entry.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  late DocumentRepository repository;
  late DocumentController controller;

  setUp(() {
    repository = DocumentRepository.instance;
    repository.configure(apiService: null);
    repository.documents.value = [];
    repository.unreadCounts.value = {};

    controller = DocumentController(
      repository: repository,
      profileId: 10,
    );
  });

  tearDown(() {
    controller.dispose();
    repository.documents.value = [];
    repository.unreadCounts.value = {};
  });

  DocumentEntry createDocument({
    required String id,
    required int profileId,
    required String name,
    DocumentCategory category = DocumentCategory.findings,
  }) {
    return DocumentEntry(
      id: id,
      profileId: profileId,
      name: name,
      category: category,
      createdAt: DateTime(2026, 6, 23),
      sizeInBytes: 1000,
      source: DocumentSource.uploaded,
    );
  }

  test('shows only documents of the active profile by default', () async {
    await repository.addDocument(
      createDocument(
        id: '1',
        profileId: 10,
        name: 'Mutter Befund.pdf',
      ),
    );
    await repository.addDocument(
      createDocument(
        id: '2',
        profileId: 20,
        name: 'Kind Befund.pdf',
      ),
    );

    expect(controller.documents, hasLength(1));
    expect(controller.documents.first.name, 'Mutter Befund.pdf');
  });

  test('shows documents from all profiles', () async {
    await repository.addDocument(
      createDocument(
        id: '1',
        profileId: 10,
        name: 'Mutter Befund.pdf',
      ),
    );
    await repository.addDocument(
      createDocument(
        id: '2',
        profileId: 20,
        name: 'Kind Befund.pdf',
      ),
    );

    controller.showAllProfiles();

    expect(controller.documents, hasLength(2));
    expect(controller.isShowingAllProfiles, isTrue);
  });

  test('filters documents by selected profile', () async {
    await repository.addDocument(
      createDocument(
        id: '1',
        profileId: 10,
        name: 'Mutter Befund.pdf',
      ),
    );
    await repository.addDocument(
      createDocument(
        id: '2',
        profileId: 20,
        name: 'Kind Befund.pdf',
      ),
    );

    controller.showAllProfiles();
    await controller.selectProfile(20);

    expect(controller.documents, hasLength(1));
    expect(controller.documents.first.name, 'Kind Befund.pdf');
    expect(controller.selectedProfileId, 20);
    expect(controller.isShowingAllProfiles, isFalse);
  });

  test('filters visible documents by search query and category', () async {
    await repository.addDocument(
      createDocument(
        id: '1',
        profileId: 10,
        name: 'Blutwerte.pdf',
        category: DocumentCategory.laboratory,
      ),
    );
    await repository.addDocument(
      createDocument(
        id: '2',
        profileId: 10,
        name: 'Hausarzt Befund.pdf',
      ),
    );

    controller.updateSearch('Blut');
    controller.selectCategory(DocumentCategory.laboratory);

    expect(controller.visibleDocuments, hasLength(1));
    expect(controller.visibleDocuments.first.name, 'Blutwerte.pdf');
  });

  test('assigns uploaded document to the active profile', () async {
    await controller.addDocument(
      name: 'Neuer Befund.pdf',
      category: DocumentCategory.findings,
      fileBytes: Uint8List.fromList([1, 2, 3]),
      mimeType: 'application/pdf',
    );

    expect(repository.documents.value, hasLength(1));

    final document = repository.documents.value.first;

    expect(document.profileId, 10);
    expect(document.name, 'Neuer Befund.pdf');
    expect(document.fileBytes, Uint8List.fromList([1, 2, 3]));
    expect(document.mimeType, 'application/pdf');
  });
}