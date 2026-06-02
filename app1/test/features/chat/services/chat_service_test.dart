import 'package:flutter_test/flutter_test.dart';
import 'package:app1/features/chatscreen/data/models/message_model.dart';
import 'package:app1/features/chatscreen/services/chat_service.dart';

/// Unit tests for pure chat message list operations.
void main() {
  group('ChatService', () {
    final chatService = ChatService();

    test('addMessage appends without mutating the existing list', () {
      final original = <Message>[];
      final newMessage = Message(text: 'Test-Nachricht', isUser: true);

      final result = chatService.addMessage(
        messages: original,
        message: newMessage,
      );

      expect(original, isEmpty);
      expect(result, [newMessage]);
    });

    test('removeLastBotMessage removes the newest assistant bubble', () {
      // Loading bubbles are assistant messages and should disappear first.
      final messages = [
        Message(text: 'Ich habe Bauchschmerzen', isUser: true),
        Message(text: '', isUser: false, isLoading: true),
      ];

      final result = chatService.removeLastBotMessage(messages);

      expect(result, hasLength(1));
      expect(result.first.isUser, true);
    });
  });
}
