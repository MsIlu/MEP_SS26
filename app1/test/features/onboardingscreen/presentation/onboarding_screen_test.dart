import 'package:app1/core/network/api_client.dart';
import 'package:app1/core/themes/theme_controller.dart';
import 'package:app1/features/authscreen/data/auth_api_service.dart';
import 'package:app1/features/authscreen/state/auth_session.dart';
import 'package:app1/features/chatscreen/controllers/chat_controller.dart';
import 'package:app1/features/chatscreen/data/chat_api.dart';
import 'package:app1/features/chatscreen/data/chat_history_repository.dart';
import 'package:app1/features/chatscreen/data/models/careena_availability.dart';
import 'package:app1/features/chatscreen/data/models/chat_history_entry.dart';
import 'package:app1/features/chatscreen/data/models/chat_response_model.dart';
import 'package:app1/features/chatscreen/services/chat_service.dart';
import 'package:app1/features/onboardingscreen/presentation/screens/onboarding_screen.dart';
import 'package:app1/features/symptom_diary/data/symptom_repository.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;

void main() {
  group('OnboardingScreen', () {
    late AuthSession authSession;
    late ChatController chatController;
    late ThemeController themeController;

    setUp(() {
      authSession = AuthSession();
      chatController = ChatController(
        chatApi: _FakeChatApi(),
        chatService: ChatService(),
        authSession: authSession,
        chatHistoryRepository: _FakeChatHistoryRepository(),
      );
      themeController = ThemeController();
    });

    tearDown(() {
      chatController.dispose();
      themeController.dispose();
      authSession.dispose();
    });

    testWidgets('does not expose the direct home test button', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: OnboardingScreen(
            chatController: chatController,
            themeController: themeController,
            authSession: authSession,
            authApiService: AuthApiService(ApiClient(http.Client())),
            symptomRepository: SymptomRepository(),
          ),
        ),
      );

      expect(find.text('Anmelden'), findsOneWidget);
      expect(find.text('Registrieren'), findsOneWidget);
      expect(find.text('Test: direkt zur Homepage'), findsNothing);
    });
  });
}

class _FakeChatApi extends ChatApi {
  _FakeChatApi() : super(ApiClient(http.Client()));

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
    return const ChatResponse(text: 'Testantwort', redFlag: false);
  }
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