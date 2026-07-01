import 'dart:async';

import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class ThemeController extends ChangeNotifier {
  static const _themeModeKeyPrefix = 'profile_theme_mode_';
  static const _simpleViewKeyPrefix = 'profile_simple_view_';

  ThemeMode _themeMode = ThemeMode.dark;
  bool _isSimpleView = false;
  int? _activeProfileId;

  ThemeMode get themeMode => _themeMode;
  bool get isDarkMode => _themeMode == ThemeMode.dark;
  bool get isSimpleView => _isSimpleView;

  void toggleTheme() {
    setThemeMode(isDarkMode ? ThemeMode.light : ThemeMode.dark);
  }

  void setThemeMode(ThemeMode mode) {
    if (_themeMode == mode) return;
    _themeMode = mode;
    unawaited(_saveActiveProfileSettings());
    notifyListeners();
  }

  void setSimpleView(bool enabled) {
    if (_isSimpleView == enabled) return;
    _isSimpleView = enabled;
    unawaited(_saveActiveProfileSettings());
    notifyListeners();
  }

  Future<void> loadProfileSettings(int? profileId) async {
    if (_activeProfileId == profileId) return;

    if (profileId == null) {
      _activeProfileId = null;
      return;
    }

    final prefs = await SharedPreferences.getInstance();
    final savedThemeMode = prefs.getString('$_themeModeKeyPrefix$profileId');
    final savedSimpleView = prefs.getBool('$_simpleViewKeyPrefix$profileId');

    final nextThemeMode = _themeModeFromName(savedThemeMode) ?? ThemeMode.dark;
    final nextSimpleView = savedSimpleView ?? false;

    _activeProfileId = profileId;

    if (_themeMode == nextThemeMode && _isSimpleView == nextSimpleView) {
      return;
    }

    _themeMode = nextThemeMode;
    _isSimpleView = nextSimpleView;
    notifyListeners();
  }

  Future<void> _saveActiveProfileSettings() async {
    final profileId = _activeProfileId;
    if (profileId == null) return;

    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('$_themeModeKeyPrefix$profileId', _themeMode.name);
    await prefs.setBool('$_simpleViewKeyPrefix$profileId', _isSimpleView);
  }

  ThemeMode? _themeModeFromName(String? value) {
    if (value == null) return null;

    for (final mode in ThemeMode.values) {
      if (mode.name == value) return mode;
    }

    return null;
  }
}
