import 'package:flutter/material.dart';

class ThemeController extends ChangeNotifier {
  ThemeMode _themeMode = ThemeMode.dark;
  bool _isSimpleView = false;

  ThemeMode get themeMode => _themeMode;
  bool get isDarkMode => _themeMode == ThemeMode.dark;
  bool get isSimpleView => _isSimpleView;

  void toggleTheme() {
    setThemeMode(isDarkMode ? ThemeMode.light : ThemeMode.dark);
  }

  void setThemeMode(ThemeMode mode) {
    if (_themeMode == mode) return;
    _themeMode = mode;
    notifyListeners();
  }

  void setSimpleView(bool enabled) {
    if (_isSimpleView == enabled) return;
    _isSimpleView = enabled;
    notifyListeners();
  }
}
