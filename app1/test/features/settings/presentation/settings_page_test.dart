import 'package:app1/core/themes/theme_controller.dart';
import 'package:app1/features/authscreen/domain/models/account.dart';
import 'package:app1/features/authscreen/domain/models/auth_response.dart';
import 'package:app1/features/authscreen/state/auth_session.dart';
import 'package:app1/features/settings/presentation/screens/settings_page.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  setUp(() {
    SharedPreferences.setMockInitialValues({});
  });

  testWidgets('shows display, legal, and logout settings', (tester) async {
    final themeController = ThemeController();
    addTearDown(themeController.dispose);

    await tester.pumpWidget(
      MaterialApp(home: SettingsPage(themeController: themeController)),
    );
    await tester.pumpAndSettle();

    expect(find.text('Einfache Ansicht'), findsOneWidget);
    expect(find.text('Datenschutz'), findsOneWidget);
    expect(find.text('Impressum'), findsOneWidget);
    expect(find.text('Abmelden'), findsOneWidget);
  });

  testWidgets('simple view switch updates the theme controller', (
    tester,
  ) async {
    await tester.binding.setSurfaceSize(const Size(320, 700));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    final themeController = ThemeController();
    addTearDown(themeController.dispose);

    await tester.pumpWidget(
      MaterialApp(home: SettingsPage(themeController: themeController)),
    );
    await tester.pumpAndSettle();

    await tester.ensureVisible(find.text('Einfache Ansicht'));
    await tester.tap(find.text('Einfache Ansicht'));
    await tester.pumpAndSettle();

    expect(themeController.isSimpleView, isTrue);
    expect(find.text('Eingeschaltet'), findsOneWidget);
    expect(find.text('Automatisch'), findsOneWidget);
  });

  testWidgets('switches between own and managed profiles', (tester) async {
    final themeController = ThemeController();
    final authSession = _createProfileSession();
    addTearDown(themeController.dispose);
    addTearDown(authSession.dispose);

    await tester.pumpWidget(
      MaterialApp(
        home: SettingsPage(
          themeController: themeController,
          authSession: authSession,
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Anna'), findsOneWidget);
    expect(find.text('Ben'), findsOneWidget);
    expect(authSession.activeProfile?.displayName, 'Anna');

    await tester.ensureVisible(find.text('Ben'));
    await tester.tap(find.text('Ben'));
    await tester.pump();

    expect(authSession.activeProfile?.displayName, 'Ben');
  });

  testWidgets('opens the managed profile frontend draft', (tester) async {
    final themeController = ThemeController();
    addTearDown(themeController.dispose);

    await tester.pumpWidget(
      MaterialApp(home: SettingsPage(themeController: themeController)),
    );
    await tester.pumpAndSettle();

    await tester.ensureVisible(find.text('Betreutes Profil hinzufügen'));
    await tester.tap(find.text('Betreutes Profil hinzufügen'));
    await tester.pumpAndSettle();

    expect(find.text('Name der betreuten Person'), findsOneWidget);
    expect(find.textContaining('Frontend-Vorschau'), findsOneWidget);
    expect(find.text('Entwurf übernehmen'), findsOneWidget);
  });

  testWidgets('opens personal and health data settings pages', (tester) async {
    final themeController = ThemeController();
    final authSession = _createProfileSession();
    addTearDown(themeController.dispose);
    addTearDown(authSession.dispose);

    await tester.pumpWidget(
      MaterialApp(
        home: SettingsPage(
          themeController: themeController,
          authSession: authSession,
        ),
      ),
    );
    await tester.pumpAndSettle();

    await tester.ensureVisible(find.text('Persönliche Daten'));
    await tester.tap(find.text('Persönliche Daten'));
    await tester.pumpAndSettle();
    expect(find.text('Anzeigename'), findsOneWidget);
    expect(find.text('E-Mail des angemeldeten Kontos'), findsOneWidget);

    await tester.tap(find.byTooltip('Zurück'));
    await tester.pumpAndSettle();
    await tester.ensureVisible(find.text('Gesundheitsangaben'));
    await tester.tap(find.text('Gesundheitsangaben'));
    await tester.pumpAndSettle();
    expect(find.text('Geburtsgeschlecht'), findsOneWidget);
    expect(find.text('Regelmäßige Medikamente'), findsOneWidget);
  });
}

AuthSession _createProfileSession() {
  final session = AuthSession();
  session.setAuthResponse(
    const AuthResponse(
      accessToken: 'token',
      tokenType: 'bearer',
      account: Account(id: 1, email: 'anna@example.com'),
      profiles: [
        AuthProfile(
          id: 10,
          displayName: 'Anna',
          profileType: 'self',
          role: 'owner',
        ),
        AuthProfile(
          id: 11,
          displayName: 'Ben',
          profileType: 'child',
          role: 'guardian',
        ),
      ],
    ),
  );
  return session;
}
