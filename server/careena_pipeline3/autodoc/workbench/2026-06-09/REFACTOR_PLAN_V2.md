# Careena3 Refactor Plan V2

Stand: 2026-06-09
Status: aktiv
Baut auf:

- `autodoc/workbench/2026-06-09/REFACTOR_PLAN.md`
- `autodoc/wiki/SYSTEM_OVERVIEW.md`
- `autodoc/workbench/2026-06-08/TARGET_MODEL6.md`


## Zweck

Diese zweite Fassung schaerft den aktiven Refactor-Plan in einem wichtigen
Punkt nach:

Der Refactor muss nicht sofort jedes Architekturproblem praktisch loesen.

Sein primaeres Ziel ist zunaechst:

- Verantwortungsgrenzen sauber definieren
- Vertraege vom Kern nach aussen stabilisieren
- Problemverdichtungen sichtbar in passende Module schneiden
- bewusst unfertige Restlogik als Platzhalter markieren statt sie vorschnell
  unsauber "fertig" zu reparieren

Damit bleibt die Architekturentwicklung kontrollierbar, auch wenn einzelne
Bereiche voruebergehend nur mit Dummy- oder Placeholder-Logik weiterlaufen.


## Neue Hauptpraezisierung gegenueber V1

Der Refactor wird ab hier explizit als
`boundary-first refactoring` gelesen.

Das bedeutet:

1. zuerst Verantwortungsgrenzen und Vertragsanfaenge sauberziehen
2. dann Module mit klarer Problemverdichtung bilden
3. funktionale Restlogik notfalls temporaer als sichtbar markierter
   Platzhalter stehen lassen
4. komplexere echte Fachlogik erst dann nachziehen, wenn die Schichtgrenzen
   tragfaehig sind

Die Leitfrage pro Schritt lautet deshalb nicht:

- "koennen wir dieses Problem sofort fachlich voll loesen?"

sondern:

- "koennen wir klarer festlegen, welche Schicht das Problem spaeter sauber
  tragen soll?"


## Quellenbasis

Fuehrende Soll-Quellen:

- `autodoc/wiki/SYSTEM_OVERVIEW.md`
- `autodoc/workbench/2026-06-08/TARGET_MODEL6.md`

Arbeits- und Review-Quellen:

- `autodoc/workbench/2026-06-09/REFACTOR_PLAN.md`
- `autodoc/workbench/2026-06-08/CAREENA3_REFACTORING_PLAN.md`
- `autodoc/workbench/2026-06-08/CODE_REVIEW_FRAMEWORK.md`

Code-Anker:

- `application/managers/dialogue_manager.py`
- `application/managers/entry_manager.py`
- `application/managers/extraction_manager.py`
- `application/managers/case_state_manager.py`
- `application/managers/response_manager.py`
- `application/managers/safety_manager.py`
- `application/managers/confirmation_manager.py`
- `application/services/resilient_extraction_service.py`
- `application/services/extraction_result_mapper.py`
- `application/services/readiness_evaluator.py`
- `application/services/recommendation_state_service.py`
- `application/services/response_text_builder.py`
- `domain/requirement_policy.py`
- `domain/case_merge_policy.py`
- `domain/case_merger.py`
- `llm/context.py`
- `llm/prompts/case_extraction.py`
- `server/careena3.py`

Hinweis:

- `GENERAL_GOOD_ARCHITECHTURE_GUIDELINES.md` bzw.
  `GENERAL_GOOD_ARCHITECTURE_GUIDELINES.md` war im aktuellen Workspace beim
  Erstellen dieser Fassung weiterhin nicht auffindbar


## Leitprinzipien fuer V2

## 1. Grenze vor Vollausbau

Wenn eine Schicht noch unsauber ist, wird zuerst ihre Verantwortung
geschnitten, nicht sofort ihre komplette Fachlogik perfektioniert.

## 2. Vom Kern nach aussen

Die Reihenfolge bleibt:

- zuerst Truth- und Uebergangsmitte
- dann Process-State und Gate
- dann Response, Safety, Confirmation
- dann spaetere Funktionsintelligenz und aeussere Integration

## 3. Sichtbar unfertig ist erlaubt

Platzhalter sind erlaubt, wenn sie:

- klar als Platzhalter markiert sind
- keine versteckte Zweitlogik einziehen
- keine dauerhafte Autoritaet vortaeuschen
- die Zielverantwortung eher absichern als verwischen

## 4. Dummy-Logik nur unter Disziplin

Dummy- oder Placeholder-Logik ist nur dann akzeptabel, wenn:

- sie den Vertrag eines Moduls schuetzt
- sie spaetere echte Logik nicht verbaut
- sie im Code kommentiert und als vorlaeufig benannt ist
- sie nicht versehentlich als stille Fachentscheidung in andere Schichten
  ausstrahlt

