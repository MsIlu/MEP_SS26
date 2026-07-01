import 'package:flutter/material.dart';
import '../../../../core/widgets/responsive_frame.dart';
import '../../../../core/widgets/careena_page_header.dart';
import '../../../chatscreen/data/models/chat_response_model.dart';
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

  const WarningPage({
    super.key,
    required this.response,
    this.symptoms = const [],
    this.userMessages = const [],
    this.themeController,
    this.enrichedSymptoms,
    this.sessionId,
    this.authSession,
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
                    (response.recommendationResult?.summary?.trim().isNotEmpty ??
                            false)
                        ? _normalizeGermanText(
                            response.recommendationResult!.summary!.trim(),
                          )
                        : 'Aus dem Chatverlauf generierte Handlungsempfehlung.',
                recommendation: _recommendationTextFor(response),
                nextSteps:
                    response.recommendationResult?.nextStep ??
                    response.action ??
                    'Bitte folge den angezeigten Handlungsschritten. Bei akuter Gefahr kontaktiere den Notruf 112.',
                symptoms: symptoms,
                userMessages: userMessages,
                recommendationResult: response.recommendationResult,
                profileId: response.profileId,
              ),

              if ((symptoms.isNotEmpty || response.caseObservations.isNotEmpty) && themeController != null) ...[
                const SizedBox(height: 8),
                OutlinedButton.icon(
                  onPressed: () => _navigateToSymptomDiary(context),
                  icon: const Icon(Icons.book_outlined, size: 18),
                  label: const Text('Symptome ins Tagebuch'),
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
          .map((o) => SymptomImport(name: o.label, severity: o.severity, date: o.date))
          .toList();
    }
    return symptoms.map((s) => SymptomImport(name: s)).toList();
  }

  void _navigateToSymptomDiary(BuildContext context) {
    final tc = themeController;
    if (tc == null) return;
    final deps = AppDependenciesScope.of(context);
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => SymptomDiaryPage(
          themeController: tc,
          authSession: deps.authSession,
          symptomApiService: deps.symptomApiService,
          profileApiService: deps.profileApiService,
          initialSymptoms: _buildSymptomImports(),
        ),
      ),
    );
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
    final care = _CareLevelPresentation.fromResponse(response);
    final reasons = _recommendationReasonsFor(
      response,
      symptoms: symptoms,
      userMessages: userMessages,
    );
    final summary = recommendation?.summary?.trim() ?? '';
    final nextStep =
        recommendation?.nextStep ??
        response.action ??
        _legacySectionFromChatText(response.text, 'Nächster Schritt');
    final dataSources = recommendation?.dataSources ?? const <String>[];
    final isDarkMode = Theme.of(context).brightness == Brightness.dark;

    return Container(
      padding: WarningLayout.cardPadding,
      decoration: BoxDecoration(
        color: colorScheme.surface,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(
          color: isDarkMode
              ? care.color.withValues(alpha: 0.72)
              : care.color.withValues(alpha: 0.42),
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
                backgroundColor: care.color.withValues(alpha: 0.14),
                child: Icon(care.icon, color: care.color, size: 40),
              ),
              const SizedBox(width: 22),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Text(
                      care.headline,
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                            color: care.color,
                            fontWeight: FontWeight.w900,
                          ),
                    ),
                    const SizedBox(height: 14),
                    Text(
                      care.subtitle,
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
          const SizedBox(height: 18),
          _CareLevelBadge(presentation: care),
          if (summary.isNotEmpty) ...[
            const SizedBox(height: 18),
            _RecommendationDivider(color: care.color),
            const SizedBox(height: 16),
            _RecommendationActionRow(
              icon: Icons.summarize_outlined,
              text: _normalizeGermanText(summary),
              color: care.color,
              title: 'Einschätzung',
            ),
          ],
          const SizedBox(height: 18),
          _RecommendationDivider(color: care.color),
          const SizedBox(height: 18),
          Text(
            'Was solltest du jetzt tun?',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w900,
                ),
          ),
          if (nextStep != null && nextStep.trim().isNotEmpty) ...[
            const SizedBox(height: 16),
            _RecommendationActionRow(
              icon: Icons.event_available_outlined,
              text: nextStep,
              color: care.color,
            ),
          ],
          if (reasons.isNotEmpty) ...[
            const SizedBox(height: 16),
            _RecommendationDivider(color: care.color),
            const SizedBox(height: 16),
            _RecommendationActionRow(
              icon: Icons.fact_check_outlined,
              text: reasons.join('\n'),
              color: care.color,
              title: 'Gründe',
            ),
          ],
          if (dataSources.isNotEmpty) ...[
            const SizedBox(height: 18),
            _RecommendationDivider(color: care.color),
            const SizedBox(height: 14),
            _DataSourcesSection(sources: dataSources, color: care.color),
          ],
        ],
      ),
    );
  }
}

