import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:app1/core/network/api_client.dart';
import 'package:app1/core/themes/app_colors.dart';
import 'package:app1/core/themes/theme_controller.dart';
import 'package:app1/features/chatscreen/controllers/chat_controller.dart';
import 'package:app1/features/chatscreen/data/chat_api.dart';
import 'package:app1/features/chatscreen/data/chat_history_repository.dart';
import 'package:app1/features/chatscreen/data/models/chat_history_entry.dart';
import 'package:app1/features/chatscreen/data/models/message_model.dart';
import 'package:app1/features/chatscreen/services/chat_service.dart';
import 'package:app1/features/chatscreen/presentation/screens/chat_history_screen.dart';
import 'package:app1/features/homescreen/presentation/screens/home_screen.dart';
import 'package:http/http.dart' as http;
import 'package:app1/features/authscreen/domain/models/account.dart';
import 'package:app1/features/authscreen/domain/models/auth_response.dart';
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
        chatHistoryRepository: _FakeChatHistoryRepository(),
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
        chatHistoryRepository: _FakeChatHistoryRepository(),
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
        chatHistoryRepository: _FakeChatHistoryRepository(),
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
        chatHistoryRepository: _FakeChatHistoryRepository(),
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

    testWidgets('opens saved chat history from Nachrichten navigation', (
      WidgetTester tester,
    ) async {
      final firstProfileEntry = ChatHistoryEntry(
        id: 'first',
        profileId: 42,
        symptomTitle: 'Kopfschmerzen',
        createdAt: DateTime(2026, 6, 13, 10),
        messages: [
          Message(text: 'Ich habe Kopfschmerzen seit gestern', isUser: true),
          Message(text: 'Richtig', isUser: true),
        ],
        recommendation:
            'Kurze Zusammenfassung:\nKopfschmerzen seit gestern.\n\nDringlichkeit:\nniedrig',
      );
      final olderFirstProfileEntry = ChatHistoryEntry(
        id: 'older-first',
        profileId: 42,
        symptomTitle: 'Schwindel',
        createdAt: DateTime(2026, 5, 20, 9, 30),
        messages: [Message(text: 'Schwindel', isUser: true)],
        recommendation: 'Aeltere Empfehlung fuer Anna',
      );
      final secondJuneFirstProfileEntry = ChatHistoryEntry(
        id: 'second-june-first',
        profileId: 42,
        symptomTitle: 'Halsschmerzen',
        isEmergency: true,
        createdAt: DateTime(2026, 6, 12, 8, 15),
        messages: [Message(text: 'Ich habe Halsschmerzen', isUser: true)],
        recommendation:
            'Kurze Zusammenfassung:\nHalsschmerzen.\n\nDringlichkeit:\nniedrig',
      );
      final secondProfileEntry = ChatHistoryEntry(
        id: 'second',
        profileId: 43,
        symptomTitle: 'Husten',
        createdAt: DateTime(2026, 6, 13, 11),
        messages: [Message(text: 'Husten', isUser: true)],
        recommendation: 'Empfehlung fuer Ben',
      );

      final historyRepository = _FakeChatHistoryRepository(
        entries: [
          secondProfileEntry,
          olderFirstProfileEntry,
          secondJuneFirstProfileEntry,
          firstProfileEntry,
        ],
      );

      final authSession = AuthSession();
      authSession.setAuthResponse(
        AuthResponse(
          accessToken: 'test-token',
          tokenType: 'bearer',
          account: const Account(id: 1, email: 'test@example.com'),
          profiles: const [
            AuthProfile(
              id: 42,
              displayName: 'Anna',
              profileType: 'self',
              role: 'owner',
            ),
            AuthProfile(
              id: 43,
              displayName: 'Ben',
              profileType: 'child',
              role: 'guardian',
            ),
          ],
        ),
      );

      final controller = ChatController(
        chatApi: ChatApi(ApiClient(http.Client())),
        chatService: ChatService(),
        authSession: authSession,
        chatHistoryRepository: historyRepository,
      );
      final themeController = ThemeController();
      addTearDown(controller.dispose);
      addTearDown(themeController.dispose);
      addTearDown(authSession.dispose);

      await tester.pumpWidget(
        MaterialApp(
          home: HomeScreen(
            controller: controller,
            themeController: themeController,
            authSession: authSession,
          ),
        ),
      );

      await tester.tap(find.text('Nachrichten'));
      await tester.pumpAndSettle();

      expect(find.byType(ChatHistoryScreen), findsOneWidget);
      expect(find.text('Juni 2026'), findsOneWidget);
      expect(find.text('2 Verläufe'), findsOneWidget);
      expect(find.text('Mai 2026'), findsOneWidget);
      expect(find.text('Kopfschmerzen'), findsOneWidget);
      expect(find.text('Halsschmerzen'), findsOneWidget);
      expect(find.text('Notfall'), findsOneWidget);
      expect(find.text('10:00 Uhr'), findsOneWidget);
      expect(find.text('09:30 Uhr'), findsOneWidget);
      expect(find.text('Ich habe Kopfschmerzen seit gestern'), findsOneWidget);
      expect(find.text('Richtig'), findsNothing);
      expect(find.text('Schwindel'), findsWidgets);
      expect(find.text('Husten'), findsNothing);

      await tester.tap(find.text('Juni 2026'));
      await tester.pumpAndSettle();

      expect(find.text('Ich habe Kopfschmerzen seit gestern'), findsNothing);
      expect(find.text('Schwindel'), findsWidgets);

      await tester.tap(find.text('Juni 2026'));
      await tester.pumpAndSettle();

      await tester.tap(find.text('Ich habe Kopfschmerzen seit gestern'));
      await tester.pumpAndSettle();

      expect(find.text('PDF exportieren'), findsNothing);
    });
  });
}

class _FakeChatHistoryRepository extends ChatHistoryRepository {
  final List<ChatHistoryEntry> entries;

  const _FakeChatHistoryRepository({this.entries = const []});

  @override
  Future<List<ChatHistoryEntry>> loadEntries({required int profileId}) async {
    return entries.where((entry) => entry.profileId == profileId).toList()
      ..sort((a, b) => b.createdAt.compareTo(a.createdAt));
  }

  @override
  Future<void> saveCompletedChat(ChatHistoryEntry entry) async {}
}
