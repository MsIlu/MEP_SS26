import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;

import 'package:app1/core/network/api_client.dart';
import 'package:app1/features/chat/controllers/chat_controller.dart';
import 'package:app1/features/chat/data/chat_api.dart';
import 'package:app1/features/chat/data/models/message_model.dart';
import 'package:app1/features/chat/services/chat_service.dart';

void main() {
  test('cancelGeneration removes last bot message and adds cancel notice', () {
    final controller = ChatController(
      chatApi: ChatApi(ApiClient(http.Client())),
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
      'Antwort abgebrochen. Sie können Ihre Eingabe jetzt ergänzen.',
    );
    expect(controller.messages.value[1].isUser, false);
  });
}