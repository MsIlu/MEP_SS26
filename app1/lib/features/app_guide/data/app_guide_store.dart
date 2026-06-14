import 'package:shared_preferences/shared_preferences.dart';

/// Persists whether an account has completed the first-use app guide.
class AppGuideStore {
  static const _keyPrefix = 'careena_app_guide_completed_';

  Future<bool> isCompleted(int accountId) async {
    final preferences = await SharedPreferences.getInstance();
    return preferences.getBool(_key(accountId)) ?? false;
  }

  Future<void> markCompleted(int accountId) async {
    final preferences = await SharedPreferences.getInstance();
    await preferences.setBool(_key(accountId), true);
  }

  String _key(int accountId) => '$_keyPrefix$accountId';
}