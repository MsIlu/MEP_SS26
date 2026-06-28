import '../../../core/network/api_client.dart';

import 'models/chat_history_entry.dart';

abstract class ChatHistoryRepository {
  const ChatHistoryRepository();

  Future<List<ChatHistoryEntry>> loadEntries({required int profileId});

  Future<ChatHistoryEntry> saveChat(ChatHistoryEntry entry);

  Future<ChatHistoryEntry> updateChat(ChatHistoryEntry entry);

  Future<void> deleteChat(String historyId) {
    throw UnimplementedError('Deleting chat history is not supported.');
  }

  Future<ChatHistoryEntry> saveCompletedChat(ChatHistoryEntry entry) {
    return saveChat(entry);
  }
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
  Future<ChatHistoryEntry> saveChat(ChatHistoryEntry entry) async {
    final response = await _apiClient.post('/chat-history', entry.toJson());

    return ChatHistoryEntry.fromJson(response);
  }

  @override
  Future<ChatHistoryEntry> updateChat(ChatHistoryEntry entry) async {
    final response = await _apiClient.patch(
      '/chat-history/${entry.id}',
      entry.toJson(),
    );

    return ChatHistoryEntry.fromJson(response);
  }

  @override
  Future<void> deleteChat(String historyId) async {
    await _apiClient.delete('/chat-history/$historyId');
  }
}
