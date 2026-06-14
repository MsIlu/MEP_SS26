import 'package:app1/core/themes/app_colors.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'home_screen_test_harness.dart';

void main() {
  group('HomeScreen', () {
    testWidgets('renders the welcome area and Careena entry card', (
      tester,
    ) async {
      await pumpHomeScreen(tester);

      expect(find.text('Willkommen!'), findsOneWidget);
      expect(find.textContaining('Ich bin Careena!'), findsOneWidget);
      expect(find.text('Terminplanung'), findsOneWidget);
    });

    testWidgets('simple view removes distractions and enlarges navigation', (
      tester,
    ) async {
      await pumpHomeScreen(tester, simpleView: true);

      expect(find.text('Suchen...'), findsNothing);
      expect(find.textContaining('tun?'), findsOneWidget);
      expect(find.text('Kalender'), findsNothing);
      expect(find.text('Nachrichten'), findsNothing);
      expect(find.text('Einstellungen'), findsOneWidget);

      final iconBackground = find.byKey(
        const ValueKey('feature-icon-background-Terminplanung'),
      );
      expect(tester.getSize(iconBackground), const Size.square(64));
    });

    testWidgets('uses the Careena light home palette', (tester) async {
      await pumpHomeScreen(tester, themeMode: ThemeMode.light);

      final scaffold = tester.widget<Scaffold>(find.byType(Scaffold));
      final featureCard = tester.widget<Material>(
        find.byKey(const ValueKey('home-feature-card-Terminplanung')),
      );

      expect(scaffold.backgroundColor, AppColors.headerBackgroundLight);
      expect(featureCard.color, AppColors.lightCard);
      expect(featureCard.shadowColor, AppColors.careenaBorder);
    });

    testWidgets('keeps elevated feature cards in dark mode', (tester) async {
      await pumpHomeScreen(tester, themeMode: ThemeMode.dark);

      final featureCard = tester.widget<Material>(
        find.byKey(const ValueKey('home-feature-card-Terminplanung')),
      );

      expect(featureCard.elevation, 2);
      expect(featureCard.shadowColor, AppColors.darkBackground);
    });
  });
}
