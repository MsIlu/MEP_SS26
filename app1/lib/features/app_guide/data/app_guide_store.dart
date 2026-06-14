import 'package:shared_preferences/shared_preferences.dart';

/// Persists whether an account has completed the first-use app guide.
class AppGuideStore {
  static const _keyPrefix = 'careena_app_guide_completed_';
  static const guestKey = 'guest';

  static String accountKey(int accountId) => accountId.toString();

  Future<bool> isCompleted(String userKey) async {
    final preferences = await SharedPreferences.getInstance();
    return preferences.getBool(_key(userKey)) ?? false;
  }

  Future<void> markCompleted(String userKey) async {
    final preferences = await SharedPreferences.getInstance();
    await preferences.setBool(_key(userKey), true);
  }

  String _key(String userKey) => '$_keyPrefix$userKey';
}
