import 'package:flutter/material.dart';
import '../../../../core/widgets/responsive_frame.dart';
import '../../../../core/widgets/careena_page_header.dart';
import '../../../chatscreen/data/models/chat_response_model.dart';
import '../../../chatscreen/data/models/message_model.dart';
import 'package:app1/core/themes/app_colors.dart';
import 'package:app1/core/themes/theme_controller.dart';
import 'package:app1/app/app_dependencies_scope.dart';
import '../../../symptom_diary/data/symptom_import.dart';
import '../../../symptom_diary/presentation/screens/symptom_diary_page.dart';
import '../theme/warning_copy.dart';
import '../theme/warning_layout.dart';
import '../widgets/emergency_card.dart';
import '../widgets/no_diagnosis_info_box.dart';
import '../../../authscreen/state/auth_session.dart';
import '../../../recommendation_export/presentation/create_recommended_appointment_button.dart';
import '../../../recommendation_export/presentation/export_recommendation_pdf_button.dart';
import '../../../recommendation_export/presentation/save_recommendation_to_documents_button.dart';

/// Recommendation result page shown after a chat session is completed.
class WarningPage extends StatelessWidget {
  final ChatResponse response;
  final List<String> symptoms;
  final List<String> userMessages;
  final ThemeController? themeController;

  /// Symptom data enriched via the in-chat editor (body area + intensity).
  /// Takes priority over [response.caseObservations] when building the diary import list.
  final List<SymptomImport>? enrichedSymptoms;
  final String? sessionId;
  final AuthSession? authSession;
  final Message? recommendationMessage;
  final Future<void> Function(RecommendationAction)? onRecommendationAction;

  const WarningPage({
    super.key,
    required this.response,
    this.symptoms = const [],
    this.userMessages = const [],
    this.themeController,
    this.enrichedSymptoms,
    this.sessionId,
    this.authSession,
    this.recommendationMessage,
    this.onRecommendationAction,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;
    final showEmergencyActions = _showEmergencyActions(response);

    final backgroundColor = isDarkMode
        ? colorScheme.surface
        : AppColors.background;

    return Scaffold(
      backgroundColor: backgroundColor,
      appBar: const CareenaPageHeader(title: WarningCopy.pageTitle),
      body: SafeArea(
        child: ResponsivePageBody(
          maxWidth: WarningLayout.maxContentWidth,
          scrollable: true,
          padding: WarningLayout.pagePadding,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              if (showEmergencyActions)
                EmergencyCard(response: response)
              else
                _RecommendationCard(
                  response: response,
                  symptoms: symptoms,
                  userMessages: userMessages,
                ),
              const SizedBox(height: 16),

              ExportRecommendationPdfButton(
                title: WarningCopy.pageTitle,
                patientSummary:
                    'Aus dem Chatverlauf generierte Handlungsempfehlung.',
                recommendation: _recommendationTextFor(response),
                nextSteps:
                    response.recommendationResult?.nextStep ??
                    response.action ??
                    'Bitte folge den angezeigten Handlungsschritten. Bei akuter Gefahr kontaktiere den Notruf 112.',
                symptoms: symptoms,
                userMessages: userMessages,
              ),

              const SizedBox(height: 8),
              SaveRecommendationToDocumentsButton(
                title: WarningCopy.pageTitle,
                patientSummary:
                    'Aus dem Chatverlauf generierte Handlungsempfehlung.',
                recommendation: _recommendationTextFor(response),
                nextSteps:
                    response.recommendationResult?.nextStep ??
                    response.action ??
                    '',
                symptoms: symptoms,
                userMessages: userMessages,
                alreadySaved: recommendationMessage?.documentSaved ?? false,
                onSaved: () async {
                  await _markAction(RecommendationAction.document);
                },
              ),

              if ((symptoms.isNotEmpty ||
                      response.caseObservations.isNotEmpty) &&
                  themeController != null) ...[
                const SizedBox(height: 8),
                _WarningSymptomButton(
                  isCompleted: recommendationMessage?.symptomsSaved == true,
                  onPressed: () => _navigateToSymptomDiary(context),
                ),
              ],

              if (!showEmergencyActions && sessionId != null) ...[
                const SizedBox(height: 16),
                CreateRecommendedAppointmentButton(
                  title:
                      response.recommendationResult?.nextStep ??
                      response.action ??
                      'Termin finden',
                  authSession: authSession,
                  sessionId: sessionId,
                  alreadySearched:
                      recommendationMessage?.appointmentSearched ?? false,
                  onSearched: () async {
                    await _markAction(RecommendationAction.appointment);
                  },
                ),
              ],

              const SizedBox(height: 16),
              const NoDiagnosisInfoBox(),
            ],
          ),
        ),
      ),
    );
  }

  List<SymptomImport> _buildSymptomImports() {
    // User-enriched data (set via the in-chat editor) takes priority.
    final enriched = enrichedSymptoms;
    if (enriched != null && enriched.isNotEmpty) return enriched;
    // Backend observations carry the severity extracted from the conversation.
    final observations = response.caseObservations;
    if (observations.isNotEmpty) {
      return observations
          .map(
            (o) => SymptomImport(
              name: o.label,
              severity: o.severity,
              date: o.date,
            ),
          )
          .toList();
    }
    return symptoms.map((s) => SymptomImport(name: s)).toList();
  }

  Future<void> _markAction(RecommendationAction action) async {
    await onRecommendationAction?.call(action);
  }

  Future<bool> _navigateToSymptomDiary(BuildContext context) async {
    final tc = themeController;
    if (tc == null) return false;
    final deps = AppDependenciesScope.of(context);
    var saved = false;
    await Navigator.push<void>(
      context,
      MaterialPageRoute(
        builder: (_) => SymptomDiaryPage(
          themeController: tc,
          authSession: deps.authSession,
          symptomApiService: deps.symptomApiService,
          profileApiService: deps.profileApiService,
          initialSymptoms: _buildSymptomImports(),
          onInitialSymptomsSaved: () async {
            await _markAction(RecommendationAction.symptoms);
            saved = true;
          },
        ),
      ),
    );
    return saved;
  }
}

