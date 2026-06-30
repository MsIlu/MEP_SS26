import 'package:app1/core/network/api_client.dart';
import 'package:app1/core/network/api_exception.dart';
import 'package:app1/core/themes/theme_controller.dart';
import 'package:app1/features/authscreen/domain/models/account.dart';
import 'package:app1/features/authscreen/domain/models/auth_response.dart';
import 'package:app1/features/authscreen/state/auth_session.dart';
import 'package:app1/features/chatscreen/controllers/chat_controller.dart';
import 'package:app1/features/chatscreen/data/chat_api.dart';
import 'package:app1/features/chatscreen/data/chat_history_repository.dart';
import 'package:app1/features/chatscreen/data/models/chat_history_entry.dart';
import 'package:app1/features/chatscreen/data/models/message_model.dart';
import 'package:app1/features/chatscreen/presentation/screens/chat_history_screen.dart';
import 'package:app1/features/chatscreen/services/chat_service.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  testWidgets('zeigt einen Resume-Konflikt verständlich auf Deutsch', (
    tester,
  ) async {
    SharedPreferences.setMockInitialValues({});
    final authSession = AuthSession();
    authSession.setAuthResponse(
      const AuthResponse(
        accessToken: 'token',
        tokenType: 'bearer',
        account: Account(id: 1, email: 'test@example.com'),
        profiles: [
          AuthProfile(
            id: 42,
            displayName: 'Anna',
            profileType: 'self',
            role: 'owner',
          ),
        ],
      ),
    );
    final themeController = ThemeController();
    final controller = ChatController(
      chatApi: _FailingResumeChatApi(),
      chatService: ChatService(),
      authSession: authSession,
      chatHistoryRepository: _HistoryRepository(),
    );
    addTearDown(controller.dispose);
    addTearDown(authSession.dispose);
    addTearDown(themeController.dispose);

    await tester.pumpWidget(
      MaterialApp(
        home: ChatHistoryScreen(
          themeController: themeController,
          chatController: controller,
          profileId: 42,
          repository: _HistoryRepository(),
        ),
      ),
    );
    await tester.pumpAndSettle();
    await tester.tap(find.text('Kopfschmerzen'));
    await tester.pumpAndSettle();

    expect(find.textContaining('Der Chat wurde bereits'), findsOneWidget);
    expect(find.textContaining('Only active'), findsNothing);
  });
}

class _FailingResumeChatApi extends ChatApi {
  _FailingResumeChatApi() : super(ApiClient(http.Client()));

  @override
  Future<String> resumeHistorySession(String historyId) {
    throw const ApiException(
      ApiErrorType.http,
      'Only active chat history entries can be resumed.',
      statusCode: 409,
    );
  }
}

class _HistoryRepository extends ChatHistoryRepository {
  final entry = ChatHistoryEntry(
    id: 'history-1',
    profileId: 42,
    sessionId: 'old-session',
    symptomTitle: 'Kopfschmerzen',
    status: 'active',
    createdAt: DateTime(2026, 6, 30),
    messages: [Message(text: 'Ich habe Kopfschmerzen', isUser: true)],
    recommendation: '',
  );

  @override
  Future<List<ChatHistoryEntry>> loadEntries({required int profileId}) async {
    return [entry];
  }

  @override
  Future<ChatHistoryEntry> saveChat(ChatHistoryEntry entry) async => entry;

  @override
  Future<ChatHistoryEntry> updateChat(ChatHistoryEntry entry) async => entry;
}
