# Careena3: Aktuelle groesste Schwachstellen

Stand: 2026-06-08

Zweck:

- kompakter Zwischenstand der aktuell wichtigsten architektonischen und
  operativen Schwachstellen
- bewusst aus dem laufenden Refactor- und Log-Kontext geschrieben
- nicht als vollstaendige Bugliste, sondern als Arbeitsbild fuer die
  naechsten Schritte


## 1. Call-2-Vertrag ist zu gross und zu unscharf

Der aktuelle Call-2-Pfad verlangt dem LLM zu viel auf einmal ab:

- medizinische Extraktion
- Task-Gating
- Mode-Gating
- Scope-Gating
- Subject-Aufloesung
- unresolved questions
- Notizfelder
- Observationen mit offenem `attributes`-Container

Problem:

- der Call baut kein kleines Extraktionsergebnis, sondern ein breites
  Arbeitsobjekt
- dadurch wird spaetere Fehlerbehebung strukturell noetig statt nur lokal

Konsequenz:

- der Extraction->Truth-Uebergang bleibt fragil
- Mapper, Normalisierung und Reparaturlogik werden ueberlastet


## 2. Der aktuelle Kontextbuilder ist selbst eine Uebergangsprothese

Der Call-2-Kontext ist im Ist-Zustand zu breit.

Aktuell werden unter anderem kombiniert:

- `latest_user_message`
- `call2_tasks`
- `operation_mode`
- `target_scope`
- `allow_new_observations`
- `pending_slot`
- Fokusfelder
- `last_assistant_question`
- `case_summary`
- `dialogue_summary`

Problem:

- zu viele verschiedene Rollen landen in einem Paket:
  Interpretationshilfe, Dialogsteuerung, Fallsummary und operative Regeln
- das erhoeht die Wahrscheinlichkeit, dass das LLM Kontext eher als diffuse
  Zweitwahrheit denn als enge Hilfe liest

Konsequenz:

- Call 2 bekommt mehr Kontext als fuer kleine medizinische Eintraege noetig
- der Kontext selbst treibt Ueberfrachtung und spaetere Korrekturlast


## 3. Der zweite LLM-Normalisierungscall ist zu schwer

Nach der primaeren Extraktion laeuft ein zweiter LLM-Call, der wieder ein
grosses JSON bekommt und erneut ein komplettes `ExtractionResult` erzeugen
soll.

Problem:

- das ist sehr nah an einer zweiten Komplett-Extraktion
- dieselbe breite Struktur wird nochmals gebaut, geordnet und beschnitten
- danach folgt zusaetzlich noch Python-Reparaturlogik

Konsequenz:

- Call 2 ist faktisch ein zweistufiger grosser JSON-Pfad
- die gewuenschte kleine, kontrollierte LLM-Rolle wird damit verfehlt


## 4. Normalisierung passiert auf zu grossen Strukturen

Der aktuelle Pfad normalisiert nicht systematisch kleine Objekte mit engen
Guardrails, sondern ganze Extraction-Ergebnisse oder grosse Ergebnisteile.

Problem:

- Normalisierung wird dadurch zu einer Mischung aus:
  Umordnen, Wegwerfen, Vertragsrettung und Teil-Reparatur
- sie ist schwerer testbar und schwerer fachlich zu begrenzen

Konsequenz:

- die Normalisierung bekommt zu viel implizite Verantwortung
- spaetere Unschaerfen wandern leicht in Mapper oder Service-Reparaturlogik


## 5. `ResilientExtractionService` traegt zu viele Rollen zugleich

Der Service vereinigt aktuell:

- Fehlergrenze
- Subject-Gating
- optionale LLM-Normalisierung
- Follow-up-Update-Umschreibung
- Rest-Fallbacks

Problem:

- der Service wird dadurch zum Sammelort fuer operative Kompensation
- das ist architektonisch nicht die richtige Dauerrolle

Konsequenz:

- schwerer lesbarer Extraction-Pfad
- neue Edge-Cases landen leicht an derselben Stelle


## 6. `ExtractionResultMapper` war und ist eine kritische Uebergangskante

Der Mapper wurde bereits verbessert, bleibt aber Teil der Schwachstelle.

Problem:

- er lebt von einem vorgelagert zu offenen Extraktionsvertrag
- freie oder driftende `attributes` muessen downstream wieder eingeordnet
  werden

Konsequenz:

- solange der Call-2-Vertrag breit bleibt, bleibt auch der Mapper unter Druck
- Mapper-Probleme sind haeufig Symptom groesserer Vertragsunschaerfe


## 7. `guide_next_step` bleibt ein offenes Transition-Problem

Die Logs zeigen weiterhin:

- `guide_next_step` kann zu frueh aktiv werden
- `guide_next_step` springt erneut an, obwohl `pending` bereits `keiner` ist

Problem:

- das ist kein reines Textproblem
- der zugrunde liegende Dialog- und Zielzustand ist noch nicht stark genug
  modelliert

Konsequenz:

- Response-Text behauptet oder signalisiert mehr Fortschritt, als die
  Zustandslogik sauber traegt


## 8. Die sinnvolle Zielrichtung ist noch nicht eingelost

Die aktuell plausibelste Richtung lautet:

- viele kleinere medizinische Eintraege statt grosser Sammelstruktur
- engerer Kontext fuer Call 2
- objektweise Normalisierung mit klaren Guardrails
- moeglichst lokale Konfliktentscheidung zwischen zwei konkurrierenden
  Objekten
- klare Trennung zwischen dem, was Code stabil erledigen kann, und dem, was
  ein LLM als enger Hilfsschritt gut leisten kann

Aktueller Stand:

- diese Richtung ist fachlich und architektonisch sichtbar
- sie ist im Code aber noch nicht als neuer Call-2-Vertrag real umgesetzt


## Verdichtetes Fazit

Die groessten Schwachstellen sitzen aktuell nicht primaer im `DialogueManager`
oder in der groben Systemstruktur, sondern an der Extraction-Kante:

- zu grosser Kontext
- zu grosser Outputvertrag
- zu schwerer Normalisierungspfad
- zu viel nachgelagerte Kompensation

Der naechste saubere Hebel ist deshalb:

- nicht immer mehr Fehlerbehebung
- sondern ein kleinerer, klarerer Call-2-Vertrag fuer begrenzte medizinische
  Eintraege
