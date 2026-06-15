import '../../../core/network/api_client.dart';

import 'models/chat_history_entry.dart';

abstract class ChatHistoryRepository {
  const ChatHistoryRepository();

  Future<List<ChatHistoryEntry>> loadEntries({required int profileId});

  Future<void> saveCompletedChat(ChatHistoryEntry entry);
}

class ApiChatHistoryRepository extends ChatHistoryRepository {
  final ApiClient _apiClient;

  const ApiChatHistoryRepository(this._apiClient);

  @override
  Future<List<ChatHistoryEntry>> loadEntries({required int profileId}) async {
    final response = await _apiClient.getList('/chat-history/$profileId');

    return response
        .map((item) => ChatHistoryEntry.fromJson(item as Map<String, dynamic>))
        .toList()
      ..sort((a, b) => b.createdAt.compareTo(a.createdAt));
  }

  @override
  Future<void> saveCompletedChat(ChatHistoryEntry entry) async {
    await _apiClient.post('/chat-history', entry.toJson());
  }
}
