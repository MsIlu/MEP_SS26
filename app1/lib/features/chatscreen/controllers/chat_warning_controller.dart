import 'package:shared_preferences/shared_preferences.dart';

class ChatWarningController {
  static const _key = 'chat_warning_accepted';

  // Checks local storage to determine if the warning was already accepted
  Future<bool> shouldShowWarning() async {
    final prefs = await SharedPreferences.getInstance();
    
    // Reads the stored acceptance flag (defaults to false if not set)
    final accepted = prefs.getBool(_key) ?? false;
    
    return !accepted;
  }

  // Persists that the user has accepted the warning
  Future<void> acceptWarning() async {
    final prefs = await SharedPreferences.getInstance();
    
    // Stores the acceptance flag so the warning won't be shown again
    await prefs.setBool(_key,true);
  }
}