import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:app1/core/network/api_client.dart';
import 'package:app1/features/authscreen/presentation/screens/login_screen.dart';
import 'package:app1/features/authscreen/presentation/screens/registration_screen.dart';
import 'package:app1/features/chatscreen/controllers/chat_controller.dart';
import 'package:app1/features/chatscreen/data/chat_api.dart';
import 'package:app1/features/chatscreen/data/models/chat_response_model.dart';
import 'package:app1/features/chatscreen/presentation/screens/chat_screen.dart';
import 'package:app1/features/chatscreen/services/chat_service.dart';
import 'package:app1/features/homescreen/presentation/screens/home_screen.dart';
import 'package:app1/features/warningscreen/presentation/screens/warning_page.dart';
import 'package:app1/main.dart';

void main() {
  late ChatController chatController;

  setUp(() {
    chatController = ChatController(
      chatApi: _FakeChatApi(),
      chatService: ChatService(),
    );
  });

  tearDown(() {
    chatController.dispose();
  });

  testWidgets('Login opens the home screen', (WidgetTester tester) async {
    await tester.pumpWidget(MyApp(chatController: chatController));

    expect(find.text('Anmelden'), findsOneWidget);

    await tester.tap(find.text('Anmelden'));
    await tester.pumpAndSettle();

    expect(find.byType(LoginScreen), findsOneWidget);

    await tester.tap(find.widgetWithText(FilledButton, 'Anmelden'));
    await tester.pumpAndSettle();

    expect(find.byType(HomeScreen), findsOneWidget);
    expect(find.text('Willkommen!'), findsOneWidget);
    expect(
      find.text('Ich bin Careena!\nWie kann ich dir helfen?'),
      findsOneWidget,
    );
    expect(find.text('Deine Funktionen...'), findsOneWidget);
  });

  testWidgets('App allows selecting and copying visible text', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(MyApp(chatController: chatController));

    // The root selection area makes normal Text widgets copyable across pages.
    expect(find.byType(SelectionArea), findsOneWidget);
  });

  testWidgets('Registration opens the multi-step account flow', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(MyApp(chatController: chatController));

    await tester.tap(find.text('Registrieren'));
    await tester.pumpAndSettle();

    expect(find.byType(RegistrationScreen), findsOneWidget);
    expect(find.text('Konto erstellen'), findsOneWidget);
    expect(find.text('Persönliche Daten eingeben'), findsOneWidget);
  });

  testWidgets('Primary onboarding action opens the chatscreen', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(MyApp(chatController: chatController));

    await tester.tap(find.text('Jetzt mit Careena sprechen'));
    await tester.pump();

    expect(find.byType(ChatScreen), findsOneWidget);
  });

  testWidgets('Temporary onboarding test button opens the home screen', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(MyApp(chatController: chatController));

    await tester.tap(find.text('Test: direkt zur Homepage'));
    await tester.pumpAndSettle();

    expect(find.byType(HomeScreen), findsOneWidget);
    expect(find.text('Deine Funktionen...'), findsOneWidget);
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
}

class _FakeChatApi extends ChatApi {
  _FakeChatApi() : super(ApiClient(http.Client()));

  @override
  Future<String> createSession() async => 'test-session';

  @override
  Future<void> warmup() async {}

  @override
  Future<ChatResponse> sendMessage(String text, String sessionId) async {
    return const ChatResponse(text: 'Testantwort', redFlag: false);
  }
}
