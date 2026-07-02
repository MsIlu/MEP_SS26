### Hinweis

Diese Datei wurde KI-generiert, um uns bei der Übersicht und Pflege des Projekts zu unterstützen.

# Flutter lib structure

Diese Datei beschreibt die aktuelle Struktur von `app1/lib` und die wichtigsten
Verantwortlichkeiten der einzelnen Bereiche.

## Überblick

`app1/lib` enthält das Flutter-Frontend. Die App startet im Onboarding, teilt
eine Chat-Session über Onboarding, Home und Chat hinweg und öffnet bei einer
medizinischen Red-Flag-Antwort des Backends einen eigenen Warning-Flow. Über
das Home ist außerdem `Meine Medikamente` mit lokalen täglichen Erinnerungen
und `Symptomtagebuch` für tägliches Symptomtracking erreichbar. Weitere
Hauptbereiche sind Terminverwaltung, Dokumente, Kalenderübersicht,
Profilverwaltung und PDF-/Terminexport aus Empfehlungen.

## Ordnerstruktur

```text
app1/lib/
|-- main.dart
|-- app/
|   `-- app_dependencies.dart
|-- core/
|   |-- config/
|   |   |-- app_assets.dart
|   |   `-- app_config.dart
|   |-- network/
|   |   |-- api_client.dart
|   |   `-- api_exception.dart
|   `-- widgets/
|       `-- responsive_frame.dart
`-- features/
    |-- app_guide/
    |   |-- data/
    |   `-- presentation/
    |-- appointmentscreen/
    |   |-- controllers/
    |   |-- data/
    |   `-- presentation/
    |-- authscreen/
    |   |-- data/
    |   |-- domain/
    |   |-- presentation/
    |   |-- state/
    |   `-- utils/
    |-- calendar_overview/
    |   `-- presentation/
    |-- chatscreen/
    |   |-- controllers/
    |   |-- data/
    |   |-- presentation/
    |   |-- services/
    |   `-- utils/
    |-- documents/
    |   |-- controllers/
    |   |-- data/
    |   `-- presentation/
    |-- homescreen/
    |   |-- data/
    |   `-- presentation/
    |-- medication_plan/
    |   |-- data/
    |   |-- presentation/
    |   |   |-- controllers/
    |   |   |-- screens/
    |   |   |-- utils/
    |   |   `-- widgets/
    |   |       |-- actions/
    |   |       |-- common/
    |   |       |-- daily_plan/
    |   |       |-- day_selector/
    |   |       |-- form/
    |   |       |-- list/
    |   |       `-- summary/
    |   `-- services/
    |-- symptom_diary/
    |   |-- data/
    |   `-- presentation/
    |       |-- controllers/
    |       |-- screens/
    |       |-- utils/
    |       `-- widgets/
    |-- settings/
    |   `-- presentation/
    |       |-- settings_icons.dart
    |       |-- screens/
    |       `-- widgets/
    |-- onboardingscreen/
    |   `-- presentation/
    |-- profiles/
    |   |-- data/
    |   `-- domain/
    |-- recommendation_export/
    |   |-- data/
    |   `-- presentation/
    `-- warningscreen/
        `-- presentation/
```

## App-Start

`main.dart` bleibt bewusst klein. Die Datei erstellt `MyApp`; die langlebigen
Abhängigkeiten werden in `_AppDependencyScope` gehalten. Die App setzt außerdem
Deutsch als Material-Locale, damit Systemdialoge wie Time-Picker deutsche Texte
verwenden.

`ResponsivePageBody` legt eine `SelectionArea` um Seiteninhalte, damit normale
sichtbare Texte innerhalb der App markiert und kopiert werden können, ohne
jedes Text-Widget einzeln anzupassen.

`app/app_dependencies.dart` ist der Composition Root der App. Dort werden diese
Objekte einmal erstellt und gemeinsam verwendet:

- `http.Client`

## App-Guide

Die sichtbaren Home-Komponenten stellen ihre exakten Guide-Ziele bereit. Das
Overlay übernimmt ausschließlich Positionierung und themeabhängige
Darstellung. Guide-Schritte können dadurch sowohl Inhaltskarten als auch
gemeinsame Header-Aktionen hervorheben.

Die Guide-Presentation trennt Overlay-Orchestrierung, Spotlight-Painter,
Careena-Companion und Aktionen in eigene Widgets. Gemeinsames Homescreen-Test-
Setup liegt in einer kleinen Test-Fixture; Guide-Ablauf und allgemeine
Homescreen-Darstellung werden getrennt getestet.

`features/app_guide` enthält den einmaligen Guide nach einer erfolgreichen
Registrierung. Die Guide-Schritte liegen als einfache Datenobjekte vor, die
Presentation hebt vorhandene Home-Bereiche mit einem Coachmark-Overlay hervor.
`AppGuideStore` speichert den Abschluss getrennt je Konto sowie unter einem
expliziten Schlüssel für Gäste.

Der Ordner `app` darf `core` und Features kennen, weil er die App verdrahtet.
`core` bleibt dadurch frei von Feature-Imports und kann als gemeinsame
Grundlage wiederverwendet werden.

## Core

`core/config/app_config.dart` enthält zentrale Konfiguration:

- `appName`
- `welcomeMessage`
- `baseUrl`

Die Backend-Adresse kann zur Laufzeit überschrieben werden:

```bash
flutter run --dart-define=API_BASE_URL=http://<host>:8000
```

Ohne Override nutzt die App `http://localhost:8000` im Web und
`http://10.0.2.2:8000` im Android-Emulator.

