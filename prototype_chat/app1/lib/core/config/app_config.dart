import 'package:flutter/foundation.dart';

/// Central configuration class
///
/// This class holds global constants and environment-specific values,
/// such as the app name, default messages, colors oder backend URLs.
///
/// It is intentionally designed with only static members
/// so no instance needs to be created

class AppConfig {

  static const String appName = "MedBitAid v0.3"; // Display name shown in the app bar
  static const String welcomeMessage = "Hallo! 👋 \nWie kann ich dir helfen?"; // Default welcome message shown in the chat

  /// Base URL for backend communication
  ///
  /// Returns the correct URL depending on the platform:
  /// - Web: localhost
  /// - Android Emulator: special loopback address (10.0.2.2)
  /// 
  /// DEV NOTE: 
  /// Currently only distinguishes between Web and Android Emulator.
  /// For a physical Android device, replace the URL with your machine's local IP.
  static String get baseUrl {
    return kIsWeb
    ? "http://localhost:8000"   // Web
    : "http://10.0.2.2:8000"    // Android Emulator
      //"PC/FastAPIServerIP"             // Android device (physical) (no //)
    ;    
  }
}