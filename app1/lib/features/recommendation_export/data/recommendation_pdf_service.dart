import 'package:flutter/services.dart';
import 'package:pdf/pdf.dart';
import 'package:pdf/widgets.dart' as pw;
import 'package:app1/features/profiles/domain/models/profile.dart';

/// Creates a PDF document for a care recommendation.
class RecommendationPdfService {
  static const String _logoPath = 'assets/images/logo.png';

  static const double _noticeTitleSize = 13;
  static const double _noticeBodySize = 10;
  static const double _noticeLineSpacing = 2.5;

  static final PdfColor _primaryColor = PdfColor.fromInt(0xFF00897B);
  static final PdfColor _primaryLight = PdfColor.fromInt(0xFFE0F2F1);
  static final PdfColor _warningColor = PdfColor.fromInt(0xFFE65100);
  static final PdfColor _warningLight = PdfColor.fromInt(0xFFFFF3E0);
  static final PdfColor _textColor = PdfColor.fromInt(0xFF263238);
  static final PdfColor _mutedTextColor = PdfColor.fromInt(0xFF607D8B);
  static final PdfColor _borderColor = PdfColor.fromInt(0xFFE0E0E0);
  static final PdfColor _pageBackground = PdfColor.fromInt(0xFFFAFAFA);
  static final PdfColor _cardBackground = PdfColor.fromInt(0xFFFFFFFF);

  Future<Uint8List> buildRecommendationPdf({
    required String title,
    required String patientSummary,
    required String recommendation,
    required String nextSteps,
    required List<String> symptoms,
    required List<String> userMessages,
    Profile? profile,
  }) async {
    final pdf = pw.Document();
    final logo = await _loadOptionalLogo();
    final regularFont = pw.Font.ttf(
      await rootBundle.load('assets/fonts/Nunito-Regular.ttf'),
    );
    final boldFont = pw.Font.ttf(
      await rootBundle.load('assets/fonts/Nunito-Bold.ttf'),
    );

    pdf.addPage(
      pw.MultiPage(
        pageFormat: PdfPageFormat.a4,
        margin: pw.EdgeInsets.zero,
        theme: pw.ThemeData.withFont(base: regularFont, bold: boldFont),
        build: (context) {
          return [
            _buildHeader(title: title, logo: logo, createdAt: DateTime.now()),
            pw.Container(
              color: _pageBackground,
              padding: const pw.EdgeInsets.fromLTRB(32, 28, 32, 28),
              child: pw.Column(
                crossAxisAlignment: pw.CrossAxisAlignment.stretch,
                children: [
                  if (profile != null) ...[
                    _buildSectionCard(
                      title: 'Profilangaben',
                      text: _formatProfile(profile),
                    ),
                    pw.SizedBox(height: 14),
                  ],

                  _buildSectionCard(
                    title: 'Im Chat angegebene bzw. erkannte Beschwerden',
                    text: _formatSymptoms(symptoms),
                  ),
                  pw.SizedBox(height: 14),

                  _buildSectionCard(
                    title: 'Vom Nutzer im Chat angegebene Informationen',
                    text: _formatUserMessages(userMessages),
                  ),
                  pw.SizedBox(height: 14),

                  if (patientSummary.trim().isNotEmpty &&
                      patientSummary.trim() !=
                          'Zusammenfassung des Chatverlaufes') ...[
                    _buildSectionCard(
                      title: 'Zusammenfassung der Situation',
                      text: patientSummary,
                    ),
                    pw.SizedBox(height: 14),
                  ],

                  _buildSectionCard(
                    title: 'Versorgungsempfehlung',
                    text: _extractRecommendationText(recommendation),
                    highlighted: true,
                  ),
                  pw.SizedBox(height: 14),

                  _buildSectionCard(
                    title: 'Nächster Schritt',
                    text: _formatNextSteps(nextSteps),
                  ),
                  pw.SizedBox(height: 18),

                  _buildEmergencyNotice(),
                  pw.SizedBox(height: 20),

                  _buildDisclaimer(),
                ],
              ),
            ),
          ];
        },
        footer: (context) => _buildFooter(context),
      ),
    );

    return pdf.save();
  }

  Future<pw.MemoryImage?> _loadOptionalLogo() async {
    try {
      final bytes = await rootBundle.load(_logoPath);
      return pw.MemoryImage(bytes.buffer.asUint8List());
    } catch (_) {
      return null;
    }
  }

