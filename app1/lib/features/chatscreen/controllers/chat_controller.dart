import 'dart:async';

import 'package:flutter/material.dart';
import '../../../core/network/api_exception.dart';
import '../../../core/config/app_config.dart';
import '../../authscreen/state/auth_session.dart';
import '../data/chat_api.dart';
import '../data/chat_history_repository.dart';
import '../data/models/careena_availability.dart';
import '../data/models/chat_history_entry.dart';
import '../data/models/chat_response_model.dart';
import '../data/models/chat_run_state.dart';
import '../data/models/message_model.dart';
import '../services/chat_service.dart';
import '../services/chat_session_service.dart';
import '../services/symptom_draft_service.dart';

class ChatController {
  static const recommendationRequestDisplayText =
      'Ich möchte jetzt eine Handlungsempfehlung.';

  final ChatApi chatApi;
  final ChatService chatService;
  final ChatSessionService chatSessionService;
  final SymptomDraftService symptomDraftService;
  final ChatHistoryRepository chatHistoryRepository;
  final AuthSession authSession;
  int? _activeProfileId;
  bool _isCompleted = false;
  final Map<String, ChatRunState> _chatRunStates = {};
  final Map<String, Future<void>> _resumeOperations = {};
  final Map<String, Future<void>> _continueOperations = {};
  final Set<String> _openingHistoryEntries = {};
  String? _activeHistoryEntryId;
  DateTime? _activeHistoryCreatedAt;
  int _profileChangeGeneration = 0;
  Timer? _availabilityRetryTimer;
  Future<void>? _availabilityRefreshFuture;
  bool _isDisposed = false;
  static const Duration _availabilityRetryDelay = Duration(seconds: 5);
  static const Duration _availabilityOnlineRecheckDelay = Duration(seconds: 10);

  String? get currentSessionId => chatSessionService.sessionId;

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

  /// Structured reply options from the last backend response.
  /// Non-empty only when the backend expects a structured answer (ask_safety_question).
  /// Cleared when the user sends the next message.
  final ValueNotifier<List<String>> lastReplyOptions =
      ValueNotifier<List<String>>([]);
  final ValueNotifier<bool> isCompleted = ValueNotifier<bool>(false);
  final ValueNotifier<int> historyRevision = ValueNotifier<int>(0);
  final ValueNotifier<Set<String>> continuingHistoryIds =
      ValueNotifier<Set<String>>(<String>{});

  bool get isActiveChatContinuing {
    final historyEntryId = _activeHistoryEntryId;
    return historyEntryId != null &&
        continuingHistoryIds.value.contains(historyEntryId);
  }

  bool tryBeginOpeningHistory(String historyEntryId) {
    return _openingHistoryEntries.add(historyEntryId);
  }

  void finishOpeningHistory(String historyEntryId) {
    _openingHistoryEntries.remove(historyEntryId);
  }

  final ValueNotifier<CareenaAvailability> availability =
      ValueNotifier<CareenaAvailability>(CareenaAvailability.checking);

  Future<void>? _initFuture;

  Future<void> init() async {
    final wasAlreadyInitialized = _initFuture != null;
    _initFuture ??= _initialize();
    await _initFuture;

    if (wasAlreadyInitialized) {
      await refreshAvailability(refreshLlmStatus: true);
    }
  }

