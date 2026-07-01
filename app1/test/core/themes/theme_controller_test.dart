import 'package:app1/core/themes/theme_controller.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  group('ThemeController', () {
    setUp(() {
      SharedPreferences.setMockInitialValues({});
    });

    test('stores display settings per active profile', () async {
      final controller = ThemeController();
      addTearDown(controller.dispose);

      await controller.loadProfileSettings(1);
      controller.setThemeMode(ThemeMode.light);
      controller.setSimpleView(true);
      await Future<void>.delayed(const Duration(milliseconds: 10));

      await controller.loadProfileSettings(2);

      expect(controller.themeMode, ThemeMode.dark);
      expect(controller.isSimpleView, isFalse);

      await controller.loadProfileSettings(1);

      expect(controller.themeMode, ThemeMode.light);
      expect(controller.isSimpleView, isTrue);
    });
  });
}
