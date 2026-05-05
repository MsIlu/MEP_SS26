/// Represents a single chat message.
///
/// A message consists of the textual content and metadata indicating
/// whether it was sent by the user or received from another source
/// (e.g., a bot or system).
class Message {
  final String text; /// The textual content of the message.
  final bool isUser; /// Indicates whether the message was sent by the user.

  /// Creates an immutable [Message] instance.
  const Message({
    required this.text,
    required this.isUser,
  });

  /// Returns a copy of this message with optional updated values.
  ///
  /// Useful for modifying a message while keeping immutability.
  Message copyWith({
    String? text,
    bool? isUser,
  }) {
    return Message(
      text: text ?? this.text,
      isUser: isUser ?? this.isUser,
    );
  }

  @override
  /// For debugging
  String toString() {
    return 'Message(text: $text, isUser: $isUser)';
  }
}