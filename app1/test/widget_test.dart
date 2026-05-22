import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:app1/features/chatscreen/controllers/chat_controller.dart';
import 'package:app1/features/chatscreen/data/chat_api_contract.dart';
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
    tester.view.physicalSize = const Size(1200, 1000);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await tester.pumpWidget(MyApp(chatController: chatController));
    await tester.pump(const Duration(milliseconds: 300));

    expect(find.text('Anmelden'), findsOneWidget);

    await tester.ensureVisible(find.text('Anmelden'));
    await tester.pump(const Duration(milliseconds: 300));

    final loginButton = find.ancestor(
      of: find.text('Anmelden'),
      matching: find.byType(InkWell),
    );

    expect(loginButton, findsOneWidget);

    await tester.tap(loginButton);
    await tester.pump(const Duration(seconds: 1));

    expect(find.byType(HomeScreen), findsOneWidget);
    expect(find.text('Willkommen!'), findsOneWidget);
    //TODO: Update test after navigation flow is finalized
  }, skip: true);

  testWidgets('Primary onboarding action opens the chatscreen', (
      WidgetTester tester,
      ) async {
    tester.view.physicalSize = const Size(1200, 1000);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await tester.pumpWidget(MyApp(chatController: chatController));
    await tester.pump(const Duration(milliseconds: 300));

    await tester.ensureVisible(find.text('Anmelden'));
    await tester.pump(const Duration(milliseconds: 300));

    final loginButton = find.ancestor(
      of: find.text('Anmelden'),
      matching: find.byType(InkWell),
    );

    expect(loginButton, findsOneWidget);

    await tester.tap(loginButton);
    await tester.pump(const Duration(seconds: 1));

    expect(find.byType(HomeScreen), findsOneWidget);

    await tester.ensureVisible(find.text('Jetzt mit Careena sprechen'));
    await tester.pump(const Duration(milliseconds: 300));

    await tester.tap(find.text('Jetzt mit Careena sprechen'));
    await tester.pump(const Duration(seconds: 1));

    expect(find.byType(ChatScreen), findsOneWidget);
    //TODO: Update when the onboarding/home navigation flow is finalized.
  }, skip: true);

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

class _FakeChatApi implements ChatApiContract {
  @override
  Future<String> createSession() async => 'test-session';

  @override
  Future<void> warmup() async {}

  @override
  Future<ChatResponse> sendMessage(String text, String sessionId) async {
    return const ChatResponse(text: 'Testantwort', redFlag: false);
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