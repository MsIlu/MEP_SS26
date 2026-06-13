# Bug Reports V4

Stand: 2026-06-12
Status: aktiv

## Zweck

Diese Datei sammelt laufende reale Bugbefunde und scharfe Laufprobleme fuer
den V4-Refactor.

Sie ist bewusst kein zweiter Refactor-Plan.

Sie soll:

- konkrete reproduzierbare Fehlerbilder festhalten
- sie den passenden V4-Bloecken zuordnen
- zwischen Architekturrest,
  Prompt-/LLM-Drift
  und sichtbarem Nutzerfehler unterscheiden
- kuenftige neue Befunde in derselben Form fortlaufend aufnehmbar machen


## Format

Pro Bugreport:

- ID
- Datum
- Status
- Betroffene V4-Bloecke
- Kurzbefund
- Reproduktionskontext
- Beobachtetes Verhalten
- Warum das problematisch ist
- Wahrscheinlichste Hauptkante
- Naechster sinnvoller Schnitt


## Offene Bugreports

### BR-V4-001 Datum: 12-06-26 Status: offen

- Betroffene V4-Bloecke:
  - Block 2
  - Block 3
- Kurzbefund:
  - der aktive Recommendation-Abschlussknoten wird zwar jetzt ueber einen
    kleinen Zwei-Wege-Resolver normalisiert,
    freie Antworttexte laufen danach aber teils trotzdem wieder in den
    normalen Intent-/Call-2-Pfad
- Reproduktionskontext:
  - `server/careena_pipeline3/server_log/logs/debug_log_pipeline3.txt`
  - Zeitfenster um `2026-06-12 02:13:17` bis `02:13:33`
- Beobachtetes Verhalten:
  - zuerst laeuft erfolgreich ein
    `RecommendationTransitionResolution`
  - direkt danach startet trotzdem noch ein normaler
    `IntentGateway`-Call
    und anschliessend ein `Call2ExtractionResult`-Call
  - fuer
    `Ich will erstmal wissen, ob ich ins KH muss oder so.`
    liefert der Intent-Gateway danach:
    `category:symptom_report`,
    `message_role:new_information`,
    `next_step:extract`
    und sogar
    `dialogue_hint:recommendation_requested`
- Warum das problematisch ist:
  - die Kante
    `Abschlussknoten -> Recommendation-Freigabe oder medizinischer Rueckweg`
    ist damit noch nicht wirklich sauber geschaltet
  - der Spezialknoten wird zwar separat gelesen,
    aber das Ergebnis kontrolliert den weiteren Turn-Pfad noch nicht klein und
    eindeutig genug
- Wahrscheinlichste Hauptkante:
  - primaer Block 2:
    noch unsaubere Trennung zwischen dialogischer Transition
    und normalem medizinischem Weiterpfad
  - sekundaer Block 3:
    es fehlt noch eine explizitere Antwortstrategie,
    so dass freie Antwortabsicht zu leicht wieder als medizinischer
    Default-Pfad gelesen wird
- Naechster sinnvoller Schnitt:
  - den Abschlussknoten-Endpunkt nicht nur normalisieren,
    sondern den weiteren Turn-Fluss danach expliziter an die aufgeloeste
    Reaktionsart binden
  - dabei sauber unterscheiden:
    blosse Wahl
    `report_more_information`
    vs.
    echter freier medizinischer Zusatzinhalt
  - Nachschnitt 12-06-26:
    der Intent-Gateway-Kontext und Prompt wurden inzwischen enger auf aktive
    `recommendation_ready_check`-Knoten zugeschnitten;
    fuer den Fall
    `Rueckweg gewaehlt, aber noch keine konkreten neuen medizinischen Fakten`
    gibt es jetzt den expliziten Scout-Hinweis
    `dialogue_hint:transition_continue_without_medical_content`
    als kleine Guardrail gegen unnoetige `Call 2`-Starts
  - weiterhin offen:
    ob die reale Runtime diesen engeren Scout-Vertrag im Live-Lauf jetzt
    robust genug befolgt und wie stark danach noch die zu aggressive
    `ready_for_transition`-Lage erneut dazwischenfunkt


### BR-V4-002 Datum: 12-06-26 Status: offen

- Betroffene V4-Bloecke:
  - Block 3
  - Block 2
