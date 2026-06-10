import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:app1/core/network/api_client.dart';
import 'package:app1/core/themes/theme_controller.dart';
import 'package:app1/features/chatscreen/controllers/chat_controller.dart';
import 'package:app1/features/chatscreen/data/chat_api.dart';
import 'package:app1/features/chatscreen/services/chat_service.dart';
import 'package:app1/features/homescreen/presentation/screens/home_screen.dart';
import 'package:http/http.dart' as http;
import 'package:app1/features/authscreen/state/auth_session.dart';

/// Widget tests for the home screen presentation layer.
void main() {
  group('HomeScreen', () {
    testWidgets('renders the welcome area and Careena entry card', (
      WidgetTester tester,
    ) async {
      // The home screen needs the same controllers it receives in production.
      final apiClient = ApiClient(http.Client());
      final chatApi = ChatApi(apiClient);
      final controller = ChatController(
        chatApi: chatApi,
        chatService: ChatService(),
        authSession: AuthSession(),
      );
      final themeController = ThemeController();
      addTearDown(controller.dispose);
      addTearDown(themeController.dispose);

      await tester.pumpWidget(
        MaterialApp(
          home: HomeScreen(
            controller: controller,
            themeController: themeController,
          ),
        ),
      );

      expect(find.text('Willkommen!'), findsOneWidget);
      expect(find.textContaining('Ich bin Careena!'), findsOneWidget);
      expect(find.text('Medikamentenplan'), findsOneWidget);
    });
  });
}
