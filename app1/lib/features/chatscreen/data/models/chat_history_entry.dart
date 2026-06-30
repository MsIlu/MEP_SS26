import 'dart:convert';

import 'message_model.dart';

class ChatHistoryEntry {
  final String id;
  final int? profileId;
  final String? sessionId;
  final String? symptomTitle;
  final String status;
  final bool isEmergency;
  final DateTime createdAt;
  final DateTime? updatedAt;
  final List<Message> messages;
  final String recommendation;
  final String? nextSteps;

  const ChatHistoryEntry({
    required this.id,
    required this.profileId,
    this.sessionId,
    this.symptomTitle,
    this.status = 'completed',
    this.isEmergency = false,
    required this.createdAt,
    this.updatedAt,
    required this.messages,
    required this.recommendation,
    this.nextSteps,
  });

  String get title {
    final normalizedTitle = symptomTitle?.trim();
    if (normalizedTitle != null && normalizedTitle.isNotEmpty) {
      return _oneWordTitle(normalizedTitle);
    }

    return 'Verlauf';
  }

  String get preview {
    final firstMessage = _firstUserMessage;
    if (firstMessage == null) {
      return recommendation;
    }

    return firstMessage;
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'profile_id': profileId,
      'session_id': sessionId,
      'title': symptomTitle,
      'status': status,
      'is_emergency': isEmergency,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt?.toIso8601String(),
      'recommendation': recommendation,
      'next_steps': nextSteps,
      'messages': messages.map(_messageToJson).toList(),
    };
  }

  String encode() => jsonEncode(toJson());

  factory ChatHistoryEntry.decode(String encodedEntry) {
    return ChatHistoryEntry.fromJson(
      jsonDecode(encodedEntry) as Map<String, dynamic>,
    );
  }

  factory ChatHistoryEntry.fromJson(Map<String, dynamic> json) {
    final rawMessages = json['messages'] as List<dynamic>? ?? const [];

    return ChatHistoryEntry(
      id: json['id'].toString(),
      profileId: json['profile_id'] as int,
      sessionId: json['session_id'] as String?,
      symptomTitle: json['title'] as String?,
      status: json['status'] as String? ?? 'completed',
      isEmergency: json['is_emergency'] == true,
      createdAt: _parseServerDateTime(json['created_at'] as String),
      updatedAt: json['updated_at'] == null
          ? null
          : _parseServerDateTime(json['updated_at'] as String),
      recommendation: json['recommendation'] as String? ?? '',
      nextSteps: json['next_steps'] as String?,
      messages: rawMessages
          .map((item) => _messageFromJson(item as Map<String, dynamic>))
          .toList(),
    );
  }

  static DateTime _parseServerDateTime(String value) {
    final parsed = DateTime.parse(value);

    if (parsed.isUtc) {
      return parsed.toLocal();
    }

    return DateTime.utc(
      parsed.year,
      parsed.month,
      parsed.day,
      parsed.hour,
      parsed.minute,
      parsed.second,
      parsed.millisecond,
      parsed.microsecond,
    ).toLocal();
  }

  static Map<String, dynamic> _messageToJson(Message message) {
    return {
      'text': message.text,
      'is_user': message.isUser,
      'timestamp': message.timestamp?.toIso8601String(),
      'can_export_pdf': message.canExportPdf,
      'export_title': message.exportTitle,
      'export_recommendation': message.exportRecommendation,
      'export_next_steps': message.exportNextSteps,
    };
  }

  static Message _messageFromJson(Map<String, dynamic> json) {
    return Message(
      text: json['text'] as String? ?? '',
      isUser: json['is_user'] == true,
      timestamp: DateTime.tryParse(json['timestamp'] as String? ?? ''),
      canExportPdf: json['can_export_pdf'] == true,
      exportTitle: json['export_title'] as String?,
      exportRecommendation: json['export_recommendation'] as String?,
      exportNextSteps: json['export_next_steps'] as String?,
    );
  }

  String? get _firstUserMessage {
    for (final message in messages) {
      final text = message.text.trim();
      if (message.isUser && text.isNotEmpty) {
        return text;
      }
    }

    return null;
  }

  static String _oneWordTitle(String rawText) {
    final words = rawText
        .replaceAll(RegExp(r'^[\-*•]\s*'), '')
        .split(RegExp(r'[\s,.;:!?/()]+'))
        .where((word) => word.trim().isNotEmpty)
        .toList();

    return words.isEmpty ? 'Verlauf' : words.first.trim();
  }
}
