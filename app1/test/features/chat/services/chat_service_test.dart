import 'package:flutter_test/flutter_test.dart';
import 'package:app1/features/chatscreen/services/chat_service.dart';
import 'package:app1/features/chatscreen/data/models/message_model.dart';

/// ChatService Unit Tests
/// 
/// Der ChatService isoliert die reine Geschäftslogik der Nachrichten-Manipulation 
/// vom Flutter-UI-Framework. Hier testen wir die Kernoperationen der Chat-Historie:
/// 1. Das korrekte Anhängen neuer Nachrichten an ein bestehendes Array.
/// 2. Das Entfernen der temporären "Lade-Blase" (Thinking Bubble), sobald die echte Serverantwort da ist.
void main() {
  group('ChatService - Logik zur Historien-Manipulation', () {
    final chatService = ChatService();

    test('addMessage() muss eine neue Nachricht unverändert an das Listenende anhängen', () {
      // Setup
      final alteListe = <Message>[];
      final neueNachricht = Message(text: 'Test-Nachricht', isUser: true);

      // Execution
      final ergebnis = chatService.addMessage(messages: alteListe, message: neueNachricht);

      // Verification
      expect(ergebnis.length, 1);
      expect(ergebnis.first.text, 'Test-Nachricht');
      expect(ergebnis.first.isUser, true);
    });

    test('removeLastBotMessage() muss die allerletzte Assistenz-Nachricht (z.B. Lade-Indikator) aus der Liste löschen', () {
      // Setup: Eine Liste simulieren, bei der die letzte Nachricht vom Bot (Ladezustand) stammt
      final liste = [
        Message(text: 'Ich habe Bauchschmerzen', isUser: true),
        Message(text: '', isUser: false, isLoading: true), // Zu entfernender Ladeindikator
      ];

      // Execution
      final ergebnis = chatService.removeLastBotMessage(liste);

      // Verification
      expect(ergebnis.length, 1, 
          reason: 'Die Liste darf nach dem Entfernen des Lade-Indikators nur noch die User-Eingabe enthalten.');
      expect(ergebnis.first.isUser, true);
    });
  });
}