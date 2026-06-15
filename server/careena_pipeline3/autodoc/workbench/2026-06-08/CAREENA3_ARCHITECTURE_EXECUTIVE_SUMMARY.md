# Careena3: Executive Summary

## Worum es bei Careena3 im Kern geht

`careena_pipeline3` soll nicht einfach die alte Pipeline in neuer Verpackung
sein, sondern ein sauber orchestriertes medizinisches Dialogsystem mit klaren
Rollen, klaren Vertraegen und bewusst begrenztem KI-Einsatz.

Die zentrale Idee lautet:

- nicht mehr versteckte Heuristiken und Sonderlogik
- sondern sichtbare Architektur, kanonischer Zustand und kleine klar benannte
  LLM-Aufgaben


## Die 10 wichtigsten Erkenntnisse

## 1. Careena3 ist ein Architektur-Neuschnitt, keine klassische Migration

Das Ziel ist nicht Altverhalten moeglichst treu zu kopieren, sondern entlang
von `TARGET_MODEL5.md` eine bessere Struktur aufzubauen.


## 2. Der `DialogueManager` ist das Zentrum des Systems

Die gesamte Turn-Steuerung soll dort sichtbar zusammenlaufen.
Unterkomponenten sollen Signale liefern, aber moeglichst nicht heimlich
Gesamtentscheidungen treffen.


## 3. Rollen- und Vertragstrennung ist der wichtigste Designwert

Getrennt werden sollen insbesondere:

- Entry / Call 1
- Extraction / Call 2
- Case-State
- Safety
- Response-Policy
- Recommendation-Inhalt / Call 3
- finaler Antworttext


## 4. Extraktion ist nicht gleich Wahrheit

Call 2 soll medizinische Information extrahieren, aber nicht direkt den
kanonischen `MedicalCase` festlegen. Dazwischen braucht es bewusste
Normalisierung, Update-Entscheidung und Merge-Semantik.


## 5. Der wichtigste offene Kern ist nicht Prompting, sondern
## Observation-Identitaet

Die groesste strategische Baustelle ist:

- wann neue Information dieselbe Observation erweitert
- wann sie korrigiert
- wann sie bestaetigt
- wann sie eine neue Observation ist

Davon haengen spaeter Focus, Requirements, Readiness, Recommendation und
stabile Antworten ab.


## 6. Kontext soll helfen, aber nicht zur versteckten Faktenquelle werden

Ein zentrales Designprinzip lautet:

- Kontext dient der Einordnung und Zielbindung
- neue Fakten duerfen nicht frei aus Summaries oder Altkontext
  "nachmaterialisiert" werden


## 7. Kleine sichtbare Signale sind ein Schluesselansatz

Statt alles hartzucoden oder alles frei dem Modell zu ueberlassen, arbeitet
Careena3 auf kleine Steuersignale hin, etwa:

- `call2_tasks`
- `operation_mode`
- `message_role`
- `pending_followup`
- Fokusanker

Das ist wahrscheinlich die tragfaehigste Bruecke zwischen klassischer
Orchestrierung und LLM-Flexibilitaet.


## 8. Versteckte medizinische Heuristik wird als Grundrisiko gesehen

Die Dokumente warnen sehr konsistent vor:

- Keyword-Routing
- stillen Merge-Tricks
- Follow-up-Magie
- Gate-Logik, die schlechte Modellierung kaschiert

Das ist nicht nur Technikstil, sondern eine klare Designethik.


## 9. Recommendation wird bewusst in mehrere Stufen zerlegt

Sauber getrennt werden sollen:

- Nutzer wuenscht Empfehlung
- System ist informationsseitig bereit
- Recommendation-Pfad ist freigegeben
- Recommendation-Inhalt wird erzeugt
- finaler Text wird formuliert

Diese Trennung ist ein staerkerer Ansatz als direkte "was soll ich tun?"-
Antwortlogik.


## 10. Offene Probleme sollen sichtbar bleiben, statt mit Schnellfixes
## kaschiert zu werden

Die Dokumentation behandelt es als Staerke, Probleme wie inkonsistente
Observation-Merges oder unklare Recommendation-Strecken offen zu markieren,
wenn die saubere Loesung noch nicht feststeht.


## Gesamtbild

Careena3 zielt auf ein System, das:

- dialogisch orchestriert statt heuristisch zusammengestueckelt ist
- medizinische Information kontrolliert in Zustand ueberfuehrt
- Recommendation erst nach explizitem Gate erlaubt
- LLMs als begrenzte Bausteine nutzt, nicht als unkontrollierte
  Allzweckinstanz
- Unsicherheit und Konflikte eher sichtbar haelt als ueberdeckt


## Management-Implikation

Wenn man den bisherigen Stand strategisch liest, ist die wichtigste Prioritaet
nicht noch mehr lokales Verhalten, sondern die Stabilisierung der
Case-Wahrheit:

- Observation-Identitaet
- Update-Semantik
- Merge-Vertrag

Erst wenn diese Basis sauberer ist, lohnt sich tieferer Ausbau von
Recommendation, Response-Verfeinerung oder weiterer Dialogintelligenz wirklich.
