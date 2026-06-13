# Careena3: Architecture Stop Rules

Stand: 2026-06-13
Status: Arbeitsregel


## Zweck

Diese Notiz ist kein Zielbild.
Sie ist ein Stoppschild.

Sie soll verhindern, dass neue Arbeit wieder:

- eine Parallelwelt baut
- Glue-Code skaliert
- fehlende Heimatorte durch Arbeitsstrukturen ersetzt
- und am Ende mehr Code erzeugt, ohne die eigentliche Architektur zu klaeren


## Stop-Regeln

### 1. Keine neue Arbeitswirklichkeit bauen

Wenn eine Aenderung eine neue Zwischenwelt, Schattenwelt oder
Arbeitswirklichkeit erzeugt, ist das ein Warnsignal.

Frage:

- Loest das die eigentliche Verantwortung?
- Oder beschreibt es nur die alte Unklarheit neu?


### 2. Fehlende Heimat nicht durch Transport ersetzen

Wenn eine Verantwortung keinen klaren Heimatort hat, darf sie nicht einfach:

- in den Turn
- in einen Kontext
- in ein Payload
- in einen Manager
- in ein Summary-Feld

verschoben werden.

Erst die Heimat klaeren, dann den Code aendern.


### 3. Keine zweite Wahrheit fuer dasselbe Problem

Wenn dieselbe Sache an zwei Orten gehalten oder gesteuert wird, ist das ein
Architekturproblem, kein Komfortgewinn.

Frage:

- Was ist die primaere Wahrheit?
- Warum existiert die zweite ueberhaupt?


### 4. Glue-Code ist kein Fortschritt

Wenn eine Aenderung vor allem:

- Mapping
- Weiterreichen
- Spiegeln
- Zusammenfassen
- Reparieren

hinzufuegt, dann ist sie verdaechtig.

Mehr Glue ist nicht automatisch mehr Architektur.


### 5. Ausfuehrung ist nicht Wahrheit

Turn, Kontext, Laufzeitobjekte und Response-Artefakte sind nicht automatisch
die Heimat einer fachlichen Verantwortung.

Frage:

- Ist das echte Wahrheit?
- Oder nur Ausfuehrungszustand?


### 6. Nicht die Verpackung verbessern, wenn der Schnitt falsch ist

Sauberere Namen, neue Vertraege oder neue Objekte helfen nicht, wenn der
Verantwortungsschnitt darunter weiter falsch bleibt.

Frage:

- Verbessern wir gerade wirklich den Schnitt?
- Oder machen wir die falsche Struktur nur lesbarer?


### 7. Vor jedem groesseren Refactor

Vor jedem groesseren Umbau zuerst fragen:

- Welches Problem ist lokal?
- Welches Problem ist strukturell?
- Welche Verantwortung hat keinen klaren Heimatort?
- Bauen wir gerade eine Loesung um das Problem herum?


## Die wichtigste Rueckfrage

Wenn eine Aenderung gut aussieht, aber viel neuen Code, neue Objekte oder
neue Vermittlungsschichten erzeugt, dann ist die erste Rueckfrage:

- Loest das das Heimatproblem?
- Oder baut es nur eine besser benannte Parallelwelt?
