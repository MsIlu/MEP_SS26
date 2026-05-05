import 'dart:convert';

import '../../../core/network/api_client.dart';

/// Handles all communication with the chat backend API.
///
/// This layer is responsible for:
/// - Sending messages to the server
/// - Creating chat sessions
/// - Triggering backend warmup requests
/// - Decoding JSON responses
class ChatApi {
  final ApiClient client;

  ChatApi(this.client);

  /// Sends a message to the backend and returns the AI response
  ///
  /// [text] is the user's message.
  /// [sessionId] identifies the current chat session.
  ///
  /// Returns the response text from the server.
  Future<String> sendMessage(
    String text,
    String sessionId,
  ) async {
    final res = await client.post(
        "/chat",
        {
          "message": text,
          "session_id": sessionId,
        },
    );

    final Map<String, dynamic> data = jsonDecode(res.body);
    final response = data["response"];

    /// Checks whether the API returned a valid String response.
    /// This avoids runtime crashes caused by invalid JSON types
    /// (e.g. int, bool, list instead of String).
    if (response is String) {
      return response;
    }
    /// Fallback value if the response is missing or not a String.
    /// Ensures the app always has a safe return value.
    return "Ungültige Antwort des Servers";
  }

  /// Sends a warmup request to the backend.
  ///
  /// This is typically used to "wake up" a serverless backend
  /// before the first real request.
  Future<void> warmup() async {
    try {
      await client.post("/warmup", {});
    } catch (e) {
      // Optional: log error if needed
    }
  }

  /// Creates a new chat session and returns the session ID.
  ///
  /// The session ID is required for subsequent chat requests.
  Future<String> createSession() async {
    final res = await client.post("/session", {});
    final Map<String, dynamic> data = jsonDecode(res.body);

    final sessionId = data["session_id"] as String?;

    if (sessionId == null) {
      throw Exception("Failed to create session: missing session_id");
    }

    return sessionId;
  }
}