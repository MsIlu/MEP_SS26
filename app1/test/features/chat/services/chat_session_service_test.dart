import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;

import 'package:app1/core/network/api_client.dart';
import 'package:app1/features/chatscreen/data/chat_api.dart';
import 'package:app1/features/chatscreen/services/chat_session_service.dart';

void main() {
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

    test('clearSession returns and removes the current session id', () async {
      final chatApi = _FakeChatApi();
      final service = ChatSessionService(chatApi);

      await service.ensureSession();

      expect(service.clearSession(), 'session-1');
      expect(service.sessionId, isNull);
    });
  });
}

class _FakeChatApi extends ChatApi {
  _FakeChatApi() : super(ApiClient(http.Client()));

  int createSessionCalls = 0;
  int warmupCalls = 0;

  @override
  Future<String> createSession() async {
    createSessionCalls += 1;
    return 'session-$createSessionCalls';
  }

  @override
  Future<void> warmup() async {
    warmupCalls += 1;
  }
}