class _WarningSymptomButton extends StatefulWidget {
  final bool isCompleted;
  final Future<bool> Function() onPressed;

  const _WarningSymptomButton({
    required this.isCompleted,
    required this.onPressed,
  });

  @override
  State<_WarningSymptomButton> createState() => _WarningSymptomButtonState();
}

class _WarningSymptomButtonState extends State<_WarningSymptomButton> {
  bool _isLoading = false;
  late bool _isCompleted;

  @override
  void initState() {
    super.initState();
    _isCompleted = widget.isCompleted;
  }

  @override
  void didUpdateWidget(covariant _WarningSymptomButton oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.isCompleted) _isCompleted = true;
  }

  @override
  Widget build(BuildContext context) {
    return Tooltip(
      message: _isCompleted
          ? 'Symptome im Tagebuch gespeichert'
          : 'Symptome ins Tagebuch übernehmen',
      child: OutlinedButton.icon(
        style: OutlinedButton.styleFrom(
          foregroundColor: AppColors.careenaTeal,
          side: const BorderSide(color: AppColors.careenaTeal),
          padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(18),
          ),
        ),
        onPressed: _isCompleted || _isLoading ? null : _run,
        icon: _isLoading
            ? const SizedBox.square(
                dimension: 18,
                child: CircularProgressIndicator(strokeWidth: 2),
              )
            : Icon(
                _isCompleted ? Icons.check_circle_outline : Icons.book_outlined,
              ),
        label: Text(
          _isCompleted ? 'Bereits gespeichert' : 'Symptome speichern',
        ),
      ),
    );
  }

  Future<void> _run() async {
    setState(() => _isLoading = true);
    try {
      final completed = await widget.onPressed();
      if (mounted && completed) setState(() => _isCompleted = true);
    } catch (_) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Symptome konnten nicht geöffnet werden')),
      );
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }
}

bool _showEmergencyActions(ChatResponse response) {
  if (response.redFlag) return true;
  // Use the structured urgency field from the recommendation result — the
  // backend classifier is the source of truth. Text keyword scanning is
  // unreliable because routine advisory language includes words like "sofort"
  // and "112" even for non-emergency recommendations.
  return response.recommendationResult?.urgency == 'emergency';
}

String _recommendationTextFor(ChatResponse response) {
  final chatText = response.text.trim();
  if (chatText.isNotEmpty) {
    return chatText;
  }
  return response.recommendationResult?.summary ?? '';
}

