import 'package:shared_preferences/shared_preferences.dart';

enum AppPage {
  onboarding,
  login,
  registration,
  home,
  chat,
  calendar,
  history,
  settings,
  documents,
  appointments,
  symptomDiary,
  medicationPlan,
}

/// Persists the last resumable app page so browser reloads can resume there.
class AppPageStore {
  static const _currentPageKey = 'current_app_page';

  static Future<AppPage?> loadCurrentPage() async {
    final prefs = await SharedPreferences.getInstance();
    final value = prefs.getString(_currentPageKey);

    for (final page in AppPage.values) {
      if (page.name == value) return page;
    }

    return null;
  }

  static Future<void> saveCurrentPage(AppPage page) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_currentPageKey, page.name);
  }

  static Future<void> clearCurrentPage() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_currentPageKey);
  }
}
