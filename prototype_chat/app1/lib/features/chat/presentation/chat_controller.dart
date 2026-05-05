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
  final messages = ValueNotifier<List<Message>>([]);

  String? _sessionId;

  /// Initializes the chat session and loads the welcome message.
  Future<void> init() async {
    _sessionId = await chatApi.createSession();
    chatApi.warmup();
    _addWelcomeMessage();
  }

  /// Sends a message to the backend and updates the chat state.
  Future<void> sendMessage(String text) async {
  assert(_sessionId != null);

  if (_sessionId == null) {
    throw Exception("Chat session wurde nicht initialisiert.");
  }

  final trimmedText = text.trim();
  if (trimmedText.isEmpty) return;

  // Add user message
  final updatedMessages = [...messages.value];
  updatedMessages.add(Message(text: trimmedText, isUser: true));
  messages.value = updatedMessages;

  try {
    final reply = await chatApi.sendMessage(trimmedText, _sessionId!);

    // Add bot response
    messages.value = [
        ...messages.value,
        Message(text: reply, isUser: false),
      ];
  } catch (e) {
    // Add error message to chat
    messages.value = [
        ...messages.value,
        Message(text: "Fehler: $e", isUser: false),
      ];
    }
  }

  /// Adds the initial welcome message to the chat.
  void _addWelcomeMessage() {
    messages.value = [
        Message(
          text: AppConfig.welcomeMessage,
          isUser: false,
        ),
    ];
  }

}