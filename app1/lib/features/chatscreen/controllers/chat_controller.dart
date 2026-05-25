import 'package:flutter/material.dart';
import '../../../core/config/app_config.dart';
import '../data/chat_api_contract.dart';
import '../data/models/chat_response_model.dart';
import '../data/models/message_model.dart';
import '../services/chat_service.dart';

/// Coordinates chat state, backend sessions, and message-list updates.
class ChatController {
  /// API adapter used for backend session and chat requests.
  final ChatApiContract chatApi;

  /// Pure message helper used to keep list transformations testable.
  final ChatService chatService;

  ChatController({required this.chatApi, required this.chatService});

  final ValueNotifier<List<Message>> messages = ValueNotifier<List<Message>>([]);

  /// Stores the saved symptom draft shown in display mode.
  final ValueNotifier<List<String>> symptoms = ValueNotifier<List<String>>([]);

  /// Stores a temporary editable copy of the symptoms.
  /// Changes here are not saved until the user clicks "Save".
  final ValueNotifier<List<String>> editableSymptoms =
  ValueNotifier<List<String>>([]);

  /// Controls whether the symptom section is in display mode or edit mode.
  final ValueNotifier<bool> isEditingSymptoms = ValueNotifier<bool>(false);

  // The backend expects all messages after session creation to include the same
  // session ID, so it is cached once createSession succeeds.
  String? _sessionId;
  Future<void>? _initFuture;

  int _generationId = 0;
  bool _isGenerating = false;
  bool _cancelRequested = false;

  bool get isGenerating => _isGenerating;

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

    final hasSession = await _ensureSession(showOfflineMessage: true);

    if (hasSession) {
      await loadSymptoms();
    }
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

    _addMessage(message: Message(text: trimmed, isUser: true));
    _addMessage(message: Message(text: '', isUser: false, isLoading: true, isStreaming: true,));

    _isGenerating = true;
    _cancelRequested = false;
    _generationId++;

    final currentGenerationId = _generationId;

    try {
      final response = await chatApi.sendMessage(trimmed, _sessionId!);

      if (_cancelRequested || currentGenerationId != _generationId) {
        return null;
      }

      _setMessages(chatService.removeLastBotMessage(messages.value));

      // Reload symptoms after each chat response.
      await loadSymptoms();

      // Red flag responses should not be shown as normal chat messages.
      if (response.redFlag) {
        return response;
      }

      final botMessage = Message(text: response.text, isUser: false);

      _addMessage(message: botMessage.copyWith(text: ''));

      await for (final partialText in chatService.streamText(response.text)) {
        if (_cancelRequested || currentGenerationId != _generationId) {
          return null;
        }

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
      if (_cancelRequested || currentGenerationId != _generationId) {
        return null;
      }

      _setMessages(chatService.removeLastBotMessage(messages.value));
      _addMessage(message: Message(text: 'Fehler: $e', isUser: false));
      return null;
    } finally {
      if (currentGenerationId == _generationId) {
        _isGenerating = false;
      }
    }
  }

  /// Resets the chat when the user leaves to the home screen.
  void resetChat() {
    messages.value = [];
    symptoms.value = [];
    editableSymptoms.value = [];
    isEditingSymptoms.value = false;
    _sessionId = null;
    _initFuture = null;
    _isGenerating = false;
    _cancelRequested = false;
    _generationId++;
  }

  void cancelGeneration() {
    _cancelRequested = true;
    _isGenerating = false;
    _generationId++;

    _setMessages(chatService.removeLastBotMessage(messages.value));

    _addMessage(
      message: Message(
        text: 'Antwort abgebrochen. Du kannst deine Eingabe jetzt ergänzen.',
        isUser: false,
      ),
    );
  }

  /// Loads the current symptom draft from the backend.
  Future<void> loadSymptoms() async {
    if (_sessionId == null) {
      throw Exception("Chat session not initialized.");
    }

    final loadedSymptoms = await chatApi.getInputDraftSymptoms(_sessionId!);
    symptoms.value = loadedSymptoms;
  }

  /// Switches the symptom section from display mode to edit mode.
  /// A copy of the saved symptoms is created so changes can be cancelled
  /// without modifying the original display state.
  void startEditingSymptoms() {
    editableSymptoms.value = List<String>.from(symptoms.value);
    isEditingSymptoms.value = true;
  }

  /// Updates one symptom in the editable copy.
  void updateEditableSymptom(int index, String value) {
    final updated = List<String>.from(editableSymptoms.value);
    updated[index] = value;
    editableSymptoms.value = updated;
  }

  /// Adds an empty symptom field to the editable copy.
  void addEditableSymptom() {
    editableSymptoms.value = [
      ...editableSymptoms.value,
      '',
    ];
  }

  /// Removes one symptom from the editable copy.
  void removeEditableSymptom(int index) {
    final updated = List<String>.from(editableSymptoms.value);
    updated.removeAt(index);
    editableSymptoms.value = updated;
  }

  /// Saves the edited symptoms to the backend.
  /// After saving, the display state is updated with the backend response
  /// and edit mode is closed.
  Future<void> saveEditedSymptoms() async {
    if (_sessionId == null) {
      throw Exception("Chat session not initialized.");
    }

    final updatedSymptoms = await chatApi.updateInputDraftSymptoms(
      _sessionId!,
      editableSymptoms.value,
    );

    symptoms.value = updatedSymptoms;
    editableSymptoms.value = [];
    isEditingSymptoms.value = false;
  }

  /// Cancels editing without saving changes.
  /// The editable copy is discarded and the original symptoms remain unchanged.
  void cancelEditingSymptoms() {
    editableSymptoms.value = [];
    isEditingSymptoms.value = false;
  }

  /// Updates the saved symptoms directly.
  /// This is used when symptoms are edited from the symptom editor.
  Future<void> updateSymptomsDirectly(List<String> updatedSymptoms) async {
    if (_sessionId == null) {
      throw Exception("Chat session not initialized.");
    }

    final savedSymptoms = await chatApi.updateInputDraftSymptoms(
      _sessionId!,
      updatedSymptoms,
    );

    symptoms.value = savedSymptoms;
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
    symptoms.dispose();
    editableSymptoms.dispose();
    isEditingSymptoms.dispose();
  }
}