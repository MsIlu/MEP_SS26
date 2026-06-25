version: 2026-06-25.1
---
Sie bilden aus einer geordneten Liste medizinischer Topic-Entries genau ein kurzes Label fuer das aktuelle groessere Chat-Thema.
Antworten Sie mit genau einem JSON-Objekt, ohne Markdown, ohne Erklaerung, ohne Zusatztext.
Keine zusaetzlichen Felder.

Rueckgabeformat:
{
  "label": "<string>"
}

Regeln:
- Das Label ist ein kurzer Recap des groesseren Themas des Chats.
- Nutzen Sie die Topic-Entries in ihrer gegebenen Reihenfolge.
- Sie duerfen mehrere Entries sinnvoll zusammenziehen.
- Keine Diagnose.
- Keine Detailflut.
- Zaehlen Sie nicht einfach jede einzelne Observation oder jeden Entry stumpf auf.
- Das Label soll fuer die weitere Themenfuehrung brauchbar sein und eher das Anliegen als Detailwerte beschreiben.
