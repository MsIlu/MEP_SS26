import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:app1/core/network/api_client.dart';
import 'package:app1/core/themes/app_colors.dart';
import 'package:app1/core/themes/theme_controller.dart';
import 'package:app1/features/chatscreen/controllers/chat_controller.dart';
import 'package:app1/features/chatscreen/data/chat_api.dart';
import 'package:app1/features/chatscreen/services/chat_service.dart';
import 'package:app1/features/homescreen/presentation/screens/home_screen.dart';
import 'package:http/http.dart' as http;
import 'package:app1/features/authscreen/state/auth_session.dart';

/// Widget tests for the home screen presentation layer.
void main() {
  group('HomeScreen', () {
    testWidgets('renders the welcome area and Careena entry card', (
      WidgetTester tester,
    ) async {
      // The home screen needs the same controllers it receives in production.
      final apiClient = ApiClient(http.Client());
      final chatApi = ChatApi(apiClient);
      final controller = ChatController(
        chatApi: chatApi,
        chatService: ChatService(),
        authSession: AuthSession(),
      );
      final themeController = ThemeController();
      addTearDown(controller.dispose);
      addTearDown(themeController.dispose);

      await tester.pumpWidget(
        MaterialApp(
          home: HomeScreen(
            controller: controller,
            themeController: themeController,
          ),
        ),
      );

      expect(find.text('Willkommen!'), findsOneWidget);
      expect(find.textContaining('Ich bin Careena!'), findsOneWidget);
      expect(find.text('Medikamentenplan'), findsOneWidget);
    });

    testWidgets('simple view removes distractions and enlarges navigation', (
      WidgetTester tester,
    ) async {
      final apiClient = ApiClient(http.Client());
      final controller = ChatController(
        chatApi: ChatApi(apiClient),
        chatService: ChatService(),
        authSession: AuthSession(),
      );
      final themeController = ThemeController()..setSimpleView(true);
      addTearDown(controller.dispose);
      addTearDown(themeController.dispose);

      await tester.pumpWidget(
        MaterialApp(
          home: HomeScreen(
            controller: controller,
            themeController: themeController,
          ),
        ),
      );

      expect(find.text('Suchen...'), findsNothing);
      expect(find.text('Was möchtest du tun?'), findsOneWidget);
      expect(find.text('Kalender'), findsNothing);
      expect(find.text('Nachrichten'), findsNothing);
      expect(find.text('Einstellungen'), findsOneWidget);

      final iconBackground = find.byKey(
        const ValueKey('feature-icon-background-Terminplanung'),
      );
      final iconBox = tester.getSize(iconBackground);

      expect(iconBox, const Size.square(64));
    });

    testWidgets('uses the Careena light home palette', (
      WidgetTester tester,
    ) async {
      final controller = ChatController(
        chatApi: ChatApi(ApiClient(http.Client())),
        chatService: ChatService(),
        authSession: AuthSession(),
      );
      final themeController = ThemeController()..setThemeMode(ThemeMode.light);
      addTearDown(controller.dispose);
      addTearDown(themeController.dispose);

      await tester.pumpWidget(
        MaterialApp(
          theme: ThemeData.light(),
          home: HomeScreen(
            controller: controller,
            themeController: themeController,
          ),
        ),
      );

      final scaffold = tester.widget<Scaffold>(find.byType(Scaffold));
      final featureCard = tester.widget<Material>(
        find.byKey(const ValueKey('home-feature-card-Terminplanung')),
      );

      expect(scaffold.backgroundColor, AppColors.headerBackgroundLight);
      expect(featureCard.color, AppColors.lightCard);
      expect(featureCard.shadowColor, AppColors.careenaBorder);
    });

    testWidgets('keeps elevated feature cards in dark mode', (
      WidgetTester tester,
    ) async {
      final controller = ChatController(
        chatApi: ChatApi(ApiClient(http.Client())),
        chatService: ChatService(),
        authSession: AuthSession(),
      );
      final themeController = ThemeController()..setThemeMode(ThemeMode.dark);
      addTearDown(controller.dispose);
      addTearDown(themeController.dispose);

      await tester.pumpWidget(
        MaterialApp(
          theme: ThemeData.dark(),
          home: HomeScreen(
            controller: controller,
            themeController: themeController,
          ),
        ),
      );

      final featureCard = tester.widget<Material>(
        find.byKey(const ValueKey('home-feature-card-Terminplanung')),
      );

      expect(featureCard.elevation, 2);
      expect(featureCard.shadowColor, AppColors.darkBackground);
    });
  });
}
