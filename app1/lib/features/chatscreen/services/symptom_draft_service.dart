import '../data/chat_api.dart';

/// Handles symptom draft persistence for the active chat session.
///
/// Loading and cleanup failures are intentionally contained here, so the chat
/// remains usable even when the draft endpoint is temporarily unavailable.
class SymptomDraftService {
  final ChatApi chatApi;

  SymptomDraftService(this.chatApi);

  Future<List<String>> loadSymptoms(String? sessionId) async {
    if (sessionId == null) {
      return [];
    }

    try {
      return await chatApi.getInputDraftSymptoms(sessionId);
    } catch (_) {
      return [];
    }
  }

  Future<List<String>> updateSymptoms(
    String? sessionId,
    List<String> symptoms,
  ) async {
    if (sessionId == null) {
      throw Exception("Chat session not initialized.");
    }

    return chatApi.updateInputDraftSymptoms(sessionId, symptoms);
  }

  Future<void> cancelDraft(String? sessionId) async {
    if (sessionId == null) {
      return;
    }

    try {
      await chatApi.cancelInputDraft(sessionId);
    } catch (_) {}
  }
}
