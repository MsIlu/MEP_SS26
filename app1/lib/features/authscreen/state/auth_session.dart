// Created as part of the authentication and profile management implementation.
// Holds the current frontend authentication and active-profile session state.

import 'package:flutter/foundation.dart';

import '../domain/models/account.dart';
import '../domain/models/auth_response.dart';

class AuthSession extends ChangeNotifier {
  /// Access token returned by the backend after login or registration.
  String? _accessToken;

  /// Currently authenticated account.
  Account? _account;

  /// Profiles accessible by the authenticated account.
  List<AuthProfile> _profiles = [];

  /// Currently selected medical profile.
  AuthProfile? _activeProfile;

  String? get accessToken => _accessToken;
  Account? get account => _account;
  List<AuthProfile> get profiles => List.unmodifiable(_profiles);
  AuthProfile? get activeProfile => _activeProfile;
  int? get activeProfileId => _activeProfile?.id;

  bool get isAuthenticated => _accessToken != null && _account != null;
  bool get hasActiveProfile => _activeProfile != null;

  /// Stores authentication data after login or registration.
  ///
  /// The first available profile is selected as the active profile by default.
  void setAuthResponse(AuthResponse response) {
    _accessToken = response.accessToken;
    _account = response.account;
    _profiles = response.profiles;
    _activeProfile = response.profiles.isNotEmpty
        ? response.profiles.first
        : null;

    notifyListeners();
  }

  /// Updates the active profile by id.
  ///
  /// Throws if the profile is not part of the current authenticated session.
  void setActiveProfileById(int profileId) {
    final matchingProfiles = _profiles.where(
          (profile) => profile.id == profileId,
    );

    if (matchingProfiles.isEmpty) {
      throw StateError('Profile is not available in the current session.');
    }

    _activeProfile = matchingProfiles.first;
    notifyListeners();
  }

  /// Replaces the available profile list and keeps the active profile valid.
  ///
  /// This is useful after loading profiles from /profiles or after deleting a profile.
  void setProfiles(List<AuthProfile> profiles) {
    _profiles = profiles;

    if (_activeProfile == null ||
        !_profiles.any((profile) => profile.id == _activeProfile!.id)) {
      _activeProfile = _profiles.isNotEmpty ? _profiles.first : null;
    }

    notifyListeners();
  }

  /// Clears all frontend authentication and profile session data.
  void clear() {
    _accessToken = null;
    _account = null;
    _profiles = [];
    _activeProfile = null;

    notifyListeners();
  }
}