/// Structured response returned by the chat backend.
///
/// A response can be either a normal assistant answer or a red-flag result that
/// should redirect the user to the warning flow.
/// TODO: add other "Handlungsempfehlungen"
class ChatResponse {
  /// Text intended for the normal chat bubble or warning explanation.
  final String text;

  /// True when the backend detected a medical red flag.
  final bool redFlag;

  /// Optional backend severity for red-flag classification.
  final String? severity;

  /// Optional recommended next action supplied by the backend rule.
  final String? action;

  /// Identifier of the matched backend safety rule.
  final String? ruleId;

  /// Human-readable name of the matched backend safety rule.
  final String? ruleName;

  /// Medical or safety category reported by the backend.
  final String? category;

  /// Optional translation or message key for backend-provided copy.
  final String? messageKey;

  /// Keywords that triggered the red-flag rule.
  final List<String> matchedKeywords;

  const ChatResponse({
    required this.text,
    required this.redFlag,
    this.severity,
    this.action,
    this.ruleId,
    this.ruleName,
    this.category,
    this.messageKey,
    this.matchedKeywords = const [],
  });

  /// Maps raw JSON from the backend into a typed chat response.
  factory ChatResponse.fromJson(Map<String, dynamic> json) {
    return ChatResponse(
      text: json['response']?.toString() ?? 'Ungültige Serverantwort',
      redFlag: json['red_flag'] == true,
      severity: json['severity']?.toString(),
      action: json['action']?.toString(),
      ruleId: json['rule_id']?.toString(),
      ruleName: json['rule_name']?.toString(),
      category: json['category']?.toString(),
      messageKey: json['message_key']?.toString(),
      matchedKeywords:
          (json['matched_keywords'] as List<dynamic>?)
              ?.map((item) => item.toString())
              .toList() ??
          const [],
    );
  }
}