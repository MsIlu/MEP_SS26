import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:app1/core/network/api_client.dart';
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

    expect(find.byType(HomeScreen), findsOneWidget);
    expect(find.text('Willkommen!'), findsOneWidget);
  });

  testWidgets('Primary onboarding action opens the chatscreen', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(MyApp(chatController: chatController));

    await tester.tap(find.text('Jetzt mit Careena sprechen'));
    await tester.pump();

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