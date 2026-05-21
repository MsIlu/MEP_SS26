import '../../../chatscreen/data/models/chat_response_model.dart';

class EmergencyReason {
  final List<String> parts;

  const EmergencyReason(this.parts);

  factory EmergencyReason.fromResponse(ChatResponse response) {
    final parts = <String>[
      if (response.ruleName != null) response.ruleName!,
      if (response.category != null) response.category!,
      if (response.matchedKeywords.isNotEmpty)
        response.matchedKeywords.join(', '),
    ];

    return EmergencyReason(parts);
  }

  bool get hasDetails => parts.isNotEmpty;

  String get label => parts.join(' | ');
}
