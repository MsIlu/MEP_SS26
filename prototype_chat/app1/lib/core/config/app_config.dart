import 'package:flutter/foundation.dart';

/// Zentrale Konfigurationsklasse
///
/// Hier werden globale Konstanten und Umgebungswerte definiert,
/// z. B. App-Name, Standardtexte, Farben oder Backend-URLs
///
/// Die Klasse ist bewusst statisch, damit keine Instanz
/// erzeugt werden muss.

class AppConfig {

  static const String appName = "MedBitAid v0.3"; // Anzeigename in der Leiste oben
  static const String welcomeMessage = "Hallo! 👋 Wie kann ich dir helfen?"; // Begrüßung im Chat

  /// Methode stellt entsprechend der Plattform den richtigen URL zum Backend zur Verfügung
  /// 
  /// DEV NOTE: 
  /// Aktuell nur Unterscheidung zwischen Web und Android Emulator
  static String get baseUrl {
    return kIsWeb
    ? "http://localhost:8000"   // Web Anwendung
    : "http://10.0.2.2:8000"    // Android Emulator
      //"PC/FastAPIServerIP"             // Android Gerät (physisch) (einkommentieren)
    ;    
  }
}