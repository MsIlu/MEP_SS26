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

  void configureTestViewport(WidgetTester tester) {
    tester.view.physicalSize = const Size(1080, 2400);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.resetPhysicalSize);
  }

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
    configureTestViewport(tester);
    await tester.pumpWidget(MyApp(chatController: chatController));

    // Erster Klick im Onboarding (Wechsel zum LoginScreen)
    final initialLoginBtn = find.text('Anmelden');
    await tester.ensureVisible(initialLoginBtn);
    await tester.tap(initialLoginBtn);
    await tester.pumpAndSettle(); // Das ist okay, hier animiert noch nichts unendlich

    expect(find.byType(LoginScreen), findsOneWidget);

    // Flexibler Finder für den Absende-Button im Login-Formular
    final formLoginBtn = find.descendant(
      of: find.byType(LoginScreen),
      matching: find.text('Anmelden'),
    );
    
    await tester.tap(formLoginBtn.first);
    
    // REPARATUR: Ersetzt pumpAndSettle(), um den Timeout durch unendliche Animationen auf dem HomeScreen zu verhindern
    for (int i = 0; i < 5; i++) {
      await tester.pump(const Duration(milliseconds: 200));
    }

    // Überprüfung, ob der HomeScreen geladen wurde
    expect(find.byType(HomeScreen), findsOneWidget);
  });

  testWidgets('Registration opens the multi-step account flow', (WidgetTester tester) async {
    configureTestViewport(tester);
    await tester.pumpWidget(MyApp(chatController: chatController));

    final registerBtn = find.text('Registrieren');
    await tester.ensureVisible(registerBtn);
    await tester.tap(registerBtn);
    await tester.pumpAndSettle();

    expect(find.byType(RegistrationScreen), findsOneWidget);
    expect(find.text('Konto erstellen'), findsOneWidget);
  });

  testWidgets('Primary onboarding action opens the chatscreen', (WidgetTester tester) async {
    configureTestViewport(tester);
    await tester.pumpWidget(MyApp(chatController: chatController));

    final startChatBtn = find.text('Jetzt mit Careena sprechen');
    await tester.ensureVisible(startChatBtn);
    await tester.tap(startChatBtn);
    
    // REPARATUR: pumpAndSettle statt pump, damit die Seiten-Wechsel-Animation durchläuft
    await tester.pumpAndSettle();

    expect(find.byType(ChatScreen), findsOneWidget);
  });

  testWidgets('Temporary onboarding test button opens the home screen', (WidgetTester tester) async {
    configureTestViewport(tester);
    await tester.pumpWidget(MyApp(chatController: chatController));

    final directHomeBtn = find.text('Test: direkt zur Homepage');
    await tester.ensureVisible(directHomeBtn);
    await tester.tap(directHomeBtn);
    
    // Wir pumpen die UI mehrfach in Mikroschritten weiter.
    // Das erlaubt der Navigation den Wechsel, ignoriert aber dauerhaft laufende Widgets.
    for (int i = 0; i < 5; i++) {
      await tester.pump(const Duration(milliseconds: 200));
    }

    expect(find.byType(HomeScreen), findsOneWidget);
    expect(find.text('Deine Funktionen...'), findsOneWidget);
  });

  testWidgets('Warning page shows emergency action', (WidgetTester tester) async {
    configureTestViewport(tester);
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