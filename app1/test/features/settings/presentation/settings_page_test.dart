import 'package:app1/core/themes/app_colors.dart';
import 'package:app1/core/themes/theme_controller.dart';
import 'package:app1/features/authscreen/domain/models/account.dart';
import 'package:app1/features/authscreen/domain/models/auth_response.dart';
import 'package:app1/features/authscreen/state/auth_session.dart';
import 'package:app1/features/settings/presentation/settings_icons.dart';
import 'package:app1/features/settings/presentation/screens/settings_page.dart';
import 'package:app1/features/settings/presentation/widgets/settings_components.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
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
    expect(find.text('Ben'), findsOneWidget);

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

    await tester.tap(find.text('Profile und persönliche Daten'));
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

    await tester.tap(find.text('Profile und persönliche Daten'));
    await tester.pumpAndSettle();
    await tester.ensureVisible(find.text('Persönliche Daten'));
    await tester.tap(find.text('Persönliche Daten'));
    await tester.pumpAndSettle();
    expect(find.text('Anzeigename'), findsOneWidget);
    expect(find.text('E-Mail des angemeldeten Kontos'), findsOneWidget);
    final saveButton = tester.widget<FilledButton>(
      find.descendant(
        of: find.byKey(const ValueKey('settings-save-button')),
        matching: find.byType(FilledButton),
      ),
    );
    expect(
      saveButton.style?.backgroundColor?.resolve(<WidgetState>{}),
      AppColors.toolbarButtonBackground,
    );

    await tester.tap(find.byTooltip('Zurück'));
    await tester.pumpAndSettle();
    await tester.ensureVisible(find.text('Gesundheitsangaben'));
    await tester.tap(find.text('Gesundheitsangaben'));
    await tester.pumpAndSettle();
    expect(find.text('Geburtsgeschlecht'), findsOneWidget);
    expect(find.text('Regelmäßige Medikamente'), findsOneWidget);
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
