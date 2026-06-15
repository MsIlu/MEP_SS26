# Careena3 Bounded Master Prompt Response Lane

Stand: 2026-06-12
Status: Architektur- und Entstau-Notiz

Baut auf:

- `autodoc/2026-06-12/REFACTOR_PLAN_V5.md`
- `autodoc/2026-06-12/CALL2_RUNTIME_STABILISIERUNGSKONZEPT.md`
- dem historischen `MASTER_PROMPT` in `server/config.py`


## Zweck

Dieses Dokument haelt einen moeglichen bewussten Entstau-Schritt fest:

- kurzfristig wieder intelligentere Gespraechsfuehrung bekommen
- ohne die aktuelle Refactor-Richtung komplett aufzugeben
- und ohne unkontrolliert in den alten Voll-Chat-Modus zurueckzufallen


## Ausgangsproblem

Das aktuelle System gewinnt zwar schrittweise an expliziterer Concern-,
Gate-
und Response-Struktur,
aber die sichtbare Gespraechsfuehrung bleibt noch zu stumpf.

Folge:

- das System fuehlt sich im Chat oft nicht intelligent genug an
- Hardcode-Antwortpfade tragen zu viel Last
- die weitere Architekturarbeit dreht sich leichter im Kreis,
  weil der reale Gespraechsfluss selbst noch zu schwach ist


## Grundidee

Als temporaere Zwischenarchitektur kann ein eigener staerkerer
LLM-Antwortcall eingefuehrt werden,
der sich vorlaeufig wieder staerker am historischen `MASTER_PROMPT`
orientiert.

Wichtig:

- das ist nicht als Rueckkehr zum ungebremsten Voll-Chat gemeint
- das ist eine bewusst begrenzte
  `bounded response lane`

Die Idee lautet:

- die KI bekommt wieder mehr Gespraechsfuehrungsintelligenz
- aber nur innerhalb eines engeren kontrollierten Runtime-Rahmens


## Was diese Lane kurzfristig leisten darf

- natuerlichere Gespraechsfuehrung
- intelligentere Formulierung von Rueckfragen
- bessere Aufnahme und Rueckspiegelung des Nutzeranliegens
- adaptiveres Antworten,
  solange die erlaubte Richtung schon durch Runtime-Signale begrenzt ist

Kurz:

- die Lane darf die Konversation wieder geschmeidiger machen
- sie darf nicht wieder die ganze Systemlogik heimlich uebernehmen


## Was ausdruecklich draussen bleiben soll

Die Lane soll nicht:

- selbst medizinische Wahrheit festlegen
- selbst Recommendation freigeben
- selbst Safety-Entscheidungen ersetzen
- selbst Merge- oder Konfliktlogik des Falls entscheiden
- ungebremst in nicht vorgesehene Themenbereiche driften
- die neuen Concern- oder Gate-Vertraege wieder unsichtbar machen


## Saubere Lesart

Die richtige Lesart ist nicht:

- "der alte Master Prompt macht wieder alles"

Sondern:

- "wir geben der Antwortschicht kurzfristig wieder mehr LLM-getragene
  Gespraechsintelligenz,
  waehrend wir die fachlichen und steuernden Verantwortungen schrittweise
  in explizite Runtime-Vertraege herausziehen"


## Moegliche Rollenverteilung in dieser Zwischenstufe

### Runtime bleibt zustaendig fuer

- Concern-/Fortschrittslage
- Freigabelogik
- harte Sonderpfade
- Safety
- Recommendation-Gates
- strukturierten Fallzustand

### Bounded Master Prompt Lane wird zustaendig fuer

- natuerliche Formulierung
- begrenzte adaptive Gespraechsfuehrung
- gezielte Rueckfragen innerhalb eines erlaubten Antwortkorridors
- besseres sprachliches Aufgreifen des Nutzeranliegens


## Warum das sinnvoll sein kann

Dieser Schritt kann helfen,
frueher wieder auf einem brauchbaren Gespraechssystem zu arbeiten.

Das bringt:

- besseres reales Feedback auf die Runtime-Architektur
- weniger Stumpfheit im aktiven Chatverlauf
- weniger Druck,
  die ganze Gespraechsintelligenz sofort ueber Hardcode oder spaeter allein
  ueber `Call 2` retten zu muessen


## Risiko

Das zentrale Risiko ist,
dass diese Lane unbewusst wieder zur neuen versteckten Hauptarchitektur wird.

Deshalb braucht sie:

- klare Grenzen
- klaren Input
- klaren erlaubten Antwortkorridor
- spaetere Rueckverlagerung ihrer impliziten Verantwortung in explizite
  Runtime-Vertraege


## Wie sie spaeter wieder sauber auseinandergezogen wird

Die Lane ist nur dann gesund,
wenn sie als Uebergangsschicht gelesen wird.

Spaeter sollen schrittweise herausgezogen werden:

- Concern-/Anliegenlogik
- Gate-/Freigabelogik
- strukturierte Follow-up-Entscheidungen
- spaetere Call-2-Aufgabenpakete
- Recommendation-Zugang und -Inhalt

Das Zielbild bleibt also:

- weniger versteckte Master-Prompt-Verantwortung
- mehr sichtbare Runtime-Vertraege

Aber der Weg dorthin darf ueber eine bewusst begrenzte
stabilisierende Antwortschicht fuehren.


## Verdichtetes Fazit

Eine `bounded master prompt response lane` kann ein sinnvoller
Entstau-Schritt sein,
wenn sie:

- intelligenter formuliert
- die Gespraechsfuehrung kurzfristig verbessert
- aber fachlich und steuernd begrenzt bleibt

Sie ist dann keine Abkehr vom Refactor,
sondern eine temporaere Hilfe,
damit die weitere Architekturarbeit nicht auf einem stumpfen
Geschaeftsverlauf aufsetzt.