- Kurzbefund:
  - Careena antwortet im aktiven Pfad noch zu stark als feste
    Kategorien-/Template-Maschine;
    dadurch wird das eigentliche Antwortverhalten selbst zum offenen
    Architekturrest
- Reproduktionskontext:
  - allgemeiner aktueller Codezustand von
    `application/managers/response_manager.py`
    und
    `application/services/response_text_builder.py`
  - bestaetigt durch die juengeren Logbefunde aus
    `debug_log_pipeline3.txt`
- Beobachtetes Verhalten:
  - die sichtbare Reaktion entsteht weitgehend aus
    `response_mode`
    plus statischen Textpfaden
  - ein freier sinnvoller Antwortpfad,
    der den laufenden medizinischen Fall,
    die aktuelle Turn-Absicht
    und das Nutzungsanliegen gemeinsam ausformuliert,
    fehlt noch
  - dadurch kippen freie Antworten leichter in unpassende medizinische oder
    dialogische Folgepfade
- Warum das problematisch ist:
  - der Turn-Fluss
    `Nachricht -> Verarbeitung -> Antwort -> naechste Nachricht`
    bleibt instabil,
    solange die Antwortseite fast nur aus festen Textreaktionen auf kleine
    Modi besteht
  - gerade jetzt,
    wo die Struktur stabiler wird,
    wird sichtbar,
    dass ein zentraler Teil des eigentlichen Antwortverhaltens noch fehlt
- Wahrscheinlichste Hauptkante:
  - primaer Block 3:
    Antwortstrategie ist noch nicht als eigene Schicht explizit genug
  - sekundaer Block 1:
    der neue Reaktionskern ist da,
    aber noch nicht bis zu einer sauberen Antwortstrategie weitergezogen
- Naechster sinnvoller Schnitt:
  - einen kleinen expliziten Strategy-Vertrag einziehen,
    der mindestens zwischen
    statischer Rueckfrage,
    KI-gestuetzter Antwort,
    Recommendation-Uebergang
    und einfacher kurzer Weiterfuehrung unterscheiden kann
  - den vorhandenen `MASTER_PROMPT` aus `server/config.py` nur lesend als
    Basis fuer einen spaeteren Careena3-spezifischen Antwortprompt mitdenken,
    statt von null neu zu formulieren


### BR-V4-003 Datum: 12-06-26 Status: offen

- Betroffene V4-Bloecke:
  - Block 2
  - Block 5
- Kurzbefund:
  - im juengsten echten Lauf driftet der medizinische Pfad fachlich stark:
    Alter,
    Geschlecht
    und sogar Symptomtyp werden falsch materialisiert
- Reproduktionskontext:
  - `server/careena_pipeline3/server_log/logs/debug_log_pipeline3.txt`
  - Szenario dazu in
    `server/careena_pipeline3/server_log/logs/debug_log_simulation3.txt`
    ab `2026-06-12 02:12:46`
- Beobachtetes Verhalten:
  - Simulationsszenario:
    Lukas,
    58,
    Sturz auf die Huefte,
    kaum auftreten
  - im Pipeline-Log taucht stattdessen auf:
    `subject.age: 34`,
    `subject.sex: female`
    und spaeter sogar
    `normalized_concept: abdominal_pain`
    fuer
    `Ich weiss nicht, ob ins KH muss. Es tut halt echt mega weh.`
- Warum das problematisch ist:
  - das ist nicht nur ein kleiner Extraktionsfehler,
    sondern ein deutlicher Drift zwischen realem Verlauf und materialisierter
    Fallwahrheit
  - solange dieser Drift offen ist,
    werden spaetere Readiness-,
    Response-
    und Recommendation-Entscheidungen auf instabiler Wahrheitsbasis gebaut
- Wahrscheinlichste Hauptkante:
  - primaer Block 2:
    die freie Antwort auf dem Abschlussknoten wird noch nicht sauber genug vom
    normalen medizinischen Pfad getrennt
  - sekundaer Block 5:
    der medizinische Werkzeugkasten bzw. Prompt-/Kontextzuschnitt bleibt in
    dieser Lage noch driftanfaellig
- Naechster sinnvoller Schnitt:
  - zuerst den freien Antwortfluss sauberer schalten,
    damit dieser Pfad nicht schon unnnoetig in die falsche medizinische
    Verarbeitung faellt
  - danach den betroffenen Call-2-Lauf gesondert gegen Prompt,
    Kontext und Outputvertrag sezieren
