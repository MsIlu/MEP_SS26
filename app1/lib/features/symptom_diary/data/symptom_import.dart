/// A symptom carrying optional enrichment data (severity, body area).
///
/// Used both for chat→diary import and for the in-chat symptom editor.
class SymptomImport {
  final String name;
  /// Severity on a 1–10 scale, or null if not known.
  final int? severity;
  /// Body area (e.g. "Kopf"), or null if not specified.
  final String? bodyArea;

  const SymptomImport({required this.name, this.severity, this.bodyArea});
}
