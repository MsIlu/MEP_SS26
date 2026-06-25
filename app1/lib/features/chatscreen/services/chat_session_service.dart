import '../data/chat_api.dart';

/// Owns the lifecycle of the backend chat session.
///
/// The controller can ask for a usable session without knowing how the session
/// is created, warmed up, or cleared.
class ChatSessionService {
  final ChatApi chatApi;

  String? _sessionId;
  int? _profileId;

  ChatSessionService(this.chatApi);

  String? get sessionId => _sessionId;
  int? get profileId => _profileId;

  Future<String?> ensureSession({int? profileId}) async {
    if (_sessionId != null && _profileId == profileId) {
      return _sessionId;
    }

    _sessionId = await chatApi.createSession(profileId);
    _profileId = profileId;
    await chatApi.warmup();
    return _sessionId;
  }

  Future<String> resumeHistorySession({
    required String historyId,
    required int? profileId,
  }) async {
    _sessionId = await chatApi.resumeHistorySession(historyId);
    _profileId = profileId;
    await chatApi.warmup();
    return _sessionId!;
  }

  String? clearSession() {
    final previousSessionId = _sessionId;
    _sessionId = null;
    _profileId = null;
    return previousSessionId;
  }
}
