import 'package:flutter/foundation.dart';

/// Central configuration for app name, copy, and environment values.
class AppConfig {
  static const String appName = "MedBitAid v0.4";
  static const String welcomeMessage = "Hallo! Ich bin Careena, deine virtuelle Gesundheitsassistentin.\nIch unterstütze dich dabei, Beschwerden einzuordnen, Symptome zu dokumentieren und eine passende Handlungsempfehlung zu erhalten."
      "\nBitte beschreibe deine Beschwerden möglichst genau: Was spürst du, wo tritt es auf, seit wann besteht es und wie stark ist es?";

  /// Base URL for backend communication.
  ///
  /// Can be overridden for deployment with:
  /// --dart-define=API_BASE_URL=https://your-backend.example.com
  ///
  /// Returns the correct URL depending on the platform:
  /// - Web: localhost
  /// - Android Emulator: special loopback address (10.0.2.2)
  ///
  /// DEV NOTE:
  /// Currently only distinguishes between Web and Android Emulator.
  /// For a physical Android device, replace the URL with your machine's local IP.
  static const String _configuredBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
  );

  static String get baseUrl {
    if (_configuredBaseUrl.isNotEmpty) {
      return _configuredBaseUrl;
    }

    return kIsWeb
        ? "http://localhost:8000" // Web
        : "http://10.0.2.2:8000"; // Android Emulator
    // : "http://localhost:8000" // IOS-Simulator
    //"PC/FastAPIServerIP"             // Android device (physical) (no //)
  }
}
