import 'package:app1/app/app_dependencies.dart';
import 'package:app1/app/app_dependencies_scope.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:app1/core/network/api_client.dart';
import 'package:app1/core/themes/theme_controller.dart';
import 'package:app1/core/widgets/responsive_frame.dart';
import 'package:app1/features/chatscreen/controllers/chat_controller.dart';
import 'package:app1/features/chatscreen/data/chat_api.dart';
import 'package:app1/features/chatscreen/data/chat_history_repository.dart';
import 'package:app1/features/chatscreen/data/models/careena_availability.dart';
import 'package:app1/features/chatscreen/data/models/chat_history_entry.dart';
import 'package:app1/features/chatscreen/data/models/chat_response_model.dart';
import 'package:app1/features/chatscreen/presentation/screens/chat_screen.dart';
import 'package:app1/features/chatscreen/services/chat_service.dart';
import 'package:app1/features/homescreen/presentation/screens/home_screen.dart';
import 'package:app1/features/warningscreen/presentation/screens/warning_page.dart';
import 'package:app1/features/authscreen/state/auth_session.dart';
import 'package:app1/features/chatscreen/presentation/widgets/chat_warning_dialog.dart';

void main() {
  // Test case references: documents/Testfaelle_Frontend.md#t11-app-smoke-warning-flow
  late ChatController chatController;
  late ThemeController themeController;

  setUp(() {
    chatController = ChatController(
      chatApi: _FakeChatApi(),
      chatService: ChatService(),
      authSession: AuthSession(),
      chatHistoryRepository: _FakeChatHistoryRepository(),
    );
    themeController = ThemeController();
  });

  tearDown(() {
    chatController.dispose();
    themeController.dispose();
  });

  testWidgets('Home screen renders the authenticated entry point', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      MaterialApp(
        home: HomeScreen(
          controller: chatController,
          themeController: themeController,
        ),
      ),
    );

    expect(find.byType(HomeScreen), findsOneWidget);
    expect(find.text('Willkommen!'), findsOneWidget);
    expect(find.textContaining('Ich bin Careena!'), findsOneWidget);
  });

  testWidgets('App allows selecting and copying visible text', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: ResponsivePageBody(child: Text('Kopierbarer Text')),
        ),
      ),
    );

    expect(find.byType(SelectionArea), findsOneWidget);
    expect(find.text('Kopierbarer Text'), findsOneWidget);
  });

  testWidgets('Chat screen opens with controller-backed UI', (
    WidgetTester tester,
  ) async {
    final authSession = AuthSession();

    final dependencies = AppDependencies(authSession: authSession);

    await tester.pumpWidget(
      AppDependenciesScope(
        dependencies: dependencies,
        child: MaterialApp(
          home: ChatScreen(
            controller: chatController,
            themeController: themeController,
          ),
        ),
      ),
    );
    await tester.pump();

    expect(find.byType(ChatScreen), findsOneWidget);
    expect(find.text('Careena'), findsOneWidget);
    expect(find.byType(TextField), findsOneWidget);
  });

  testWidgets('red flag response replaces chat with warning page', (
    WidgetTester tester,
  ) async {
    final authSession = AuthSession();
    final dependencies = AppDependencies(authSession: authSession);
    final redFlagController = ChatController(
      chatApi: _FakeChatApi(
        response: const ChatResponse(
          text: 'Bitte sofort den Notruf 112 kontaktieren.',
          redFlag: false,
          action: 'Notruf 112',
        ),
      ),
      chatService: ChatService(),
      authSession: authSession,
      chatHistoryRepository: _FakeChatHistoryRepository(),
    );

    addTearDown(dependencies.dispose);
    addTearDown(redFlagController.dispose);
    addTearDown(authSession.dispose);

    await tester.pumpWidget(
      AppDependenciesScope(
        dependencies: dependencies,
        child: MaterialApp(
          home: ChatScreen(
            controller: redFlagController,
            themeController: themeController,
          ),
        ),
      ),
    );
    await tester.pump();

    await tester.enterText(find.byType(TextField), 'Ich blute stark');
    await tester.tap(find.byIcon(Icons.send));
    await tester.pumpAndSettle();

    expect(find.byType(WarningPage), findsOneWidget);
    expect(find.byType(ChatScreen), findsNothing);
  });

  testWidgets('Warning page shows emergency action', (
    WidgetTester tester,
  ) async {
    const response = ChatResponse(
      text: 'Warnhinweis',
      redFlag: true,
      ruleName: 'Starke oder unstillbare Blutung',
      category: 'bleeding',
      matchedKeywords: ['starke blutung'],
    );

    await tester.pumpWidget(
      const MaterialApp(home: WarningPage(response: response)),
    );

    expect(find.text('Handlungsempfehlung'), findsOneWidget);
    expect(find.text('Achtung: Möglicher Notfall'), findsOneWidget);
    expect(find.textContaining('Notruf 112'), findsWidgets);
  });

  testWidgets('Warning page lists chat details as recommendation reasons', (
    WidgetTester tester,
  ) async {
    const response = ChatResponse(
      text: 'Kein akuter Notfall erkannt.',
      redFlag: false,
      recommendationReady: true,
    );

    await tester.pumpWidget(
      const MaterialApp(
        home: WarningPage(
          response: response,
          symptoms: ['pulsierende Kopfschmerzen'],
          userMessages: ['Ich habe seit 2 Tagen Kopfschmerzen links'],
        ),
      ),
    );

    expect(find.text('Gründe'), findsOneWidget);
    expect(find.textContaining('pulsierende Kopfschmerzen'), findsOneWidget);
    expect(find.textContaining('Seit 2 Tagen Kopfschmerzen links'), findsOneWidget);
  });

  testWidgets('Warning page summarizes duplicate recommendation reasons', (
    WidgetTester tester,
  ) async {
    const response = ChatResponse(
      text: 'Kein akuter Notfall erkannt.',
      redFlag: false,
      recommendationReady: true,
      recommendationResult: RecommendationResult(
        allowed: true,
        urgency: 'routine',
        urgencyLevel: 'low',
        careLevel: 'Hausarztpraxis',
        specialty: 'Allgemeinmedizin',
        reasons: ['Kopfschmerzen seit 2 Tagen'],
      ),
    );

    await tester.pumpWidget(
      const MaterialApp(
        home: WarningPage(
          response: response,
          symptoms: ['pulsierende Kopfschmerzen', 'Übelkeit'],
          userMessages: [
            'Ich habe seit 2 Tagen pulsierende Kopfschmerzen und Übelkeit',
            'Ja',
          ],
        ),
      ),
    );

    expect(
      find.text('• Seit 2 Tagen pulsierende Kopfschmerzen und Übelkeit'),
      findsOneWidget,
    );
    expect(find.text('• Kopfschmerzen seit 2 Tagen'), findsNothing);
    expect(find.text('• pulsierende Kopfschmerzen'), findsNothing);
    expect(find.text('• Übelkeit'), findsNothing);
    expect(find.text('• Ja'), findsNothing);
  });

  testWidgets('shows warning title, content and button', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Builder(builder: (context) => const ChatWarningDialog()),
      ),
    );

    expect(find.text('Wichtiger Hinweis'), findsOneWidget);

    expect(
      find.textContaining('Diese Antworten dienen ausschließlich'),
      findsOneWidget,
    );

    expect(find.text('Verstanden'), findsOneWidget);
  });

  testWidgets('closes dialog when accepted', (tester) async {
    final authSession = AuthSession();
    final dependencies = AppDependencies(authSession: authSession);

    await tester.pumpWidget(
      AppDependenciesScope(
        dependencies: dependencies,
        child: MaterialApp(
          home: Builder(
            builder: (context) {
              Future.microtask(() {
                showDialog(
                  context: context,
                  builder: (_) => const ChatWarningDialog(),
                );
              });

              return const Scaffold();
            },
          ),
        ),
      ),
    );

    await tester.pumpAndSettle();

    expect(find.byType(AlertDialog), findsOneWidget);

    await tester.tap(find.text('Verstanden'));
    await tester.pumpAndSettle();

    expect(find.byType(AlertDialog), findsNothing);
  });
}

class _FakeChatApi extends ChatApi {
  final ChatResponse response;

  _FakeChatApi({
    this.response = const ChatResponse(text: 'Testantwort', redFlag: false),
  }) : super(ApiClient(http.Client()));

  @override
  Future<String> createSession([int? profileId]) async => 'test-session';

  @override
  Future<void> warmup() async {}

  @override
  Future<CareenaAvailability> getCareenaAvailability() async {
    return CareenaAvailability.online;
  }

  @override
  Future<ChatResponse> sendMessage(
    String text,
    String sessionId,
    int? profileId,
  ) async {
    return response;
  }

  @override
  Future<List<String>> getInputDraftSymptoms(String sessionId) async {
    return [];
  }

  @override
  Future<List<String>> updateInputDraftSymptoms(
    String sessionId,
    List<String> symptoms,
  ) async {
    return symptoms;
  }

  @override
  Future<void> cancelInputDraft(String sessionId) async {}
}

class _FakeChatHistoryRepository extends ChatHistoryRepository {
  @override
  Future<List<ChatHistoryEntry>> loadEntries({required int profileId}) async {
    return [];
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
