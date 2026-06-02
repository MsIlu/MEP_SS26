### Hinweis

Diese Datei wurde KI-generiert, um uns bei der Übersicht und Pflege des Projekts zu unterstützen.

# Changelog

In dieser Datei dokumentieren wir relevante Änderungen für Review, Teamarbeit
und Abgabe.

## Aktueller App-Stand

| Bereich            | Stand                        |
|--------------------|------------------------------|
| App-Version        | `1.0.0`                      |
| Quelle der Version | `app1/pubspec.yaml`          |
| Datum              | 2026-05-22                   |
| Status             | Entwicklungsstand / Prototyp |

## [Unreleased]

### Added

- `app/app_dependencies.dart` als zentraler Composition Root für langlebige
  Frontend-Abhängigkeiten ergänzt.
- `ApiException` und `ApiErrorType` für typisierte API-Fehler ergänzt.
- Unit-Tests für `ChatService` und `ChatResponse.fromJson` ergänzt.
- `MyApp` unterstützt injizierbare `ChatController`, damit Widget-Tests ohne
  echte Backend-Initialisierung laufen können.
- Neue Strukturdatei `documents/lib_structure.md` ergänzt.
- Login-Screen und mehrstufigen Registrierungs-Screen als neues
  `features/authscreen` ergänzt.
- `Meine Medikamente` als neues Feature ergänzt, inklusive lokaler Speicherung
  von Medikament, Dosis, Einnahmezeit und täglichen Push-Erinnerungen.
- Appweite Textauswahl über eine globale `SelectionArea` ergänzt, damit Nutzer
  sichtbare Texte innerhalb der App markieren und kopieren können.

### Changed

- Chat-Abhängigkeiten werden nicht mehr in `MyApp.build()` erstellt. Dadurch
  bleiben Controller, Session und HTTP-Client stabil über Rebuilds hinweg.
- Der Composition Root liegt außerhalb von `core`, damit gemeinsame Core-Module
  keine Feature-Module importieren.
- `ApiClient` bleibt generisch für HTTP/JSON zuständig; Chat-spezifische
  Endpunkte bleiben in `ChatApi`.
- `AppConfig.baseUrl` kann über
  `--dart-define=API_BASE_URL=...` überschrieben werden.
- Kommentare in den angepassten Frontend-Dateien wurden reduziert und stärker
  auf Architekturabsicht statt Code-Wiederholung ausgerichtet.
- Die alte Datei `LIB_STRUKTUR.md` wurde durch `lib_structure.md` ersetzt.
- Onboarding-Buttons führen nun in die passenden Auth-Screens statt direkt ins
  Home.
- Auth-Screens nach Single-Responsibility-Prinzip auf Screens, Widgets, Theme,
  Models und Validatoren aufgeteilt.
- Auth-Widgets nach `buttons`, `fields`, `layout`, `registration` und `review`
  gruppiert; Registrierungs-Formularzustand in einen ViewModel-Controller
  ausgelagert.
- Kleine Auth-Widget-Dateien zu fachlichen Sammeldateien konsolidiert, ohne
  Screens, ViewModels, Validatoren oder Theme zu vermischen.
- Registrierungs-Sammeldatei wieder in einzelne Step-Dateien aufgeteilt, damit
  jeder Registrierungsschritt separat wartbar bleibt.
- Auth-Widgets in `common`, `registration` und `review` organisiert; alte leere
  Widget-Unterordner entfernt und `review_consent` in einzelne Review-Bausteine
  geteilt.
- Geburtsdatum in der Registrierung formatiert automatisch zu `TT.MM.JJJJ`,
  validiert das Geburtsjahr gegen das aktuelle Jahr und zeigt das berechnete
  Alter direkt neben dem Feld an.
- Geburtsdatum in separate Felder für `TT`, `MM` und `JJJJ` aufgeteilt; Fokus
  springt automatisch weiter und das ausgegraute Altersfeld nutzt dieselbe
  Feldoptik wie die übrigen Formularfelder.
- Geburtsdatum blockiert ungültige Jahreswerte nicht mehr beim Tippen, sondern
  verhindert `Weiter` mit einheitlicher Fehlermeldung bei ungültigem Datum.
