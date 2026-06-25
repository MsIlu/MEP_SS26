import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;

import 'package:app1/core/network/api_client.dart';
import 'package:app1/features/chatscreen/data/chat_api.dart';
import 'package:app1/features/chatscreen/services/chat_session_service.dart';

void main() {
  // Test case references: documents/Testfaelle_Frontend.md#t06-chat-core-und-ui
  group('ChatSessionService', () {
    test('creates and warms up a session only once', () async {
      final chatApi = _FakeChatApi();
      final service = ChatSessionService(chatApi);

      final firstSessionId = await service.ensureSession();
      final secondSessionId = await service.ensureSession();

      expect(firstSessionId, 'session-1');
      expect(secondSessionId, 'session-1');
      expect(service.sessionId, 'session-1');
      expect(chatApi.createSessionCalls, 1);
      expect(chatApi.warmupCalls, 1);
    });

    test('creates a new session when the profile changes', () async {
      final chatApi = _FakeChatApi();
      final service = ChatSessionService(chatApi);

      final firstSessionId = await service.ensureSession(profileId: 10);
      final secondSessionId = await service.ensureSession(profileId: 11);

      expect(firstSessionId, 'session-1');
      expect(secondSessionId, 'session-2');
      expect(service.profileId, 11);
      expect(chatApi.createdProfileIds, [10, 11]);
      expect(chatApi.createSessionCalls, 2);
    });

    test('clearSession returns and removes the current session id', () async {
      final chatApi = _FakeChatApi();
      final service = ChatSessionService(chatApi);

      await service.ensureSession();

      expect(service.clearSession(), 'session-1');
      expect(service.sessionId, isNull);
      expect(service.profileId, isNull);
    });
  });
}

class _FakeChatApi extends ChatApi {
  _FakeChatApi() : super(ApiClient(http.Client()));

  int createSessionCalls = 0;
  int warmupCalls = 0;
  final List<int?> createdProfileIds = [];

  @override
  Future<String> createSession([int? profileId]) async {
    createSessionCalls += 1;
    createdProfileIds.add(profileId);
    return 'session-$createSessionCalls';
  }

  @override
  Future<void> warmup() async {
    warmupCalls += 1;
  }
}
