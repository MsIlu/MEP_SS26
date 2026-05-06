import 'package:app1/core/config/app_config.dart';
import 'package:app1/features/chat/data/chat_api.dart';
import 'package:flutter/material.dart';
import '../data/models/message_model.dart';


/// Controls all chat-related logic.
///
/// Responsibilities:
/// - Managing chat session lifecycle
/// - Handling message state
/// - Communicating with backend API
/// - Streaming bot responses
class ChatController {
  final ChatApi chatApi;

  ChatController(this.chatApi);

  final ValueNotifier<List<Message>> messages =
  ValueNotifier<List<Message>>([]);

  String? _sessionId;

  Future<void> init() async {
    messages.value = [];
    _sessionId = null;

    _addMessage(
      Message(
        text: AppConfig.welcomeMessage,
        isUser: false,
      ),
    );

    _sessionId = await chatApi.createSession();
    await chatApi.warmup();
  }

  /// send message
  Future<void> sendMessage(String text) async {
    if (_sessionId == null) {
      throw Exception("Chat session wurde nicht initialisiert.");
    }

    final trimmedText = text.trim();
    if (trimmedText.isEmpty) return;

    // User Message
    _addMessage(
      Message(text: trimmedText, isUser: true),
    );

    //  Thinking Bubble
    _addMessage(
      Message(
        text: "",
        isUser: false,
        isLoading: true,
      ),
    );

    try {
      final reply =
      await chatApi.sendMessage(trimmedText, _sessionId!);

      await _streamResponse(reply);
    } catch (e) {
      _removeLastBotMessage();

      _addMessage(
        Message(
          text: "Fehler: $e",
          isUser: false,
        ),
      );
    }
  }

  Future<void> _streamResponse(String fullText) async {
    _removeLastBotMessage();

    // Add empty bot message
    final message = Message(
      text: "",
      isUser: false,
    );

    final updated = List<Message>.from(messages.value)..add(message);
    messages.value = updated;

    String current = "";

    for (final char in fullText.split('')) {
      await Future.delayed(const Duration(milliseconds: 15));

      current += char;

      // Update last message
      final list = List<Message>.from(messages.value);
      list[list.length - 1] = message.copyWith(text: current);

      messages.value = list;
    }
  }

  ///  Remove last bot message (loading)
  void _removeLastBotMessage() {
    final updated = List<Message>.from(messages.value);

    for (int i = updated.length - 1; i >= 0; i--) {
      if (!updated[i].isUser) {
        updated.removeAt(i);
        break;
      }
    }

    messages.value = updated;
  }

  ///  Add message helper
  void _addMessage(Message message) {
    final updated = List<Message>.from(messages.value);
    updated.add(message);
    messages.value = updated;
  }
}