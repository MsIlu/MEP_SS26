import 'package:flutter/material.dart';
import '../../../core/config/app_config.dart';
import '../data/chat_api_contract.dart';
import '../data/models/message_model.dart';
import '../services/chat_service.dart';

class ChatController {
  final ChatApiContract chatApi;
  final ChatService chatService;
  int _generationId = 0;

  ChatController({required this.chatApi, required this.chatService});

  final ValueNotifier<List<Message>> messages = ValueNotifier<List<Message>>(
    [],
  );

  String? _sessionId;

  bool _isGenerating = false;
  bool _cancelRequested = false;
  bool get isGenerating => _isGenerating;

  Future<void> init() async {
    _setMessages([]);

    _sessionId = await chatApi.createSession();
    await loadSymptoms();

    _addMessage(
      message: Message(text: AppConfig.welcomeMessage, isUser: false),
    );

    await chatApi.warmup();
  }

  Future<Message?> sendMessage(String text) async {
    if (_sessionId == null) {
      throw Exception("Chat session not initialized.");
    }

    final trimmed = text.trim();
    if (trimmed.isEmpty) return null;

    _addMessage(message: Message(text: trimmed, isUser: true));
    _addMessage(message: Message(text: '', isUser: false, isLoading: true));
    _isGenerating = true;
    _cancelRequested = false;
    _generationId++;

    final currentGenerationId = _generationId;

    try {
      final response = await chatApi.sendMessage(trimmed, _sessionId!);
      if (_cancelRequested || currentGenerationId != _generationId) {
        return null;
      }
      final botMessage = Message(text: response, isUser: false);

      _setMessages(chatService.removeLastBotMessage(messages.value));
      _addMessage(message: botMessage.copyWith(text: ''));

      await for (final partialText in chatService.streamText(response)) {

        if (_cancelRequested || currentGenerationId != _generationId) {
          return null;
        }

        _setMessages(
          chatService.replaceLastMessage(
            messages: messages.value,
            message: botMessage.copyWith(text: partialText),
          ),
        );
      }
      // Reload symptoms after each chat response.
      // The backend is expected to update the symptom draft during /chat
      // once the symptom extractor is connected.
      await loadSymptoms();
      return botMessage;
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

  void _addMessage({required Message message}) {
    _setMessages(
      chatService.addMessage(messages: messages.value, message: message),
    );
  }

  void _setMessages(List<Message> updatedMessages) {
    messages.value = updatedMessages;
  }

  void cancelGeneration() {
    _cancelRequested = true;
    _isGenerating = false;
    _generationId++;

    _setMessages(
      chatService.removeLastBotMessage(messages.value),
    );

    _addMessage(
      message: Message(
        text: 'Antwort abgebrochen. Du kannst deine Eingabe jetzt ergänzen.',
        isUser: false,
      ),
    );
  }

/// Stores the saved symptom draft shown in display mode.
  final ValueNotifier<List<String>> symptoms = ValueNotifier<List<String>>([]);

  /// Stores a temporary editable copy of the symptoms.
  /// Changes here are not saved until the user clicks "Save".
  final ValueNotifier<List<String>> editableSymptoms =
  ValueNotifier<List<String>>([]);

  /// Controls whether the symptom section is in display mode or edit mode.
  final ValueNotifier<bool> isEditingSymptoms = ValueNotifier<bool>(false);

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

  /// Updates one symptom in the editable copy
  void updateEditableSymptom(int index, String value) {
    final updated = List<String>.from(editableSymptoms.value);
    updated[index] = value;
    editableSymptoms.value = updated;
  }

  /// Adds an empty symptom field to the editable copy
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
  /// This is used when a single symptom is edited from the symptom chip overlay.
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

}
