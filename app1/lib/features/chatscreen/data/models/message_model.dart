/// Represents a single chat message.
class Message {
  final String text;

  /// Indicates whether this message was sent by the user.
  /// If false, it is treated as a bot/system message.
  final bool isUser;
  final bool isLoading;
  final DateTime? timestamp;
  final bool isStreaming;

  /// Whether this assistant message can be exported as a PDF recommendation.
  final bool canExportPdf;

  /// Optional title used for the exported PDF.
  final String? exportTitle;

  /// Optional recommendation text used for the exported PDF.
  final String? exportRecommendation;

  /// Optional next steps used for the exported PDF.
  final String? exportNextSteps;

  Message({
    required this.text,
    required this.isUser,
    this.isLoading = false,
    this.isStreaming = false,
    DateTime? timestamp,
    this.canExportPdf = false,
    this.exportTitle,
    this.exportRecommendation,
    this.exportNextSteps,
  }) : timestamp = timestamp ?? DateTime.now();

  /// Creates a new instance of [Message] with updated values.
  /// Unspecified fields retain their current values.
  Message copyWith({
    String? text,
    bool? isUser,
    bool? isLoading,
    DateTime? timestamp,
    bool? isStreaming,
    bool? canExportPdf,
    String? exportTitle,
    String? exportRecommendation,
    String? exportNextSteps,
  }) {
    return Message(
      text: text ?? this.text,
      isUser: isUser ?? this.isUser,
      isLoading: isLoading ?? this.isLoading,
      isStreaming: isStreaming ?? this.isStreaming,
      timestamp: timestamp ?? this.timestamp,
      canExportPdf: canExportPdf ?? this.canExportPdf,
      exportTitle: exportTitle ?? this.exportTitle,
      exportRecommendation: exportRecommendation ?? this.exportRecommendation,
      exportNextSteps: exportNextSteps ?? this.exportNextSteps,
    );
  }

  @override
  String toString() {
    return 'Message(text: $text, isUser: $isUser, isLoading: $isLoading, timestamp: $timestamp, canExportPdf: $canExportPdf)';
  }
}