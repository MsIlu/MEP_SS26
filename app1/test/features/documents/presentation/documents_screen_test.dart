import 'package:app1/features/authscreen/domain/models/account.dart';
import 'package:app1/features/authscreen/domain/models/auth_response.dart';
import 'package:app1/features/authscreen/state/auth_session.dart';
import 'package:app1/features/documents/data/document_repository.dart';
import 'package:app1/features/documents/data/models/document_entry.dart';
import 'package:app1/features/documents/presentation/screens/documents_screen.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  late DocumentRepository repository;

  setUp(() {
    repository = DocumentRepository.instance;
    repository.documents.value = [];
    repository.unreadCounts.value = {};
  });

  tearDown(() {
    repository.documents.value = [];
    repository.unreadCounts.value = {};
  });

  AuthSession createSession({int activeProfileId = 10}) {
    final session = AuthSession();

    session.setAuthResponse(
      const AuthResponse(
        accessToken: 'test-token',
        tokenType: 'bearer',
        account: Account(
          id: 1,
          email: 'mutter@example.com',
        ),
        profiles: [
          AuthProfile(
            id: 10,
            displayName: 'Mutter',
            profileType: 'self',
            role: 'owner',
          ),
          AuthProfile(
            id: 20,
            displayName: 'Kind',
            profileType: 'child',
            role: 'guardian',
          ),
        ],
      ),
    );

    session.setActiveProfileById(activeProfileId);
    return session;
  }

  DocumentEntry createDocument({
    required String id,
    required int profileId,
    required String name,
  }) {
    return DocumentEntry(
      id: id,
      profileId: profileId,
      name: name,
      category: DocumentCategory.findings,
      createdAt: DateTime(2026, 6, 23),
      sizeInBytes: 1000,
      source: DocumentSource.uploaded,
    );
  }

  Future<void> pumpDocumentsScreen(
    WidgetTester tester,
    AuthSession session,
  ) async {
    await tester.binding.setSurfaceSize(const Size(430, 900));

    addTearDown(() {
      tester.binding.setSurfaceSize(null);
      session.dispose();
    });

    await tester.pumpWidget(
      MaterialApp(
        home: DocumentsScreen(authSession: session),
      ),
    );

    await tester.pumpAndSettle();
  }

  testWidgets('shows empty state without documents', (tester) async {
    final session = createSession();

    await pumpDocumentsScreen(tester, session);

    expect(find.text('Noch keine Dokumente'), findsOneWidget);
    expect(find.text('Deine Dokumente'), findsOneWidget);
  });

  testWidgets('main profile sees profile filter', (tester) async {
    final session = createSession(activeProfileId: 10);

    await pumpDocumentsScreen(tester, session);

    expect(find.text('Alle Profile'), findsOneWidget);
    expect(find.text('Mutter'), findsOneWidget);
    expect(find.text('Kind'), findsOneWidget);
  });

  testWidgets('managed profile does not see profile filter', (tester) async {
    final session = createSession(activeProfileId: 20);

    await pumpDocumentsScreen(tester, session);

    expect(find.text('Alle Profile'), findsNothing);
    expect(find.text('Mutter'), findsNothing);
    expect(find.text('Kind'), findsNothing);
  });

  testWidgets('all profiles shows documents from mother and child', (
    tester,
  ) async {
    repository.addDocument(
      createDocument(
        id: '1',
        profileId: 10,
        name: 'Mutter Befund.pdf',
      ),
    );

    repository.addDocument(
      createDocument(
        id: '2',
        profileId: 20,
        name: 'Kind Befund.pdf',
      ),
    );

    final session = createSession(activeProfileId: 10);

    await pumpDocumentsScreen(tester, session);

    expect(find.text('Mutter Befund.pdf'), findsOneWidget);
    expect(find.text('Kind Befund.pdf'), findsNothing);

    await tester.tap(find.text('Alle Profile'));
    await tester.pumpAndSettle();

    expect(find.text('Mutter Befund.pdf'), findsOneWidget);
    expect(find.text('Kind Befund.pdf'), findsOneWidget);
  });

  testWidgets('opens document upload dialog', (tester) async {
    final session = createSession();

    await pumpDocumentsScreen(tester, session);

    await tester.tap(find.text('Dokument hinzufügen'));
    await tester.pumpAndSettle();

    expect(find.byType(AlertDialog), findsOneWidget);
    expect(find.text('Datei'), findsOneWidget);
    expect(find.text('Foto'), findsOneWidget);
    expect(find.text('Kamera'), findsOneWidget);
    expect(find.text('Abbrechen'), findsOneWidget);
  });

  testWidgets('search filters visible documents', (tester) async {
    repository.addDocument(
      createDocument(
        id: '1',
        profileId: 10,
        name: 'Blutwerte.pdf',
      ),
    );

    repository.addDocument(
      createDocument(
        id: '2',
        profileId: 10,
        name: 'Hausarzt Befund.pdf',
      ),
    );

    final session = createSession();

    await pumpDocumentsScreen(tester, session);

    await tester.enterText(
      find.byWidgetPredicate(
        (widget) =>
            widget is TextField &&
            widget.decoration?.hintText == 'Dokumente durchsuchen',
      ),
      'Blut',
    );

    await tester.pumpAndSettle();

    expect(find.text('Blutwerte.pdf'), findsOneWidget);
    expect(find.text('Hausarzt Befund.pdf'), findsNothing);
  });
}