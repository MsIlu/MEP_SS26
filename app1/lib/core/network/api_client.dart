import 'dart:async';
import 'dart:convert';

import 'package:http/http.dart' as http;

import '../config/app_config.dart';
import 'api_exception.dart';

/// HTTP client wrapper for JSON API requests.
///
/// This class is responsible only for making HTTP requests.
/// It does not:
/// - interpret business logic
/// - parse domain models
/// - handle feature-specific application state
///
/// Responsibilities:
/// - Execute HTTP requests
/// - Attach the base URL
/// - Encode request bodies as JSON
/// - Attach the bearer token if one is available
/// - Convert HTTP/network errors into ApiException
class ApiClient {
  /// Injected HTTP client so tests can provide a mock implementation.
  final http.Client _client;

  /// Bearer token used for authenticated backend requests.
  ///
  /// This is kept in memory for now. Later, the token can be loaded from
  /// secure storage or shared preferences when the app starts.
  String? _accessToken;

  ApiClient(this._client);

  /// Stores the access token after login or registration.
  void setAccessToken(String token) {
    _accessToken = token;
  }

  /// Removes the access token, for example after logout or account deletion.
  void clearAccessToken() {
    _accessToken = null;
  }

  /// Sends a POST request to the given [path] with a JSON-encoded [body].
  Future<Map<String, dynamic>> post(
    String path,
    Map<String, dynamic> body,
  ) async {
    final uri = Uri.parse("${AppConfig.baseUrl}$path");

    try {
      final response = await _client
          .post(uri, headers: _buildHeaders(), body: jsonEncode(body))
          .timeout(const Duration(minutes: 3));

      return _handleJsonObjectResponse(response);
    } on TimeoutException {
      throw const ApiException(ApiErrorType.timeout, 'Der Server hat nicht rechtzeitig geantwortet. Bitte versuchen Sie es erneut.');
    } on FormatException  {
      throw ApiException(
        ApiErrorType.invalidResponse,
        'Die Serverantwort konnte nicht verarbeitet werden. Bitte versuchen Sie es später erneut.',
      );
    } on ApiException {
      rethrow;
    } catch (e) {
      throw ApiException(ApiErrorType.network, 'Es konnte keine Verbindung zum Server hergestellt werden. Bitte versuchen Sie es erneut.');
    }
  }

  /// Sends a GET request to the given [path].
  Future<Map<String, dynamic>> get(String path) async {
    final uri = Uri.parse("${AppConfig.baseUrl}$path");

    try {
      final response = await _client
          .get(uri, headers: _buildHeaders())
          .timeout(const Duration(minutes: 3));

      return _handleJsonObjectResponse(response);
    } on TimeoutException {
      throw const ApiException(ApiErrorType.timeout, 'Der Server hat nicht rechtzeitig geantwortet. Bitte versuchen Sie es erneut.');
    } on FormatException  {
      throw ApiException(
        ApiErrorType.invalidResponse,
        'Die Serverantwort konnte nicht verarbeitet werden. Bitte versuchen Sie es später erneut.',
      );
    } on ApiException {
      rethrow;
    } catch (e) {
      throw ApiException(ApiErrorType.network, 'Es konnte keine Verbindung zum Server hergestellt werden. Bitte versuchen Sie es erneut.');
    }
  }

  /// Sends a GET request and expects a JSON list response.
  Future<List<dynamic>> getList(String path) async {
    final uri = Uri.parse("${AppConfig.baseUrl}$path");

    try {
      final response = await _client
          .get(uri, headers: _buildHeaders())
          .timeout(const Duration(minutes: 3));

      if (response.statusCode < 200 || response.statusCode >= 300) {
        String message;

        switch (response.statusCode) {
          case 400:
            message = 'Die Anfrage ist ungültig. Bitte überprüfen Sie Ihre Eingaben.';
            break;
          case 401:
            message = 'Sie sind nicht angemeldet. Bitte melden Sie sich erneut an.';
            break;
          case 403:
            message = 'Sie haben keine Berechtigung für diese Aktion.';
            break;
          case 404:
            message = 'Die angefragten Daten wurden nicht gefunden.';
            break;
          default:
            message = 'Es ist ein Serverfehler aufgetreten. Bitte versuchen Sie es später erneut.';
        }

        throw ApiException(
          ApiErrorType.http,
          message,
          statusCode: response.statusCode,
        );
      }

      final decoded = jsonDecode(response.body);

      if (decoded is List<dynamic>) {
        return decoded;
      }

      throw const ApiException(
        ApiErrorType.invalidResponse,
        'Die Serverantwort konnte nicht verarbeitet werden. Bitte versuchen Sie es später erneut.',
      );
    } on TimeoutException {
      throw const ApiException(ApiErrorType.timeout, 'Der Server hat nicht rechtzeitig geantwortet. Bitte versuchen Sie es erneut.');
    } on FormatException {
      throw ApiException(
        ApiErrorType.invalidResponse,
        'Die Serverantwort konnte nicht verarbeitet werden. Bitte versuchen Sie es später erneut.',
      );
    } on ApiException {
      rethrow;
    } catch (e) {
      throw ApiException(ApiErrorType.network, 'Es konnte keine Verbindung zum Server hergestellt werden. Bitte versuchen Sie es erneut.');
    }
  }

