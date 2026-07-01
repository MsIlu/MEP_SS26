import 'package:app1/app/app_dependencies_scope.dart';
import 'package:app1/features/profiles/domain/models/profile.dart';
import 'package:flutter/material.dart';
import 'package:printing/printing.dart';
import 'package:app1/core/themes/app_colors.dart';
import '../../chatscreen/data/models/chat_response_model.dart';
import '../../medication_plan/data/medication_api_service.dart';
import '../../medication_plan/data/medication_entry.dart';
import '../../symptom_diary/domain/symptom_response.dart';
import '../data/recommendation_pdf_service.dart';

/// User-facing label for a backend `care_level` value, used in the PDF.
String careLevelLabelForPdf(String? careLevel) {
  return switch (careLevel) {
    'self_care' => 'Selbstbehandlung – Maßnahmen für zu Hause',
    'pharmacy' => 'Apotheke – Beratung und rezeptfreie Mittel',
    'general_practice' => 'Hausarztpraxis – zeitnahe Abklärung',
    'specialist' => 'Facharztpraxis – gezielte Abklärung',
    '116117' => 'Ärztlicher Bereitschaftsdienst (116117)',
    'emergency_department' => 'Notaufnahme aufsuchen',
    '112' => 'Notruf 112 wählen',
    _ => null,
  } ?? '';
}

/// Button that exports a generated care recommendation as a PDF.
class ExportRecommendationPdfButton extends StatelessWidget {
  final String title;
  final String patientSummary;
  final String recommendation;
  final String nextSteps;
  final List<String> symptoms;
  final List<String> userMessages;

  /// Structured backend result, used to enrich the PDF with the recommended
  /// care level, the reasons and the deterministic data-source provenance.
  final RecommendationResult? recommendationResult;

  /// Profile the recommendation is about (resolved by the backend session).
  /// Preferred over the app's active profile so the exported PDF shows the
  /// correct person, diary and medication plan.
  final int? profileId;

  const ExportRecommendationPdfButton({
    super.key,
    required this.title,
    required this.patientSummary,
    required this.recommendation,
    required this.nextSteps,
    required this.symptoms,
    required this.userMessages,
    this.recommendationResult,
    this.profileId,
  });

  @override
  Widget build(BuildContext context) {
    return OutlinedButton.icon(
      style: OutlinedButton.styleFrom(
        foregroundColor: AppColors.careenaTeal,
        side: const BorderSide(color: AppColors.careenaTeal),
        padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
      ),
      icon: const Icon(Icons.picture_as_pdf),
      label: const Text('PDF exportieren'),
      onPressed: () async {
        final dependencies = AppDependenciesScope.maybeOf(context);
        final profileApiService = dependencies?.profileApiService;
        final symptomApiService = dependencies?.symptomApiService;
        final apiClient = dependencies?.apiClient;
        // Use only the session-resolved profile. If the session has no profile
        // (profile_id == null), do not pull the app's active profile — that
        // could expose data of a different person.
        final activeProfileId = profileId;

        Profile? profile;
        var diaryLines = const <String>[];
        var medicationLines = const <String>[];

        if (activeProfileId != null) {
          if (profileApiService != null) {
            try {
              profile = await profileApiService.getProfile(activeProfileId);
            } catch (_) {
              profile = null;
            }
          }
          if (symptomApiService != null) {
            try {
              final entries = await symptomApiService.getSymptoms(
                profileId: activeProfileId,
              );
              diaryLines = entries.map(_formatDiaryEntry).toList();
            } catch (_) {
              diaryLines = const [];
            }
          }
          if (apiClient != null) {
            try {
              final medications = await MedicationApiService(
                apiClient,
              ).getMedications(activeProfileId);
              medicationLines = medications.map(_formatMedicationEntry).toList();
            } catch (_) {
              medicationLines = const [];
            }
          }
        }

        final pdfService = RecommendationPdfService();

        final pdfBytes = await pdfService.buildRecommendationPdf(
          title: title,
          patientSummary: patientSummary,
          recommendation: recommendation,
          nextSteps: nextSteps,
          symptoms: symptoms,
          profile: profile,
          userMessages: userMessages,
          careLevelLabel: careLevelLabelForPdf(recommendationResult?.careLevel),
          reasons: recommendationResult?.reasons ?? const [],
          dataSources: recommendationResult?.dataSources ?? const [],
          diaryLines: diaryLines,
          medicationLines: medicationLines,
        );

        await Printing.layoutPdf(
          name: 'versorgungsempfehlung.pdf',
          onLayout: (_) async => pdfBytes,
        );
      },
    );
  }

  static String _formatDiaryEntry(SymptomResponse entry) {
    final date =
        '${entry.date.day.toString().padLeft(2, '0')}.'
        '${entry.date.month.toString().padLeft(2, '0')}.'
        '${entry.date.year}';
    final buffer = StringBuffer(
      '$date – ${entry.symptom}, Intensität ${entry.intensity}/10',
    );
    if (entry.bodyArea.isNotEmpty) {
      buffer.write(', ${entry.bodyArea}');
    }
    if (entry.temperatureC != null) {
      buffer.write(', Temperatur ${entry.temperatureC!.toStringAsFixed(1)} °C');
    }
    if (entry.note.isNotEmpty) {
      buffer.write(' (${entry.note})');
    }
    return buffer.toString();
  }

  static String _formatMedicationEntry(MedicationEntry entry) {
    final times = entry.intakeTimes
        .map(
          (t) =>
              '${t.hour.toString().padLeft(2, '0')}:'
              '${t.minute.toString().padLeft(2, '0')}',
        )
        .join(', ');
    final buffer = StringBuffer(entry.name);
    if (entry.dose.isNotEmpty) {
      buffer.write(' ${entry.dose}');
    }
    buffer.write(' – ${entry.frequency.label}');
    if (times.isNotEmpty) {
      buffer.write(' ($times)');
    }
    final substance = entry.catalogItem?.activeSubstance ?? '';
    if (substance.isNotEmpty) {
      buffer.write(', Wirkstoff: $substance');
    }
    return buffer.toString();
  }
}
