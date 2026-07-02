import 'package:flutter/services.dart';
import 'package:pdf/pdf.dart';
import 'package:pdf/widgets.dart' as pw;
import 'package:app1/features/profiles/domain/models/profile.dart';

String biologicalSexLabelForPdf(String? value) {
  return switch (value?.trim().toLowerCase()) {
    'female' => 'weiblich',
    'male' => 'männlich',
    null || '' => 'Keine Angabe',
    _ => value!.trim(),
  };
}

/// Creates a PDF document for a care recommendation.
class RecommendationPdfService {
  static const String _logoPath = 'assets/images/logo_medbitaid.png';

  static const double _noticeTitleSize = 13;
  static const double _noticeBodySize = 10;
  static const double _noticeLineSpacing = 2.5;

  static final PdfColor _primaryColor = PdfColor.fromInt(0xFF315B9D);
  static final PdfColor _primaryLight = PdfColor.fromInt(0xFFF7F9FC);
  static final PdfColor _warningColor = PdfColor.fromInt(0xFFC43F3A);
  static final PdfColor _warningLight = PdfColor.fromInt(0xFFFFF8F7);
  static final PdfColor _textColor = PdfColor.fromInt(0xFF263238);
  static final PdfColor _mutedTextColor = PdfColor.fromInt(0xFF607D8B);
  static final PdfColor _borderColor = PdfColor.fromInt(0xFFE0E0E0);
  static final PdfColor _pageBackground = PdfColor.fromInt(0xFFFFFFFF);
  static final PdfColor _cardBackground = PdfColor.fromInt(0xFFFFFFFF);

