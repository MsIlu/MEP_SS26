import 'package:app1/features/documents/data/document_repository.dart';
import 'package:app1/features/documents/data/models/document_entry.dart';
import 'package:app1/features/recommendation_export/presentation/save_recommendation_to_documents_button.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

/// Tests for the profile-isolation bug in SaveRecommendationToDocumentsButton.
///
/// Before the fix the button used AppDependenciesScope.authSession.activeProfileId
/// to check whether the document is already saved. This caused it to show
/// "Gespeichert" for a different person's document when profiles were switched.
/// After the fix it exclusively uses widget.profileId.
void main() {
  Widget wrap(Widget child) => MaterialApp(home: Scaffold(body: child));

  setUp(() {
    DocumentRepository.instance.documents.value = [];
  });

  tearDown(() {
    DocumentRepository.instance.documents.value = [];
  });

  testWidgets(
    'Dokument existiert in Repository für profileId=42 — Button zeigt Gespeichert',
    (tester) async {
      DocumentRepository.instance.addRecommendationIfMissing(
        DocumentEntry(
          id: '1',
          profileId: 42,
          name: 'handlungsempfehlung.pdf',
          category: DocumentCategory.recommendations,
          createdAt: DateTime(2026, 7, 1),
          sizeInBytes: 100,
          source: DocumentSource.careena,
          fileBytes: null,
          mimeType: 'application/pdf',
        ),
      );

      await tester.pumpWidget(
        wrap(
          SaveRecommendationToDocumentsButton(
            title: 'Handlungsempfehlung',
            patientSummary: '',
            recommendation: '',
            nextSteps: '',
            symptoms: const [],
            userMessages: const [],
            profileId: 42,
          ),
        ),
      );

      expect(find.text('Gespeichert'), findsOneWidget);
      expect(find.text('Dokument speichern'), findsNothing);
    },
  );

  testWidgets(
    'Dokument existiert für profileId=42 — Button mit profileId=99 zeigt Dokument speichern',
    (tester) async {
      // Core regression test: the document belongs to profile 42, but the
      // button is shown for a session with profile 99. Before the fix the
      // button would have reported "Gespeichert" because it used the active
      // session profile instead of widget.profileId.
      DocumentRepository.instance.addRecommendationIfMissing(
        DocumentEntry(
          id: '1',
          profileId: 42,
          name: 'handlungsempfehlung.pdf',
          category: DocumentCategory.recommendations,
          createdAt: DateTime(2026, 7, 1),
          sizeInBytes: 100,
          source: DocumentSource.careena,
          fileBytes: null,
          mimeType: 'application/pdf',
        ),
      );

      await tester.pumpWidget(
        wrap(
          SaveRecommendationToDocumentsButton(
            title: 'Handlungsempfehlung',
            patientSummary: '',
            recommendation: '',
            nextSteps: '',
            symptoms: const [],
            userMessages: const [],
            profileId: 99,
          ),
        ),
      );

      expect(find.text('Dokument speichern'), findsOneWidget);
      expect(find.text('Gespeichert'), findsNothing);
    },
  );

  testWidgets(
    'Nicht-profilgebundene Session (profileId=null) zeigt Dokument speichern wenn kein profilloses Dokument existiert',
    (tester) async {
      await tester.pumpWidget(
        wrap(
          const SaveRecommendationToDocumentsButton(
            title: 'Handlungsempfehlung',
            patientSummary: '',
            recommendation: '',
            nextSteps: '',
            symptoms: [],
            userMessages: [],
          ),
        ),
      );

      expect(find.text('Dokument speichern'), findsOneWidget);
    },
  );

  testWidgets(
    'Nicht-profilgebundene Session zeigt Gespeichert wenn profilloses Dokument vorhanden',
    (tester) async {
      DocumentRepository.instance.addRecommendationIfMissing(
        DocumentEntry(
          id: '2',
          profileId: null,
          name: 'handlungsempfehlung.pdf',
          category: DocumentCategory.recommendations,
          createdAt: DateTime(2026, 7, 1),
          sizeInBytes: 100,
          source: DocumentSource.careena,
          fileBytes: null,
          mimeType: 'application/pdf',
        ),
      );

      await tester.pumpWidget(
        wrap(
          const SaveRecommendationToDocumentsButton(
            title: 'Handlungsempfehlung',
            patientSummary: '',
            recommendation: '',
            nextSteps: '',
            symptoms: [],
            userMessages: [],
          ),
        ),
      );

      expect(find.text('Gespeichert'), findsOneWidget);
    },
  );
}
