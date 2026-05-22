import 'models/chat_response_model.dart';

abstract class ChatApiContract {
  Future<ChatResponse> sendMessage(String text, String sessionId);

  Future<void> warmup();

  Future<String> createSession();

  Future<List<String>> getInputDraftSymptoms(String sessionId);

  Future<List<String>> updateInputDraftSymptoms(
      String sessionId,
      List<String> symptoms,
      );

  Future<void> cancelInputDraft(String sessionId);
}