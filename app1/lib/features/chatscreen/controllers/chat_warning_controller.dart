import 'package:shared_preferences/shared_preferences.dart';

import '../../profiles/data/profile_api_service.dart';

class ChatWarningController {
  static const _key = 'chat_warning_accepted';
  static const _acceptanceValidity = Duration(days: 30);

  final ProfileApiService _profileApiService;

  bool warningAccepted = false;

  ChatWarningController(this._profileApiService);

  // Checks local storage to determine if the warning was already accepted
  Future<bool> shouldShowWarning(int? profileId, String? acceptedAt) async {
    if (profileId != null) {
      final key = _profileKey(profileId);

      if (_isStillValid(acceptedAt)) {
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString(key, acceptedAt!);
        return false;
      }

      return true;
    }

    final prefs = await SharedPreferences.getInstance();

    // Uses the local timestamp only as a fallback. The database timestamp is
    // refreshed on every confirmation and is the source of truth after login.
    final accepted = prefs.getBool(_key) ?? false;
    
    return !accepted;

  }

  // Persists that the user has accepted the warning
  Future<String> acceptWarning(int? profileId) async {
    final acceptedAt = DateTime.now().toUtc().toIso8601String();
    if (warningAccepted == false) return "";
    warningAccepted = false;
    if (profileId != null) {
      await _profileApiService.updateProfile(
        profileId: profileId,
        aiDisclaimerAcceptedAt: acceptedAt,
      );
    }

    final prefs = await SharedPreferences.getInstance();

    // Stores the acceptance flag so the warning won't be shown again
    if (profileId != null) {
      await prefs.setString(_profileKey(profileId), acceptedAt);
    } else {
      await prefs.setBool(_key,true);
    }

    return acceptedAt;
  }

  String _profileKey(int profileId) => '${_key}_$profileId';

  bool _isStillValid(String? acceptedAt) {
    if (acceptedAt == null || acceptedAt.isEmpty) {
      return false;
    }

    final acceptedDate = DateTime.tryParse(acceptedAt);

    if (acceptedDate == null) {
      return false;
    }

    return DateTime.now().toUtc().difference(acceptedDate.toUtc()) <
        _acceptanceValidity;
  }
}
