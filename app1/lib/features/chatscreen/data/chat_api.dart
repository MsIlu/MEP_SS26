import '../../../core/network/api_client.dart';
import 'chat_api_contract.dart';
import 'models/chat_response_model.dart';

/// Handles all communication with the chat backend API.
///
/// This class is responsible for:
/// - Sending requests to the backend
/// - Receiving and decoding responses
/// - Mapping raw API data into usable values
class ChatApi implements ChatApiContract {
  /// Low-level API client that handles JSON requests.
  final ApiClient client;

  ChatApi(this.client);

  /// Sends a user message to the backend and returns the full chat response.
  ///
  /// The response may contain a normal chat message or red flag metadata.
  @override
  Future<ChatResponse> sendMessage(String text, String sessionId) async {
    final data = await client.post("/chatscreen", {
      "message": text,
      "session_id": sessionId,
    });

    return ChatResponse.fromJson(data);
  }

  /// Sends a warm up request to the backend.
  ///
  /// This is used to prepare the backend before the first real user request.
  @override
  Future<void> warmup() async {
    try {
      await client.post("/warmup", {});
    } catch (_) {
      // Ignore warmup errors because the actual chat request can still work.
    }
  }

  /// Creates a new chat session and returns its session ID.
  ///
  /// The session ID is required for all subsequent chat requests.
  @override
  Future<String> createSession() async {
    final data = await client.post("/session", {});

    final sessionId = data['session_id'];

    // A missing session ID would make every follow-up chat request invalid, so
    // fail early with a clear error instead of caching a bad state.
    if (sessionId == null) {
      throw Exception("Failed to create session: missing session_id");
    }

    return sessionId;
  }

  /// Loads the current symptom draft for a session.
  @override
  Future<List<String>> getInputDraftSymptoms(String sessionId) async {
    final data = await client.get("/input-drafts/$sessionId");

    final symptoms = data['symptoms'];

    if (symptoms == null) {
      return [];
    }

    return List<String>.from(symptoms);
  }

  /// Updates the symptom draft for a session.
  @override
  Future<List<String>> updateInputDraftSymptoms(
      String sessionId,
      List<String> symptoms,
      ) async {
    final data = await client.patch("/input-drafts/$sessionId", {
      "symptoms": symptoms,
    });

    return List<String>.from(data['symptoms'] ?? []);
  }

  /// Cancels the current input draft for a session.
  @override
  Future<void> cancelInputDraft(String sessionId) async {
    await client.delete("/input-drafts/$sessionId");
  }
}