- Auth-Farben in die bestehende `AppColors`-Datei verschoben, damit die App ein
  zentrales Farbsystem behält.
- Login leitet im UI-only Prototyp direkt in das Home weiter, ohne lokale
  Formularvalidierung zu erzwingen.
- `ResponsivePageBody` gibt non-scrollable Seiten jetzt eine feste verfügbare
  Höhe, damit Home-Inhalte mit `Expanded` nach Login sichtbar rendern.
- Temporären Test-Button auf dem Onboarding ergänzt, der ohne Auth direkt in
  das Home führt.
- Home-Bottom-Navigation höhenkompakt gemacht, damit sie dem Home-Body nicht
  den verfügbaren Platz wegnimmt.
- Registrierungsabschluss um verpflichtende Zustimmung zu Nutzungsbedingungen,
  Datenschutz, Gesundheitsdatenverarbeitung und Notfall-Hinweis ergänzt.
- Begriffe `Nutzungsbedingungen` und `Datenschutzhinweise` in der
  Registrierungszustimmung als klickbare Dialog-Links umgesetzt.
- Geburtsdatum zeigt nach vollständiger Eingabe sofort eine Fehlermeldung,
  wenn das Datum ungültig ist.
- Altersfeld um ein Info-Icon mit Tooltip und Dialog zur Berechnungserklärung
  ergänzt.
- `registration_personal_step.dart` verschlankt und die Geburtsdatum-/Alter-UI
  in getrennte Widgets unter `widgets/registration/birth_date` ausgelagert.
- Persönliche Registrierungsfelder in `widgets/registration/personal`
  ausgelagert und Backend-TODOs an Login, Registrierung und Form-DTO ergänzt.
- Abstände im persönlichen Registrierungsstep thematisch optimiert; zusammen-
  gehörige Felder wie Passwort und Passwortbestätigung stehen enger zusammen.
- Vorname und Nachname blockieren Zahleneingaben direkt und validieren Namen
  zusätzlich ohne Ziffern.
- Monatsfeld im segmentierten Geburtsdatum verbreitert, damit der Platzhalter
  `Monat` vollständig lesbar ist.
- Gesundheitsangaben auf `Geburtsgeschlecht` umbenannt, Größe auf 1 bis 250 cm
  validiert und Gewicht als Dezimalwert in kg mit bis zu drei Nachkommastellen
  erlaubt.
- Geburtsgeschlecht-Auswahl optisch als eigener Eingabeblock gestaltet und um
  einen Info-Hinweis mit Tooltip und Dialog ergänzt.
- BMI wird aus Größe und Gewicht automatisch berechnet, als read-only Feld mit
  Info-Hinweis angezeigt und in der Registrierungsübersicht aufgeführt.
- Doppelte Info-Dialog- und read-only-Feldlogik in gemeinsame Auth-Widgets
  zusammengeführt; Spezialdateien für Alter/BMI und leeren Health-Widgetordner
  entfernt.
- Registrierungs-Step-Indicator mit längeren Verbindungslinien versehen und
  abgeschlossene Schritte zum nachträglichen Bearbeiten anklickbar gemacht.
- Registrierungsüberprüfung in `Persönliche Daten` und `Gesundheitsangaben`
  unterteilt; beide Bereiche haben ein Stift-Icon zum direkten Bearbeiten.
- Step-Indicator responsiv überarbeitet: größere Schrittflächen, größere
  Labels und flexible Verbindungslinien für schmale Smartphone-Breiten.
- `Meine Medikamente` nach Single-Responsibility-Prinzip refaktoriert:
  Persistenz und Reminder-Synchronisierung liegen im Controller, während
  Formular, Zusammenfassung, Liste, Eintrag und Empty-State eigene Widgets sind.
- Deutsche UI-Texte in `Meine Medikamente` verwenden Umlaute statt Umschreibungen
  wie `ae`, `oe` oder `ue`.
- `Meine Medikamente` verwendet die bestehende `AuthTopBar`, damit Zurück-Button
  und Light-/Darkmode-Umschalter konsistent mit den Auth-Screens bleiben.