class _RecommendationCard extends StatelessWidget {
  final ChatResponse response;
  final List<String> symptoms;
  final List<String> userMessages;

  const _RecommendationCard({
    required this.response,
    required this.symptoms,
    required this.userMessages,
  });

  @override
  Widget build(BuildContext context) {
    final recommendation = response.recommendationResult;
    final colorScheme = Theme.of(context).colorScheme;
    final reasons = _recommendationReasonsFor(
      response,
      symptoms: symptoms,
      userMessages: userMessages,
    );
    final nextStep =
        recommendation?.nextStep ??
        response.action ??
        _legacySectionFromChatText(response.text, 'Nächster Schritt');
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;
    final accent = AppColors.primary;

    return Container(
      padding: WarningLayout.cardPadding,
      decoration: BoxDecoration(
        color: colorScheme.surface,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(
          color: isDarkMode
              ? accent.withValues(alpha: 0.72)
              : accent.withValues(alpha: 0.42),
          width: 1.4,
        ),
        boxShadow: [
          BoxShadow(
            color: AppColors.black.withValues(alpha: isDarkMode ? 0.18 : 0.05),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              CircleAvatar(
                radius: 42,
                backgroundColor: accent.withValues(alpha: 0.14),
                child: Icon(
                  Icons.warning_amber_rounded,
                  color: accent,
                  size: 40,
                ),
              ),
              const SizedBox(width: 22),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Text(
                      'Kein Notfall erkannt',
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        color: accent,
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                    const SizedBox(height: 14),
                    Text(
                      'Auf Grundlage deiner Angaben besteht derzeit kein Hinweis auf einen akuten Notfall.',
                      style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                        fontWeight: FontWeight.w700,
                        height: 1.35,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 22),
          _RecommendationDivider(color: accent),
          const SizedBox(height: 18),
          Text(
            'Was solltest du jetzt tun?',
            style: Theme.of(
              context,
            ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w900),
          ),
          if (nextStep != null && nextStep.trim().isNotEmpty) ...[
            const SizedBox(height: 16),
            _RecommendationActionRow(
              icon: Icons.event_available_outlined,
              text: nextStep,
              color: accent,
            ),
          ],
          if (reasons.isNotEmpty) ...[
            const SizedBox(height: 16),
            _RecommendationDivider(color: accent),
            const SizedBox(height: 16),
            _RecommendationActionRow(
              icon: Icons.fact_check_outlined,
              text: reasons.join('\n'),
              color: accent,
              title: 'Gründe',
            ),
          ],
        ],
      ),
    );
  }
}

List<String> _recommendationReasonsFor(
  ChatResponse response, {
  required List<String> symptoms,
  required List<String> userMessages,
}) {
  final chatReason = _chatReasonFromRecommendationText(response.text);
  final concreteReasons = <String>[
    ?chatReason,
    ...userMessages.map(_userMessageReason),
    ...(response.recommendationResult?.reasons ?? const <String>[])
        .where((reason) => !_isGenericReason(reason))
        .map(_normalizeGermanText),
    ...symptoms.map(_normalizeGermanText),
  ];

  return _summarizeReasons(concreteReasons);
}

List<String> _summarizeReasons(Iterable<String> reasons) {
  final seen = <String>{};
  final uniqueReasons = reasons
      .map((reason) => reason.trim())
      .where((reason) => reason.isNotEmpty && !_isShortConfirmation(reason))
      .where((reason) => seen.add(_reasonKey(reason)))
      .toList(growable: false);

  return uniqueReasons
      .where((reason) => !_isContainedInBetterReason(reason, uniqueReasons))
      .toList(growable: false);
}

bool _isShortConfirmation(String reason) {
  final normalized = reason.toLowerCase();
  return normalized == 'ja' || normalized == 'nein' || normalized == 'ok';
}

bool _isContainedInBetterReason(String reason, List<String> allReasons) {
  final key = _reasonKey(reason);
  if (key.length < 4) return true;
  final tokens = _reasonTokens(reason);

  return allReasons.any((candidate) {
    final candidateKey = _reasonKey(candidate);
    return candidateKey != key &&
        candidateKey.length > key.length &&
        (candidateKey.contains(key) ||
            tokens.difference(_reasonTokens(candidate)).isEmpty);
  });
}

String _reasonKey(String reason) {
  return reason.toLowerCase().replaceAll(RegExp(r'[^a-zäöüß0-9]+'), ' ').trim();
}

Set<String> _reasonTokens(String reason) {
  return _reasonKey(
    reason,
  ).split(' ').where((token) => token.length > 1).toSet();
}

String _userMessageReason(String message) {
  final cleaned = _normalizeGermanText(message)
      .replaceFirst(
        RegExp(
          r'^\s*(ich\s+(habe|hab|hatte|spüre|fühle)\s+|mir\s+ist\s+)',
          caseSensitive: false,
        ),
        '',
      )
      .trim();
  if (cleaned.isEmpty) return '';
  return cleaned[0].toUpperCase() + cleaned.substring(1);
}

String? _chatReasonFromRecommendationText(String text) {
  // Prefer the old chat text because it contains the user's concrete details.
  final source = _legacySectionFromChatText(text, 'Orientierung') ?? text;
  final match = RegExp(
    r'\bBei\s+(.+?)(?:\s+(?:gibt|liegt|liegen|besteht|bestehen)\b|[,.])',
    caseSensitive: false,
    dotAll: true,
  ).firstMatch(source);
  final reason = match?.group(1)?.trim();
  if (reason == null || reason.isEmpty) return null;
  return _normalizeGermanText(reason.replaceAll('**', ''));
}

bool _isGenericReason(String reason) {
  final normalized = reason.toLowerCase();
  return normalized.contains('ausreichend angaben') ||
      normalized.contains('ausreichend informationen');
}

String? _legacySectionFromChatText(String text, String label) {
  final marker = '**$label:**';
  final start = text.indexOf(marker);
  if (start < 0) return null;

  final body = text.substring(start + marker.length).trim();
  final end = body.indexOf('\n\n');
  final section = end < 0 ? body : body.substring(0, end);
  return _normalizeGermanText(section.replaceAll('**', '').trim());
}

String _normalizeGermanText(String text) {
  return text
      .replaceAll('Uebel', 'Übel')
      .replaceAll('uebel', 'übel')
      .replaceAll('aerzt', 'ärzt')
      .replaceAll('Aerzt', 'Ärzt')
      .replaceAll('fuer', 'für')
      .replaceAll('Fuer', 'Für')
      .replaceAll('koerper', 'körper')
      .replaceAll('Koerper', 'Körper')
      .replaceAll('Ruecken', 'Rücken')
      .replaceAll('ruecken', 'rücken')
      .replaceAll('Huefte', 'Hüfte')
      .replaceAll('huefte', 'hüfte')
      .replaceAll('Fuesse', 'Füße')
      .replaceAll('fuesse', 'füße');
}

class _RecommendationActionRow extends StatelessWidget {
  final IconData icon;
  final String text;
  final Color color;
  final String? title;

  const _RecommendationActionRow({
    required this.icon,
    required this.text,
    required this.color,
    this.title,
  });

  @override
  Widget build(BuildContext context) {
    final lines = text
        .split('\n')
        .map((line) => line.trim())
        .where((line) => line.isNotEmpty)
        .toList(growable: false);

    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        CircleAvatar(
          radius: 18,
          backgroundColor: color.withValues(alpha: 0.12),
          child: Icon(icon, color: color, size: 20),
        ),
        const SizedBox(width: 14),
        Expanded(
          child: Padding(
            padding: const EdgeInsets.only(top: 3),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                if (title != null) ...[
                  Text(
                    title!,
                    style: const TextStyle(fontWeight: FontWeight.w900),
                  ),
                  const SizedBox(height: 6),
                ],
                for (final line in lines)
                  Padding(
                    padding: const EdgeInsets.only(bottom: 4),
                    child: Text(
                      title == null
                          ? _normalizeGermanText(line)
                          : '• ${_normalizeGermanText(line)}',
                      style: const TextStyle(height: 1.35),
                    ),
                  ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}

class _RecommendationDivider extends StatelessWidget {
  final Color color;

  const _RecommendationDivider({required this.color});

  @override
  Widget build(BuildContext context) {
    return Container(height: 1, color: color.withValues(alpha: 0.28));
  }
}
