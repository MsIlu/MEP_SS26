import 'package:flutter/material.dart';
import '../../../core/config/app_config.dart';
import '../data/chat_api.dart';
import '../data/models/chat_response_model.dart';
import '../data/models/message_model.dart';
import '../services/chat_service.dart';
import '../services/chat_session_service.dart';
import '../services/symptom_draft_service.dart';
import '../../authscreen/state/auth_session.dart';

class ChatController {
  final ChatApi chatApi;
  final ChatService chatService;
  final ChatSessionService chatSessionService;
  final SymptomDraftService symptomDraftService;
  final AuthSession authSession;

  ChatController({
    required this.chatApi,
    required this.chatService,
    required this.authSession,
    ChatSessionService? chatSessionService,
    SymptomDraftService? symptomDraftService,
  }) : chatSessionService = chatSessionService ?? ChatSessionService(chatApi),
       symptomDraftService =
           symptomDraftService ?? SymptomDraftService(chatApi);

  final ValueNotifier<List<Message>> messages = ValueNotifier<List<Message>>(
    [],
  );

  final ValueNotifier<List<String>> symptoms = ValueNotifier<List<String>>([]);

  Future<void>? _initFuture;

  Future<void> init() async {
    _initFuture ??= _initialize();
    await _initFuture;
  }

  Future<void> _initialize() async {
    if (messages.value.isEmpty) {
      _addMessage(
        message: Message(text: AppConfig.welcomeMessage, isUser: false),
      );
    }

    final hasSession = await _ensureSession(showOfflineMessage: true);

    if (hasSession) {
      await loadSymptoms();
    }
  }

  Future<bool> _ensureSession({bool showOfflineMessage = false}) async {
    try {
      await chatSessionService.ensureSession();
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

  Future<ChatResponse?> sendMessage(String text) async {
    if (_initFuture != null) {
      await _initFuture;
    }

    final hasSession = await _ensureSession();
    final sessionId = chatSessionService.sessionId;

    if (!hasSession || sessionId == null) {
      throw Exception("Chat session not initialized.");
    }

    final trimmed = text.trim();
    if (trimmed.isEmpty) return null;

    _addMessage(message: Message(text: trimmed, isUser: true));
    _addMessage(
      message: Message(
        text: '',
        isUser: false,
        isLoading: true,
        isStreaming: true,
      ),
    );

    try {
      final response = await chatApi.sendMessage(
        trimmed,
        sessionId,
        authSession.activeProfileId,
      );

      _setMessages(chatService.removeLastBotMessage(messages.value));
      await loadSymptoms();

      if (response.redFlag) {
        return response;
      }

      final botMessage = chatService.buildAssistantMessage(response);
      _addMessage(message: botMessage.copyWith(text: ''));

      await for (final partialText in chatService.streamText(response.text)) {
        _setMessages(
          chatService.replaceLastMessage(
            messages: messages.value,
            message: botMessage.copyWith(text: partialText, isStreaming: true),
          ),
        );
      }

      _setMessages(
        chatService.replaceLastMessage(
          messages: messages.value,
          message: botMessage.copyWith(isStreaming: false),
        ),
      );

      return response;
    } catch (e) {
      _setMessages(chatService.removeLastBotMessage(messages.value));
      _addMessage(message: Message(text: 'Fehler: $e', isUser: false));
      return null;
    }
  }

  Future<void> loadSymptoms() async {
    symptoms.value = await symptomDraftService.loadSymptoms(
      chatSessionService.sessionId,
    );
  }

  Future<void> updateSymptomsDirectly(List<String> updatedSymptoms) async {
    symptoms.value = await symptomDraftService.updateSymptoms(
      chatSessionService.sessionId,
      updatedSymptoms,
    );
  }

  Future<void> resetChat() async {
    final sessionId = chatSessionService.clearSession();

    messages.value = [];
    symptoms.value = [];
    _initFuture = null;

    await symptomDraftService.cancelDraft(sessionId);
  }

  void _addMessage({required Message message}) {
    _setMessages(
      chatService.addMessage(messages: messages.value, message: message),
    );
  }

  void _setMessages(List<Message> updatedMessages) {
    messages.value = updatedMessages;
  }

  bool _hasOfflineMessage() {
    return messages.value.any(
      (message) => message.text.startsWith('Der Chat ist gerade offline.'),
    );
  }

  void dispose() {
    messages.dispose();
    symptoms.dispose();
  }
}
