class ChatResponse {
  final String text;
  final bool redFlag;
  final String? severity;
  final String? action;
  final String? ruleId;
  final String? ruleName;
  final String? category;
  final String? messageKey;
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

  factory ChatResponse.fromJson(Map<String, dynamic> json) {
    return ChatResponse(
      text: json['response'] ?? 'Ungültige Serverantwort',
      redFlag: json['red_flag'] == true,
      severity: json['severity'],
      action: json['action'],
      ruleId: json['rule_id'],
      ruleName: json['rule_name'],
      category: json['category'],
      messageKey: json['message_key'],
      matchedKeywords: (json['matched_keywords'] as List<dynamic>?)
              ?.map((item) => item.toString())
              .toList() ??
          const [],
    );
  }
}