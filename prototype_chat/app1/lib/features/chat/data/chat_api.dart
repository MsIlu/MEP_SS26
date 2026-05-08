import 'dart:convert';
import 'package:url_launcher/url_launcher.dart';
import '../../../core/config/app_config.dart';
import '../../../core/network/api_client.dart';

/// Handles all communication with the chat backend API.
///
/// This class is responsible for:
/// - Sending user messages to the server
/// - Creating and managing chat sessions
/// - Triggering backend warm up requests
/// - Decoding and validating JSON responses
class ChatApi {
  final ApiClient client;

  ChatApi(this.client);

  /// Sends a message to the backend and returns the AI response.
  ///
  /// [text] is the user's input message.
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

    /// Validates that the API response is a String.
    /// This prevents runtime errors caused by unexpected JSON types
    /// (e.g. int, bool, list, or null instead of String).
    if (response is String) {
      return response;
    }

    /// Fallback response if the server returns invalid or missing data.
    /// Ensures the app always receives a safe and predictable output.
    return "Invalid server response";
  }

  /// Sends a warm up request to the backend.
  ///
  /// This is typically used to "wake up" a cold or serverless backend
  /// before handling the first real user request.
  Future<void> warmup() async {
    try {
      await client.post("/warmup", {});
    } catch (e) {
      // Optional: log error for debugging purposes
    }
  }

  /// Creates a new chat session and returns its session ID.
  ///
  /// The session ID is required for all subsequent chat requests.
  Future<String> createSession() async {
    final res = await client.post("/session", {});
    final Map<String, dynamic> data = jsonDecode(res.body);

    final sessionId = data["session_id"] as String?;

    if (sessionId == null) {
      throw Exception("Failed to create session: missing session_id");
    }

    return sessionId;
  }
  
  Future<void> exportPdf(String sessionId) async {

    // Builds the full URL using the base URL and the sessionId
    final url = Uri.parse("${AppConfig.baseUrl}/export/$sessionId");

    // Opens the generated URL using the device's external application 
    // (usually a browser or PDF viewer)
    await launchUrl(
      url,
      mode: LaunchMode.externalApplication,
    );
  }
}