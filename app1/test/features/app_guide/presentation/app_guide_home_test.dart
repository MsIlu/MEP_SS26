import 'package:app1/features/app_guide/data/app_guide_store.dart';
import 'package:app1/features/onboardingscreen/presentation/widgets/careena_chat_bubble.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../../homescreen/presentation/home_screen_test_harness.dart';

void main() {
  group('HomeScreen app guide', () {
    setUp(() {
      SharedPreferences.setMockInitialValues({});
    });

    testWidgets('opens from the test header action', (tester) async {
      await pumpHomeScreen(tester);

      await tester.tap(find.byTooltip('App-Guide testen'));
      await tester.pump();

      expect(find.textContaining('Careena ist'), findsOneWidget);
      expect(
        find.byKey(const ValueKey('app-guide-next-button')),
        findsOneWidget,
      );
      expect(
        find.byKey(const ValueKey('app-guide-white-scrim')),
        findsOneWidget,
      );

      final backButton = tester.widget<IconButton>(
        find.byKey(const ValueKey('app-guide-back-button')),
      );
      expect(backButton.onPressed, isNull);
    });

    testWidgets('guides through home areas and completes the tour', (
      tester,
    ) async {
      await pumpHomeScreen(tester, startGuide: true);
      await tester.pump();

      expect(find.textContaining('Careena ist'), findsOneWidget);
      await _nextStep(tester);
      expect(find.text('Schnell finden'), findsOneWidget);

      final backButton = tester.widget<IconButton>(
        find.byKey(const ValueKey('app-guide-back-button')).last,
      );
      expect(backButton.onPressed, isNotNull);

      await tester.tap(
        find.byKey(const ValueKey('app-guide-back-button')).last,
      );
      await tester.pump();
      expect(find.textContaining('Careena ist'), findsOneWidget);

      await _nextStep(tester);
      expect(find.text('Schnell finden'), findsOneWidget);
      await _nextStep(tester);
      expect(find.text('Aktives Profil'), findsOneWidget);
      await _nextStep(tester);
      expect(find.textContaining('Tippe auf eine Funktion'), findsOneWidget);
      await _nextStep(tester);
      expect(find.text('Immer schnell erreichbar'), findsOneWidget);
      await _nextStep(tester);

      expect(find.byKey(const ValueKey('app-guide-next-button')), findsNothing);
      expect(await AppGuideStore().isCompleted(AppGuideStore.guestKey), isTrue);
    });

    testWidgets('stays usable in simple view on a small screen', (
      tester,
    ) async {
      await tester.binding.setSurfaceSize(const Size(320, 640));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      await pumpHomeScreen(tester, simpleView: true, startGuide: true);
      await tester.pump();

      expect(find.textContaining('Careena ist'), findsOneWidget);
      expect(tester.takeException(), isNull);
    });

    testWidgets('uses the dark Careena bubble in dark mode', (tester) async {
      await pumpHomeScreen(tester, startGuide: true, themeMode: ThemeMode.dark);
      await tester.pump();

      final bubble = tester.widget<CareenaChatBubble>(
        find.byType(CareenaChatBubble),
      );

      expect(bubble.useDarkSurfaceInDarkMode, isTrue);
    });
  });
}

Future<void> _nextStep(WidgetTester tester) async {
  await tester.tap(find.byKey(const ValueKey('app-guide-next-button')).last);
  await tester.pump();
}
