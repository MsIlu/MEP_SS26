// Created as part of the authentication and profile management implementation.
// Defines frontend models for authentication responses.

import 'account.dart';

class AuthProfile {
  /// Profile summary returned after login or registration.
  final int id;
  final String displayName;
  final String profileType;
  final String? biologicalSex;
  final String? aiDisclaimerAcceptedAt;
  final String? role;

  const AuthProfile({
    required this.id,
    required this.displayName,
    required this.profileType,
    this.biologicalSex,
    this.aiDisclaimerAcceptedAt,
    this.role,
  });

  factory AuthProfile.fromJson(Map<String, dynamic> json) {
    return AuthProfile(
      id: json['id'] as int,
      displayName: json['display_name'] as String,
      profileType: json['profile_type'] as String,
      biologicalSex: json['biological_sex'] as String?,
      aiDisclaimerAcceptedAt: json['ai_disclaimer_accepted_at'] as String?,
      role: json['role'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'display_name': displayName,
      'profile_type': profileType,
      'biological_sex': biologicalSex,
      'ai_disclaimer_accepted_at': aiDisclaimerAcceptedAt,
      'role': role,
    };
  }

  AuthProfile copyWith({
    String? displayName,
    String? biologicalSex,
    String? aiDisclaimerAcceptedAt,
  }) {
    return AuthProfile(
      id: id,
      displayName: displayName ?? this.displayName,
      profileType: profileType,
      biologicalSex: biologicalSex ?? this.biologicalSex,
      aiDisclaimerAcceptedAt:
          aiDisclaimerAcceptedAt ?? this.aiDisclaimerAcceptedAt,
      role: role,
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

  Map<String, dynamic> toJson() {
    return {
      'access_token': accessToken,
      'token_type': tokenType,
      'account': account.toJson(),
      'profiles': profiles.map((profile) => profile.toJson()).toList(),
    };
  }
}