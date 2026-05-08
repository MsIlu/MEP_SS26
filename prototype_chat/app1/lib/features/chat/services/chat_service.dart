import 'package:flutter/material.dart';
import '../data/models/message_model.dart';

/// Service class responsible for handling
/// chat message operations and streaming responses.
class ChatService {

  /// Adds a new message to the chat list.
  ///
  /// Creates a copy of the current message list,
  /// appends the new message, and updates the notifier.
  void addMessage({
    required ValueNotifier<List<Message>> messages,
    required Message message,
  }) {
    // Create a mutable copy of the current messages
    final updated = List<Message>.from(messages.value);

    // Add the new message
    updated.add(message);

    // Update listeners
    messages.value = updated;
  }

  /// Removes the most recent bot message from the chat.
  ///
  /// Iterates backwards through the message list
  /// and removes the first non-user message found.
  void removeLastBotMessage(
      ValueNotifier<List<Message>> messages,
      ) {
    // Create a mutable copy of the current messages
    final updated = List<Message>.from(messages.value);

    // Search from the end of the list
    for (int i = updated.length - 1; i >= 0; i--) {
      // Remove the latest bot message
      if (!updated[i].isUser) {
        updated.removeAt(i);
        break;
      }
    }

    // Update listeners
    messages.value = updated;
  }

  /// Simulates a streamed bot response with typing animation.
  ///
  /// The response text is revealed character by character
  /// to imitate a live AI-generated message.
  Future<void> streamResponse({
    required ValueNotifier<List<Message>> messages,
    required String fullText,
  }) async {
    // Remove previous temporary bot message if needed
    removeLastBotMessage(messages);

    // Create an empty bot message
    final message = Message(
      text: "",
      isUser: false,
    );

    // Add the empty message to the list
    final updated =
    List<Message>.from(messages.value)..add(message);

    messages.value = updated;

    // Stores the progressively built response
    String current = "";

    // Loop through every character
    for (final char in fullText.split('')) {
      // Simulate typing delay
      await Future.delayed(
        const Duration(milliseconds: 15),
      );

      // Append next character
      current += char;

      // Create updated message list
      final list = List<Message>.from(messages.value);

      // Replace the last message with updated text
      list[list.length - 1] =
          message.copyWith(text: current);

      // Notify listeners
      messages.value = list;
    }
  }
}