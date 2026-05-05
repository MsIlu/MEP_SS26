import 'package:http/http.dart' as http;
import '../config/app_config.dart';
import 'dart:convert';

/// HTTP client wrapper for API requests.
///
/// Encapsulates HTTP logic to ensure that all requests
/// are handled centrally through this class
///
/// This makes it easier to:
/// - Add logging
/// - Handles errors globally
/// - Modify headers or authentication later
///
/// DEV NOTE:
/// TODO: Add proper HTTP error handling (status codes, timeouts, exceptions)
class ApiClient {
  final http.Client _client;

  ApiClient(this._client);

  /// Sends a POST request to the given [path]
  /// with a JSON-encoded [body].
  ///
  /// Example:
  /// post("/chat", {"message": "Hello"})
  Future<http.Response> post(
      String path,
      Map<String, dynamic> body,
      ) async {
    // Build the full request URL (base URL + endpoint path)
    final uri = Uri.parse("${AppConfig.baseUrl}$path");

    // Execute HTTP POST request and wait for the response
    final response = await _client.post(
      uri,
      headers: const {
        // Indicates that the request body is JSON
        "Content-Type": "application/json",
      },
      // Convert Dart Map -> JSON string (required for most APIs)
      body: jsonEncode(body),
    );

    return response;
  }
}