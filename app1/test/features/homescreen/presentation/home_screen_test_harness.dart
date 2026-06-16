import 'package:app1/core/network/api_client.dart';
import 'package:app1/core/themes/theme_controller.dart';
import 'package:app1/features/authscreen/state/auth_session.dart';
import 'package:app1/features/chatscreen/controllers/chat_controller.dart';
import 'package:app1/features/chatscreen/data/chat_api.dart';
import 'package:app1/features/chatscreen/data/chat_history_repository.dart';
import 'package:app1/features/chatscreen/data/models/chat_history_entry.dart';
import 'package:app1/features/chatscreen/services/chat_service.dart';
import 'package:app1/features/homescreen/presentation/screens/home_screen.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;

Future<void> pumpHomeScreen(
  WidgetTester tester, {
  bool simpleView = false,
  bool startGuide = false,
  ThemeMode? themeMode,
}) async {
  final controller = ChatController(
    chatApi: ChatApi(ApiClient(http.Client())),
    chatService: ChatService(),
    authSession: AuthSession(),
    chatHistoryRepository: _FakeChatHistoryRepository(),
  );
  final themeController = ThemeController();
  if (themeMode != null) themeController.setThemeMode(themeMode);
  if (simpleView) themeController.setSimpleView(true);

  addTearDown(controller.dispose);
  addTearDown(themeController.dispose);

  await tester.pumpWidget(
    MaterialApp(
      theme: themeMode == ThemeMode.dark ? ThemeData.dark() : ThemeData.light(),
      home: HomeScreen(
        controller: controller,
        themeController: themeController,
        startGuide: startGuide,
      ),
    ),
  );
}

class _FakeChatHistoryRepository extends ChatHistoryRepository {
  const _FakeChatHistoryRepository();

  @override
  Future<List<ChatHistoryEntry>> loadEntries({required int profileId}) async {
    return [];
  }

  @override
  Future<void> saveCompletedChat(ChatHistoryEntry entry) async {}
}
