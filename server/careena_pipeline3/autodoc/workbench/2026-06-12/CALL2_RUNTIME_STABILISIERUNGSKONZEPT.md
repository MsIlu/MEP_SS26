# Careena3 Call 2 Runtime- und Stabilisierungskonzept

Stand: 2026-06-12
Status: Arbeitsfassung nach V5 Block 1 bis 3

Baut auf:

- `autodoc/2026-06-12/REFACTOR_PLAN_V5.md`
- `autodoc/workbench/2026-06-09/CALL2_KONZEPT.md`
- dem aktuellen Runtime-Stand in `careena_pipeline3`


## Zweck

Dieses Dokument soll zwei Dinge zugleich leisten:

- das uebergeordnete Bild von `Call 2` festhalten
- daraus einen moeglichst schnellen und ehrlichen Stabilisierungspfad fuer
  den aktuellen Code ableiten

Es ist bewusst kein ferner Endarchitekturtext.

Es soll vor allem beantworten:

1. was `Call 2` in Careena eigentlich sein soll
2. was davon heute schon angelegt ist
3. was fuer den naechsten praktischen Schnitt jetzt wirklich wichtig ist
4. wie wir moeglichst schnell wieder auf einem rund laufenden Rad arbeiten
   statt auf einem Halbkreis


## Kurzfassung

`Call 2` soll nicht einfach "der Extraktionscall" sein.

`Call 2` soll ein begrenzter,
zustandsabhaengiger KI-Arbeitsraum sein,
der nur die Aufgaben bekommt,
die fuer die aktuelle Dialoglage und die aktuelle Nachricht wirklich sinnvoll
und erlaubt sind.

Extraktion ist ein grosser Teil davon,
aber nicht der einzige.

`Call 2` soll je nach Lage auch:

- Informationen normalisieren
- Fokus-Updates von neuen Zusatzinfos trennen
- Konflikte einordnen
- markieren,
  ob etwas geklaert werden muss
- und in begrenzten Bahnen auch gezielte Rueckfragen formulieren koennen

Wichtig:

- `Call 2` soll nicht als ungebremster Freiform-Chat laufen
- `Call 2` soll nicht breit ueber alles nachdenken
- `Call 2` soll nur in einem engen,
  steuerbaren Aufgabenrahmen arbeiten

Genau dadurch wird der Chat robuster:

- schwerer auszutricksen
- schwerer in unerwuenschte Bereiche zu ziehen
- und leichter gegen den aktiven Zustand zu kontrollieren


## Das eigentliche Zielbild

Der Kerngedanke lautet:

- `Call 1` bzw. die vordere Steuerung deutet grob,
  worum es in diesem Turn geht
- die concern-,
  Gate-
  und Response-Schichten begrenzen,
  was als naechster Zug ueberhaupt erlaubt ist
- `Call 2` bekommt daraus ein kleines Aufgabenpaket
  und arbeitet genau dieses Paket ab

Das heisst:

- nicht alles ueber alles laufen lassen
- nicht immer denselben breiten Extraktionspfad starten
- nicht jeden Turn wie einen Fall-Neuaufbau behandeln

Sondern:

- Lage lesen
- erlaubten Arbeitsraum bestimmen
- kleines Aufgabenpaket auswaehlen
- nur dieses Paket ausfuehren


## Was Call 2 inhaltlich koennen soll

### 1. Extraktion

Der offensichtlichste Bereich.

Aus Nutzernachrichten sollen medizinisch relevante Angaben geholt werden,
zum Beispiel:

- Symptome
- Verletzungen
- Messwerte
- Medikamente
- Personenbezug,
  wenn er fachlich noetig ist

Wichtig:

- Extraktion ist nicht automatisch immer gleich Fallaufbau
- Extraktion kann neue Fakten liefern
- oder nur den aktuellen Fokus aktualisieren

### 2. Normalisierung

`Call 2` soll nicht nur Rohtext ziehen,
sondern auch einzelne Angaben in eine brauchbare,
kleinere Struktur bringen.

Beispiele:

- Symptom oder Messwert sinnvoll einordnen
- Rohangabe auf Attributebene normalisieren
- Fokus-Update sauber von `new_items` trennen

### 3. Konflikt- und Klaerungsarbeit

Wenn Angaben nicht sauber zusammenpassen,
soll `Call 2` nicht blind eine Wahrheit erfinden.

Stattdessen muss es moeglich sein:

- Konflikte als Konflikte zu erkennen
- bei genug Kontext eine enge Einordnung zu liefern
- oder explizit zu markieren,
  dass geklaert werden muss

Genau dieser Bereich darf spaeter nicht als diffuse Merge-Magie
im Hintergrund verschwinden.

### 4. Gezielte Rueckfragen

Antwort ist nicht beliebig nach hinten verschiebbar.

Ohne gute Rueckfragen bleibt der Gespraechsverlauf stumpf
und die Runtime haengt an zu harter Hardcode-Logik.

Deshalb ist es sinnvoll,
dass `Call 2` perspektivisch auch gezielte Rueckfragen erzeugen kann,
wenn:

