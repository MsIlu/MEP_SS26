// Created as part of the authentication and profile management implementation.
// Holds the current frontend authentication and active-profile session state.

import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../domain/models/account.dart';
import '../domain/models/auth_response.dart';

class AuthSession extends ChangeNotifier {
  static const _lastProfileKeyPrefix = 'last_active_profile_';
  static const _persistedSessionKey = 'auth_session';
  static final Map<int, int> _rememberedProfileIds = {};

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
  /// The first available profile is selected unless a remembered profile fits.
  void setAuthResponse(AuthResponse response, {int? preferredProfileId}) {
    _accessToken = response.accessToken;
    _account = response.account;
    _profiles = _withMainProfileFirst(response.profiles);
    _activeProfile =
        _profileById(preferredProfileId) ??
        (_profiles.isNotEmpty ? _profiles.first : null);

    _rememberActiveProfile();
    _persistAuthResponse(response);
    notifyListeners();
  }

  /// Restores the previous login after a browser reload or app restart.
  Future<bool> restorePersistedSession() async {
    final prefs = await SharedPreferences.getInstance();
    final rawSession = prefs.getString(_persistedSessionKey);

    if (rawSession == null || rawSession.isEmpty) {
      return false;
    }

    try {
      final json = jsonDecode(rawSession) as Map<String, dynamic>;
      final response = AuthResponse.fromJson(json);
      final rememberedProfileId = await loadRememberedProfileId(
        response.account.id,
      );
      setAuthResponse(response, preferredProfileId: rememberedProfileId);
      return true;
    } catch (_) {
      await prefs.remove(_persistedSessionKey);
      return false;
    }
  }

  /// Loads the last profile used for this account on this device.
  Future<int?> loadRememberedProfileId(int accountId) async {
    final cachedProfileId = _rememberedProfileIds[accountId];
    if (cachedProfileId != null) return cachedProfileId;

    final prefs = await SharedPreferences.getInstance();
    return prefs.getInt('$_lastProfileKeyPrefix$accountId');
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
    _rememberActiveProfile();
    notifyListeners();
  }

  /// Replaces the available profile list and keeps the active profile valid.
  ///
  /// This is useful after loading profiles from /profiles or after deleting a profile.
  void setProfiles(List<AuthProfile> profiles) {
    _profiles = _withMainProfileFirst(profiles);

    if (_activeProfile == null ||
        !_profiles.any((profile) => profile.id == _activeProfile!.id)) {
      _activeProfile = _profiles.isNotEmpty ? _profiles.first : null;
    }

    _rememberActiveProfile();
    notifyListeners();
  }

  /// Updates the active profile display name in local session state.
  void setActiveProfileDisplayName(String displayName) {
    final activeProfile = _activeProfile;

    if (activeProfile == null) {
      return;
    }

    final updatedProfile = activeProfile.copyWith(displayName: displayName);
    _profiles = _profiles
        .map(
          (profile) =>
              profile.id == updatedProfile.id ? updatedProfile : profile,
        )
        .toList();
    _activeProfile = updatedProfile;

    notifyListeners();
  }

  /// Updates the active profile sex in local session state.
  void setActiveProfileBiologicalSex(String? biologicalSex) {
    final activeProfile = _activeProfile;

    if (activeProfile == null) {
      return;
    }

    final updatedProfile = activeProfile.copyWith(biologicalSex: biologicalSex);
    _profiles = _profiles
        .map(
          (profile) =>
              profile.id == updatedProfile.id ? updatedProfile : profile,
        )
        .toList();
    _activeProfile = updatedProfile;

    notifyListeners();
  }

  /// Updates the warning acceptance timestamp for the active profile.
  void setActiveProfileAiDisclaimerAcceptedAt(String acceptedAt) {
    final activeProfile = _activeProfile;

    if (activeProfile == null) {
      return;
    }

    final updatedProfile = activeProfile.copyWith(
      aiDisclaimerAcceptedAt: acceptedAt,
    );

    _profiles = _profiles
        .map(
          (profile) =>
              profile.id == updatedProfile.id ? updatedProfile : profile,
        )
        .toList();
    _activeProfile = updatedProfile;

    notifyListeners();
  }

  /// Clears all frontend authentication and profile session data.
  Future<void> clear() async {
    _accessToken = null;
    _account = null;
    _profiles = [];
    _activeProfile = null;

    await _clearPersistedSession();
    notifyListeners();
  }

  AuthProfile? _profileById(int? profileId) {
    if (profileId == null) return null;

    for (final profile in _profiles) {
      if (profile.id == profileId) return profile;
    }

    return null;
  }

  List<AuthProfile> _withMainProfileFirst(List<AuthProfile> profiles) {
    return [
      ...profiles.where((profile) => profile.profileType == 'self'),
      ...profiles.where((profile) => profile.profileType != 'self'),
    ];
  }

  Future<void> _rememberActiveProfile() async {
    final accountId = _account?.id;
    final profileId = _activeProfile?.id;

    if (accountId == null || profileId == null) return;

    _rememberedProfileIds[accountId] = profileId;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setInt('$_lastProfileKeyPrefix$accountId', profileId);
  }

  Future<void> _persistAuthResponse(AuthResponse response) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_persistedSessionKey, jsonEncode(response.toJson()));
  }

  Future<void> _clearPersistedSession() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_persistedSessionKey);
  }
}