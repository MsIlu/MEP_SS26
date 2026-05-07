import 'package:flutter/material.dart';
import '../data/models/message_model.dart';

class ChatService {
  void addMessage({
    required ValueNotifier<List<Message>> messages,
    required Message message,
  }) {
    final updated = List<Message>.from(messages.value);

    updated.add(message);

    messages.value = updated;
  }

  void removeLastBotMessage(
      ValueNotifier<List<Message>> messages,
      ) {
    final updated = List<Message>.from(messages.value);

    for (int i = updated.length - 1; i >= 0; i--) {
      if (!updated[i].isUser) {
        updated.removeAt(i);
        break;
      }
    }

    messages.value = updated;
  }

  Future<void> streamResponse({
    required ValueNotifier<List<Message>> messages,
    required String fullText,
  }) async {
    removeLastBotMessage(messages);

    final message = Message(
      text: "",
      isUser: false,
    );

    final updated =
    List<Message>.from(messages.value)..add(message);

    messages.value = updated;

    String current = "";

    for (final char in fullText.split('')) {
      await Future.delayed(
        const Duration(milliseconds: 15),
      );

      current += char;

      final list = List<Message>.from(messages.value);

      list[list.length - 1] =
          message.copyWith(text: current);

      messages.value = list;
    }
  }
}