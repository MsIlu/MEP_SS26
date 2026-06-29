/// A symptom to be imported into the diary, optionally carrying a known severity.
class SymptomImport {
  final String name;
  /// Severity on a 1–10 scale as reported in the chat, or null if not known.
  final int? severity;

  const SymptomImport({required this.name, this.severity});
}
