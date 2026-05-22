/// Represents a single chat message.
class Message {
  final String text;

  /// Indicates whether this message was sent by the user.
  /// If false, it is treated as a bot/system message.
  final bool isUser;
  final bool isLoading;
  final DateTime? timestamp;

  Message({
    required this.text,
    required this.isUser,
    this.isLoading = false,
    DateTime? timestamp,
  }) : timestamp = timestamp ?? DateTime.now();

  /// Creates a new instance of [Message] with updated values.
  /// Unspecified fields retain their current values.
  Message copyWith({
    String? text,
    bool? isUser,
    bool? isLoading,
    DateTime? timestamp,
  }) {
    return Message(
      text: text ?? this.text,
      isUser: isUser ?? this.isUser,
      isLoading: isLoading ?? this.isLoading,
      timestamp: timestamp ?? this.timestamp,
    );
  }

  @override
  String toString() {
    return 'Message(text: $text, isUser: $isUser, isLoading: $isLoading, timestamp: $timestamp)';
  }
}