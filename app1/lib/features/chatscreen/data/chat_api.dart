import '../../../core/network/api_client.dart';
import 'models/chat_response_model.dart';

class ChatApi {
  final ApiClient client;

  ChatApi(this.client);

  Future<ChatResponse> sendMessage(
    String text,
    String sessionId,
    int? profileId,
  ) async {
    final body = <String, dynamic>{"message": text, "session_id": sessionId};

    if (profileId != null) {
      body["profile_id"] = profileId;
    }

    final data = await client.post("/chatscreen", body);

    return ChatResponse.fromJson(data);
  }

  Future<List<String>> getInputDraftSymptoms(String sessionId) async {
    final data = await client.get("/input-drafts/$sessionId");

    return List<String>.from(data['symptoms'] ?? []);
  }

  Future<List<String>> updateInputDraftSymptoms(
    String sessionId,
    List<String> symptoms,
  ) async {
    final data = await client.patch("/input-drafts/$sessionId", {
      "symptoms": symptoms,
    });

    return List<String>.from(data['symptoms'] ?? []);
  }

  Future<void> cancelInputDraft(String sessionId) async {
    await client.delete("/input-drafts/$sessionId");
  }

  Future<void> warmup() async {
    try {
      await client.post("/warmup", {});
    } catch (_) {}
  }

  Future<String> createSession() async {
    final data = await client.post("/session", {});

    final sessionId = data['session_id'];

    if (sessionId == null) {
      throw Exception("Failed to create session: missing session_id");
    }

    return sessionId;
  }
}