  pw.Widget _buildHeader({
    required String title,
    required pw.MemoryImage? logo,
    required DateTime createdAt,
  }) {
    return pw.Container(
      width: double.infinity,
      padding: const pw.EdgeInsets.fromLTRB(32, 24, 32, 18),
      decoration: pw.BoxDecoration(
        color: _cardBackground,
        border: pw.Border(
          bottom: pw.BorderSide(color: _primaryColor, width: 2),
        ),
      ),
      child: pw.Row(
        crossAxisAlignment: pw.CrossAxisAlignment.center,
        children: [
          if (logo != null)
            pw.Container(width: 34, height: 34, child: pw.Image(logo))
          else
            pw.Container(
              width: 34,
              height: 34,
              decoration: pw.BoxDecoration(
                color: _primaryLight,
                borderRadius: pw.BorderRadius.circular(8),
              ),
              child: pw.Center(
                child: pw.Text(
                  'Careena',
                  style: pw.TextStyle(
                    color: _primaryColor,
                    fontSize: 18,
                    fontWeight: pw.FontWeight.bold,
                  ),
                ),
              ),
            ),
          pw.SizedBox(width: 12),
          pw.Expanded(
            child: pw.Column(
              crossAxisAlignment: pw.CrossAxisAlignment.start,
              children: [
                pw.Text(
                  title,
                  style: pw.TextStyle(
                    color: _textColor,
                    fontSize: 20,
                    fontWeight: pw.FontWeight.bold,
                  ),
                ),
                pw.SizedBox(height: 4),
                pw.Text(
                  'KI-generierte Orientierung auf Basis der angegebenen Informationen',
                  style: pw.TextStyle(color: _mutedTextColor, fontSize: 10),
                ),
              ],
            ),
          ),
          pw.Column(
            crossAxisAlignment: pw.CrossAxisAlignment.end,
            children: [
              pw.Text(
                'Erstellt am',
                style: pw.TextStyle(color: _mutedTextColor, fontSize: 8),
              ),
              pw.SizedBox(height: 2),
              pw.Text(
                _formatDate(createdAt),
                style: pw.TextStyle(
                  color: _textColor,
                  fontSize: 10,
                  fontWeight: pw.FontWeight.bold,
                ),
              ),
              pw.SizedBox(height: 6),
              pw.Text(
                'Quelle',
                style: pw.TextStyle(color: _mutedTextColor, fontSize: 8),
              ),
              pw.SizedBox(height: 2),
              pw.Text(
                'Careena Chat',
                style: pw.TextStyle(
                  color: _textColor,
                  fontSize: 10,
                  fontWeight: pw.FontWeight.bold,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  pw.Widget _buildSectionCard({
    required String title,
    required String text,
    bool highlighted = false,
  }) {
    return pw.Container(
      padding: const pw.EdgeInsets.all(18),
      decoration: pw.BoxDecoration(
        color: highlighted ? _primaryLight : _cardBackground,
        borderRadius: pw.BorderRadius.circular(14),
        border: pw.Border.all(
          color: highlighted ? _primaryColor : _borderColor,
          width: highlighted ? 1.2 : 1,
        ),
      ),
      child: pw.Column(
        crossAxisAlignment: pw.CrossAxisAlignment.start,
        children: [
          pw.Text(
            title,
            style: pw.TextStyle(
              color: highlighted ? _primaryColor : _textColor,
              fontSize: 15,
              fontWeight: pw.FontWeight.bold,
            ),
          ),
          pw.SizedBox(height: 10),
          pw.Text(
            text,
            style: pw.TextStyle(
              color: _textColor,
              fontSize: 11,
              lineSpacing: 4,
            ),
          ),
        ],
      ),
    );
  }

  pw.Widget _buildEmergencyNotice() {
    return pw.Container(
      padding: const pw.EdgeInsets.all(14),
      decoration: pw.BoxDecoration(
        color: _warningLight,
        borderRadius: pw.BorderRadius.circular(14),
        border: pw.Border.all(color: _warningColor),
      ),
      child: pw.Column(
        crossAxisAlignment: pw.CrossAxisAlignment.start,
        children: [
          pw.Text(
            'Wichtiger Hinweis',
            style: pw.TextStyle(
              color: _warningColor,
              fontSize: _noticeTitleSize,
              fontWeight: pw.FontWeight.bold,
            ),
          ),
          pw.SizedBox(height: 8),
          pw.Text(
            'Bei akuter Gefahr, Selbstgefährdung oder einem medizinischen Notfall '
            'sollte sofort der Notruf 112 kontaktiert oder eine Notaufnahme '
            'aufgesucht werden.',
            style: pw.TextStyle(
              color: _textColor,
              fontSize: _noticeBodySize,
              lineSpacing: _noticeLineSpacing,
            ),
          ),
          pw.SizedBox(height: 8),
          pw.Text(
            'Diese Einschätzung ersetzt keine ärztliche Untersuchung und stellt keine Diagnose dar.',
            style: pw.TextStyle(
              color: _textColor,
              fontSize: 10.5,
              lineSpacing: 3,
            ),
          ),
        ],
      ),
    );
  }

  pw.Widget _buildDisclaimer() {
    return pw.Container(
      padding: const pw.EdgeInsets.all(14),
      decoration: pw.BoxDecoration(
        color: PdfColor.fromInt(0xFFF5F5F5),
        borderRadius: pw.BorderRadius.circular(12),
      ),
      child: pw.Text(
        'Dieses Dokument wurde mithilfe künstlicher Intelligenz erstellt. Es stellt keine Diagnose dar '
        'und ersetzt keine ärztliche Untersuchung, Beratung oder Behandlung. Die Angaben beruhen '
        'auf den im Chat genannten Informationen und gegebenenfalls auf vom Nutzer gespeicherten '
        'Profilangaben.',
        style: pw.TextStyle(
          color: _mutedTextColor,
          fontSize: 9,
          lineSpacing: 3,
        ),
      ),
    );
  }

  pw.Widget _buildFooter(pw.Context context) {
    return pw.Container(
      padding: const pw.EdgeInsets.fromLTRB(32, 8, 32, 18),
      color: _pageBackground,
      child: pw.Row(
        mainAxisAlignment: pw.MainAxisAlignment.spaceBetween,
        children: [
          pw.Text(
            'Careena · MEP26',
            style: pw.TextStyle(color: _mutedTextColor, fontSize: 9),
          ),
          pw.Text(
            'Seite ${context.pageNumber} von ${context.pagesCount}',
            style: pw.TextStyle(color: _mutedTextColor, fontSize: 9),
          ),
        ],
      ),
    );
  }

  String _extractRecommendationText(String recommendation) {
    final lines = recommendation
        .split('\n')
        .map((line) => line.trim())
        .where((line) => line.isNotEmpty)
        .toList();

    final filteredLines = <String>[];
    var skipNextLine = false;

    for (final line in lines) {
      if (skipNextLine) {
        skipNextLine = false;
        continue;
      }

      final lowerLine = line.toLowerCase();

      if (lowerLine.startsWith('wichtiger hinweis')) {
        skipNextLine = true;
        continue;
      }

      if (lowerLine.startsWith('hinweis')) {
        skipNextLine = true;
        continue;
      }

      filteredLines.add(line);
    }

    final cleanedText = filteredLines.join('\n');

    if (cleanedText.isEmpty) {
      return 'Bitte beachten Sie den nächsten Schritt und den wichtigen Hinweis.';
    }

    return cleanedText;
  }

  String _formatNextSteps(String nextSteps) {
    final trimmed = nextSteps.trim();

    switch (trimmed) {
      case 'call_112':
        return 'Notruf 112 kontaktieren';
      case 'see_doctor':
        return 'Ärztliche Abklärung vereinbaren';
      case 'urgent_doctor':
        return 'Zeitnah ärztliche Hilfe aufsuchen';
      case 'self_care':
        return 'Selbsthilfemaßnahmen beachten';
      case '':
        return 'Keine Angabe';
      default:
        return trimmed;
    }
  }

  String _formatSymptoms(List<String> symptoms) {
    final cleanedSymptoms = symptoms
        .map((symptom) => symptom.trim())
        .where((symptom) => symptom.isNotEmpty)
        .toList();

    if (cleanedSymptoms.isEmpty) {
      return 'Keine Beschwerden angegeben oder erkannt.';
    }

    return cleanedSymptoms.map((symptom) => '- $symptom').join('\n');
  }

  String _formatUserMessages(List<String> userMessages) {
    final cleanedMessages = userMessages
        .map((message) => message.trim())
        .where((message) => message.isNotEmpty)
        .toList();

    if (cleanedMessages.isEmpty) {
      return 'Keine zusätzlichen Angaben verfügbar.';
    }

    return cleanedMessages.map((message) => '- $message').join('\n');
  }

  String _formatProfile(Profile profile) {
    final rows = <String>[
      'Name / Profil: ${profile.displayName}',
      if (profile.dateOfBirth != null && profile.dateOfBirth!.isNotEmpty)
        'Geburtsdatum: ${_formatProfileDate(profile.dateOfBirth)}',
      if (profile.biologicalSex != null && profile.biologicalSex!.isNotEmpty)
        'Biologisches Geschlecht: ${profile.biologicalSex}',
      if (profile.heightCm != null) 'Größe: ${profile.heightCm} cm',
      if (profile.weightKg != null) 'Gewicht: ${profile.weightKg} kg',
    ];

    if (profile.relevantPreconditionsSummary != null &&
        profile.relevantPreconditionsSummary!.trim().isNotEmpty) {
      rows.add('');
      rows.add('Vom Nutzer gespeicherte Vorerkrankungen:');
      rows.add(profile.relevantPreconditionsSummary!.trim());
    }

    if (profile.relevantMedicationsSummary != null &&
        profile.relevantMedicationsSummary!.trim().isNotEmpty) {
      rows.add('');
      rows.add('Vom Nutzer gespeicherte Medikamente:');
      rows.add(profile.relevantMedicationsSummary!.trim());
    }

    if (profile.symptomDiarySummary != null &&
        profile.symptomDiarySummary!.trim().isNotEmpty) {
      rows.add('');
      rows.add('Vom Nutzer gespeicherte Gesundheitsnotizen:');
      rows.add(profile.symptomDiarySummary!.trim());
    }

    return rows.join('\n');
  }

  String _formatProfileDate(String? rawDate) {
    if (rawDate == null || rawDate.trim().isEmpty) {
      return 'Keine Angabe';
    }

    final parsed = DateTime.tryParse(rawDate);
    if (parsed == null) {
      return rawDate;
    }

    return _formatDate(parsed);
  }

  String _formatDate(DateTime date) {
    final day = date.day.toString().padLeft(2, '0');
    final month = date.month.toString().padLeft(2, '0');
    final year = date.year.toString();

    return '$day.$month.$year';
  }
}
