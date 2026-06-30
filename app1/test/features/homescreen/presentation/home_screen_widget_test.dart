import 'package:app1/core/network/api_client.dart';
import 'package:app1/core/themes/app_colors.dart';
import 'package:app1/core/themes/theme_controller.dart';
import 'package:app1/features/authscreen/domain/models/account.dart';
import 'package:app1/features/authscreen/domain/models/auth_response.dart';
import 'package:app1/features/authscreen/state/auth_session.dart';
import 'package:app1/features/chatscreen/controllers/chat_controller.dart';
import 'package:app1/features/chatscreen/data/chat_api.dart';
import 'package:app1/features/chatscreen/data/chat_history_repository.dart';
import 'package:app1/features/chatscreen/data/models/chat_history_entry.dart';
import 'package:app1/features/chatscreen/data/models/message_model.dart';
import 'package:app1/features/calendar_overview/presentation/screens/calendar_overview_page.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:app1/features/chatscreen/presentation/screens/chat_history_screen.dart';
import 'package:app1/features/chatscreen/services/chat_service.dart';
import 'package:app1/features/homescreen/presentation/screens/home_screen.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;

import 'home_screen_test_harness.dart';

void main() {
  // Test case references: documents/Testfaelle_Frontend.md#t07-home-screen
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
      expect(find.text('Kalender'), findsOneWidget);
      expect(find.text('Chathistorie'), findsNothing);
      expect(find.text('Einstellungen'), findsOneWidget);

      final iconBackground = find.byKey(
        const ValueKey('feature-icon-background-Symptomtagebuch'),
      );
      expect(tester.getSize(iconBackground), const Size.square(64));
    });

    testWidgets('filters home functions through the search bar', (
      tester,
    ) async {
      await pumpHomeScreen(tester);

      await tester.enterText(find.byType(TextField), 'Sy');
      await tester.pump();

      expect(find.text('Symptomtagebuch'), findsOneWidget);
      expect(find.text('Medikamententagebuch'), findsNothing);
      expect(find.text('Terminplanung'), findsNothing);
      expect(find.text('Dokumente'), findsNothing);

      await tester.tap(find.byTooltip('Suche löschen'));
      await tester.pump();

      expect(find.text('Symptomtagebuch'), findsOneWidget);
      expect(find.text('Medikamententagebuch'), findsOneWidget);
      expect(find.text('Terminplanung'), findsOneWidget);
      expect(find.text('Dokumente'), findsOneWidget);
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

    testWidgets('opens saved chat history from bottom navigation', (
      tester,
    ) async {
      SharedPreferences.setMockInitialValues({});

      await pumpHomeScreen(tester);
      await tester.tap(find.text('Kalender'));
      await tester.pumpAndSettle();

      expect(find.byType(CalendarOverviewPage), findsOneWidget);
      expect(find.text('Keine Einträge'), findsOneWidget);
    });

    testWidgets('opens saved chat history from Chathistorie navigation', (
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

      await tester.tap(find.text('Chathistorie'));
      await tester.pumpAndSettle();

      expect(find.byType(ChatHistoryScreen), findsOneWidget);
      expect(find.text('Juni 2026'), findsOneWidget);
      expect(find.text('2 Verläufe'), findsOneWidget);
      expect(find.text('Mai 2026'), findsOneWidget);
      expect(find.text('Kopfschmerzen'), findsOneWidget);
      expect(find.text('Halsschmerzen'), findsOneWidget);
      expect(find.text('Notfall'), findsOneWidget);
      expect(find.text('13.06.2026'), findsOneWidget);
      expect(find.text('12.06.2026'), findsOneWidget);
      expect(find.text('20.05.2026'), findsOneWidget);
      expect(find.text('10:00 Uhr'), findsOneWidget);
      expect(find.text('09:30 Uhr'), findsOneWidget);
      expect(find.text('Ich habe Kopfschmerzen seit gestern'), findsOneWidget);
      expect(find.text('Richtig'), findsNothing);
      expect(find.text('Schwindel'), findsWidgets);
      expect(find.text('Husten'), findsNothing);
      expect(find.text('Neueste'), findsOneWidget);
      expect(find.text('Älteste'), findsOneWidget);
      expect(
        tester.getTopLeft(find.text('Juni 2026')).dy,
        lessThan(tester.getTopLeft(find.text('Mai 2026')).dy),
      );
      expect(
        tester.getTopLeft(find.text('Kopfschmerzen')).dy,
        lessThan(tester.getTopLeft(find.text('Halsschmerzen')).dy),
      );

      await tester.tap(find.text('Älteste'));
      await tester.pumpAndSettle();

      expect(
        tester.getTopLeft(find.text('Mai 2026')).dy,
        lessThan(tester.getTopLeft(find.text('Juni 2026')).dy),
      );
      expect(
        tester.getTopLeft(find.text('Halsschmerzen')).dy,
        lessThan(tester.getTopLeft(find.text('Kopfschmerzen')).dy),
      );

      await tester.tap(find.text('Neueste'));
      await tester.pumpAndSettle();

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
  Future<ChatHistoryEntry> saveChat(ChatHistoryEntry entry) async {
    return entry;
  }

  @override
  Future<ChatHistoryEntry> updateChat(ChatHistoryEntry entry) async {
    return entry;
  }

  @override
  Future<ChatHistoryEntry> saveCompletedChat(ChatHistoryEntry entry) async {
    return saveChat(entry);
  }
}
