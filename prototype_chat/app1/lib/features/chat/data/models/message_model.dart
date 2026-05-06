/// Represents a single chat message.
///
/// A message consists of the textual content and metadata indicating
/// whether it was sent by the user or received from another source
/// (e.g., a bot or system).
class Message {
  final String text;
  final bool isUser;

  /// 🤖 Used for "Thinking..." / loading state bubbles
  final bool isLoading;

  /// ⏱ optional: useful later for ordering / persistence
  final DateTime? timestamp;

  const Message({
    required this.text,
    required this.isUser,
    this.isLoading = false,
    this.timestamp,
  });

  /// Returns a copy of this message with optional updated values.
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