/// Visual presentation (label, color, icon, copy) derived from the backend
/// `care_level` so the recommendation header reflects the actual escalation
/// stage instead of a hardcoded "Kein Notfall erkannt".
class _CareLevelPresentation {
  final String label;
  final String headline;
  final String subtitle;
  final IconData icon;
  final Color color;

  const _CareLevelPresentation({
    required this.label,
    required this.headline,
    required this.subtitle,
    required this.icon,
    required this.color,
  });

  static _CareLevelPresentation fromResponse(ChatResponse response) {
    final careLevel = response.recommendationResult?.careLevel ?? 'unknown';
    switch (careLevel) {
      case 'self_care':
        return const _CareLevelPresentation(
          label: 'Selbstbehandlung',
          headline: 'Selbstbehandlung möglich',
          subtitle:
              'Deine Angaben sprechen für Beschwerden, die du voraussichtlich '
              'selbst zu Hause lindern kannst.',
          icon: Icons.self_improvement_outlined,
          color: Color(0xFF2E7D32),
        );
      case 'pharmacy':
        return const _CareLevelPresentation(
          label: 'Apotheke',
          headline: 'Rat in der Apotheke',
          subtitle:
              'Eine Beratung in der Apotheke und rezeptfreie Mittel sind hier '
              'voraussichtlich ausreichend.',
          icon: Icons.local_pharmacy_outlined,
          color: Color(0xFF00897B),
        );
      case 'general_practice':
        return const _CareLevelPresentation(
          label: 'Hausarztpraxis',
          headline: 'Hausärztliche Abklärung',
          subtitle:
              'Deine Beschwerden sollten in einer Hausarztpraxis abgeklärt '
              'werden – nicht dringend, aber zeitnah.',
          icon: Icons.medical_services_outlined,
          color: Color(0xFF1565C0),
        );
      case 'specialist':
        return const _CareLevelPresentation(
          label: 'Facharztpraxis',
          headline: 'Fachärztliche Abklärung',
          subtitle:
              'Für deine Beschwerden ist eine gezielte fachärztliche '
              'Abklärung sinnvoll.',
          icon: Icons.medical_services_outlined,
          color: Color(0xFF3949AB),
        );
      case '116117':
        return const _CareLevelPresentation(
          label: 'Bereitschaftsdienst 116117',
          headline: 'Ärztlicher Bereitschaftsdienst',
          subtitle:
              'Außerhalb der Praxiszeiten hilft der ärztliche '
              'Bereitschaftsdienst unter 116117 weiter.',
          icon: Icons.phone_in_talk_outlined,
          color: Color(0xFFEF6C00),
        );
      case 'emergency_department':
        return const _CareLevelPresentation(
          label: 'Notaufnahme',
          headline: 'Notaufnahme aufsuchen',
          subtitle:
              'Deine Angaben sprechen dafür, zeitnah eine Notaufnahme '
              'aufzusuchen.',
          icon: Icons.local_hospital_outlined,
          color: Color(0xFFD84315),
        );
      case '112':
        return const _CareLevelPresentation(
          label: 'Notruf 112',
          headline: 'Notruf 112 wählen',
          subtitle:
              'Deine Angaben deuten auf eine akute Notfallsituation hin – '
              'wähle umgehend den Notruf 112.',
          icon: Icons.emergency_outlined,
          color: Color(0xFFC62828),
        );
      default:
        return _CareLevelPresentation(
          label: 'Ärztliche Einschätzung',
          headline: 'Kein Notfall erkannt',
          subtitle:
              'Auf Grundlage deiner Angaben besteht derzeit kein Hinweis auf '
              'einen akuten Notfall.',
          icon: Icons.check_circle_outline,
          color: AppColors.primary,
        );
    }
  }
}