  Future<void> _initialize() async {
    if (messages.value.isEmpty) {
      _addMessage(
        message: Message(text: AppConfig.welcomeMessage, isUser: false),
      );
    }

    final hasSession = await _ensureSession(showOfflineMessage: true);
    await refreshAvailability();

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
                'Der Chat ist gerade offline. Bitte prüfe die Backend-Verbindung und versuche es erneut.',
            isUser: false,
          ),
        );
      }

      _initFuture = null;
      return false;
    }
  }

  Future<void> refreshAvailability({
    bool showChecking = true,
    bool refreshLlmStatus = false,
  }) async {
    if (_isDisposed) {
      return;
    }

    final currentRefresh = _availabilityRefreshFuture;
    if (currentRefresh != null) {
      await currentRefresh;
      if (_isDisposed) {
        return;
      }
      if (!refreshLlmStatus) {
        return;
      }
    }

    final refreshFuture = _refreshAvailability(
      showChecking: showChecking,
      refreshLlmStatus: refreshLlmStatus,
    );
    _availabilityRefreshFuture = refreshFuture;

    try {
      await refreshFuture;
    } finally {
      if (identical(_availabilityRefreshFuture, refreshFuture)) {
        _availabilityRefreshFuture = null;
      }
    }
  }

  Future<void> _refreshAvailability({
    required bool showChecking,
    required bool refreshLlmStatus,
  }) async {
    _availabilityRetryTimer?.cancel();
    _availabilityRetryTimer = null;

    if (showChecking) {
      if (_isDisposed) {
        return;
      }
      availability.value = CareenaAvailability.checking;
    }

    if (refreshLlmStatus) {
      await chatApi.warmup();
      if (_isDisposed) {
        return;
      }
    }

    final nextAvailability = await chatApi.getCareenaAvailability();
    if (_isDisposed) {
      return;
    }
    availability.value = nextAvailability;

    final nextDelay =
        nextAvailability.status == CareenaAvailabilityStatus.online
        ? _availabilityOnlineRecheckDelay
        : _availabilityRetryDelay;
    _availabilityRetryTimer = Timer(nextDelay, () {
      unawaited(refreshAvailability(showChecking: false));
    });
  }

  Future<ChatResponse?> sendMessage(String text) async {
    return _sendMessage(text);
  }

  Future<ChatResponse?> requestRecommendation() async {
    return _sendSessionRequest(
      visibleUserText: recommendationRequestDisplayText,
      request: (sessionId) => chatApi.requestRecommendation(sessionId),
    );
  }

  Future<ChatResponse?> _sendMessage(
    String text, {
    String? visibleUserText,
  }) async {
    final trimmed = text.trim();
    if (trimmed.isEmpty) return null;

    if (trimmed.toLowerCase() == '/hp') {
      _addTestRecommendation();
      return null;
    }

    return _sendSessionRequest(
      visibleUserText: visibleUserText?.trim() ?? trimmed,
      request: (sessionId) =>
          chatApi.sendMessage(trimmed, sessionId, authSession.activeProfileId),
    );
  }

  Future<ChatResponse?> _sendSessionRequest({
    required String visibleUserText,
    required Future<ChatResponse> Function(String sessionId) request,
  }) async {
    if (_isCompleted) {
      return null;
    }

    if (_initFuture != null) {
      await _initFuture;
    }

    final expectedProfileId = authSession.activeProfileId;
    final expectedGeneration = _profileChangeGeneration;
    if (availability.value.status != CareenaAvailabilityStatus.online) {
      await refreshAvailability();
    }

    final hasSession = await _ensureSession();
    final sessionId = chatSessionService.sessionId;

    if (!hasSession || sessionId == null) {
      throw Exception("Chat session not initialized.");
    }

    if (expectedGeneration != _profileChangeGeneration ||
        expectedProfileId != authSession.activeProfileId) {
      return null;
    }

    _addMessage(message: Message(text: visibleUserText, isUser: true));

    lastReplyOptions.value = [];

    await _persistActiveChat(status: 'waiting_for_assistant');
    final expectedHistoryEntryId = _activeHistoryEntryId;

    if (!_isChatRequestActive(
      generation: expectedGeneration,
      profileId: expectedProfileId,
      historyEntryId: expectedHistoryEntryId,
      sessionId: sessionId,
    )) {
      return null;
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
      final response = await request(sessionId);

      if (!_isChatRequestActive(
        generation: expectedGeneration,
        profileId: expectedProfileId,
        historyEntryId: expectedHistoryEntryId,
        sessionId: sessionId,
      )) {
        return response;
      }

      _setMessages(chatService.removeLastBotMessage(messages.value));
      final loadedSymptoms = await symptomDraftService.loadSymptoms(sessionId);

      if (!_isChatRequestActive(
        generation: expectedGeneration,
        profileId: expectedProfileId,
        historyEntryId: expectedHistoryEntryId,
        sessionId: sessionId,
      )) {
        return response;
      }
      symptoms.value = loadedSymptoms;

      lastReplyOptions.value = response.replyOptions;

      if (response.redFlag) {
        final botMessage = chatService.buildAssistantMessage(response);
        _addMessage(message: botMessage);
        await _persistActiveChat();
        if (!_isChatRequestActive(
          generation: expectedGeneration,
          profileId: expectedProfileId,
          historyEntryId: expectedHistoryEntryId,
          sessionId: sessionId,
        )) {
          return response;
        }
        await _completeChat(
          recommendation: response.text,
          nextSteps: response.action,
          isEmergency: chatService.isEmergencyRecommendation(response),
        );
        return response;
      }

      final isEmergency = chatService.isEmergencyRecommendation(response);

      if (chatService.isFinalRecommendation(response) || isEmergency) {
        await _completeChat(
          recommendation:
              response.recommendationResult?.summary ?? response.text,
          nextSteps: response.recommendationResult?.nextStep ?? response.action,
          isEmergency: isEmergency,
        );
        return response;
      }

      final botMessage = chatService.buildAssistantMessage(response);
      _addMessage(message: botMessage.copyWith(text: ''));

      await for (final partialText in chatService.streamText(response.text)) {
        if (!_isChatRequestActive(
          generation: expectedGeneration,
          profileId: expectedProfileId,
          historyEntryId: expectedHistoryEntryId,
          sessionId: sessionId,
        )) {
          return response;
        }

        _setMessages(
          chatService.replaceLastMessage(
            messages: messages.value,
            message: botMessage.copyWith(text: partialText, isStreaming: true),
          ),
        );
      }

      if (!_isChatRequestActive(
        generation: expectedGeneration,
        profileId: expectedProfileId,
        historyEntryId: expectedHistoryEntryId,
        sessionId: sessionId,
      )) {
        return response;
      }

      _setMessages(
        chatService.replaceLastMessage(
          messages: messages.value,
          message: botMessage.copyWith(isStreaming: false),
        ),
      );

      await _persistActiveChat(status: 'active');

      return response;
    } catch (e) {
      if (!_isChatRequestActive(
        generation: expectedGeneration,
        profileId: expectedProfileId,
        historyEntryId: expectedHistoryEntryId,
        sessionId: sessionId,
      )) {
        return null;
      }

      await refreshAvailability();

      if (!_isChatRequestActive(
        generation: expectedGeneration,
        profileId: expectedProfileId,
        historyEntryId: expectedHistoryEntryId,
        sessionId: sessionId,
      )) {
        return null;
      }

      _setMessages(chatService.removeLastBotMessage(messages.value));
      _addMessage(
        message: Message(text: userFacingChatError(e), isUser: false),
      );
      await _markActiveChatFailed();
      return null;
    }
  }

  String userFacingChatError(Object error) {
    if (error is ApiException) {
      if (error.type == ApiErrorType.timeout) {
        return 'Careena braucht gerade zu lange für eine Antwort. Bitte versuchen Sie es gleich erneut.';
      }

      if (error.type == ApiErrorType.network) {
        return 'Careena kann den Server gerade nicht erreichen. Bitte prüfen Sie Ihre Verbindung.';
      }

      if (error.statusCode == 401) {
        return 'Ihre Sitzung ist abgelaufen. Bitte melden Sie sich erneut an.';
      }

      if (error.statusCode == 403) {
        return 'Careena kann diese Anfrage für das aktuelle Profil nicht ausführen.';
      }

      if (error.statusCode == 409) {
        final detail = error.message;

        if (detail.contains('different profile')) {
          return 'Dieser Chat gehört zu einem anderen Profil. Bitte wechseln '
              'Sie zum passenden Profil oder starten Sie einen neuen Chat.';
        }

        if (detail.contains('Last user message is empty')) {
          return 'Die letzte Nachricht ist leer und kann nicht verarbeitet '
              'werden. Bitte senden Sie eine neue Nachricht.';
        }

        if (detail.contains('Only active chat history entries') ||
            detail.contains('Only waiting chat history entries') ||
            detail.contains('does not wait for an assistant response')) {
          return 'Der Chat wurde bereits auf einem anderen Gerät oder in '
              'einem anderen Fenster aktualisiert. Bitte öffnen Sie den '
              'Verlauf erneut.';
        }

        return 'Der Chat befindet sich nicht mehr im erwarteten Zustand. '
            'Bitte öffnen Sie den Verlauf erneut.';
      }

      if (error.statusCode != null && error.statusCode! >= 500) {
        return 'Beim Verarbeiten der Anfrage ist auf dem Server ein Fehler '
            'aufgetreten. Bitte versuchen Sie es später erneut.';
      }
    }

    return 'Careena konnte gerade nicht antworten. Bitte versuchen Sie es erneut.';
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

  Future<void> resumeHistoryEntry(
    ChatHistoryEntry entry, {
    bool continuePendingResponse = true,
  }) {
    final existingOperation = _resumeOperations[entry.id];
    if (existingOperation != null) {
      return existingOperation;
    }

    final operation = _resumeHistoryEntry(
      entry,
      continuePendingResponse: continuePendingResponse,
    );
    _resumeOperations[entry.id] = operation;

    return operation.whenComplete(() {
      if (identical(_resumeOperations[entry.id], operation)) {
        _resumeOperations.remove(entry.id);
      }
    });
  }

  Future<void> _resumeHistoryEntry(
    ChatHistoryEntry entry, {
    required bool continuePendingResponse,
  }) async {
    final resumedMessages = _collapseStreamingSnapshots(entry.messages);
    _activeHistoryEntryId = entry.id;
    _activeHistoryCreatedAt = entry.createdAt;
    _setCompleted(entry.status == 'completed');
    messages.value = resumedMessages;
    _setChatRunState(
      ChatRunState(
        historyId: entry.id,
        sessionId: entry.sessionId,
        profileId: entry.profileId,
        messages: resumedMessages,
        status: entry.status,
      ),
    );

    if (_canResumeStatus(entry.status)) {
      await chatSessionService.resumeHistorySession(
        historyId: entry.id,
        profileId: entry.profileId,
      );
      _updateChatRunState(
        entry.id,
        sessionId: chatSessionService.sessionId,
        profileId: entry.profileId,
      );
      _initFuture = Future.value();

      if (continuePendingResponse) {
        await continuePendingAssistantResponseIfNeeded();
      }
    }
  }

  Future<void> continuePendingAssistantResponseIfNeeded() async {
    final historyEntryId = _activeHistoryEntryId;

    if (historyEntryId == null) {
      return;
    }

    final existingOperation = _continueOperations[historyEntryId];
    if (existingOperation != null) {
      await existingOperation;
      return;
    }

    if (!_currentMessagesWaitForAssistantResponse()) {
      return;
    }

    _setHistoryContinuing(historyEntryId, true);
    final operation = _continuePendingAssistantResponse(historyEntryId);
    _continueOperations[historyEntryId] = operation;

    try {
      await operation;
    } finally {
      if (identical(_continueOperations[historyEntryId], operation)) {
        _continueOperations.remove(historyEntryId);
        _setHistoryContinuing(historyEntryId, false);
      }
    }
  }

  void _setHistoryContinuing(String historyEntryId, bool isContinuing) {
    _updateChatRunState(historyEntryId, isContinuing: isContinuing);
    final updatedIds = Set<String>.from(continuingHistoryIds.value);

    if (isContinuing) {
      updatedIds.add(historyEntryId);
    } else {
      updatedIds.remove(historyEntryId);
    }

    continuingHistoryIds.value = updatedIds;
  }

  Future<void> _continuePendingAssistantResponse(String historyEntryId) async {
    final expectedHistoryEntryId = historyEntryId;
    final expectedProfileId = authSession.activeProfileId;
    final expectedGeneration = _profileChangeGeneration;
    final expectedSessionId = chatSessionService.sessionId;

    if (_isCompleted) {
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
      if (!_isChatRequestActive(
        generation: expectedGeneration,
        profileId: expectedProfileId,
        historyEntryId: expectedHistoryEntryId,
        sessionId: expectedSessionId,
      )) {
        _updateChatRunState(
          historyEntryId,
          status: _statusForResponse(response),
          hasUnreadUpdate: true,
        );
        return;
      }

      _setMessages(chatService.removeLastBotMessage(messages.value));
      final loadedSymptoms = await symptomDraftService.loadSymptoms(
        expectedSessionId,
      );

      if (!_isChatRequestActive(
        generation: expectedGeneration,
        profileId: expectedProfileId,
        historyEntryId: expectedHistoryEntryId,
        sessionId: expectedSessionId,
      )) {
        _updateChatRunState(
          historyEntryId,
          status: _statusForResponse(response),
          hasUnreadUpdate: true,
        );
        return;
      }
      symptoms.value = loadedSymptoms;

      final isEmergency = chatService.isEmergencyRecommendation(response);

      if (chatService.isFinalRecommendation(response) || isEmergency) {
        await _completeChat(
          recommendation:
              response.recommendationResult?.summary ?? response.text,
          nextSteps: response.recommendationResult?.nextStep ?? response.action,
          isEmergency: isEmergency,
        );
        return;
      }

      final botMessage = chatService.buildAssistantMessage(response);
      _addMessage(message: botMessage.copyWith(text: ''));

      await for (final partialText in chatService.streamText(response.text)) {
        if (!_isChatRequestActive(
          generation: expectedGeneration,
          profileId: expectedProfileId,
          historyEntryId: expectedHistoryEntryId,
          sessionId: expectedSessionId,
        )) {
          _updateChatRunState(
            historyEntryId,
            status: _statusForResponse(response),
            hasUnreadUpdate: true,
          );
          return;
        }

        _setMessages(
          chatService.replaceLastMessage(
            messages: messages.value,
            message: botMessage.copyWith(text: partialText, isStreaming: true),
          ),
        );
      }

      if (!_isChatRequestActive(
        generation: expectedGeneration,
        profileId: expectedProfileId,
        historyEntryId: expectedHistoryEntryId,
        sessionId: expectedSessionId,
      )) {
        _updateChatRunState(
          historyEntryId,
          status: _statusForResponse(response),
          hasUnreadUpdate: true,
        );
        return;
      }

      _setMessages(
        chatService.replaceLastMessage(
          messages: messages.value,
          message: botMessage.copyWith(isStreaming: false),
        ),
      );

      await _persistActiveChat(status: 'active');
    } catch (e) {
      if (!_isChatRequestActive(
        generation: expectedGeneration,
        profileId: expectedProfileId,
        historyEntryId: expectedHistoryEntryId,
        sessionId: expectedSessionId,
      )) {
        _updateChatRunState(
          historyEntryId,
          status: 'failed',
          hasUnreadUpdate: true,
        );
        return;
      }

      _setMessages(chatService.removeLastBotMessage(messages.value));
      if (e is ApiException && e.statusCode == 409) {
        final synchronized = await _synchronizeHistoryAfterConflict(
          historyEntryId,
          expectedProfileId,
        );
        if (!synchronized) {
          _addMessage(
            message: Message(text: userFacingChatError(e), isUser: false),
          );
        }
        return;
      }

      _addMessage(
        message: Message(text: userFacingChatError(e), isUser: false),
      );
      await _markActiveChatFailed();
    }
  }

  Future<bool> _synchronizeHistoryAfterConflict(
    String historyEntryId,
    int? expectedProfileId,
  ) async {
    if (expectedProfileId == null) {
      return false;
    }

    try {
      final entries = await chatHistoryRepository.loadEntries(
        profileId: expectedProfileId,
      );
      final matchingEntries = entries.where(
        (entry) => entry.id == historyEntryId,
      );
      if (matchingEntries.isEmpty ||
          expectedProfileId != authSession.activeProfileId ||
          historyEntryId != _activeHistoryEntryId) {
        return false;
      }

      final entry = matchingEntries.first;
      final synchronizedMessages = _collapseStreamingSnapshots(entry.messages);
      _activeHistoryCreatedAt = entry.createdAt;
      _setCompleted(entry.status == 'completed');
      messages.value = synchronizedMessages;
      _setChatRunState(
        ChatRunState(
          historyId: entry.id,
          sessionId: entry.sessionId,
          profileId: entry.profileId,
          messages: synchronizedMessages,
          status: entry.status,
        ),
      );
      historyRevision.value += 1;
      return true;
    } catch (_) {
      return false;
    }
  }

  bool _currentMessagesWaitForAssistantResponse() {
    if (messages.value.isEmpty) {
      return false;
    }

    final lastMessage = messages.value.last;
    return lastMessage.isUser && lastMessage.text.trim().isNotEmpty;
  }

  List<Message> _collapseStreamingSnapshots(List<Message> source) {
    final collapsed = <Message>[];

    for (final message in source) {
      if (collapsed.isNotEmpty) {
        final previous = collapsed.last;
        final timestampDifference = message.timestamp!
            .difference(previous.timestamp!)
            .abs();
        final isLikelyStreamingSnapshot =
            !previous.isUser &&
            !message.isUser &&
            timestampDifference <= const Duration(seconds: 2) &&
            (message.text.startsWith(previous.text) ||
                previous.text.startsWith(message.text));

        if (isLikelyStreamingSnapshot) {
          if (message.text.length >= previous.text.length) {
            collapsed[collapsed.length - 1] = message;
          }
          continue;
        }
      }

      collapsed.add(message);
    }

    return collapsed;
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

    _profileChangeGeneration++;
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

  bool _isChatRequestActive({
    required int generation,
    required int? profileId,
    required String? historyEntryId,
    required String? sessionId,
  }) {
    return generation == _profileChangeGeneration &&
        profileId == authSession.activeProfileId &&
        historyEntryId == _activeHistoryEntryId &&
        sessionId == chatSessionService.sessionId;
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

  Future<void> _persistActiveChat({String status = 'active'}) async {
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

    await _persistChatHistory(status: status);
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

    final expectedGeneration = _profileChangeGeneration;
    final expectedHistoryEntryId = _activeHistoryEntryId;
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

    if (expectedGeneration != _profileChangeGeneration ||
        activeProfileId != authSession.activeProfileId ||
        expectedHistoryEntryId != _activeHistoryEntryId) {
      return;
    }

    _activeHistoryEntryId = savedEntry.id;
    _activeHistoryCreatedAt = savedEntry.createdAt;
    _setChatRunState(
      ChatRunState(
        historyId: savedEntry.id,
        sessionId: savedEntry.sessionId,
        profileId: savedEntry.profileId,
        messages: savedEntry.messages,
        status: savedEntry.status,
        isContinuing: _chatRunStates[savedEntry.id]?.isContinuing ?? false,
        hasUnreadUpdate: false,
      ),
    );
    historyRevision.value += 1;
  }

  Future<void> _markActiveChatFailed() async {
    if (_activeHistoryEntryId == null || authSession.activeProfileId == null) {
      return;
    }

    await _persistChatHistory(status: 'failed');
  }

  void _setChatRunState(ChatRunState state) {
    _chatRunStates[state.historyId] = state;
  }

  void _updateChatRunState(
    String historyId, {
    String? sessionId,
    int? profileId,
    List<Message>? messages,
    String? status,
    bool? isContinuing,
    bool? hasUnreadUpdate,
  }) {
    final current = _chatRunStates[historyId];

    if (current == null) {
      return;
    }

    _chatRunStates[historyId] = current.copyWith(
      sessionId: sessionId,
      profileId: profileId,
      messages: messages,
      status: status,
      isContinuing: isContinuing,
      hasUnreadUpdate: hasUnreadUpdate,
    );
  }

  bool _canResumeStatus(String status) {
    return status == 'active' || status == 'waiting_for_assistant';
  }

  String _statusForResponse(ChatResponse response) {
    final isEmergency = chatService.isEmergencyRecommendation(response);

    if (chatService.isFinalRecommendation(response) || isEmergency) {
      return 'completed';
    }

    return 'active';
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
    Nächster Schritt: Bitte vereinbare einen Termin beim Hausarzt, wenn die Beschwerden anhalten oder sich verschlechtern.
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
    if (_isDisposed) {
      return;
    }
    _isDisposed = true;
    authSession.removeListener(_handleAuthSessionChanged);
    _availabilityRetryTimer?.cancel();
    messages.dispose();
    symptoms.dispose();
    isCompleted.dispose();
    lastReplyOptions.dispose();
    continuingHistoryIds.dispose();
    historyRevision.dispose();
    availability.dispose();
  }
}
