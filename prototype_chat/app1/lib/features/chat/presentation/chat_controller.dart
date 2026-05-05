import 'package:app1/core/config/app_config.dart';
import 'package:app1/features/chat/data/chat_api.dart';
import 'package:flutter/material.dart';
import '../data/models/message_model.dart';

/// Central state management for the chat feature.
///
/// Responsible for:
/// - Managing message state
/// - Handling API communication
/// - Maintaining session lifecycle
/// - Updating UI via ValueNotifier
///
/// DEV NOTE:
/// ValueNotifier is used for simplicity.
/// 
/// ***Don't touch*** if you're not sure about it
/// as it can lead to duplicated state logic in larger apps.
class ChatController {
  final ChatApi chatApi;

  ChatController(this.chatApi);

  /// Holds the current list of chat messages.
  final ValueNotifier<List<Message>> messages =
  ValueNotifier<List<Message>>([]);

  String? _sessionId;

  /// Initializes the chat session and loads the welcome message.
  Future<void> init() async {
    messages.value = [];
    _sessionId = null;

    _sessionId = await chatApi.createSession();
    await chatApi.warmup();

    _addMessage(
      Message(
        text: AppConfig.welcomeMessage,
        isUser: false,
      ),
    );
  }

  /// Sends a message to the backend and updates the chat state.
  Future<void> sendMessage(String text) async {
  if (_sessionId == null) {
    throw Exception("Chat session wurde nicht initialisiert.");
  }

  final trimmedText = text.trim();
  if (trimmedText.isEmpty) return;

  // Add user message
  _addMessage(Message(text: trimmedText, isUser:true));

  _addMessage(
    Message(text: "Ich denke nach...", isUser: false),
  );

  try {
    final reply = await chatApi.sendMessage(trimmedText, _sessionId!);
  _removeLastBotMessage();
    // Add bot response
    _addMessage(Message(text: reply, isUser: false));
  } catch (e) {
    // Add error message to chat
    _addMessage(
        Message(
            text: "Fehler: $e",
            isUser: false,
        ),
    );
  }
  }

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

  /// Adds the initial welcome message to the chat.
  void _addMessage(Message message) {
    final updated = List<Message>.from(messages.value);
    updated.add(message);
    messages.value = updated;
  }
}