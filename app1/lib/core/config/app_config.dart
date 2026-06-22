import 'package:flutter/foundation.dart';

/// Central configuration for app name, copy, and environment values.
class AppConfig {
  static const String appName = "MedBitAid v0.4";
  static const String welcomeMessage = "Hallo! 👋 \nWie kann ich dir helfen?";

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
    
    const useHttps = bool.fromEnvironment(
      'BACKEND_USE_HTTPS',
      defaultValue: true,
    );
    final scheme = useHttps ? 'https' : 'http';


    // For iOS Simulator, use: "https://localhost:8000"
    // For a physical Android device, use your PC/FastAPI server IP address.

    return kIsWeb
        ? "$scheme://localhost:8000" // Web
        : "$scheme://10.0.2.2:8000"; // Android Emulator
  }
}
