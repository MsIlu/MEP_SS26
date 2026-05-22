import 'package:flutter_test/flutter_test.dart';

import 'package:app1/features/chatscreen/controllers/chat_controller.dart';
import 'package:app1/features/chatscreen/data/chat_api_contract.dart';
import 'package:app1/features/chatscreen/data/models/chat_response_model.dart';
import 'package:app1/features/chatscreen/data/models/message_model.dart';
import 'package:app1/features/chatscreen/services/chat_service.dart';

class FakeChatApi implements ChatApiContract {
  @override
  @override
  Future<ChatResponse> sendMessage(String text, String sessionId) async {
    return ChatResponse(
      text: 'Fake response',
      redFlag: false,
    );
  }

  @override
  Future<void> warmup() async {}

  @override
  Future<String> createSession() async {
    return 'test-session';
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

void main() {
  test('cancelGeneration removes last bot message and adds cancel notice', () {
    final controller = ChatController(
      chatApi: FakeChatApi(),
      chatService: ChatService(),
    );

    controller.messages.value = [
      Message(text: 'Hallo', isUser: true),
      Message(text: 'Antwort wird generiert...', isUser: false),
    ];

    controller.cancelGeneration();

    expect(controller.isGenerating, false);
    expect(controller.messages.value.length, 2);

    expect(controller.messages.value[0].text, 'Hallo');
    expect(controller.messages.value[0].isUser, true);

    expect(
      controller.messages.value[1].text,
      'Antwort abgebrochen. Du kannst deine Eingabe jetzt ergänzen.',
    );
    expect(controller.messages.value[1].isUser, false);
  });
}