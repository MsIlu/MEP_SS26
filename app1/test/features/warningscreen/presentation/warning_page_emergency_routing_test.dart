import 'package:app1/core/themes/theme_controller.dart';
import 'package:app1/features/chatscreen/data/models/chat_response_model.dart';
import 'package:app1/features/warningscreen/presentation/screens/warning_page.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

/// Tests for the three confirmed bugs in PR #156.
///
/// Bug 1 (Notfallanzeige): care_level '112' and 'emergency_department' must
///   trigger EmergencyCard even when urgency != 'emergency'.
/// Bug 2 (Symptom-Button-Isolation): The symptom-to-diary button must only
///   appear when response.profileId != null so a non-profile-bound chat cannot
///   silently write symptoms to whatever profile happens to be active.
void main() {
  // ───────────────────────────────────────────────────────────────────────────
  // Bug 1 – Notfallanzeige
  // ───────────────────────────────────────────────────────────────────────────

  group('WarningPage – Notfallansicht', () {
    testWidgets(
      'care_level=112 zeigt EmergencyCard auch wenn urgency nicht emergency ist',
      (tester) async {
        // Represents a backend response where the LLM picked care_level='112'
        // but set urgency='today' instead of 'emergency'.
        // Before the fix _showEmergencyActions only checked urgency, so the
        // EmergencyCard was never shown for this combination.
        const response = ChatResponse(
          text: 'Notruf 112 kontaktieren.',
          redFlag: false,
          recommendationResult: RecommendationResult(
            allowed: true,
            urgency: 'today',
            urgencyLevel: 'high',
            careLevel: '112',
            specialty: 'emergency_medicine',
          ),
        );

        await tester.pumpWidget(
          const MaterialApp(home: WarningPage(response: response)),
        );

        expect(find.text('Achtung: Möglicher Notfall'), findsOneWidget);
      },
    );

    testWidgets(
      'care_level=emergency_department zeigt EmergencyCard auch ohne urgency=emergency',
      (tester) async {
        const response = ChatResponse(
          text: 'Bitte suche die Notaufnahme auf.',
          redFlag: false,
          recommendationResult: RecommendationResult(
            allowed: true,
            urgency: 'soon',
            urgencyLevel: 'high',
            careLevel: 'emergency_department',
            specialty: 'emergency_medicine',
          ),
        );

        await tester.pumpWidget(
          const MaterialApp(home: WarningPage(response: response)),
        );

        expect(find.text('Achtung: Möglicher Notfall'), findsOneWidget);
      },
    );

    testWidgets(
      'urgency=emergency zeigt EmergencyCard auch wenn care_level nicht 112 ist',
      (tester) async {
        // Backend may rarely set urgency='emergency' with a lower care_level —
        // urgency stays sufficient alone for the emergency view.
        const response = ChatResponse(
          text: 'Dringend handeln.',
          redFlag: false,
          recommendationResult: RecommendationResult(
            allowed: true,
            urgency: 'emergency',
            urgencyLevel: 'emergency',
            careLevel: 'general_practice',
            specialty: 'general_practice',
          ),
        );

        await tester.pumpWidget(
          const MaterialApp(home: WarningPage(response: response)),
        );

        expect(find.text('Achtung: Möglicher Notfall'), findsOneWidget);
      },
    );

    testWidgets(
      'routine-Empfehlung zeigt KEINE EmergencyCard',
      (tester) async {
        const response = ChatResponse(
          text: 'Keine akute Gefahr erkannt.',
          redFlag: false,
          recommendationResult: RecommendationResult(
            allowed: true,
            urgency: 'routine',
            urgencyLevel: 'low',
            careLevel: 'general_practice',
            specialty: 'general_practice',
          ),
        );

        await tester.pumpWidget(
          const MaterialApp(home: WarningPage(response: response)),
        );

        expect(find.text('Achtung: Möglicher Notfall'), findsNothing);
        expect(find.text('Hausärztliche Abklärung'), findsOneWidget);
      },
    );

    testWidgets(
      'redFlag=true zeigt EmergencyCard unabhängig von care_level und urgency',
      (tester) async {
        const response = ChatResponse(
          text: 'Notruf.',
          redFlag: true,
          ruleName: 'Starke Blutung',
          recommendationResult: RecommendationResult(
            allowed: false,
            urgency: 'unknown',
            urgencyLevel: 'unclear',
            careLevel: 'unknown',
            specialty: 'unknown',
          ),
        );

        await tester.pumpWidget(
          const MaterialApp(home: WarningPage(response: response)),
        );

        expect(find.text('Achtung: Möglicher Notfall'), findsOneWidget);
      },
    );
  });

  // ───────────────────────────────────────────────────────────────────────────
  // Bug 2 – Symptom-Button-Profil-Isolation
  // ───────────────────────────────────────────────────────────────────────────

  group('WarningPage – Symptom-Button Profil-Isolation', () {
    late ThemeController themeController;

    setUp(() {
      themeController = ThemeController();
    });

    tearDown(() {
      themeController.dispose();
    });

    testWidgets(
      'Symptom-Button ist NICHT sichtbar wenn profileId null ist',
      (tester) async {
        // Non-profile-bound session: profileId = null.
        // Before the fix the button appeared and would save to whatever active
        // profile was set in the app — wrong person's diary.
        const response = ChatResponse(
          text: 'Kein Profil gebunden.',
          redFlag: false,
          recommendationResult: RecommendationResult(
            allowed: true,
            urgency: 'routine',
            urgencyLevel: 'low',
            careLevel: 'self_care',
            specialty: 'general_practice',
          ),
          // profileId deliberately omitted (null)
        );

        await tester.pumpWidget(
          MaterialApp(
            home: WarningPage(
              response: response,
              symptoms: const ['Kopfschmerzen'],
              themeController: themeController,
            ),
          ),
        );

        expect(find.text('Symptome speichern'), findsNothing);
      },
    );

    testWidgets(
      'Symptom-Button erscheint wenn profileId gesetzt ist und Symptome vorhanden',
      (tester) async {
        const response = ChatResponse(
          text: 'Empfehlung für Profil 42.',
          redFlag: false,
          recommendationResult: RecommendationResult(
            allowed: true,
            urgency: 'routine',
            urgencyLevel: 'low',
            careLevel: 'self_care',
            specialty: 'general_practice',
          ),
          profileId: 42,
        );

        await tester.pumpWidget(
          MaterialApp(
            home: WarningPage(
              response: response,
              symptoms: const ['Kopfschmerzen'],
              themeController: themeController,
            ),
          ),
        );

        expect(find.text('Symptome speichern'), findsOneWidget);
      },
    );

    testWidgets(
      'Symptom-Button fehlt wenn themeController null ist auch bei gesetztem profileId',
      (tester) async {
        // themeController=null means we are not in the symptom-diary context
        // (e.g. opened from chat history), so the button must stay hidden
        // regardless of profileId.
        const response = ChatResponse(
          text: 'Test.',
          redFlag: false,
          profileId: 42,
        );

        await tester.pumpWidget(
          const MaterialApp(
            home: WarningPage(
              response: response,
              symptoms: ['Kopfschmerzen'],
              // themeController deliberately null
            ),
          ),
        );

        expect(find.text('Symptome speichern'), findsNothing);
      },
    );
  });
}
