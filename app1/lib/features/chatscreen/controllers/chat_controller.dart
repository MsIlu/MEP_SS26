import 'dart:async';

import 'package:flutter/material.dart';
import '../../../core/config/app_config.dart';
import '../data/chat_api.dart';
import '../data/chat_history_repository.dart';
import '../data/models/chat_history_entry.dart';
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
  final ChatHistoryRepository chatHistoryRepository;
  final AuthSession authSession;
  int? _activeProfileId;
  bool _isCompleted = false;
  String? _activeHistoryEntryId;
  DateTime? _activeHistoryCreatedAt;

  ChatController({
    required this.chatApi,
    required this.chatService,
    required this.authSession,
    required this.chatHistoryRepository,
    ChatSessionService? chatSessionService,
    SymptomDraftService? symptomDraftService,
  }) : chatSessionService = chatSessionService ?? ChatSessionService(chatApi),
       symptomDraftService =
           symptomDraftService ?? SymptomDraftService(chatApi) {
    _activeProfileId = authSession.activeProfileId;
    authSession.addListener(_handleAuthSessionChanged);
  }

  final ValueNotifier<List<Message>> messages = ValueNotifier<List<Message>>(
    [],
  );

  final ValueNotifier<List<String>> symptoms = ValueNotifier<List<String>>([]);
  final ValueNotifier<bool> isCompleted = ValueNotifier<bool>(false);

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
      await chatSessionService.ensureSession(
        profileId: authSession.activeProfileId,
      );
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
    final trimmed = text.trim();
    if (trimmed.isEmpty) return null;

    if (trimmed.toLowerCase() == '/hp') {
      _addTestRecommendation();
      return null;
    }

    if (_isCompleted) {
      return null;
    }

    if (_initFuture != null) {
      await _initFuture;
    }

    final hasSession = await _ensureSession();
    final sessionId = chatSessionService.sessionId;

    if (!hasSession || sessionId == null) {
      throw Exception("Chat session not initialized.");
    }

    _addMessage(message: Message(text: trimmed, isUser: true));
    await _persistActiveChat();

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
        final botMessage = chatService.buildAssistantMessage(response);
        _addMessage(message: botMessage);
        await _persistActiveChat();
        await _completeChat(
          recommendation: response.text,
          nextSteps: response.action,
          isEmergency: chatService.isEmergencyRecommendation(response),
        );
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

      await _persistActiveChat();

      final isEmergency = chatService.isEmergencyRecommendation(response);

      if (chatService.isFinalRecommendation(response) || isEmergency) {
        await _completeChat(
          recommendation:
              response.recommendationResult?.summary ?? response.text,
          nextSteps: response.recommendationResult?.nextStep ?? response.action,
          isEmergency: isEmergency,
        );
      }

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

  Future<void> resumeHistoryEntry(ChatHistoryEntry entry) async {
    _activeHistoryEntryId = entry.id;
    _activeHistoryCreatedAt = entry.createdAt;
    _setCompleted(entry.status == 'completed');
    messages.value = entry.messages;

    if (entry.status == 'active') {
      await chatSessionService.resumeHistorySession(
        historyId: entry.id,
        profileId: entry.profileId,
      );
      _initFuture = Future.value();

      if (_waitsForAssistantResponse(entry)) {
        await _continuePendingAssistantResponse();
      }
    }
  }

  Future<void> _continuePendingAssistantResponse() async {
    final historyEntryId = _activeHistoryEntryId;

    if (historyEntryId == null || _isCompleted) {
      return;
    }

    _addMessage(
      message: Message(
        text: '',
        isUser: false,
        isLoading: true,
        isStreaming: true,
      ),
    );

    try {
      final response = await chatSessionService.continueHistorySession(
        historyId: historyEntryId,
      );

      _setMessages(chatService.removeLastBotMessage(messages.value));
      await loadSymptoms();

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

      await _persistActiveChat();

      final isEmergency = chatService.isEmergencyRecommendation(response);

      if (chatService.isFinalRecommendation(response) || isEmergency) {
        await _completeChat(
          recommendation:
              response.recommendationResult?.summary ?? response.text,
          nextSteps: response.recommendationResult?.nextStep ?? response.action,
          isEmergency: isEmergency,
        );
      }
    } catch (e) {
      _setMessages(chatService.removeLastBotMessage(messages.value));
      _addMessage(message: Message(text: 'Fehler: $e', isUser: false));
    }
  }

  bool _waitsForAssistantResponse(ChatHistoryEntry entry) {
    if (entry.messages.isEmpty) {
      return false;
    }

    final lastMessage = entry.messages.last;
    return lastMessage.isUser && lastMessage.text.trim().isNotEmpty;
  }

  Future<void> resetChat() async {
    await _clearCurrentSession();
  }

  Future<void> _clearCurrentSession() async {
    final sessionId = chatSessionService.clearSession();

    messages.value = [];
    symptoms.value = [];
    _activeHistoryEntryId = null;
    _activeHistoryCreatedAt = null;
    _setCompleted(false);
    _initFuture = null;

    await symptomDraftService.cancelDraft(sessionId);
  }

  void _handleAuthSessionChanged() {
    final nextProfileId = authSession.activeProfileId;

    if (nextProfileId == _activeProfileId) {
      return;
    }

    _activeProfileId = nextProfileId;
    unawaited(_resetAfterProfileChange());
  }

  Future<void> _resetAfterProfileChange() async {
    final wasInitialized = _initFuture != null || messages.value.isNotEmpty;

    await _clearCurrentSession();

    if (wasInitialized) {
      await init();
    }
  }

  void _addMessage({required Message message}) {
    _setMessages(
      chatService.addMessage(messages: messages.value, message: message),
    );
  }

  void _setMessages(List<Message> updatedMessages) {
    messages.value = updatedMessages;
  }

  Future<void> _completeChat({
    required String recommendation,
    String? nextSteps,
    bool isEmergency = false,
  }) async {
    if (_isCompleted) {
      return;
    }

    final activeProfileId = authSession.activeProfileId;

    if (activeProfileId != null) {
      await _persistChatHistory(
        status: 'completed',
        recommendation: recommendation,
        nextSteps: nextSteps,
        isEmergency: isEmergency,
      );
    }

    _setCompleted(true);
  }

  Future<void> _persistActiveChat() async {
    if (_isCompleted) {
      return;
    }

    if (authSession.activeProfileId == null) {
      return;
    }

    final hasUserMessage = messages.value.any(
      (message) => message.isUser && message.text.trim().isNotEmpty,
    );

    if (!hasUserMessage) {
      return;
    }

    await _persistChatHistory(status: 'active');
  }

  Future<void> _persistChatHistory({
    required String status,
    String recommendation = '',
    String? nextSteps,
    bool isEmergency = false,
  }) async {
    final activeProfileId = authSession.activeProfileId;

    if (activeProfileId == null) {
      return;
    }

    final now = DateTime.now();
    final createdAt = _activeHistoryCreatedAt ?? now;

    final entry = ChatHistoryEntry(
      id: _activeHistoryEntryId ?? now.microsecondsSinceEpoch.toString(),
      profileId: activeProfileId,
      sessionId: chatSessionService.sessionId,
      symptomTitle: _historyTitleFromSymptoms(),
      status: status,
      isEmergency: isEmergency,
      createdAt: createdAt,
      updatedAt: now,
      messages: messages.value,
      recommendation: recommendation,
      nextSteps: nextSteps,
    );

    final savedEntry = _activeHistoryEntryId == null
        ? await chatHistoryRepository.saveChat(entry)
        : await chatHistoryRepository.updateChat(entry);

    _activeHistoryEntryId = savedEntry.id;
    _activeHistoryCreatedAt = savedEntry.createdAt;
  }

  void _setCompleted(bool value) {
    _isCompleted = value;
    isCompleted.value = value;
  }

  String? _historyTitleFromSymptoms() {
    for (final symptom in symptoms.value) {
      final normalizedSymptom = symptom.trim();
      if (normalizedSymptom.isNotEmpty) {
        return normalizedSymptom;
      }
    }

    return null;
  }

  void _addTestRecommendation() {
    const recommendationText = '''Dringlichkeit: Nicht akut
    Empfohlene Versorgungsebene: Hausarzt
    Nächster Schritt: Bitte vereinbaren Sie einen Termin beim Hausarzt, wenn die Beschwerden anhalten oder sich verschlechtern.
    Hinweis: Diese Test-Handlungsempfehlung dient nur der Frontend-Entwicklung und ersetzt keine ärztliche Diagnose.''';

    _addMessage(message: Message(text: '/hp', isUser: true));
    _addMessage(
      message: Message(
        text: recommendationText,
        isUser: false,
        canExportPdf: true,
        exportTitle: 'Handlungsempfehlung',
        exportRecommendation: recommendationText,
        exportNextSteps: 'Termin beim Hausarzt vereinbaren.',
        canCreateAppointment: true,
        appointmentTitle: 'Hausarzttermin vereinbaren',
      ),
    );
  }

  bool _hasOfflineMessage() {
    return messages.value.any(
      (message) => message.text.startsWith('Der Chat ist gerade offline.'),
    );
  }

  void dispose() {
    authSession.removeListener(_handleAuthSessionChanged);
    messages.dispose();
    symptoms.dispose();
    isCompleted.dispose();
  }
}
