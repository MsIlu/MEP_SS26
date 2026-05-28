import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/app_config.dart';
import 'api_exception.dart';

/// HTTP client wrapper for JSON API requests.
///
/// This class is responsible ONLY for making HTTP requests.
/// It does NOT:
/// - interpret business logic
/// - parse domain models
/// - handle application state
///
/// Responsibilities:
/// - Execute HTTP requests
/// - Attach base URL
/// - Encode request body to JSON
/// TODO: Add proper HTTP error handling (status codes, timeouts, exceptions)
class ApiClient {
  /// Injected HTTP client so tests can provide a mock implementation.
  final http.Client _client;

  ApiClient(this._client);

  /// Sends a POST request to the given [path]
  /// with a JSON-encoded [body].
  ///
  /// Example:
  /// post("/chatscreen", {"message": "Hello"})
  Future<Map<String, dynamic>> post(
    String path,
    Map<String, dynamic> body,
  ) async {
    // Build the full request URL (base URL + endpoint path)
    final uri = Uri.parse("${AppConfig.baseUrl}$path");
    try {
      // Execute the HTTP POST request and limit the wait time so the UI can
      // recover from an unreachable backend.
      final response = await _client
          .post(
            uri,
            headers: const {"Content-Type": "application/json"},
        // Convert Dart Map -> JSON string (required for most APIs)
        body: jsonEncode(body),
          )
          .timeout(const Duration(seconds: 15));

      if (response.statusCode < 200 || response.statusCode >= 300) {
        throw ApiException(
          ApiErrorType.http,
          response.body.isEmpty ? 'HTTP request failed' : response.body,
          statusCode: response.statusCode,
        );
      }

      final decoded = jsonDecode(response.body);
      if (decoded is Map<String, dynamic>) {
        return decoded;
      }

      throw const ApiException(
        ApiErrorType.invalidResponse,
        'Server returned an invalid JSON object',
      );
    } on TimeoutException {
      throw const ApiException(ApiErrorType.timeout, 'Server Timeout');
    } on FormatException catch (e) {
      throw ApiException(
        ApiErrorType.invalidResponse,
        'Server returned invalid JSON: ${e.message}',
      );
    } on ApiException {
      rethrow;
    } catch (e) {
      throw ApiException(ApiErrorType.network, 'Network Error: $e');
    }
  }
}