## 5. Dokumentation ist Teil des Refactors

Wenn ein Modul im Refactor semantisch umgeschnitten wird, gehoert eine kleine
strukturierte Rollendokumentation dazu.

Nicht als Nacharbeit, sondern als Teil des eigentlichen Refactor-Schritts.


## Zielbild der Refactor-Haltung

Der Refactor soll schrittweise Module erzeugen, die entweder:

- bereits eine saubere finale Verantwortung tragen
- oder sichtbar als Uebergangsmodul mit enger begrenzter Restrolle markiert
  sind

Er soll gerade nicht zu einem Zwischenzustand fuehren, in dem viele Klassen:

- ein bisschen Signal
- ein bisschen Wahrheit
- ein bisschen Process-State
- und ein bisschen Antwortpolitik

gleichzeitig tragen.


## Erlaubte Formen von Platzhaltern

Folgende Arten von Platzhaltern sind im Refactor ausdruecklich erlaubt:

- Dummy-Rueckgabewerte, wenn ein Modulvertrag bereits festgezogen wurde,
  die finale Fachlogik aber spaeter folgt
- Platzhalterpfade in Response, Safety oder Confirmation, wenn die fehlende
  Logik als solche offen benannt bleibt
- vorlaeufige Adapter, wenn sie ausdruecklich als transitional markiert sind
  und gerade verkleinert statt vergroessert werden
- kleine Kommentare wie:
  `placeholder until requirement model is explicit`
  oder
  `temporary bridge while MessageDelta is still active`

Nicht erlaubt sind dagegen:

- versteckte Platzhalter, die wie echte Fachlogik aussehen
- Dummy-Logik ohne Markierung
- Platzhalter, die schon wieder neue implizite Verantwortung einsammeln
- "nur kurz" eingebaute Sonderfaelle, die spaeter faktisch dauerhaft bleiben


## Dokumentationsdisziplin waehrend des Refactors

Wenn ein Modul oder eine Klasse im Zuge des Refactors semantisch neu
geschnitten wird, soll geprueft werden, ob bereits eine strukturierte
Kurz-Dokumentation existiert.

Falls vorhanden:

- aktualisieren

Falls nicht vorhanden und die Klasse architektonisch wichtig ist:

- knapp einfuehren

Bevorzugte Inhalte direkt im Modul:

- Rolle
- Schichtzuordnung
- was das Modul explizit verantwortet
- was es explizit nicht verantwortet
- falls relevant: warum es noch transitional oder placeholderhaft ist

Diese Dokumentation soll kurz bleiben, aber den naechsten Refactor-Schritt
lesbarer machen.


## Arbeitsfragen pro Refactor-Schritt

Zusaetzlich zu den Leitfragen aus V1 gelten jetzt besonders:

- Welche Grenze wird durch diesen Schritt klarer?
- Welches Problem wird hier nicht geloest, aber sauber eingegrenzt?
- Welches Modul wird dadurch zu einer klareren Problemverdichtung?
- Ist ein Platzhalter hier sinnvoller als eine unsaubere Scheinausloesung?
- Ist der Platzhalter sichtbar genug kommentiert?
- Wurde die Modul-Dokumentation bei einer Rollenveraenderung mitgezogen?


## Neue Definition von Fortschritt

Ein Schritt ist in V2 bereits dann gut, wenn mindestens eines davon erreicht
wird:

- eine Verantwortung ist klarer begrenzt
- eine bisher gemischte Klasse ist sauberer in eine Zielrolle verschoben
- ein Platzhalter ersetzt unsaubere versteckte Fachlogik
- ein Restproblem ist jetzt sichtbar in einem passenden Modul konzentriert
- eine Uebergangsklasse ist ehrlicher als solche markiert
- die Modul-Dokumentation macht den neuen Stand besser lesbar

Ein Schritt muss also nicht sofort die perfekte Endlogik liefern, solange er
die Architektur sauberer aufspannt.


## Ueberarbeitete globale Reihenfolge

1. Call-2-Vertrag und Kontextpolitik verengen
2. Extraction-zu-Truth-Bruecke in kleinere Module schneiden
3. Requirement-, Follow-up- und Readiness-Verantwortungen sauber begrenzen
4. Response-Policy und Transition-Zustand explizit machen
5. Safety als klar abgegrenztes Modul vorbereiten, notfalls mit sichtbaren
   Platzhaltern
6. Confirmation/Korrektur als eigenen Rueckkanal vorbereiten, notfalls mit
   minimalem Dummy-Pfad
7. kleine Signalgrammatik und spaetere Prompt-Komposition nur auf den
   gefestigten Grenzen aufbauen
8. Recommendation-Content und aeussere Integration zuletzt nachziehen


## Block 0: Arbeitsvertrag fuer Boundary-First-Refactoring [aktiv]

## Ziel

