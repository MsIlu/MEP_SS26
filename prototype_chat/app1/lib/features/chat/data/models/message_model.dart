/// Represents a single chat message.
///
/// A message contains the textual content and metadata that describes
/// whether it was sent by the user or received from another source
/// (e.g., a bot or system).
class Message {
  final String text;
  final bool isUser;

  /// Indicates whether this message is currently in a loading state
  /// (e.g., "Thinking…" or waiting for a response).
  final bool isLoading;

  /// Optional timestamp used for ordering messages or future persistence.
  final DateTime? timestamp;

  const Message({
    required this.text,
    required this.isUser,
    this.isLoading = false,
    this.timestamp,
  });

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