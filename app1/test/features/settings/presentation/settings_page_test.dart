import 'dart:convert';

import 'package:app1/core/network/api_client.dart';
import 'package:app1/core/themes/app_colors.dart';
import 'package:app1/core/themes/theme_controller.dart';
import 'package:app1/features/authscreen/domain/models/account.dart';
import 'package:app1/features/authscreen/domain/models/auth_response.dart';
import 'package:app1/features/authscreen/state/auth_session.dart';
import 'package:app1/features/profiles/data/profile_api_service.dart';
import 'package:app1/features/settings/presentation/settings_icons.dart';
import 'package:app1/features/settings/presentation/screens/settings_page.dart';
import 'package:app1/features/settings/presentation/widgets/settings_components.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  // Test case references: documents/Testfaelle_Frontend.md#t10-settings
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
    expect(find.text('Einstellung suchen...'), findsOneWidget);
    expect(find.text('Datenschutz und Sicherheit'), findsOneWidget);
    expect(find.text('Über Careena'), findsOneWidget);
    expect(find.text('Vom Konto abmelden'), findsOneWidget);
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
    expect(
      find.text('Große Elemente und reduzierte Navigation'),
      findsOneWidget,
    );
  });

  testWidgets('display settings starts directly with appearance choices', (
    tester,
  ) async {
    final themeController = ThemeController();
    addTearDown(themeController.dispose);

    await tester.pumpWidget(
      MaterialApp(home: SettingsPage(themeController: themeController)),
    );
    await tester.pumpAndSettle();

    await tester.tap(find.text('Darstellung'));
    await tester.pumpAndSettle();

    expect(find.text('Darstellung'), findsOneWidget);
    expect(
      find.text('Wähle die Ansicht, die du gut erkennen kannst.'),
      findsNothing,
    );
    expect(find.text('Aussehen'), findsOneWidget);
  });

  testWidgets('shows language settings as Careena-styled UI only', (
    tester,
  ) async {
    final themeController = ThemeController();
    addTearDown(themeController.dispose);

    await tester.pumpWidget(
      MaterialApp(home: SettingsPage(themeController: themeController)),
    );
    await tester.pumpAndSettle();

    expect(find.text('Sprache ändern'), findsOneWidget);
    expect(find.text('Deutsch ist aktuell ausgewählt'), findsOneWidget);

    await tester.tap(find.text('Sprache ändern'));
    await tester.pumpAndSettle();

    expect(find.text('Wähle die Sprache für Careena.'), findsOneWidget);
    expect(find.text('Deutsch'), findsOneWidget);
    expect(find.text('Aktuelle App-Sprache'), findsOneWidget);
    expect(find.text('English'), findsOneWidget);
    expect(find.text('Türkçe'), findsOneWidget);
    expect(find.text('Demnächst verfügbar'), findsNWidgets(2));
  });

  testWidgets('reuses settings icons on matching detail pages', (tester) async {
    final themeController = ThemeController();
    addTearDown(themeController.dispose);

    await tester.pumpWidget(
      MaterialApp(home: SettingsPage(themeController: themeController)),
    );
    await tester.pumpAndSettle();

    expect(find.byIcon(SettingsIcons.privacy), findsOneWidget);
    await tester.tap(find.text('Datenschutz und Sicherheit'));
    await tester.pumpAndSettle();
    expect(find.byIcon(SettingsIcons.privacy), findsOneWidget);

    await tester.tap(find.byTooltip('Zurück'));
    await tester.pumpAndSettle();
    expect(find.byIcon(SettingsIcons.help), findsOneWidget);
    await tester.ensureVisible(find.text('Hilfe und Support'));
    await tester.tap(find.text('Hilfe und Support'));
    await tester.pumpAndSettle();
    expect(find.byIcon(SettingsIcons.help), findsOneWidget);
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

    expect(find.text('Aktives Profil: Anna'), findsOneWidget);
    expect(authSession.activeProfile?.displayName, 'Anna');

    await tester.tap(find.text('Profile und persönliche Daten'));
    await tester.pumpAndSettle();
    expect(find.text('Profile'), findsOneWidget);
    expect(find.text('Profile verwalten'), findsOneWidget);
    expect(
      find.text('Verwalte Profile und persönliche Angaben.'),
      findsNothing,
    );
    expect(find.text('Anna'), findsOneWidget);
    expect(find.text('Wechseln'), findsOneWidget);
    expect(find.text('Profildaten bearbeiten'), findsOneWidget);
    expect(find.text('Ben'), findsNothing);

    await tester.tap(find.text('Wechseln'));
    await tester.pumpAndSettle();
    expect(find.text('Aktives Profil wechseln'), findsOneWidget);
    await tester.tap(find.text('Ben'));
    await tester.pumpAndSettle();

    expect(authSession.activeProfile?.displayName, 'Ben');
  });

  testWidgets('creates a managed profile through the profile api', (
    tester,
  ) async {
    final themeController = ThemeController();
    final authSession = _createProfileSession();
    Map<String, dynamic>? requestBody;
    addTearDown(themeController.dispose);
    addTearDown(authSession.dispose);

    final apiClient = ApiClient(
      MockClient((request) async {
        expect(request.method, 'POST');
        expect(request.url.path, contains('/profiles'));
        requestBody = jsonDecode(request.body) as Map<String, dynamic>;

        return http.Response(
          jsonEncode({
            'id': 12,
            'display_name': requestBody!['display_name'],
            'date_of_birth': null,
            'biological_sex': null,
            'profile_type': requestBody!['profile_type'],
            'relevant_preconditions_summary': null,
            'relevant_medications_summary': null,
            'symptom_diary_summary': null,
            'ai_disclaimer_accepted_at': null,
            'role': 'guardian',
          }),
          200,
          headers: {'content-type': 'application/json'},
        );
      }),
    );
    apiClient.setAccessToken('token');

    await tester.pumpWidget(
      MaterialApp(
        home: SettingsPage(
          themeController: themeController,
          authSession: authSession,
          profileApiService: ProfileApiService(apiClient),
        ),
      ),
    );
    await tester.pumpAndSettle();

    await tester.tap(find.text('Profile und persönliche Daten'));
    await tester.pumpAndSettle();
    await tester.ensureVisible(find.text('Betreutes Profil hinzufügen'));
    await tester.tap(find.text('Betreutes Profil hinzufügen'));
    await tester.pumpAndSettle();

    expect(find.text('Name der betreuten Person'), findsOneWidget);
    expect(find.text('Profil speichern'), findsOneWidget);

    await tester.enterText(
      find.widgetWithText(TextField, 'Name der betreuten Person'),
      'Mia',
    );
    await tester.pump();
    await tester.tap(find.text('Profil speichern'));
    await tester.pumpAndSettle();

    expect(requestBody?['display_name'], 'Mia');
    expect(requestBody?['profile_type'], 'child');
    expect(authSession.activeProfile?.displayName, 'Mia');
    expect(authSession.profiles.map((profile) => profile.id), contains(12));
    expect(find.text('Profil "Mia" wurde erstellt.'), findsOneWidget);
  });

  testWidgets('opens personal and health data settings pages', (tester) async {
    final themeController = ThemeController();
    final authSession = _createProfileSession();
    final patchBodies = <Map<String, dynamic>>[];
    addTearDown(themeController.dispose);
    addTearDown(authSession.dispose);
    final apiClient = ApiClient(
      MockClient((request) async {
        expect(request.url.path, contains('/profiles/10'));

        final body = request.method == 'PATCH'
            ? jsonDecode(request.body) as Map<String, dynamic>
            : <String, dynamic>{};

        if (request.method == 'PATCH') {
          patchBodies.add(body);
        } else {
          expect(request.method, 'GET');
        }

        return http.Response(
          jsonEncode({
            'id': 10,
            'display_name': body['display_name'] ?? 'Anna',
            'date_of_birth': body['date_of_birth'] ?? '2000-04-12',
            'biological_sex': body['biological_sex'] ?? 'female',
            'height_cm': body['height_cm'] ?? 170,
            'weight_kg': body['weight_kg'] ?? 70.5,
            'profile_type': 'self',
            'relevant_preconditions_summary':
                body['relevant_preconditions_summary'],
            'relevant_medications_summary':
                body['relevant_medications_summary'],
            'symptom_diary_summary': body['symptom_diary_summary'],
            'ai_disclaimer_accepted_at': null,
            'role': 'owner',
          }),
          200,
          headers: {'content-type': 'application/json'},
        );
      }),
    );
    apiClient.setAccessToken('token');

    await tester.pumpWidget(
      MaterialApp(
        home: SettingsPage(
          themeController: themeController,
          authSession: authSession,
          profileApiService: ProfileApiService(apiClient),
        ),
      ),
    );
    await tester.pumpAndSettle();

    await tester.tap(find.text('Profile und persönliche Daten'));
    await tester.pumpAndSettle();
    await tester.ensureVisible(find.text('Profildaten bearbeiten'));
    await tester.tap(find.text('Profildaten bearbeiten'));
    await tester.pumpAndSettle();
    expect(find.text('1. Persönliche Angaben'), findsOneWidget);
    expect(find.text('2. Gesundheitsangaben'), findsOneWidget);
    expect(find.text('Anzeigename'), findsOneWidget);
    expect(find.text('E-Mail des angemeldeten Kontos'), findsOneWidget);
    expect(find.text('12'), findsOneWidget);
    expect(find.text('04'), findsOneWidget);
    expect(find.text('2000'), findsOneWidget);
    await tester.enterText(
      find.widgetWithText(TextField, 'Anzeigename'),
      'Anna Lokal',
    );
    final saveButton = tester.widget<FilledButton>(
      find.descendant(
        of: find.byKey(const ValueKey('personal-data-save-button')),
        matching: find.byType(FilledButton),
      ),
    );
    expect(
      saveButton.style?.backgroundColor?.resolve(<WidgetState>{}),
      AppColors.toolbarButtonBackground,
    );
    await tester.ensureVisible(
      find.byKey(const ValueKey('personal-data-save-button')),
    );
    await tester.tap(find.byKey(const ValueKey('personal-data-save-button')));
    await tester.pumpAndSettle();
    expect(authSession.activeProfile?.displayName, 'Anna Lokal');
    expect(patchBodies.first['display_name'], 'Anna Lokal');
    expect(patchBodies.first['date_of_birth'], '2000-04-12');

    await tester.ensureVisible(find.text('Geburtsgeschlecht'));
    expect(find.text('Geburtsgeschlecht'), findsOneWidget);
    expect(find.text('Regelmäßige Medikamente'), findsOneWidget);
    expect(find.text('Symptomtagebuch-Zusammenfassung'), findsNothing);
    expect(find.widgetWithText(TextField, 'Größe'), findsOneWidget);
    expect(find.widgetWithText(TextField, 'Gewicht'), findsOneWidget);

    await tester.enterText(find.widgetWithText(TextField, 'Größe'), '172');
    await tester.enterText(find.widgetWithText(TextField, 'Gewicht'), '71,5');
    await tester.enterText(
      find.widgetWithText(TextField, 'Regelmäßige Medikamente'),
      'Ibuprofen bei Bedarf',
    );
    await tester.ensureVisible(
      find.byKey(const ValueKey('health-data-save-button')),
    );
    await tester.tap(find.byKey(const ValueKey('health-data-save-button')));
    await tester.pumpAndSettle();

    expect(patchBodies.last['biological_sex'], 'female');
    expect(patchBodies.last['height_cm'], 172);
    expect(patchBodies.last['weight_kg'], 71.5);
    expect(
      patchBodies.last['relevant_medications_summary'],
      'Ibuprofen bei Bedarf',
    );
    expect(patchBodies.last.containsKey('symptom_diary_summary'), isFalse);
  });

  testWidgets('filters settings while keeping logout visible', (tester) async {
    final themeController = ThemeController();
    addTearDown(themeController.dispose);

    await tester.pumpWidget(
      MaterialApp(home: SettingsPage(themeController: themeController)),
    );
    await tester.pumpAndSettle();

    await tester.enterText(
      find.widgetWithText(TextField, 'Einstellung suchen...'),
      'datenschutz',
    );
    await tester.pump();

    expect(find.text('Datenschutz und Sicherheit'), findsOneWidget);
    expect(find.text('Hilfe und Support'), findsNothing);
    expect(
      find.byKey(const ValueKey('settings-logout-button')),
      findsOneWidget,
    );
  });

  testWidgets('logout clears the session and returns to the first route', (
    tester,
  ) async {
    final themeController = ThemeController();
    final authSession = _createProfileSession();
    addTearDown(themeController.dispose);
    addTearDown(authSession.dispose);

    await tester.pumpWidget(
      MaterialApp(
        home: Builder(
          builder: (context) {
            return Scaffold(
              body: Center(
                child: FilledButton(
                  onPressed: () {
                    Navigator.of(context).push(
                      MaterialPageRoute(
                        builder: (context) => SettingsPage(
                          themeController: themeController,
                          authSession: authSession,
                        ),
                      ),
                    );
                  },
                  child: const Text('Onboarding mock'),
                ),
              ),
            );
          },
        ),
      ),
    );

    await tester.tap(find.text('Onboarding mock'));
    await tester.pumpAndSettle();
    expect(find.text('Einstellungen'), findsWidgets);
    expect(authSession.isAuthenticated, isTrue);

    await tester.ensureVisible(find.byKey(const ValueKey('settings-logout-button')));
    await tester.tap(find.byKey(const ValueKey('settings-logout-button')));
    await tester.pumpAndSettle();

    expect(authSession.isAuthenticated, isFalse);
    expect(authSession.activeProfile, isNull);
    expect(find.text('Onboarding mock'), findsOneWidget);
    expect(find.text('Einstellungen'), findsNothing);
  });

  testWidgets('centers logout and highlights light settings panels', (
    tester,
  ) async {
    final themeController = ThemeController()..setThemeMode(ThemeMode.light);
    addTearDown(themeController.dispose);

    await tester.pumpWidget(
      MaterialApp(
        theme: ThemeData.light(),
        home: SettingsPage(themeController: themeController),
      ),
    );
    await tester.pumpAndSettle();

    final logout = find.byKey(const ValueKey('settings-logout-button'));
    final panelMaterial = find.descendant(
      of: find.byType(SettingsPanel).first,
      matching: find.byType(Material),
    );
    final material = tester.widget<Material>(panelMaterial.first);

    expect(tester.getCenter(logout).dx, closeTo(400, 0.1));
    expect(material.color, AppColors.careenaNoteBackground);
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
