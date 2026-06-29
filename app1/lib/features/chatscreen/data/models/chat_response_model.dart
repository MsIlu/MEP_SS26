class CaseObservation {
  final String label;
  final int? severity;

  const CaseObservation({required this.label, this.severity});

  factory CaseObservation.fromJson(Map<String, dynamic> json) {
    final rawSeverity = json['severity'];
    int? parsedSeverity;
    if (rawSeverity is int) {
      parsedSeverity = rawSeverity;
    } else if (rawSeverity is String) {
      parsedSeverity = int.tryParse(rawSeverity);
    }
    return CaseObservation(
      label: json['label']?.toString() ?? '',
      severity: parsedSeverity,
    );
  }
}

/// Structured response returned by the chat backend.
class RecommendationResult {
  final bool allowed;
  final String? summary;
  final String urgency;
  final String urgencyLevel;
  final String careLevel;
  final String specialty;
  final List<String> reasons;
  final String? nextStep;
  final List<String> limitations;

  const RecommendationResult({
    required this.allowed,
    this.summary,
    required this.urgency,
    required this.urgencyLevel,
    required this.careLevel,
    required this.specialty,
    this.reasons = const [],
    this.nextStep,
    this.limitations = const [],
  });

  factory RecommendationResult.fromJson(Map<String, dynamic> json) {
    return RecommendationResult(
      allowed: json['allowed'] == true,
      summary: json['summary']?.toString(),
      urgency: json['urgency']?.toString() ?? 'unknown',
      urgencyLevel: json['urgency_level']?.toString() ?? 'unclear',
      careLevel: json['care_level']?.toString() ?? 'unknown',
      specialty: json['specialty']?.toString() ?? 'unknown',
      reasons: (json['reasons'] as List<dynamic>?)
          ?.map((item) => item.toString())
          .toList() ??
          const [],
      nextStep: json['next_step']?.toString(),
      limitations: (json['limitations'] as List<dynamic>?)
          ?.map((item) => item.toString())
          .toList() ??
          const [],
    );
  }
}

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

  final String? responseMode;
  final bool recommendationReady;
  final RecommendationResult? recommendationResult;

  /// Structured reply options provided by the backend (non-empty only for
  /// ask_safety_question responses). Used to populate smart reply chips.
  final List<String> replyOptions;

  /// Active observations from the medical case, including their severity when known.
  final List<CaseObservation> caseObservations;

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
    this.responseMode,
    this.recommendationReady = false,
    this.recommendationResult,
    this.replyOptions = const [],
    this.caseObservations = const [],
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
      responseMode: json['response_mode']?.toString(),
      recommendationReady: json['recommendation_ready'] == true,
      recommendationResult: json['recommendation_result'] is Map<String, dynamic>
          ? RecommendationResult.fromJson(
        json['recommendation_result'] as Map<String, dynamic>,
      )
          : null,
      replyOptions:
          (json['reply_options'] as List<dynamic>?)
              ?.map((item) => item.toString())
              .toList() ??
          const [],
      caseObservations:
          (json['case_observations'] as List<dynamic>?)
              ?.whereType<Map<String, dynamic>>()
              .map(CaseObservation.fromJson)
              .where((o) => o.label.isNotEmpty)
              .toList() ??
          const [],
    );
  }
}