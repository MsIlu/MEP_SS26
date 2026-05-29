import 'package:flutter_test/flutter_test.dart';
import 'package:app1/features/chat/utils/smart_replies.dart';

/// SmartReplies Algorithmus-Tests
/// 
/// Diese Komponente analysiert die Texteingaben und schlägt dem Nutzer passende
/// Folgefragen vor. Wir testen hier die deterministischen Pfade:
/// 1. Erkennt das System schmerzbezogene Wörter und liefert medizinisch passende Folgefragen?
/// 2. Greift bei unklaren Eingaben der vordefinierte (allgemeine Kontrollfragen = Fallback)-Mechanismus?
void main() {
  group('SmartReplies - Keyword-Erkennungs-Algorithmus', () {
    
    test('Sollte spezifische Schmerz-Folgefragen generieren, wenn "schmerz" oder "weh" im Text vorkommt', () {
      // Execution: Übergabe eines Beispielsatzes mit dem Keyword "Bauchschmerzen"
      final ergebnis = SmartReplies.generate("Ich habe starke Bauchschmerzen");

      // Verification
      expect(ergebnis, contains("Wo genau tut es weh?"));
      expect(ergebnis, contains("Seit wann habe ich das?"));
      expect(ergebnis.length, 3);
    });

    test('Sollte allgemeine Kontroll-Fragen (Fallback) liefern, wenn kein vordefiniertes Keyword matcht', () {
      // Execution: Übergabe eines neutralen Satzes ohne direkte Keywords
      final ergebnis = SmartReplies.generate("Hallo Careena");

      // Verification
      expect(ergebnis, contains("Erklär mir das einfacher"));
      expect(ergebnis, contains("Was soll ich jetzt tun?"));
    });
  });
}