  /// Sends a PATCH request to the given [path] with a JSON-encoded [body].
  Future<Map<String, dynamic>> patch(
    String path,
    Map<String, dynamic> body,
  ) async {
    final uri = Uri.parse("${AppConfig.baseUrl}$path");

    try {
      final response = await _client
          .patch(uri, headers: _buildHeaders(), body: jsonEncode(body))
          .timeout(const Duration(minutes: 3));

      return _handleJsonObjectResponse(response);
    } on TimeoutException {
      throw const ApiException(ApiErrorType.timeout, 'Der Server hat nicht rechtzeitig geantwortet. Bitte versuchen Sie es erneut.');
    } on FormatException  {
      throw ApiException(
        ApiErrorType.invalidResponse,
        'Die Serverantwort konnte nicht verarbeitet werden. Bitte versuchen Sie es später erneut.',
      );
    } on ApiException {
      rethrow;
    } catch (e) {
      throw ApiException(ApiErrorType.network, 'Es konnte keine Verbindung zum Server hergestellt werden. Bitte versuchen Sie es erneut.');
    }
  }

  /// Sends a DELETE request to the given [path].
  Future<Map<String, dynamic>> delete(String path) async {
    final uri = Uri.parse("${AppConfig.baseUrl}$path");

    try {
      final response = await _client
          .delete(uri, headers: _buildHeaders())
          .timeout(const Duration(minutes: 3));

      return _handleJsonObjectResponse(response);
    } on TimeoutException {
      throw const ApiException(ApiErrorType.timeout, 'Der Server hat nicht rechtzeitig geantwortet. Bitte versuchen Sie es erneut.');
    } on FormatException  {
      throw ApiException(
        ApiErrorType.invalidResponse,
        'Die Serverantwort konnte nicht verarbeitet werden. Bitte versuchen Sie es später erneut.',
      );
    } on ApiException {
      rethrow;
    } catch (e) {
      throw ApiException(ApiErrorType.network, 'Es konnte keine Verbindung zum Server hergestellt werden. Bitte versuchen Sie es erneut.');
    }
  }

  /// Builds common headers for JSON requests.
  Map<String, String> _buildHeaders() {
    return {
      'Content-Type': 'application/json',
      if (_accessToken != null) 'Authorization': 'Bearer $_accessToken',
    };
  }

  /// Validates an HTTP response and decodes it as a JSON object.
  Map<String, dynamic> _handleJsonObjectResponse(http.Response response) {
    if (response.statusCode < 200 || response.statusCode >= 300) {
      String message;

      switch (response.statusCode) {
        case 400:
          message = 'Die Anfrage ist ungültig. Bitte überprüfen Sie Ihre Eingaben.';
          break;
        case 401:
          message = 'Sie sind nicht angemeldet. Bitte melden Sie sich erneut an.';
          break;
        case 403:
          message = 'Sie haben keine Berechtigung für diese Aktion.';
          break;
        case 404:
          message = 'Die angefragten Daten wurden nicht gefunden.';
          break;
        default:
          message = 'Es ist ein Serverfehler aufgetreten. Bitte versuchen Sie es später erneut.';
      }

      throw ApiException(
        ApiErrorType.http,
        message,
        statusCode: response.statusCode,
      );
    }

    final decoded = jsonDecode(response.body);

    if (decoded is Map<String, dynamic>) {
      return decoded;
    }

    throw const ApiException(
      ApiErrorType.invalidResponse,
      'Die Serverantwort konnte nicht verarbeitet werden. Bitte versuchen Sie es später erneut.',
    );
  }

  String _errorMessage(String responseBody) {
    if (responseBody.isEmpty) return 'HTTP request failed';

    try {
      final decoded = jsonDecode(responseBody);
      if (decoded is Map<String, dynamic> && decoded['detail'] is String) {
        return decoded['detail'] as String;
      }
    } on FormatException {
      // Plain-text backend errors are already readable.
    }

    return responseBody;
  }
}
