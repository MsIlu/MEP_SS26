import '../../../chatscreen/data/models/chat_response_model.dart';

/// Presentation-friendly summary of why the warning screen was shown.
class EmergencyReason {
  /// Individual backend details that are safe to display to the user.
  final List<String> parts;

  const EmergencyReason(this.parts);

  /// Extracts human-readable reason parts from backend red-flag metadata.
  factory EmergencyReason.fromResponse(ChatResponse response) {
    final parts = <String>[
      if (response.ruleName != null) response.ruleName!,
      if (response.category != null) response.category!,
      if (response.matchedKeywords.isNotEmpty)
        // Join keywords into one part so the reason box remains compact.
        response.matchedKeywords.join(', '),
    ];

    return EmergencyReason(parts);
  }

  /// Whether there is any detail worth rendering.
  bool get hasDetails => parts.isNotEmpty;

  /// Single display string used by the warning reason box.
  String get label => parts.join(' | ');
}