`core/network/api_client.dart` ist der generische JSON-POST-Client. Er kennt
keine Chat-Endpunkte und keine Chat-Modelle.

`core/network/api_exception.dart` enthält typisierte API-Fehler, damit UI und
Controller keine rohen Exception-Texte auswerten müssen.

`core/widgets/responsive_frame.dart` enthält gemeinsame Layout-Wrapper für
Maximalbreiten, Padding und Scroll-Verhalten.

## Settings-Feature

`features/settings` trennt die durchsuchbare Einstellungsübersicht von den
komplexeren Detailseiten. `SettingsPage` koordiniert nur Suche und Navigation.
Wiederverwendbare Listen, Suchfeld, Panels und die feste Abmelde-Aktion liegen
in `presentation/widgets/settings_components.dart`.
Zusammengehörige Icons für Übersicht und Detailseiten liegen zentral in
`presentation/settings_icons.dart`.

`SettingsDetailScaffold` stellt Header, responsive Breite und Scrollverhalten
für Detailseiten bereit. Sein einleitender Abschnitt kann ausgeblendet werden,
wenn ein eingebetteter Bereich bereits eine eigene Überschrift besitzt.

## Chat-Feature

`features/chatscreen/controllers/chat_controller.dart` koordiniert Chat-State,
Backend-Session, Lade-Nachrichten, Red-Flag-Antworten und Message-Updates. Der
Controller enthält keinen Widget-Code.

`features/chatscreen/data/chat_api.dart` kennt die Backend-Endpunkte:

- `/session`
- `/warmup`
- `/chatscreen`

`features/chatscreen/data/models` enthält Datenobjekte wie `Message` und
`ChatResponse`.

`features/chatscreen/services/chat_service.dart` enthält reine Chat-Logik für
Nachrichtenlisten und lokales Text-Streaming. Dieser Service hat keine
Flutter-UI-Abhängigkeit und ist durch Unit-Tests abgedeckt.

`features/chatscreen/presentation` enthält Screen, Widgets und visuelle Tokens
für die Chat-Oberfläche.

`features/chatscreen/utils` enthält kleine Frontend-Helfer wie Smart Replies und
medizinische Begriffserklärungen.

## Medication-Plan-Feature

`features/medication_plan` enthält `Meine Medikamente` für selbst gepflegte
Medikamenteneinträge. Nutzer erfassen Medikament, Dosis und Einnahmezeit und
können pro Eintrag eine tägliche Push-Erinnerung aktivieren.

Die Verantwortlichkeiten sind getrennt in:

- `data`: `MedicationEntry`, `MedicationCatalogItem`,
  `DemoMedicationCatalog`, `DoseUnitCatalog`, `MedicationFrequency` und
  `MedicationRepository` für lokale Persistenz, Einnahmehäufigkeiten sowie eine
  bewusst einfache Demo-Katalogsuche mit anwendernahen Arzneimitteldaten und
  Dosis-Einheiten
- `services`: `MedicationNotificationService` für lokale tägliche
  Benachrichtigungen über `flutter_local_notifications`
- `presentation/controllers`: `MedicationPlanController` für Laden, Speichern,
  Löschen, Sortieren und Reminder-Synchronisierung
- `presentation/screens`: `MedicationPlanPage` als Scaffold- und
  Navigationsschicht
- `presentation/models`: `PlannedMedicationDose` als Presentation-Modell für
  einzelne geplante Einnahmen
- `presentation/utils`: kleine Formatierungs- und Planungshelfer wie die
  24-Stunden-Anzeige von Einnahmezeiten, deutsche Datumslabels und die
  Erzeugung geplanter Tagesdosen für Tagesplan und Datumsleisten-Marker
- `presentation/widgets/actions`: untere Aktionsbuttons für Hinzufügen und
  Verwaltung
- `presentation/widgets/common`: kleine wiederverwendbare Bausteine wie Titel
  und Empty-State
- `presentation/widgets/daily_plan`: Tagesplan und Einnahme-Abhaken
- `presentation/widgets/day_selector`: scrollbare Tagesleiste mit
  Monatsmarkierungen
- `presentation/widgets/form`: Formular, Arzneimittel-Autocomplete,
  Einheiten-Autocomplete, Katalogdetails, Frequenzauswahl, Zeit-Auswahl und
  Formular-Dialogzustand
- `presentation/widgets/layout`: Seitenlayout für den Medikamentenplan, damit
  `MedicationPlanPage` Navigation und Dialog-Orchestrierung fokussiert hält