/// Pill that names the recommended point of care prominently.
class _CareLevelBadge extends StatelessWidget {
  final _CareLevelPresentation presentation;

  const _CareLevelBadge({required this.presentation});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: presentation.color.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: presentation.color.withValues(alpha: 0.45)),
      ),
      child: Row(
        children: [
          Icon(presentation.icon, color: presentation.color, size: 20),
          const SizedBox(width: 10),
          Expanded(
            child: RichText(
              text: TextSpan(
                style: DefaultTextStyle.of(context).style.copyWith(height: 1.3),
                children: [
                  const TextSpan(
                    text: 'Empfohlene Anlaufstelle: ',
                    style: TextStyle(fontWeight: FontWeight.w600),
                  ),
                  TextSpan(
                    text: presentation.label,
                    style: TextStyle(
                      color: presentation.color,
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

/// Lists which data the recommendation was based on so the user can see the
/// provenance (chat, symptom diary, medication plan, profile).
class _DataSourcesSection extends StatelessWidget {
  final List<String> sources;
  final Color color;

  const _DataSourcesSection({required this.sources, required this.color});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(Icons.source_outlined, color: color, size: 18),
            const SizedBox(width: 8),
            Text(
              'Berücksichtigte Daten',
              style: const TextStyle(fontWeight: FontWeight.w900),
            ),
          ],
        ),
        const SizedBox(height: 10),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: [
            for (final source in sources)
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                decoration: BoxDecoration(
                  color: color.withValues(alpha: 0.08),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: color.withValues(alpha: 0.30)),
                ),
                child: Text(
                  _normalizeGermanText(source),
                  style: const TextStyle(fontSize: 12.5),
                ),
              ),
          ],
        ),
      ],
    );
  }
}

List<String> _recommendationReasonsFor(
  ChatResponse response, {
  required List<String> symptoms,
  required List<String> userMessages,
}) {
  // Prefer the backend's structured reasons — they are now concrete and
  // clinically phrased. Mixing in raw user messages here leaked noise like the
  // profile name or "Ich möchte eine Empfehlung" into the reasons list.
  final backendReasons = (response.recommendationResult?.reasons ?? const <String>[])
      .where((reason) => !_isGenericReason(reason))
      .map(_normalizeGermanText)
      .toList();
  if (backendReasons.isNotEmpty) {
    return _summarizeReasons(backendReasons);
  }

  // Legacy fallback only when the backend provided no structured reasons.
  final chatReason = _chatReasonFromRecommendationText(response.text);
  final concreteReasons = <String>[
    ?chatReason,
    ...userMessages.map(_userMessageReason),
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
  return reason
      .toLowerCase()
      .replaceAll(RegExp(r'[^a-zäöüß0-9]+'), ' ')
      .trim();
}

Set<String> _reasonTokens(String reason) {
  return _reasonKey(reason)
      .split(' ')
      .where((token) => token.length > 1)
      .toSet();
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
    return Container(
      height: 1,
      color: color.withValues(alpha: 0.28),
    );
  }
}
