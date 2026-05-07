class SmartReplies {
  static List<String> generate(String text) {
    final lower = text.toLowerCase();

    /// Symptoms
    if (lower.contains("schmerz") || lower.contains("weh")) {
      return [
        "Wo genau tut es weh?",
        "Seit wann habe ich das?",
        "Ist das gefährlich?",
      ];
    }

    /// Diagnosis/disease
    if (lower.contains("könnte") || lower.contains("möglich")) {
      return [
        "Welche Ursachen gibt es?",
        "Was kann ich tun?",
        "Sollte ich zum Arzt?",
      ];
    }

    /// Treatment
    if (lower.contains("behandlung") || lower.contains("medikament")) {
      return [
        "Gibt es Hausmittel?",
        "Wie lange dauert das?",
        "Nebenwirkungen?",
      ];
    }

    /// Default
    return [
      "Erklär mir das einfacher",
      "Was soll ich jetzt tun?",
      "Mehr Details bitte",
    ];
  }
}