- `presentation/widgets/list`: Verwaltungsdialog, Liste und Eintragskarten
- `presentation/widgets/summary`: zusammenfassende Darstellungen für gespeicherte
  Medikamente

## Symptom-Diary-Feature

`features/symptom_diary` enthält das `Symptomtagebuch` für kurze tägliche
Symptomeinträge. Nutzer erfassen Symptom, betroffene Körperstelle, Intensität
von 1 bis 10 und optional eine Notiz. Die Einträge werden lokal gespeichert und
pro Kalendertag angezeigt.

Die Verantwortlichkeiten sind getrennt in:

- `data`: `SymptomEntry` und `SymptomRepository` für lokale Persistenz über
  `SharedPreferences`
- `presentation/controllers`: `SymptomDiaryController` für Laden, Speichern,
  Löschen, Tagesfilterung und Durchschnittsberechnung
- `presentation/screens`: `SymptomDiaryPage` als Scaffold-, Datums- und
  State-Orchestrierung
- `presentation/utils`: deutsche Datumslabels und Kalendervergleich
- `presentation/widgets`: Tageskopf, Tageszusammenfassung, Eingabeformular und
  Eintragsliste

## Warning-Feature

`features/warningscreen` rendert die Handlungsempfehlung bei Red-Flag-Antworten.
Die medizinische Entscheidung bleibt im Backend; das Frontend reagiert nur auf
`ChatResponse.redFlag`.

Die Präsentation ist getrennt in:

- `screens`: Scaffold und Navigationsebene
- `widgets`: wiederverwendbare Warning-UI-Bausteine
- `theme`: Texte, Farben, Layoutwerte und Decorations
- `models`: Präsentationsmodelle wie `EmergencyAction`
- `view_models`: Anzeigeaufbereitung wie `EmergencyReason`

## Auth, Home und Onboarding

`features/onboardingscreen` ist die erste Seite und routet direkt in den Chat
oder in die Auth-Flows.

`features/authscreen` enthält den UI-only Login- und Registrierungsflow. Login
und Registrierung validieren lokale Formularfelder und leiten nach erfolgreichem
Absenden in das Home weiter. Eine echte Authentifizierung oder Persistenz ist
noch nicht angebunden.

Die Auth-Präsentation ist nach Verantwortlichkeiten getrennt:

- `screens`: Flow-State, Formularzustand und Navigation
- `widgets/common`: Buttons, Textfelder, Info-Dialoge und gemeinsame
  Layout-Bausteine
- `widgets/registration`: einzelne Registrierungsschritte und Fortschrittsanzeige
- `widgets/registration/birth_date`: Container, segmentierte Datumseingabe und
  read-only Altersfeld jeweils als getrennte Widgets
- `widgets/registration/personal`: Vorname/Nachname- und Account-Feldgruppen
  des ersten Registrierungsschritts
- `widgets/review`: Review-Box, Datenschutz-Hinweis und Zustimmungs-Checkbox
- `theme`: Auth-spezifische TextStyles, Layoutwerte und Input-Decorations
- `models`: einfache Präsentationsmodelle wie Review-Einträge
- `view_models`: Formular-Controller für Textfelder, Step-Validierung und Review-Daten
- `data`: statische Optionen für Formularauswahlen
- `utils`: reine Validierungsfunktionen ohne Widget-Abhängigkeit

Farben kommen aus `features/chatscreen/presentation/themes/app_colors.dart`, damit
kein zweites Farbsystem im Auth-Feature entsteht.

`features/homescreen` enthält die Startseite nach Login/Registrierung. Der
Screen bekommt den geteilten `ChatController` und reicht ihn an den Chat weiter.

## Datenfluss

```text
ChatScreen
  -> ChatController
  -> ChatApi
  -> ApiClient
  -> FastAPI-Backend
  -> ChatResponse
  -> ChatController.messages
  -> ChatScreen-Widgets
```

Bei Red Flags:

```text
Backend liefert red_flag: true
  -> ChatController gibt ChatResponse zurück, ohne normale Bot-Bubble
  -> ChatScreen öffnet WarningPage
  -> Warning-Widgets zeigen Handlungsempfehlung
```

## Tests

Das Frontend enthält jetzt fokussierte Tests für:

- Onboarding-Navigation
- Login- und Registrierungs-Navigation
- Warning-Page-Rendering
- `ChatService`-Transformationen
- `ChatResponse.fromJson`
- Medikamentenplan-Planungslogik unter
  `test/features/medication_plan/presentation/utils`
- Medikamentenplan-Widgets unter
  `test/features/medication_plan/presentation/widgets`, unter anderem
  Tagesplan, `Eingenommen`-Status und untere Aktionen
- Symptomtagebuch-Controller unter
  `test/features/symptom_diary/presentation/controllers`

Sinnvolle nächste Testziele sind Controller-Fehlerpfade, API-Exceptions und die
Red-Flag-Navigation.