Den Refactor so fuehren, dass Verantwortungsgrenzen selbst als erster
Arbeitsgegenstand behandelt werden.

## Sollzustand

- nicht jedes Problem wird sofort geloest
- aber jedes groessere Problem wird in eine passendere Schicht einsortiert
- Platzhalter sind erlaubt, wenn sie den Vertrag schuetzen
- Modul-Dokumentation wird bei semantischen Schnitten mitgefuehrt

## Zusatzausfuehrung

Wenn ein Modul nach einem Refactor-Schritt noch nicht fachlich stark genug
ist, ist das okay, solange mindestens diese drei Dinge stimmen:

1. seine Rolle ist klarer
2. seine Grenze ist kleiner
3. seine Unfertigkeit ist sichtbar

## Block-Gate / Done

- die laufende Arbeit driftet nicht in "alles gleichzeitig loesen"
- Grenzdefinition ist als eigener Fortschritt akzeptiert


## Block 1: Call-2-Vertrag und Kontextpolitik verengen [hoechste Prioritaet]

## Ziel

Call 2 soll nicht "moeglichst viel medizinisch auf einmal" tun, sondern eine
enge klar definierte Rolle tragen.

## Verschaerfte Lesart in V2

Der erste Erfolg dieses Blocks ist nicht schon ein perfekter neuer
Extraktionspfad.

Der erste Erfolg ist:

- dass klarer ist, was Call 2 dauerhaft darf
- und was ausdruecklich nicht mehr seine Aufgabe sein soll

## Praktische Arbeitsrichtung

1. minimalen Outputvertrag definieren
2. ueberfluessigen Kontext identifizieren
3. wo noetig lieber vorlaeufigen Placeholder-Kontext stehen lassen als
   wieder breite Summary-Autoritaet zurueckzuholen
4. begleitende Kurz-Doku in den betroffenen Modulen nachziehen oder
   aktualisieren

## Block-Gate / Done

- Call 2 ist enger beschrieben als zuvor
- Unklarheiten sind eher als offener Rest am Vertrag markiert als wieder in
  Python- oder Promptmagie versteckt
- relevante Module tragen aktualisierte Rollendoku, wenn sich ihre Aufgabe
  merklich geaendert hat


## Block 2: Extraction-zu-Truth-Bruecke in Problemverdichtungen schneiden [offen]

## Ziel

Die heutige Mischzone aus `ExtractionResultMapper`, `MessageDelta` und
`ResilientExtractionService` in klarere Teilverantwortungen zerlegen.

## Verschaerfte Lesart in V2

Dieser Block muss nicht sofort den finalen Endzustand herstellen.

Er darf auch zunaechst solche Zwischenziele erreichen:

- ein Adapter wird kleiner und ehrlicher transitional
- ein Follow-up-Reparaturpfad wird in ein eigenes kleines Modul gezogen
- ein Dummy-Bridge-Vertrag ersetzt eine unsaubere implizite Mischrolle

## Praktische Arbeitsrichtung

1. Problemverdichtungen explizit benennen:
   Fehlergrenze,
   optionale Nachnormalisierung,
   Follow-up-Anpassung,
   Bridge zur Truth-Schicht
2. diese Verantwortungen notfalls zuerst mit kleinen Platzhalterobjekten oder
   Dummypfaden voneinander trennen
3. Modul-Doku immer dann aktualisieren, wenn aus einer Sammelklasse eine
   kleinere Zielrolle herausgeloest wird

## Block-Gate / Done

- die Mischzone ist in sichtbarere Teilrollen geschnitten
- verbleibende Restadapter sind ehrlich markiert
- Uebergangspfade wirken weniger wie heimliche Zweitwahrheit


## Block 3: Requirement-, Follow-up- und Readiness-Grenzen festziehen [offen]

## Ziel

Diese Schicht soll klarer entscheiden koennen:

- was ist Process-State
- was ist Pflichtfeldlogik
- was ist abgeleitete Freigabelage

## Verschaerfte Lesart in V2

Hier muss nicht sofort das perfekte finale Requirement-System entstehen.

Es reicht fuer guten Fortschritt schon, wenn:

- die heutige Modul-/Requirement-Mischung klarer getrennt wird
- `Readiness` weniger implizite Provisorik traegt
- ein expliziter Platzhalter fuer spaetere feinere Gate-Semantik sauber
  eingefuehrt wird

## Praktische Arbeitsrichtung

1. Requirement fachlich definieren
2. Readiness als abgeleitete Wahrheit klarer vom Requirement-Modell trennen
3. lieber einen klaren begrenzten Placeholder fuer spaetere feinere
   Recommendation-Gates setzen als neue Hilfsheuristik verteilen
4. betroffene Services und Policies dokumentarisch nachschaerfen

## Block-Gate / Done

