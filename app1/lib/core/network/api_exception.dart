/// Error categories that the UI can handle without parsing raw messages.
enum ApiErrorType { timeout, http, invalidResponse, network }

/// Typed exception for backend communication failures.
class ApiException implements Exception {
  final ApiErrorType type;
  final String message;
  final int? statusCode;

  const ApiException(this.type, this.message, {this.statusCode});

  @override
  String toString() {
    final status = statusCode == null ? '' : ' ($statusCode)';
    return '$message$status';
  }
}
