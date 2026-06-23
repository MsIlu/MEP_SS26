import 'dart:async';
import '../data/models/chat_response_model.dart';
import '../data/models/message_model.dart';

/// Handles chat-domain message operations without depending on Flutter UI state.
class ChatService {
  static const Duration defaultTypingDelay = Duration(milliseconds: 15);

  List<Message> addMessage({
    required List<Message> messages,
    required Message message,
  }) {
    return List<Message>.from(messages)..add(message);
  }

  List<Message> removeLastBotMessage(List<Message> messages) {
    final updated = List<Message>.from(messages);

    for (int i = updated.length - 1; i >= 0; i--) {
      if (!updated[i].isUser) {
        updated.removeAt(i);
        break;
      }
    }

    return updated;
  }

  List<Message> replaceLastMessage({
    required List<Message> messages,
    required Message message,
  }) {
    if (messages.isEmpty) {
      return [message];
    }

    final updated = List<Message>.from(messages);
    updated[updated.length - 1] = message;
    return updated;
  }

  Message buildAssistantMessage(ChatResponse response) {
    final recommendation = response.recommendationResult;
    final canExport = isFinalRecommendation(response);
    final canCreateAppointment = hasAppointmentRecommendation(response);

    return Message(
      text: response.text,
      isUser: false,
      canExportPdf: canExport,
      exportTitle: 'Handlungsempfehlung',
      exportRecommendation: recommendation?.summary ?? response.text,
      exportNextSteps: recommendation?.nextStep ?? response.action,
      canCreateAppointment: canCreateAppointment,
      appointmentTitle: canCreateAppointment
          ? appointmentTitleForRecommendation(response.text)
          : null,
    );
  }

  bool isFinalRecommendation(ChatResponse response) {
    return response.responseMode == 'recommend' &&
        response.recommendationResult?.allowed == true;
  }

  bool hasRecommendation(ChatResponse response) {
    if (isFinalRecommendation(response)) {
      return true;
    }

    final responseText = response.text.toLowerCase();

    return (response.action != null && response.action!.trim().isNotEmpty) ||
        responseText.contains('dringlichkeit:') ||
        responseText.contains('empfohlene versorgungsebene:') ||
        responseText.contains('nächster schritt:') ||
        responseText.contains('naechster schritt:') ||
        responseText.contains('hinweis:');
  }

  bool hasAppointmentRecommendation(ChatResponse response) {
    final careLevel = response.recommendationResult?.careLevel;

    if (response.responseMode == 'recommend' &&
        response.recommendationResult?.allowed == true) {
      return careLevel == 'general_practice' ||
          careLevel == 'specialist' ||
          careLevel == '116117' ||
          careLevel == 'emergency_department';
    }

    final responseText = response.text.toLowerCase();
    final actionText = response.action?.toLowerCase() ?? '';
    final combinedText = '$responseText $actionText';

    return combinedText.contains('hausarzt') ||
        combinedText.contains('facharzt') ||
        combinedText.contains('arztbesuch') ||
        combinedText.contains('arzttermin') ||
        combinedText.contains('ärztlich') ||
        combinedText.contains('aerztlich');
  }

  String _appointmentTitleForRecommendation(ChatResponse response) {
    final careLevel = response.recommendationResult?.careLevel;

    if (careLevel == 'general_practice') {
      return 'Hausarzttermin vereinbaren';
    }

    if (careLevel == 'specialist') {
      return 'Facharzttermin vereinbaren';
    }

    if (careLevel == '116117') {
      return 'Termin über 116117 prüfen';
    }

    if (careLevel == 'emergency_department') {
      return 'Ärztliche Abklärung organisieren';
    }

    return 'Arzttermin vereinbaren';
  }

  bool isEmergencyRecommendation(ChatResponse response) {
    final responseText = response.text.toLowerCase();
    final actionText = response.action?.toLowerCase() ?? '';
    final severityText = response.severity?.toLowerCase() ?? '';
    final ruleText = response.ruleName?.toLowerCase() ?? '';
    final categoryText = response.category?.toLowerCase() ?? '';
    final messageKeyText = response.messageKey?.toLowerCase() ?? '';
    final matchedKeywordText = response.matchedKeywords.join(' ').toLowerCase();
    final combinedText =
        '$responseText $actionText $severityText $ruleText '
        '$categoryText $messageKeyText $matchedKeywordText';

    return response.redFlag ||
        severityText.contains('sofort') ||
        severityText.contains('hoch') ||
        severityText.contains('high') ||
        severityText.contains('emergency') ||
        categoryText.contains('emergency') ||
        categoryText.contains('notfall') ||
        combinedText.contains('notruf 112') ||
        combinedText.contains('112') ||
        combinedText.contains('notruf') ||
        combinedText.contains('rettungsdienst') ||
        combinedText.contains('notarzt') ||
        combinedText.contains('akute notfallsituation') ||
        combinedText.contains('akuter notfall') ||
        combinedText.contains('sofort medizinische hilfe') ||
        combinedText.contains('notaufnahme') ||
        combinedText.contains('umgehend medizinische hilfe') ||
        combinedText.contains('wählen sie sofort') ||
        combinedText.contains('waehlen sie sofort') ||
        combinedText.contains('rufen sie sofort') ||
        combinedText.contains('holen sie umgehend') ||
        combinedText.contains('lebensgefahr');
  }

  Stream<String> streamText(
    String fullText, {
    Duration delay = defaultTypingDelay,
  }) async* {
    var current = '';

    for (final codePoint in fullText.runes) {
      await Future.delayed(delay);
      current += String.fromCharCode(codePoint);
      yield current;
    }
  }
}
