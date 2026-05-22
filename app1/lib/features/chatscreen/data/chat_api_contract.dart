abstract class ChatApiContract {
  Future<String> sendMessage(String text, String sessionId);

  Future<void> warmup();

  Future<String> createSession();

  Future<List<String>> getInputDraftSymptoms(String sessionId);

  Future<List<String>> updateInputDraftSymptoms(
      String sessionId,
      List<String> symptoms,
      );

  Future<void> cancelInputDraft(String sessionId);
}