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
    await tester.pump(const Duration(milliseconds: 500));

    final onboardingLoginButton = find.text('Anmelden');
    expect(onboardingLoginButton, findsOneWidget);

    await tester.ensureVisible(onboardingLoginButton);
    await tester.pump();

    await tester.tap(onboardingLoginButton);
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 500));

    expect(find.byType(LoginScreen), findsOneWidget);

    expect(find.byType(EditableText), findsAtLeastNWidgets(2));

    await tester.enterText(find.byType(EditableText).at(0), 'test@example.com');
    await tester.enterText(find.byType(EditableText).at(1), 'password123');
    await tester.pump();

    final loginSubmitButton = find.text('Anmelden').last;

    await tester.ensureVisible(loginSubmitButton);
    await tester.pump();

    await tester.tap(loginSubmitButton);
    await tester.pump();
    await tester.pump(const Duration(seconds: 1));

    expect(find.byType(HomeScreen), findsOneWidget);
    expect(find.text('Willkommen!'), findsOneWidget);
    expect(find.textContaining('Ich bin Careena!'), findsOneWidget);
  });

  testWidgets('Registration opens the multi-step account flow', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(MyApp(chatController: chatController));

    final registerButton = find.text('Registrieren');
    expect(registerButton, findsOneWidget);

    await tester.ensureVisible(registerButton);
    await tester.pumpAndSettle();

    await tester.tap(registerButton);
    await tester.pumpAndSettle();

    expect(find.byType(RegistrationScreen), findsOneWidget);
    expect(find.text('Konto erstellen'), findsOneWidget);
    expect(find.text('Persönliche Daten eingeben'), findsOneWidget);
  });

  testWidgets('Primary onboarding action opens the chatscreen', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(MyApp(chatController: chatController));

    final chatButton = find.text('Jetzt mit Careena sprechen');
    expect(chatButton, findsOneWidget);

    await tester.ensureVisible(chatButton);
    await tester.pumpAndSettle();

    await tester.tap(chatButton);
    await tester.pumpAndSettle();

    expect(find.byType(ChatScreen), findsOneWidget);
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
