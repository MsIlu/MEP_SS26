import '../data/chat_api.dart';

/// Owns the lifecycle of the backend chat session.
///
/// The controller can ask for a usable session without knowing how the session
/// is created, warmed up, or cleared.
class ChatSessionService {
  final ChatApi chatApi;

  String? _sessionId;

  ChatSessionService(this.chatApi);

  String? get sessionId => _sessionId;

  Future<String?> ensureSession() async {
    if (_sessionId != null) {
      return _sessionId;
    }

    _sessionId = await chatApi.createSession();
    await chatApi.warmup();
    return _sessionId;
  }

  String? clearSession() {
    final previousSessionId = _sessionId;
    _sessionId = null;
    return previousSessionId;
  }
}
