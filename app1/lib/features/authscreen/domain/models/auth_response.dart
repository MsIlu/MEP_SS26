// Created as part of the authentication and profile management implementation.
// Defines frontend models for authentication responses.

import 'account.dart';

class AuthProfile {
  /// Profile summary returned after login or registration.
  final int id;
  final String displayName;
  final String profileType;
  final String? role;

  const AuthProfile({
    required this.id,
    required this.displayName,
    required this.profileType,
    this.role,
  });

  factory AuthProfile.fromJson(Map<String, dynamic> json) {
    return AuthProfile(
      id: json['id'] as int,
      displayName: json['display_name'] as String,
      profileType: json['profile_type'] as String,
      role: json['role'] as String?,
    );
  }
}

class AuthResponse {
  /// Response returned by /auth/register and /auth/login.
  final String accessToken;
  final String tokenType;
  final Account account;
  final List<AuthProfile> profiles;

  const AuthResponse({
    required this.accessToken,
    required this.tokenType,
    required this.account,
    required this.profiles,
  });

  factory AuthResponse.fromJson(Map<String, dynamic> json) {
    final rawProfiles = json['profiles'] as List<dynamic>;

    return AuthResponse(
      accessToken: json['access_token'] as String,
      tokenType: json['token_type'] as String,
      account: Account.fromJson(json['account'] as Map<String, dynamic>),
      profiles: rawProfiles
          .map((item) => AuthProfile.fromJson(item as Map<String, dynamic>))
          .toList(),
    );
  }
}