- `Meine Medikamente` zeigt Einnahmezeiten konsequent im 24-Stunden-Format an und
  erzwingt dieses Format auch im Time-Picker.
- Medikamenten-Eingabe um einen lokalen Demo-Arzneimittelkatalog mit
  Autocomplete ergänzt; ausgewählte Vorschläge speichern zusätzliche Metadaten
  wie Wirkstoff, Stärke und Darreichungsform.
- Demo-Arzneimittelkatalog auf anwendernahe Daten reduziert: Name, Wirkstoff,
  Stärke und Darreichungsform reichen für die aktuelle Eingabe aus.
- `Meine Medikamente` um eine iPhone-inspirierte, Careena-angepasste Tagesleiste
  ergänzt. Der ausgewählte Tag steuert einen Tagesplan für aktive tägliche
  Medikamentenerinnerungen.
- Tagesleiste verdichtet Wochentage innerhalb einer Woche, trennt Wochen nach
  Sonntag deutlicher, markiert Monatswechsel mit kleinem Monatslabel und kann
  zusätzlich über Pfeilbuttons links und rechts gescrollt werden.
- Scrollbarer Bereich der Tagesleiste blendet an den linken und rechten Kanten
  leicht aus, damit weitere Tage natürlicher angedeutet werden.
- Tagesplan zeigt Medikamente erst ab ihrem Hinzufügedatum an; die Verwaltung
  `Meine Medikamente` ist jetzt als eigener Button unten links erreichbar.
- Medikamente können im Tagesplan pro ausgewähltem Datum als eingenommen
  abgehakt werden; die Verwaltung `Meine Medikamente` hat jetzt ein `X` zum
  Schließen und ein kleines `+` zum direkten Hinzufügen.
- Abgehakte Medikamente werden im Tagesplan visuell verblasst und mit
  `Eingenommen` beschriftet; für heute abgehakte Medikamente brechen ihre
  ausstehende lokale Erinnerung für diesen Tag ab. Popups öffnen nun zentriert.
- Neues Medikament wird nicht mehr direkt im Log-Body eingetragen, sondern über
  einen kleinen `+`-Button unten rechts geöffnet.
- Dosiseingabe im Medikamenten-Formular in getrennte Felder für Menge und
  Einheit aufgeteilt; die Einheit nutzt ein Autocomplete mit typischen
  Dosiseinheiten wie `mg`.
- Medikamenten-Formular im Bottom Sheet um einen `X`-Button zum Abbrechen
  ergänzt; Uhrzeiten zeigen jetzt `Uhr`, und Menge/Einheit nutzen
  Beispiel-Hints wie `z. B. 5` und `z. B. mg`.
- Eingenommene Medikamente im Tagesplan bleiben lesbar: Der Status wird über
  Hintergrund, Rand und Haken-Icon statt über starke Gesamt-Transparenz
  visualisiert. Wochentage in der Tagesleiste nutzen im Lightmode wieder eine
  kontrastreiche Schriftfarbe.
- Der `Eingenommen`-Haken kann nur noch für heute oder vergangene Tage gesetzt
  werden. Der Button `Meine Medikamente` ist größer und prägnanter, und
  Monatslabels in der Tagesleiste stehen nun rechts neben dem Trennstrich.
- Das Feature heißt in der UI nun `Meine Medikamente`, damit es für alle
  Altersgruppen persönlicher und weniger technisch wirkt.
- In der Medikamentenverwaltung steht der Schalter
  `Benachrichtigungen aktivieren` nun in einer eigenen Zeile, damit die
  Beschriftung nicht ungewollt umbricht.
- Flutter-Material-Dialoge sind jetzt global auf Deutsch lokalisiert, damit
  Time-Picker-Texte wie `Select time`, `Cancel`, `Hour`, `Minute` und `OK`
  deutsch angezeigt werden.
- Presentation-Widgets von `Meine Medikamente` in fachliche Unterordner
  (`actions`, `common`, `daily_plan`, `day_selector`, `form`, `list`,
  `summary`) sortiert. Die Page enthält dadurch weniger private UI-Klassen und
  bleibt stärker auf Navigation, Dialoge und State-Verknüpfung fokussiert.
