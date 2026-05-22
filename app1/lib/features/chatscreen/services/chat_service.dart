import '../data/models/message_model.dart';

/// Handles chat-domain message operations without depending on Flutter UI state.
///
/// Keeping these transformations outside the controller makes message-list
/// updates easier to test and prevents widgets from mutating shared lists.
class ChatService {
  static const Duration defaultTypingDelay = Duration(milliseconds: 15);

  List<Message> addMessage({
    required List<Message> messages,
    required Message message,
  }) {
    return List<Message>.from(messages)..add(message);
  }

  List<Message> removeLastBotMessage(List<Message> messages) {
    final updated = List<Message>.from(messages);

    for (int i = updated.length - 1; i >= 0; i--) {
      if (!updated[i].isUser) {
        updated.removeAt(i);
        break;
      }
    }

    return updated;
  }

  List<Message> replaceLastMessage({
    required List<Message> messages,
    required Message message,
  }) {
    if (messages.isEmpty) {
      return [message];
    }

    final updated = List<Message>.from(messages);
    updated[updated.length - 1] = message;
    return updated;
  }

  Stream<String> streamText(
    String fullText, {
    Duration delay = defaultTypingDelay,
  }) async* {
    var current = '';

    for (final char in fullText.split('')) {
      await Future.delayed(delay);
      current += char;
      yield current;
    }
  }
}