- keine dringlichere strukturierte Rueckfrage offen ist
- die aktuelle Lage weitere medizinische Klaerung braucht
- und die Gate-/Concern-Lage eine solche Rueckfrage erlaubt

Wichtig dabei:

- nicht als freie Allzweck-Antwort
- sondern als begrenzte,
  zustandsabhaengige Rueckfragen-Erzeugung

### 5. Eventuell begrenzte Antwortgenerierung

Es ist sinnvoll,
die Frage offen und praktisch zu halten:

- harte praktische Ausnahmen bleiben statisch
- aber jenseits davon kann `Call 2` spaeter in begrenztem Rahmen auch
  Antwort- oder Rueckfragetext erzeugen,
  wenn der erlaubte Arbeitsraum das sauber vorgibt

Das bedeutet nicht,
dass `Call 2` der ganze Response-Manager werden soll.

Es bedeutet nur:

- fuer bestimmte enge Antwortlagen
  kann `Call 2` ein geeignetes Arbeitswerkzeug sein


## Was daraus fuer die Architektur folgt

`Call 2` ist am besten nicht als einzelner "schlauer Call" zu lesen,
sondern als Werkzeugkasten.

Dieser Werkzeugkasten bekommt kleine Aufgabenpakete.

Die Steuerungsidee ist:

- beliebige Aufgabenpakete sind denkbar
- aber nur innerhalb eines begrenzten,
  expliziten Rahmens
- und nur dann,
  wenn Zustand und Nachricht dieses Paket wirklich rechtfertigen

Damit ist der richtige Architekturgedanke nicht:

- "wenn medizinisch, dann Call 2"

Sondern:

- "welches kleine Aufgabenpaket ist fuer diesen Turn erlaubt und noetig"


## Sinnvolle Aufgabenklassen fuer Call 2

Aus dem aktuellen Stand ergibt sich diese sinnvolle Palette.

### Bereits heute klar sinnvoll

- `resolve_subject_context`
- `extract_medical_facts`
- `update_focus_fact`
- `identify_additional_new_info`
- `mark_open_question`

### Sehr wahrscheinlich naechster sinnvoller Ausbau

- `normalize_observation`
- `resolve_fact_conflict`
- `decide_followup_needed`
- `generate_followup_question`

### Spaeter optional

- `generate_bounded_response`

Wichtig:

- diese Liste ist keine Pflicht,
  alles sofort zu bauen
- sie ist eine bessere Lesebrille fuer die heutige `operation_mode`- und
  `tasks`-Logik


## Was der aktuelle Call 2 heute schon macht

Im aktuellen Code ist bereits einiges von dieser Richtung sichtbar.

### Aktuelle Modi

- `focused_new_fact_extraction`
- `followup_slot_update`
- `existing_fact_revision`
- `mixed_update_and_new_info`
- `no_medical_update_expected`

### Aktuelle Tasks

- `resolve_subject_context`
- `extract_symptoms`
- `extract_injuries`
- `extract_measurements`
- `extract_medications`

### Aktueller kleiner Outputkern

- `subject_update`
- `focus_update`
- `new_items`
- `open_questions`

Das ist bereits keine ganz schlechte Basis.

Der eigentliche Restfehler liegt weniger darin,
dass gar nichts da waere,
sondern darin,
dass die heutige Palette noch zu stark als Extraktionspalette
und noch zu wenig als allgemeiner Aufgabenraum gelesen wird.


## Was aus dem aelteren Call-2-Konzept weiter wertvoll bleibt

Aus `autodoc/workbench/2026-06-09/CALL2_KONZEPT.md`
bleiben besonders folgende Punkte weiter stark:

### 1. `Call 2` soll nicht breiter Fall-Rekonstruktionscall sein

Das bleibt voll gueltig.

### 2. Der Input soll klein bleiben

Besonders wichtig bleibt:

- `latest_user_message` als primaere Faktquelle
- kleiner steuernder Kontext
- kein breites `case_summary`
  als Zweitwahrheit

### 3. `focus_update` und `new_items` muessen klar getrennt bleiben

Das ist weiterhin einer der wichtigsten Vertraege.

### 4. Python und LLM sollen verschiedene Rollen haben

Weiter starke Lesart:

- LLM fuer kleine Deutung,
  Claim-Bildung,
  Fokus-Update,
  Zusatzinfo,
  enge offene Fragen
- Python fuer banale Vertragsdisziplin,
  Pruning,
  kleine deterministische Normalisierung

### 5. Ein enger Werkzeugkasten ist besser als ein breiter Einheitscall

Das passt exakt zu der jetzigen Richtung aus V5.


## Was sich durch V5 Block 1 bis 3 geaendert hat

Durch die neuen concern-,
Gate-
und Response-Schnitte hat sich der Massstab fuer `Call 2` verschaerft.

Heute ist die zentrale Frage nicht mehr nur:

- was kann `Call 2` extrahieren

Sondern:

- welche Art von Arbeit ist in der aktuellen Dialoglage ueberhaupt erlaubt