- Englische Kommentare/Dartdocs in der Presentation-Schicht ergänzt, wo
  Funktionen nicht nur reines Widget-Rendering, sondern Verhalten, Validierung
  oder Zustandswechsel kapseln.
- Seitentitel der Medication-Page auf `Medikamentenplan` geändert. Die unteren
  Aktionen `Meine Medikamente` und `+` liegen nun innerhalb derselben
  responsiven Seitenfläche wie Zurück- und Theme-Button, damit ein klarerer
  Fenster-/Rahmeneffekt entsteht.
- Feature-Ordner und zentrale Presentation-Klassen von `medication_log` /
  `MedicationLog...` auf `medication_plan` / `MedicationPlan...` umbenannt,
  passend zur Funktion `Medikamentenplan`. Der bestehende lokale Storage-Key
  bleibt aus Kompatibilitätsgründen erhalten.
- Einnahmehäufigkeit im Medikamentenplan erweitert: Neben `Täglich`, `2x
  täglich` und `Wöchentlich` stehen jetzt auch `Werktags` und `Monatlich` zur
  Auswahl. Tagesplan, Datumsleisten-Marker und lokale Erinnerungen verwenden
  dieselbe Planungslogik.
- Medication-Plan-Code um englische, erklärende Kommentare/Dartdocs ergänzt,
  insbesondere für Datenmodell, Frequenzmodell, lokale Persistenz,
  Plan-Erzeugung und Reminder-Scheduling.
- Lange Presentation-Dateien im Medikamentenplan weiter aufgeteilt:
  Formularzustand liegt jetzt in `MedicationFormDialog`, der Seiteninhalt in
  `MedicationPlanContent`, Tagesplan-Zeilen/Checkbox/Empty-State und
  Tagesleisten-Chips/Pfeile/Monatsseparatoren sind eigene Widgets. Bestehende
  gemeinsame Widgets wie `ResponsiveFrame`, `ResponsivePageBody` und
  `AuthTopBar` werden dabei wiederverwendet.
- Tests für den Medikamentenplan ergänzt: Planungslogik für
  Einnahmehäufigkeiten, Tagesplan-Darstellung, 24-Stunden-Zeiten,
  Zukunftssperre beim `Eingenommen`-Haken und untere Seitenaktionen werden
  abgedeckt.

### Fixed

- Sichtbare Encoding-Artefakte in den berührten deutschen UI-Texten korrigiert.
- Unicode-Streaming in `ChatService` korrigiert, damit Emoji-Codepoints nicht
  zerschnitten werden.
- Warning-Page-Test auf die korrigierte deutsche Copy angepasst.
- Home- und Chatscreen-Tests auf die aktuelle `features/chatscreen`-Struktur
  und den benötigten `ThemeController` angepasst.

### Known Issues

- `flutter test` scheitert lokal weiterhin vor der Testausführung, weil der
  Flutter-Native-Assets-Hook den Pfad `C:\Users\Eli Hehl\...` falsch quotet.
- Einige generierte Plattformdateien und `pubspec.lock` waren bereits vor
  diesen Änderungen im Working Tree geändert und wurden nicht zurückgesetzt.

## [1.0.0] - 2026-05-19

### Added

- Flutter-App `app1` als aktuelles Haupt-Frontend.
- Onboarding-, Home-, Chat- und Warning-Screen-Flows.
- Backend-gestützte Chat-Sessions mit simuliertem Frontend-Typing.
- Red-Flag-Warning-Page mit Handlungsempfehlung.
- FastAPI-Backend, Docker-Compose-Setup und PostgreSQL-Anbindung.

### Changed

- Frontend-Code in `core` und Feature-Ordner gegliedert.
- Chat-Logik in Controller, API-Adapter, Service und Presentation-Widgets
  getrennt.
- Warning-UI in Screen, Widgets, Theme/Copy, Models und ViewModels getrennt.

### Known Issues

- Medizinisches Red-Flag-Verhalten braucht weitere automatisierte und manuelle
  Validierung.
- Chat-Sessions werden noch nicht über Backend-Neustarts hinweg persistiert.
