import 'package:flutter_test/flutter_test.dart';
import 'package:app1/features/chatscreen/data/models/message_model.dart';
import 'package:app1/features/chatscreen/services/chat_service.dart';

void main() {
  // Test case references: documents/Testfaelle_Frontend_Aufgaben.md#t06-chat-core-und-ui
  group('ChatService', () {
    final service = ChatService();

    test('adds messages without mutating the original list', () {
      final original = [Message(text: 'Hallo', isUser: true)];
      final added = Message(text: 'Antwort', isUser: false);

      final result = service.addMessage(messages: original, message: added);

      expect(original, hasLength(1));
      expect(result, [original.first, added]);
    });

    test('removes the last assistant message only', () {
      final user = Message(text: 'Symptom', isUser: true);
      final firstBot = Message(text: 'Frage', isUser: false);
      final secondBot = Message(text: '', isUser: false, isLoading: true);

      final result = service.removeLastBotMessage([firstBot, user, secondBot]);

      expect(result, [firstBot, user]);
    });

    test('streams unicode text without splitting emoji code points', () async {
      final chunks = await service
          .streamText('Hi 👋', delay: Duration.zero)
          .toList();

      expect(chunks.last, 'Hi 👋');
      expect(chunks, isNot(contains('Hi �')));
    });
  });
}
