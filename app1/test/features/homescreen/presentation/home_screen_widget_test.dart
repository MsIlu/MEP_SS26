import 'package:flutter_test/flutter_test.dart';
import 'package:flutter/material.dart';
import 'package:app1/features/homescreen/presentation/screens/home_screen.dart';
import 'package:app1/features/chat/controllers/chat_controller.dart';
import 'package:app1/features/chat/data/chat_api.dart';
import 'package:app1/features/chat/services/chat_service.dart';
import 'package:app1/core/network/api_client.dart';
import 'package:http/http.dart' as http;

/// HomeScreen Widget- und Integrationstest
/// 
/// Dieser Widget-Test überprüft die visuelle Präsentationsschicht des Hauptbildschirms.
/// Da wir echte UI-Komponenten rendern, testen wir hier:
/// 1. Wird die Willkommens-Überschrift korrekt für den Patienten dargestellt?
/// 2. Existiert die interaktive Careena-Karte, über die man den Chat aufruft?
void main() {
  group('HomeScreen - UI & Widget-Rendering Tests', () {
    
    testWidgets('Sollte den Willkommenstext und die Careena-Aufforderungskarte korrekt auf dem Screen rendern', (WidgetTester tester) async {
      // Setup: Mock-Abhängigkeiten aufbauen, um das HomeScreen-Widget lauffähig in die Testumgebung zu laden
      final apiClient = ApiClient(http.Client());
      final chatApi = ChatApi(apiClient);
      final controller = ChatController(chatApi: chatApi, chatService: ChatService());

      // Execution: Widget in den virtuellen Test-Bildschirm "pumpen"
      await tester.pumpWidget(
        MaterialApp(
          home: HomeScreen(controller: controller),
        ),
      );

      // Verification 1: Prüfen, ob das Begrüßungs-Text-Widget existiert
      expect(find.text('Willkommen!'), findsOneWidget, 
          reason: 'Der Willkommensgruß muss auf der Startseite gut sichtbar gerendert werden.');

      // Verification 2: Prüfen, ob der Text auf der Hero-Card vorhanden ist
      expect(find.textContaining('Ich bin Careena!'), findsOneWidget,
          reason: 'Die Einstiegskarte für den Chatbot muss für den Nutzer sofort ins Auge springen.');
    });
  });
}