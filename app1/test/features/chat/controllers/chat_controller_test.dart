import 'package:flutter_test/flutter_test.dart';
import 'package:app1/core/network/api_client.dart';
import 'package:app1/features/authscreen/domain/models/account.dart';
import 'package:app1/features/authscreen/domain/models/auth_response.dart';
import 'package:app1/features/authscreen/state/auth_session.dart';
import 'package:app1/features/chatscreen/controllers/chat_controller.dart';
import 'package:app1/features/chatscreen/data/chat_api.dart';
import 'package:app1/features/chatscreen/data/models/chat_response_model.dart';
import 'package:app1/features/chatscreen/services/chat_service.dart';
import 'package:http/http.dart' as http;

/// Unit tests for chat controller state and profile-aware chat requests.
void main() {
  group('ChatController', () {
    test('starts with an empty message list before initialization', () {
      final httpClient = http.Client();
      final apiClient = ApiClient(httpClient);
      final authSession = AuthSession();

      final controller = ChatController(
        chatApi: ChatApi(apiClient),
        chatService: ChatService(),
        authSession: authSession,
      );

      addTearDown(controller.dispose);
      addTearDown(authSession.dispose);
      addTearDown(httpClient.close);

      expect(controller.messages.value, isEmpty);
    });

    test('sends active profile id from auth session to chat api', () async {
      final authSession = AuthSession();
      final chatApi = _FakeChatApi();
      final controller = ChatController(
        chatApi: chatApi,
        chatService: ChatService(),
        authSession: authSession,
      );

      addTearDown(controller.dispose);
      addTearDown(authSession.dispose);

      authSession.setAuthResponse(
        AuthResponse(
          accessToken: 'test-token',
          tokenType: 'bearer',
          account: const Account(
            id: 1,
            email: 'test@example.com',
          ),
          profiles: const [
            AuthProfile(
              id: 42,
              displayName: 'Anna',
              profileType: 'self',
              role: 'owner',
            ),
          ],
        ),
      );

      await controller.init();
      final response = await controller.sendMessage('Hallo');

      expect(response, isNotNull);
      expect(chatApi.lastText, 'Hallo');
      expect(chatApi.lastSessionId, 'fake-session-id');
      expect(chatApi.lastProfileId, 42);
    });
  });
}

class _FakeChatApi extends ChatApi {
  _FakeChatApi() : super(ApiClient(http.Client()));

  String? lastText;
  String? lastSessionId;
  int? lastProfileId;

  @override
  Future<String> createSession() async {
    return 'fake-session-id';
  }

  @override
  Future<void> warmup() async {}

  @override
  Future<ChatResponse> sendMessage(
      String text,
      String sessionId,
      int profileId,
      ) async {
    lastText = text;
    lastSessionId = sessionId;
    lastProfileId = profileId;

    return ChatResponse(
      text: 'Antwort',
      redFlag: false,
      action: null,
    );
  }
}