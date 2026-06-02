import 'package:flutter_test/flutter_test.dart';
import 'package:app1/features/chatscreen/controllers/chat_controller.dart';
import 'package:app1/features/chatscreen/data/chat_api.dart';
import 'package:app1/features/chatscreen/services/chat_service.dart';
import 'package:app1/core/network/api_client.dart';
import 'package:http/http.dart' as http;

/// ChatController Unit / State Test

/// Ziel: 
/// Das Zustandsmanagement (State Management) soll überprüft werden.
/// Da der Controller reaktive ValueNotifier nutzt, wird sichergestellt,
/// dass die App mit einer sauberen, leeren Nachrichtenliste startet, 
/// bevor API-Anfragen abgesetzt werden

void main(){
  group('ChatController - Zustandsprüfungen', () {

  test('Sollte initial mit einer komplett leeren Nachrichtenliste starten', () {
      // Setup: Erstellung der benötigten Abhängigkeiten für den Controller
      final httpClient = http.Client();
      final apiClient = ApiClient(httpClient);
      final chatApi = ChatApi(apiClient);
      
      // Instanziierung der zu testenden Komponente
      final controller = ChatController(chatApi: chatApi, chatService: ChatService());

      // Execution & Verification: Überprüfung des Ausgangszustands
      expect(controller.messages.value.isEmpty, true, 
          reason: 'Die Nachrichtenliste muss beim Start zwingend leer sein, damit keine alten Chat-Fragmente angezeigt werden.');
    });
  });
}