  Future<Uint8List> buildRecommendationPdf({
    required String title,
    required String patientSummary,
    required String recommendation,
    required String nextSteps,
    required List<String> symptoms,
    required List<String> userMessages,
    Profile? profile,
    String? careLevelCode,
    String? careLevelLabel,
    List<String> reasons = const [],
    List<String> warnings = const [],
    List<String> dataSources = const [],
    List<String> diaryLines = const [],
    List<String> medicationLines = const [],
  }) async {
    final pdf = pw.Document();
    final logo = await _loadOptionalLogo();
    final careColor = _careLevelColor(careLevelCode);
    final careBackground = _careLevelBackground(careLevelCode);
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
                  _buildSectionCard(
                    title: 'Einschätzung',
                    text: _effectiveAssessment(
                      recommendation: recommendation,
                      patientSummary: patientSummary,
                      userMessages: userMessages,
                      symptoms: symptoms,
                    ),
                  ),
                  pw.SizedBox(height: 14),

                  _buildSectionCard(
                    title: 'Nächster Schritt',
                    text: _formatNextStepWithDestination(
                      nextSteps: nextSteps,
                      careLevelLabel: careLevelLabel,
                    ),
                    highlighted: true,
                    accentColor: careColor,
                    accentBackground: careBackground,
                  ),
                  pw.SizedBox(height: 14),

                  _buildBulletSectionCard(
                    title: 'Gründe',
                    items: _cleanLines(reasons).isEmpty
                        ? const [
                            'Die Einordnung basiert auf den im Chat erfassten Angaben.',
                          ]
                        : _cleanLines(reasons),
                  ),
                  pw.SizedBox(height: 14),

                  if (_cleanLines(diaryLines).isNotEmpty ||
                      _cleanLines(medicationLines).isNotEmpty) ...[
                    pw.Row(
                      crossAxisAlignment: pw.CrossAxisAlignment.start,
                      children: [
                        pw.Expanded(
                          child: _buildBulletSectionCard(
                            title: 'Symptome der letzten 14 Tage',
                            items: _cleanLines(diaryLines).isEmpty
                                ? const ['Keine Einträge vorhanden.']
                                : _cleanLines(diaryLines),
                          ),
                        ),
                        pw.SizedBox(width: 12),
                        pw.Expanded(
                          child: _buildBulletSectionCard(
                            title: 'Aktuelle Medikamente',
                            items: _cleanLines(medicationLines).isEmpty
                                ? const ['Keine Einträge vorhanden.']
                                : _cleanLines(medicationLines),
                          ),
                        ),
                      ],
                    ),
                    pw.SizedBox(height: 14),
                  ],

                  if (_cleanLines(dataSources).isNotEmpty) ...[
                    _buildSectionCard(
                      title: 'Berücksichtigte Daten',
                      text: _cleanLines(
                        dataSources,
                      ).map((source) => '- $source').join('\n'),
                    ),
                    pw.SizedBox(height: 18),
                  ],

                  _buildSafetyNotice(
                    careLevelCode: careLevelCode,
                    warnings: warnings,
                  ),
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
    PdfColor? accentColor,
    PdfColor? accentBackground,
  }) {
    final effectiveAccent = accentColor ?? _primaryColor;
    return pw.Container(
      padding: const pw.EdgeInsets.all(18),
      decoration: pw.BoxDecoration(
        color: highlighted
            ? accentBackground ?? _primaryLight
            : _cardBackground,
        borderRadius: pw.BorderRadius.circular(14),
        border: pw.Border.all(
          color: highlighted ? effectiveAccent : _borderColor,
          width: highlighted ? 1.2 : 1,
        ),
      ),
      child: pw.Column(
        crossAxisAlignment: pw.CrossAxisAlignment.start,
        children: [
          pw.Text(
            title,
            style: pw.TextStyle(
              color: highlighted ? effectiveAccent : _textColor,
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

  pw.Widget _buildBulletSectionCard({
    required String title,
    required List<String> items,
  }) {
    return pw.Container(
      padding: const pw.EdgeInsets.all(18),
      decoration: pw.BoxDecoration(
        color: _cardBackground,
        borderRadius: pw.BorderRadius.circular(14),
        border: pw.Border.all(color: _borderColor),
      ),
      child: pw.Column(
        crossAxisAlignment: pw.CrossAxisAlignment.start,
        children: [
          pw.Text(
            title,
            style: pw.TextStyle(
              color: _textColor,
              fontSize: 15,
              fontWeight: pw.FontWeight.bold,
            ),
          ),
          pw.SizedBox(height: 10),
          for (final item in items)
            pw.Padding(
              padding: const pw.EdgeInsets.only(bottom: 5),
              child: pw.Row(
                crossAxisAlignment: pw.CrossAxisAlignment.start,
                children: [
                  pw.Text(
                    '•  ',
                    style: pw.TextStyle(color: _primaryColor, fontSize: 11),
                  ),
                  pw.Expanded(
                    child: pw.Text(
                      item,
                      style: pw.TextStyle(
                        color: _textColor,
                        fontSize: 11,
                        lineSpacing: 4,
                      ),
                    ),
                  ),
                ],
              ),
            ),
        ],
      ),
    );
  }

  List<String> _cleanLines(List<String> lines) {
    return lines
        .map((line) => line.trim())
        .where((line) => line.isNotEmpty)
        .toList();
  }

  PdfColor _careLevelColor(String? careLevelCode) {
    return switch (careLevelCode) {
      'self_care' => PdfColor.fromInt(0xFF2E7D32),
      'pharmacy' => PdfColor.fromInt(0xFF4A978B),
      'general_practice' => PdfColor.fromInt(0xFF3F6FCB),
      'specialist' => PdfColor.fromInt(0xFF6558A8),
      '116117' => PdfColor.fromInt(0xFFD66A22),
      'emergency_department' || '112' => _warningColor,
      _ => _primaryColor,
    };
  }

  PdfColor _careLevelBackground(String? careLevelCode) {
    return switch (careLevelCode) {
      'self_care' => PdfColor.fromInt(0xFFF5FAF5),
      'pharmacy' => PdfColor.fromInt(0xFFF4FAF8),
      'general_practice' => PdfColor.fromInt(0xFFF5F7FC),
      'specialist' => PdfColor.fromInt(0xFFF7F5FC),
      '116117' => PdfColor.fromInt(0xFFFFF8F2),
      'emergency_department' || '112' => _warningLight,
      _ => _primaryLight,
    };
  }

  pw.Widget _buildSafetyNotice({
    required String? careLevelCode,
    required List<String> warnings,
  }) {
    final isAcuteEmergency =
        careLevelCode == '112' || careLevelCode == 'emergency_department';
    final warningText = _cleanLines(warnings).join(' ');

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
            isAcuteEmergency
                ? 'Akuter medizinischer Hinweis'
                : 'Wichtiger Hinweis',
            style: pw.TextStyle(
              color: _warningColor,
              fontSize: _noticeTitleSize,
              fontWeight: pw.FontWeight.bold,
            ),
          ),
          pw.SizedBox(height: 8),
          pw.Text(
            isAcuteEmergency
                ? careLevelCode == '112'
                      ? 'Die Angaben weisen auf einen möglichen akuten Notfall hin. '
                            'Bitte sofort den Notruf 112 kontaktieren.'
                      : 'Die Angaben weisen auf eine mögliche akute Situation hin. '
                            'Bitte unverzüglich eine Notaufnahme aufsuchen.'
                : warningText.isNotEmpty
                ? warningText
                : 'Wenn sich die Beschwerden deutlich verschlechtern oder neue '
                      'Warnzeichen auftreten, bitte umgehend medizinische Hilfe suchen.',
            style: pw.TextStyle(
              color: _textColor,
              fontSize: _noticeBodySize,
              lineSpacing: _noticeLineSpacing,
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
      return 'Bitte beachte den nächsten Schritt und den wichtigen Hinweis.';
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

  String _formatNextStepWithDestination({
    required String nextSteps,
    required String? careLevelLabel,
  }) {
    final parts = <String>[];
    if (careLevelLabel != null && careLevelLabel.trim().isNotEmpty) {
      parts.add('Empfohlene Anlaufstelle: ${careLevelLabel.trim()}');
    }
    final formattedStep = _formatNextSteps(nextSteps);
    if (formattedStep != 'Keine Angabe') {
      parts.add(formattedStep);
    }
    return parts.isEmpty
        ? 'Keine konkrete Anlaufstelle angegeben.'
        : parts.join('\n\n');
  }

  String _effectiveAssessment({
    required String recommendation,
    required String patientSummary,
    required List<String> userMessages,
    required List<String> symptoms,
  }) {
    if (recommendation.trim().isNotEmpty) {
      return _extractRecommendationText(recommendation);
    }

    final summary = patientSummary.trim();
    if (summary.isNotEmpty &&
        summary != 'Zusammenfassung des Chatverlaufes' &&
        summary != 'Aus dem Chatverlauf generierte Handlungsempfehlung.') {
      return summary;
    }

    final chatDetails = _cleanLines(userMessages);
    if (chatDetails.isNotEmpty) {
      return chatDetails.take(5).join(' ');
    }

    final recognizedSymptoms = _cleanLines(symptoms);
    if (recognizedSymptoms.isNotEmpty) {
      return 'Im Chat wurden folgende Beschwerden beschrieben: '
          '${recognizedSymptoms.join(', ')}.';
    }

    return 'Im Chat wurden keine weiteren Angaben zur Situation erfasst.';
  }

  String _formatDate(DateTime date) {
    final day = date.day.toString().padLeft(2, '0');
    final month = date.month.toString().padLeft(2, '0');
    final year = date.year.toString();

    return '$day.$month.$year';
  }
}
