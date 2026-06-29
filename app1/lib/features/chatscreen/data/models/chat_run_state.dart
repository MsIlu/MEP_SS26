import 'message_model.dart';

class ChatRunState {
  final String historyId;
  final String? sessionId;
  final int? profileId;
  final List<Message> messages;
  final String status;
  final bool isContinuing;
  final bool hasUnreadUpdate;

  const ChatRunState({
    required this.historyId,
    required this.sessionId,
    required this.profileId,
    required this.messages,
    required this.status,
    this.isContinuing = false,
    this.hasUnreadUpdate = false,
  });

  ChatRunState copyWith({
    String? historyId,
    String? sessionId,
    int? profileId,
    List<Message>? messages,
    String? status,
    bool? isContinuing,
    bool? hasUnreadUpdate,
  }) {
    return ChatRunState(
      historyId: historyId ?? this.historyId,
      sessionId: sessionId ?? this.sessionId,
      profileId: profileId ?? this.profileId,
      messages: messages ?? this.messages,
      status: status ?? this.status,
      isContinuing: isContinuing ?? this.isContinuing,
      hasUnreadUpdate: hasUnreadUpdate ?? this.hasUnreadUpdate,
    );
  }
}
