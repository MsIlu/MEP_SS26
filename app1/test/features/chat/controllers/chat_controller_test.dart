import 'package:flutter_test/flutter_test.dart';
import 'package:app1/core/network/api_client.dart';
import 'package:app1/features/chatscreen/controllers/chat_controller.dart';
import 'package:app1/features/chatscreen/data/chat_api.dart';
import 'package:app1/features/chatscreen/services/chat_service.dart';
import 'package:http/http.dart' as http;

/// Unit tests for chat controller state.
void main() {
  group('ChatController', () {
    test('starts with an empty message list before initialization', () {
      // This verifies the raw constructor state before backend init adds copy.
      final httpClient = http.Client();
      final apiClient = ApiClient(httpClient);
      final chatApi = ChatApi(apiClient);
      final controller = ChatController(
        chatApi: chatApi,
        chatService: ChatService(),
      );
      addTearDown(controller.dispose);
      addTearDown(httpClient.close);

      expect(controller.messages.value, isEmpty);
    });
  });
}