- Process-State, Requirement und Gate sind begrifflich und technisch
  sauberer getrennt
- funktionale Restluecken sind sichtbar statt magisch repariert


## Block 4: Response-Policy und Transition sichtbar machen [offen]

## Ziel

Die heutige Uebergangslogik zwischen `continue`, `ask_followup`,
`guide_next_step` und `recommend` soll zu einer expliziteren
Antwortfreigabeschicht werden.

## Verschaerfte Lesart in V2

Auch hier ist es okay, wenn zunaechst nur ein kleiner klarer
Transition-Vertrag entsteht und Teile der Antwortlogik noch placeholderhaft
bleiben.

Wichtiger ist:

- dass der Platzhalter an der richtigen Stelle sitzt
- und nicht mehr `ResponseTextBuilder` heimlich fehlende Zustandslogik ersetzt

## Praktische Arbeitsrichtung

1. kleinen Transition- oder Goal-Status definieren
2. `ResponseManager` staerker als Policy-Schicht lesen
3. `ResponseTextBuilder` auf freigegebene Zustaende begrenzen
4. wo noetig placeholderhafte Policy-Ausgaenge klar kommentieren statt
   sprachlich zu viel zu behaupten

## Block-Gate / Done

- Antwortpfade sind zustandsseitig klarer
- verbleibende Dummy-Pfade sind sichtbar und kommentiert
- Text ersetzt weniger fehlende Architektur


## Block 5: Safety als abgegrenzte Schicht vorbereiten [spaeter]

## Ziel

Safety soll als eigene Schicht erkennbar werden, auch wenn die fachliche
Tiefe zunaechst noch begrenzt bleibt.

## Verschaerfte Lesart in V2

Ein erster guter Schritt kann hier schon sein:

- Eingangsvertraege klarziehen
- die drei Safety-Ebenen sauber benennen
- vorlaeufige Dummy-Pruefungen sichtbar als Platzhalter markieren

## Block-Gate / Done

- Safety ist strukturell klarer abgegrenzt
- selbst wenn die eigentliche Logik noch teilweise scaffold bleibt


## Block 6: Confirmation als eigener Rueckkanal vorbereiten [spaeter]

## Ziel

Confirmation und Korrektur sollen einen klaren spaeteren Platz bekommen,
nicht nur einen Kommentar am Rand.

## Verschaerfte Lesart in V2

Es ist voellig okay, wenn dieser Block zunaechst nur:

- einen klaren Vertrag beschreibt
- einen Minimalpfad oder Dummy-Hook einzieht
- und den Rueckweg in Case-Truth vorbereitet

## Block-Gate / Done

- Confirmation ist als echter Zielpfad lesbar
- selbst wenn seine operative Logik noch vorlaeufig bleibt


## Block 7: Signalgrammatik und spaetere Prompt-Komposition nur auf stabilen Grenzen [spaeter]

## Ziel

Die interessante Signallogik und spaetere Block-/Skip-Prompt-Idee erst dann
ausbauen, wenn die Kernschichten stabiler tragen.

## V2-Schutzregel

Keine neue Signalgrammatik darf eingefuehrt werden, nur um heutige
Grenzprobleme zu kaschieren.

Wenn noetig, lieber:

- weniger Signale
- klarere Platzhalter
- und mehr sichtbare Unfertigkeit

statt weitere implizite Steuerkomplexitaet.


## Block 8: Recommendation-Content und aeussere Integration zuletzt [spaeter]

## Ziel

Den aeusseren Ausbau bewusst auf spaeter verschieben, damit der Kern nicht
durch Integrationsdruck wieder unsauber wird.

## V2-Schutzregel

Wenn Recommendation oder Integration frueh einen Platzhalter braucht, darf
dieser existieren, solange er:

- die Schichtgrenze schuetzt
- nicht falsche fachliche Reife vortaeuscht
- klar kommentiert und dokumentiert ist


## Konkrete Startempfehlung

Der naechste gute praktische Schritt bleibt:

1. minimalen Call-2-Outputvertrag knapp festziehen
2. daran `llm/context.py`, `case_extraction.py` und
   `resilient_extraction_service.py` messen
3. bei der ersten echten Schnittarbeit bewusst pruefen:
   wo ist ein sauber markierter Placeholder besser als eine neue Reparaturregel
4. parallel die Rollendokumentation der betroffenen Module mitziehen


## Schlussbewertung

V2 verschaerft den Plan in einer fuer Careena wichtigen Richtung:

Der Refactor muss nicht alles sofort koennen.
Er muss zuerst dafuer sorgen, dass die spaeteren Faehigkeiten an den
richtigen Stellen wohnen.

Die wichtigste Regel lautet deshalb jetzt noch klarer:

- lieber eine saubere Grenze mit sichtbarem Placeholder
  als eine unsaubere Scheinfertigstellung mit versteckter Logik.
