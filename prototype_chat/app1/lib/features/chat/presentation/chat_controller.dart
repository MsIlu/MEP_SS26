import 'package:app1/core/config/app_config.dart';
import 'package:app1/features/chat/data/chat_api.dart';
import 'package:flutter/material.dart';
import '../data/models/message_model.dart';

/// Controls all chat-related business logic.
///
/// This controller is responsible for:
/// - Managing chat session life cycle
/// - Maintaining message state
/// - Communicating with the backend API
/// - Handling simulated streaming responses
class ChatController {
  final ChatApi chatApi;

  ChatController(this.chatApi);

  /// Reactive message list used by the UI.
  final ValueNotifier<List<Message>> messages =
  ValueNotifier<List<Message>>([]);

  /// Active chat session identifier.
  String? _sessionId;

  /// Initializes the chat session and loads the welcome message.
  ///
  /// This method:
  /// - Clears previous messages
  /// - Adds the welcome message
  /// - Creates a new backend session
  /// - Triggers backend warmup
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

  /// Sends a user message and handles the full response flow.
  ///
  /// Steps:
  /// 1. Adds user message to the chat
  /// 2. Displays a loading (thinking) message
  /// 3. Requests response from backend
  /// 4. Streams the response into the UI
  Future<void> sendMessage(String text) async {
    if (_sessionId == null) {
      throw Exception("Chat session has not been initialized.");
    }

    final trimmedText = text.trim();
    if (trimmedText.isEmpty) return;

    /// Add user message to the chat
    _addMessage(
      Message(text: trimmedText, isUser: true),
    );

    /// Add loading indicator (thinking bubble)
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
          text: "Error: $e",
          isUser: false,
        ),
      );
    }
  }

  /// Simulates a streaming response by revealing text character by character.
  ///
  /// This creates a natural "typing" effect in the UI.
  Future<void> _streamResponse(String fullText) async {
    _removeLastBotMessage();

    /// Create an empty bot message that will be updated progressively
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

      /// Update the last message with the streamed content
      final list = List<Message>.from(messages.value);
      list[list.length - 1] = message.copyWith(text: current);

      messages.value = list;
    }
  }

  /// Removes the last bot message (typically the loading indicator).
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

  /// Adds a message to the chat history.
  void _addMessage(Message message) {
    final updated = List<Message>.from(messages.value);
    updated.add(message);
    messages.value = updated;
  }
}