Das heisst fuer `Call 2` jetzt:

- nicht gegen die neue Freigabelogik arbeiten
- nicht neue Semantik ersetzen
- nicht unnoetig starten,
  wenn Concern/Gate/Response die Lage schon klar genug gemacht haben


## Was fuer Block 4 jetzt wirklich ansteht

Block 4 sollte gerade nicht bedeuten:

- den grossen dynamischen Ziel-Werkzeugkasten sofort bauen

Sondern:

- den heutigen Call-2-Runtime-Vertrag so schneiden,
  dass er das System weniger stoert

Das heisst konkret:

### 1. Unnoetige Extraktionsstarts reduzieren

Heute springt `Call 2` noch zu leicht an,
obwohl die obere Logik teilweise schon weiss,
welcher naechste Zug erlaubt ist.

Block 4 muss deshalb klarer machen:

- wann gar keine Extraktion noetig ist
- wann nur kleine Interpretationsarbeit noetig ist
- wann wirklich medizinische Tiefenarbeit noetig ist

### 2. Die heutige Palette ehrlicher lesen

Die aktuellen Modi sollten nicht mehr nur als Extraktionsmodi gelesen werden,
sondern als erste rohe Aufgabenpakete.

Zum Beispiel:

- `followup_slot_update`
  ist nicht einfach Extraktion,
  sondern Fokus-Update-Arbeit
- `mixed_update_and_new_info`
  ist nicht einfach "mehr Extraktion",
  sondern die Trennung aus Fokus-Update plus Zusatzinfo
- `existing_fact_revision`
  ist eher enge Revisions- und Normalisierungsarbeit

### 3. Truth-write sauberer fassen

Der wichtige Unterschied muss expliziter werden zwischen:

- keine Extraktion
- Extraktion ohne Truth-Write
- Extraktion mit Truth-Write

Gerade dieser Punkt ist zentral,
damit Call 2 nicht weiter stoerend in Gate und Response hineinwirkt.

### 4. Antwortthema nicht ignorieren,
aber richtig einordnen

Antwort ist wichtig
und kann nicht beliebig spaeter kommen.

Aber fuer Block 4 bedeutet das nicht:

- sofort die ganze Antwortarchitektur in Call 2 verschieben

Sondern eher:

- den Call-2-Vertrag so vorbereiten,
  dass spaeter begrenzte gezielte Rueckfragen oder enge bounded Antworten
  als Aufgabenpaket sauber andocken koennen


## Der schnellste sinnvolle Stabilisierungspfad

Wenn wir moeglichst schnell wieder auf einem rund laufenden Rad arbeiten
wollen,
dann ist dieser Pfad sinnvoll:

1. die heutige Call-2-Palette explizit als Aufgabenraum lesen
   statt nur als Extraktionsrampe
2. fuer die aktuelle Runtime sichtbar trennen:
   kein Call 2 /
   Call 2 ohne Truth-Write /
   Call 2 mit Truth-Write
3. unnoetige oder zu breite Extraktionsstarts gegen Concern/Gate/Response
   wegschneiden
4. die bestehenden Modi enger auf ihre echte Rolle zurueckziehen
5. erst danach die Frage weiter aufziehen,
   welche zusaetzlichen Pakete wie
   `resolve_fact_conflict`
   oder
   `generate_followup_question`
   als naechstes wirklich noetig sind


## Konkrete Arbeitsfolgen fuer den naechsten Schnitt

Wenn wir aus diesem Dokument direkt handeln wollen,
dann ist fuer den unmittelbaren naechsten Schritt am wichtigsten:

### Nicht jetzt sofort

- den vollen Werkzeugkasten bauen
- den ganzen Response-Weg in `Call 2` ziehen
- neue breite Kontextsummaries einbauen

### Sondern jetzt

- die aktuelle Runtime-Palette gegen die neue Gate-Lage pruefen
- `operation_mode` und `tasks` auf echte Aufgabenrollen abbilden
- die Truth-write-Schwelle expliziter machen
- pruefen,
  welche heutigen `Call 2`-Starts eigentlich nur alte Drift
  oder alte Uebergangslogik mittragen


## Verdichtetes Fazit

`Call 2` sollte in Careena nicht als breiter medizinischer Einheitscall
verstanden werden.

Er sollte ein begrenzter,
zustandsabhaengiger,
konfigurierbarer Aufgabenraum sein.

Die aktuelle Nachricht bleibt die Hauptfaktquelle.
Die Steuerung entscheidet,
welches kleine Arbeitspaket erlaubt ist.
`Call 2` fuehrt dieses Paket aus.

Fuer jetzt ist deshalb der richtige Fokus:

- nicht `Call 2` sofort groesser machen
- sondern ihn kleiner,
  ehrlicher
  und aufgabenbasierter machen

Dann koennen wir spaeter darauf aufbauen:

- bessere gezielte Rueckfragen
- bessere Konfliktarbeit
- begrenzte Antwortgenerierung
- und irgendwann ein wirklich sauberer dynamischer Werkzeugkasten
