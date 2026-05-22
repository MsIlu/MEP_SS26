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
    final uri = Uri.parse("${AppConfig.baseUrl}$path");

    try {
      final response = await _client
          .post(
        uri,
        headers: const {"Content-Type": "application/json"},
        body: jsonEncode(body),
      )
          .timeout(const Duration(seconds: 15));

      return _decodeJsonObjectResponse(response);
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

  /// Sends a GET request to the given [path].
  Future<Map<String, dynamic>> get(String path) async {
    final uri = Uri.parse("${AppConfig.baseUrl}$path");

    try {
      final response = await _client
          .get(uri)
          .timeout(const Duration(seconds: 15));

      return _decodeJsonObjectResponse(response);
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

  /// Sends a PATCH request to the given [path]
  /// with a JSON-encoded [body].
  Future<Map<String, dynamic>> patch(
      String path,
      Map<String, dynamic> body,
      ) async {
    final uri = Uri.parse("${AppConfig.baseUrl}$path");

    try {
      final response = await _client
          .patch(
        uri,
        headers: const {"Content-Type": "application/json"},
        body: jsonEncode(body),
      )
          .timeout(const Duration(seconds: 15));

      return _decodeJsonObjectResponse(response);
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

  /// Sends a DELETE request to the given [path].
  Future<Map<String, dynamic>> delete(String path) async {
    final uri = Uri.parse("${AppConfig.baseUrl}$path");

    try {
      final response = await _client
          .delete(uri)
          .timeout(const Duration(seconds: 15));

      return _decodeJsonObjectResponse(response);
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

  Map<String, dynamic> _decodeJsonObjectResponse(http.Response response) {
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
  }
}