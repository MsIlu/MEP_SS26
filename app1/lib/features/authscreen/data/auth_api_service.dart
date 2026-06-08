// Created as part of the authentication and profile management implementation.
// Provides API methods for registration, login, account lookup, and account deletion.

import '../../../core/network/api_client.dart';
import '../domain/models/account.dart';
import '../domain/models/auth_response.dart';

class AuthApiService {
  /// API client used to communicate with the backend.
  final ApiClient _apiClient;

  const AuthApiService(this._apiClient);

  /// Registers a new account and creates the initial main profile.
  Future<AuthResponse> register({
    required String email,
    required String password,
    required String displayName,
    String? dateOfBirth,
    String? biologicalSex,
  }) async {
    final response = await _apiClient.post(
      '/auth/register',
      {
        'email': email,
        'password': password,
        'display_name': displayName,
        'date_of_birth': dateOfBirth,
        'biological_sex': biologicalSex,
      },
    );

    final authResponse = AuthResponse.fromJson(response);
    _apiClient.setAccessToken(authResponse.accessToken);

    return authResponse;
  }

  /// Logs in an existing account.
  Future<AuthResponse> login({
    required String email,
    required String password,
  }) async {
    final response = await _apiClient.post(
      '/auth/login',
      {
        'email': email,
        'password': password,
      },
    );

    final authResponse = AuthResponse.fromJson(response);
    _apiClient.setAccessToken(authResponse.accessToken);

    return authResponse;
  }

  /// Returns the currently authenticated account.
  Future<Account> getMe() async {
    final response = await _apiClient.get('/auth/me');
    return Account.fromJson(response);
  }

  /// Soft-deletes the currently authenticated account.
  Future<void> deleteAccount() async {
    await _apiClient.delete('/auth/me');
    _apiClient.clearAccessToken();
  }

  /// Clears the locally stored in-memory access token.
  void logout() {
    _apiClient.clearAccessToken();
  }
}