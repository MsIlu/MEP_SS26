/// Generates lightweight follow-up suggestions from assistant responses.
class SmartReplies {
  /// Returns a small set of suggested user replies based on simple keywords.
  static List<String> generate(String text) {
    final lower = text.toLowerCase();

    //Todo: make the replies smart, remove hard-coded replies
    // Symptom-focused replies invite the user to add medically useful details.
    if (lower.contains("schmerz") || lower.contains("weh")) {
      return [
        "Wo genau tut es weh?",
        "Seit wann habe ich das?",
        "Ist das gefährlich?",
      ];
    }
    if (lower.contains("könnte") || lower.contains("möglich")) {
      return [
        "Welche Ursachen gibt es?",
        "Was kann ich tun?",
        "Sollte ich zum Arzt?",
      ];
    }
    if (lower.contains("behandlung") || lower.contains("medikament")) {
      return [
        "Gibt es Hausmittel?",
        "Wie lange dauert das?",
        "Nebenwirkungen?",
      ];
    }
    return [
      "Erklär mir das einfacher",
      "Was soll ich jetzt tun?",
      "Mehr Details bitte",
    ];
  }
}
