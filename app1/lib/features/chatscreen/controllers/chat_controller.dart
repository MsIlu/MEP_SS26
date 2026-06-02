import 'package:flutter/material.dart';
import '../../../core/config/app_config.dart';
import '../data/chat_api.dart';
import '../data/models/chat_response_model.dart';
import '../data/models/message_model.dart';
import '../services/chat_service.dart';

/// Coordinates chat state, backend sessions, and message-list updates.
class ChatController {
  /// API adapter used for backend session and chat requests.
  final ChatApi chatApi;

  /// Pure message helper used to keep list transformations testable.
  final ChatService chatService;

  ChatController({required this.chatApi, required this.chatService});

  final ValueNotifier<List<Message>> messages = ValueNotifier<List<Message>>(
    [],
  );

  // The backend expects all messages after session creation to include the same
  // session ID, so it is cached once createSession succeeds.
  String? _sessionId;
  Future<void>? _initFuture;

  /// Initializes the welcome message and backend session exactly once.
  Future<void> init() async {
    _initFuture ??= _initialize();
    await _initFuture;
  }

  /// Adds the first assistant message and prepares the backend session.
  Future<void> _initialize() async {
    if (messages.value.isEmpty) {
      _addMessage(
        message: Message(text: AppConfig.welcomeMessage, isUser: false),
      );
    }

    await _ensureSession(showOfflineMessage: true);
  }

  /// Ensures a usable backend session exists before sending real messages.
  Future<bool> _ensureSession({bool showOfflineMessage = false}) async {
    if (_sessionId != null) return true;

    try {
      _sessionId = await chatApi.createSession();
      await chatApi.warmup();
      return true;
    } catch (_) {
      if (showOfflineMessage && !_hasOfflineMessage()) {
        _addMessage(
          message: Message(
            text:
                'Der Chat ist gerade offline. Bitte prüfen Sie die Backend-Verbindung und versuchen Sie es erneut.',
            isUser: false,
          ),
        );
      }

      _initFuture = null;
      return false;
    }
  }

  /// Sends a user message and returns the full backend response.
  ///
  /// Normal responses are added to the chat.
  /// Red flag responses are returned without being displayed as a chat bubble,
  /// so the UI can open the warning page instead.
  Future<ChatResponse?> sendMessage(String text) async {
    if (_initFuture != null) {
      await _initFuture;
    }

    final hasSession = await _ensureSession();

    if (!hasSession || _sessionId == null) {
      throw Exception("Chat session not initialized.");
    }

    final trimmed = text.trim();
    if (trimmed.isEmpty) return null;

    // Add both the user's message and a loading assistant bubble before the
    // request so the UI reflects the pending state immediately.
    _addMessage(message: Message(text: trimmed, isUser: true));
    _addMessage(message: Message(text: '', isUser: false, isLoading: true, isStreaming: true,));

    try {
      final response = await chatApi.sendMessage(trimmed, _sessionId!);

      // Remove the loading bubble before handling the response.
      _setMessages(chatService.removeLastBotMessage(messages.value));

      // Red flag responses should not be shown as normal chat messages.
      if (response.redFlag) {
        return response;
      }

      final responseText = response.text.toLowerCase();

      final hasRecommendation =
          (response.action != null && response.action!.trim().isNotEmpty) ||
              responseText.contains('dringlichkeit:') ||
              responseText.contains('empfohlene versorgungsebene:') ||
              responseText.contains('nächster schritt:') ||
              responseText.contains('hinweis:');

      final botMessage = Message(
        text: response.text,
        isUser: false,
        canExportPdf: hasRecommendation,
        exportTitle: 'Handlungsempfehlung',
        exportRecommendation: response.text,
        exportNextSteps: response.action,
      );

      // Insert an empty assistant bubble first. The stream below gradually
      // replaces it with longer partial text values.
      _addMessage(message: botMessage.copyWith(text: ''));

      // Stream the bot response character by character for the typing effect.
      await for (final partialText in chatService.streamText(response.text)) {
        _setMessages(
          chatService.replaceLastMessage(
            messages: messages.value,
            message: botMessage.copyWith(text: partialText, isStreaming: true,),
          ),
        );
      }

      _setMessages(
        chatService.replaceLastMessage(
          messages: messages.value, 
          message: botMessage.copyWith(isStreaming: false),)
      );

      return response;
    } catch (e) {
      _setMessages(chatService.removeLastBotMessage(messages.value));
      _addMessage(message: Message(text: 'Fehler: $e', isUser: false));
      return null;
    }
  }

  /// Applies a single-message append through the service helper.
  void _addMessage({required Message message}) {
    _setMessages(
      chatService.addMessage(messages: messages.value, message: message),
    );
  }

  /// Publishes a new immutable list instance to all listeners.
  void _setMessages(List<Message> updatedMessages) {
    messages.value = updatedMessages;
  }

  /// Prevents the offline explanation from being appended repeatedly.
  bool _hasOfflineMessage() {
    return messages.value.any(
      (message) => message.text.startsWith('Der Chat ist gerade offline.'),
    );
  }

  void dispose() {
    messages.dispose();
  }
}