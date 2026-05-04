import 'dart:convert';

import '../../../core/network/api_client.dart';

/// API Layer für Chat-Kommunikation.
///
/// Kommuniziert direkt mit dem Backend und verarbeitet JSON Antworten.

class ChatApi {
  final ApiClient client;

  ChatApi(this.client);

  Future<String> sendMessage(
    String text,
    String sessionId,
  ) async {
    final res = await client.post("/chat", {
      "message": text,
      "session_id": sessionId,
    });

    final data = jsonDecode(res.body);

    return data["response"] ?? "Ungültige Antwort";
  }

  Future<void> warmup() async {
    try {
      await client.post("/warmup", {});
    } catch (_) {}
  }

  Future<String> createSession() async {
    final res = await client.post("/session", {});

    final data = jsonDecode(res.body);

    return data["session_id"];
  }
}