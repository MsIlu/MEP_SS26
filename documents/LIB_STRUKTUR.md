#### _Hinweis: Diese Seite wird mit KI stetig an den Aufbau unseres Repos angepasst._
# Flutter-`lib`-Struktur

Diese Datei erklärt, was im Ordner `app1/lib` passiert und wofür die einzelnen Ordner und Dateien gedacht sind.

---

## Kurzüberblick

Der Ordner `app1/lib` enthält den eigentlichen Dart-Code der Flutter-App.

Die App besteht aktuell aus mehreren großen Bereichen:

- `main.dart`: Startpunkt der App. Hier wird die App gestartet und die wichtigsten Klassen werden miteinander verbunden.
- `core`: Gemeinsame Grundlagen, die mehrere App-Bereiche nutzen, zum Beispiel Konfiguration, Assets und Netzwerkkommunikation.
- `features`: Fachliche App-Bereiche. Aktuell vor allem `onboardingscreen`, `homescreen`, `chat` und `warningscreen`.

Die App startet auf dem Onboarding-Screen. Von dort kann der Chat mit Careena direkt geöffnet werden, oder man gelangt über die Anmeldung zum HomeScreen. Der Chat sendet Nachrichten an das FastAPI-Backend, erhält eine Antwort zurück und zeigt diese in der Oberfläche an. Wenn das Backend eine medizinische Red Flag meldet, öffnet das Frontend die Handlungsempfehlungsseite im Feature `warningscreen`.

---

## Ordnerstruktur

```text
app1/lib/
├── main.dart
├── core/
│   ├── config/
│   │   ├── app_assets.dart
│   │   └── app_config.dart
│   └── network/
│       └── api_client.dart
└── features/
    ├── chatscreen/
    │   ├── controllers/
    │   ├── data/
    │   ├── presentation/
    │   ├── services/
    │   └── utils/
    ├── homescreen/
    │   ├── data/
    │   ├── presentation/  
    ├── onboardingscreen/
    │   ├── controllers/
    │   ├── data/  
    └── warningscreen/
        └── presentation/  
```

---

Ergänzend zur kompakten Baumansicht gibt es aktuell diese wichtigen Erweiterungen:

- `core/widgets/responsive_frame.dart`: gemeinsame responsive Wrapper für Screens.
- `features/onboardingscreen`: Onboarding-Startseite mit Einstieg in Chat oder HomeScreen.
- `features/warningscreen`: Handlungsempfehlungsseite für Red-Flag-Antworten.
- `features/warningscreen/presentation/screens`: Screen/Scaffold und Navigationsebene.
- `features/warningscreen/presentation/widgets`: reine UI-Bausteine der Handlungsempfehlung.
- `features/warningscreen/presentation/theme`: Texte, Farben, Layoutwerte und Decorations der Warning-UI.
- `features/warningscreen/presentation/models`: einfache UI-Modelle, zum Beispiel `EmergencyAction`.
- `features/warningscreen/presentation/view_models`: Aufbereitung von Backend-Daten für die Anzeige, zum Beispiel `EmergencyReason`.

---

## Wie die App grundsätzlich funktioniert

1. `main.dart` startet die Flutter-App.
2. Dort wird ein `ChatController` erstellt.
3. Der `ChatController` bekommt Zugriff auf:
   - `ChatApi` für Backend-Anfragen
   - `ChatService` für lokale Chat-Logik
4. Als erste Seite wird `OnboardingScreen` angezeigt.
5. Vom Onboarding aus kann direkt der Chat geöffnet werden, oder über "Anmelden" der `HomeScreen`.
6. Der Home-Screen zeigt die Startseite mit Careena-Header und Funktionsliste.
7. Beim Tippen auf "Jetzt mit Careena sprechen" wird `ChatScreen` geöffnet.
8. `ChatScreen` initialisiert über den `ChatController` eine Chat-Session.
9. Nutzereingaben werden über `ChatController` -> `ChatApi` -> `ApiClient` an das Backend gesendet.
10. Normale Antworten werden als Chat-Nachricht angezeigt.
11. Bei `red_flag: true` öffnet der Chat die `WarningPage` mit Handlungsempfehlung.
12. Zusätzlich erzeugt die App Smart Replies und zeigt bei bestimmten medizinischen Begriffen kurze Erklärungen an.

---

## Datenfluss im Chat

```text
Nutzer schreibt Nachricht
        ↓
ChatScreen
        ↓
ChatController
        ↓
ChatApi
        ↓
ApiClient
        ↓
FastAPI-Backend
        ↓
Antwort vom Backend
        ↓
ChatController speichert Nachricht
        ↓
ChatScreen zeigt ChatBubble an
```

Wichtig: Das Frontend entscheidet nicht selbst medizinisch. Es zeigt die Antwort an, die vom Backend kommt. Die Red-Flag-Erkennung und die LLM-Kommunikation passieren im Backend.

Bei Red-Flag-Antworten ist der Ablauf etwas anders:

```text
Backend sendet red_flag: true
        ↓
ChatScreen erkennt response.redFlag
        ↓
WarningPage wird geöffnet
        ↓
EmergencyCard zeigt Handlungsempfehlung und Notruf-112-Hinweis
```

---

## `main.dart`

Pfad: `app1/lib/main.dart`

Diese Datei ist der Einstiegspunkt der Flutter-App.

Aufgaben:

- startet Flutter mit `runApp`
- erstellt die Haupt-App `MyApp`
- deaktiviert das Debug-Banner
- erstellt die Abhängigkeiten für den Chat
- zeigt als Startseite den `OnboardingScreen`

Besonders wichtig ist die Methode `_buildChatController()`.

Dort werden diese Objekte gebaut:

- `http.Client`: führt echte HTTP-Anfragen aus
- `ApiClient`: kapselt allgemeine API-Kommunikation
- `ChatApi`: kennt die Chat-Endpunkte des Backends
- `ChatService`: enthält lokale Chat-Hilfslogik
- `ChatController`: verbindet UI, Chatlogik und Backend-Kommunikation

Damit muss nicht jede UI-Datei selbst wissen, wie das Backend angesprochen wird.

---

## `core`

Der Ordner `core` enthält Code, der nicht nur zu einem einzelnen Feature gehört, sondern grundsätzlich von der App verwendet werden kann.

### `core/config/app_config.dart`

Pfad: `app1/lib/core/config/app_config.dart`

Diese Datei enthält zentrale App-Einstellungen.

Aktuell enthält sie:

- `appName`: Name der App, aktuell `MedBitAid v0.4`
- `welcomeMessage`: Begrüßung, die im Chat angezeigt wird
- `baseUrl`: Backend-Adresse, abhängig von der Plattform

Die `baseUrl` ist wichtig, weil Flutter je nach Plattform eine andere Adresse braucht:

- Web: `http://localhost:8000`
- Android Emulator: `http://10.0.2.2:8000`

Warum `10.0.2.2`?  
Im Android Emulator zeigt `localhost` auf den Emulator selbst. `10.0.2.2` ist die Spezialadresse, mit der der Emulator den lokalen Rechner erreicht.

### `core/config/app_assets.dart`

Pfad: `app1/lib/core/config/app_assets.dart`

Diese Datei sammelt Asset-Pfade an einer zentralen Stelle.

Aktuell enthält sie:

- `careenaDoctor`: Pfad zum Careena-Doctor-Bild

Vorteil: Wenn sich der Bildpfad ändert, muss er nicht in mehreren Widgets einzeln geändert werden.

### `core/network/api_client.dart`

Pfad: `app1/lib/core/network/api_client.dart`

Diese Datei enthält einen allgemeinen HTTP-Client für API-Anfragen.

Aufgaben:

- baut die vollständige URL aus `AppConfig.baseUrl` und einem API-Pfad
- sendet POST-Anfragen
- kodiert Dart-Maps als JSON
- dekodiert JSON-Antworten
- behandelt grobe Fehler wie Timeouts oder HTTP-Fehler

Der `ApiClient` kennt keine Chat-Details. Er weiß nur: "Ich sende eine Anfrage an das Backend und bekomme JSON zurück."

### `core/widgets/responsive_frame.dart`

Pfad: `app1/lib/core/widgets/responsive_frame.dart`

Diese Datei enthält wiederverwendbare Layout-Wrapper für responsive Screens.

Wichtige Bausteine:

- `ResponsiveFrame`: zentriert Inhalt und begrenzt ihn auf eine maximale Breite.
- `ResponsiveScrollableFrame`: kombiniert responsive Breitenbegrenzung mit vertikalem Scrollen.
- `ResponsivePageBody`: gemeinsamer Screen-Wrapper für neue Seiten.
- `ResponsiveBreakpoints`: zentrale Breakpoint-Helfer für kompakte und größere Layouts.

Neue Screens sollten nach Möglichkeit `ResponsivePageBody` nutzen, damit Breite, Padding und Scroll-Verhalten nicht pro Seite neu gebaut werden müssen.

---

## `features`

Der Ordner `features` enthält fachliche App-Bereiche. Ein Feature ist ein größerer Funktionsbereich der App.

Aktuell gibt es:

- `chat`: alles rund um den medizinischen Chat
- `homescreen`: alles rund um die Startseite
- `onboardingscreen`: Einstieg in die App mit Chat- und Home-Navigation
- `warningscreen`: Handlungsempfehlung bei medizinischen Red Flags

---

## `features/chatscreen`

Der Chat-Bereich ist in mehrere Unterordner aufgeteilt:

- `controllers`: verbindet UI, Services und API
- `data`: Datenzugriff und Datenmodelle
- `presentation`: sichtbare Oberfläche
- `services`: fachliche Hilfslogik ohne UI
- `utils`: kleine Hilfsklassen und statische Daten

### `chat/controllers/chat_controller.dart`

Pfad: `app1/lib/features/chatscreen/controllers/chat_controller.dart`

Der `ChatController` ist die zentrale Steuerung des Chats.

Aufgaben:

- speichert die aktuelle Liste der Chat-Nachrichten
- erstellt beim Start eine neue Session über das Backend
- fügt die Begrüßungsnachricht hinzu
- ruft das Backend auf, wenn eine Nachricht gesendet wird
- zeigt während der Anfrage eine Lade-Nachricht an
- ersetzt die Lade-Nachricht durch die echte Antwort
- simuliert das schrittweise Anzeigen der Bot-Antwort
- behandelt einfache Fehler und zeigt sie als Nachricht an

Die UI beobachtet `messages`, ein `ValueNotifier<List<Message>>`. Wenn sich die Nachrichtenliste ändert, baut Flutter die Chatliste automatisch neu.

### `chat/data/chat_api.dart`

Pfad: `app1/lib/features/chatscreen/data/chat_api.dart`

`ChatApi` kennt die Chat-Endpunkte des Backends.

Aufgaben:

- `createSession()`: ruft `/session` auf und erhält eine Session-ID
- `sendMessage(...)`: sendet Text und Session-ID an `/chat`
- `warmup()`: ruft `/warmup` auf, damit das Backend oder Modell vorgewärmt wird

`ChatApi` nutzt intern den allgemeinen `ApiClient`.

### `chat/data/models/message_model.dart`

Pfad: `app1/lib/features/chatscreen/data/models/message_model.dart`

Diese Datei definiert das Modell `Message`.

Eine `Message` beschreibt eine einzelne Chat-Nachricht.

Eigenschaften:

- `text`: Inhalt der Nachricht
- `isUser`: `true`, wenn die Nachricht vom Nutzer kommt
- `isLoading`: `true`, wenn es nur eine temporäre Lade-Nachricht ist
- `timestamp`: Zeitpunkt der Nachricht

Außerdem gibt es `copyWith(...)`. Damit kann eine neue Nachricht aus einer bestehenden Nachricht erzeugt werden, ohne alles neu angeben zu müssen.

### `chat/services/chat_service.dart`

Pfad: `app1/lib/features/chatscreen/services/chat_service.dart`

`ChatService` enthält Chat-Logik, die nicht direkt zur Oberfläche gehört.

Aufgaben:

- Nachricht zu einer Liste hinzufügen
- letzte Bot-Nachricht entfernen
- letzte Nachricht ersetzen
- Text Zeichen für Zeichen streamen

Das Streaming ist aktuell lokal simuliert. Das bedeutet: Die Backend-Antwort kommt als kompletter Text zurück, wird im Frontend aber schrittweise angezeigt.

### `chat/utils/smart_replies.dart`

Pfad: `app1/lib/features/chatscreen/utils/smart_replies.dart`

Diese Datei erzeugt Vorschläge für schnelle Folgefragen.

Beispiele:

- Bei Antworten mit "Schmerz" oder "weh" werden Schmerz-bezogene Nachfragen vorgeschlagen.
- Bei Antworten mit "Behandlung" oder "Medikament" werden Behandlungsfragen vorgeschlagen.
- Wenn kein Muster passt, erscheinen allgemeine Vorschläge.

Die Logik ist regelbasiert und läuft nur im Frontend.

### `chat/utils/medical_terms.dart`

Pfad: `app1/lib/features/chatscreen/utils/medical_terms.dart`

Diese Datei enthält einfache Erklärungen für medizinische Begriffe.

Aktuell kennt sie unter anderem:

- Symptom
- Entzündung
- Infektion
- Therapie

Wenn ein Bot-Text einen bekannten Begriff enthält, kann die App eine kleine Infobox mit Erklärung anzeigen.

---

## `features/chatscreen/presentation`

Der Ordner `presentation` enthält alles, was direkt mit der sichtbaren Oberfläche des Chats zu tun hat.

### `chat/presentation/screens/chat_screen.dart`

Pfad: `app1/lib/features/chatscreen/presentation/screens/chat_screen.dart`

`ChatScreen` ist die komplette Chat-Seite.

Aufgaben:

- initialisiert den Chat über den `ChatController`
- verwaltet das Texteingabefeld
- sendet Nachrichten
- zeigt die Nachrichtenliste an
- scrollt automatisch zur neuesten Nachricht
- zeigt Smart Replies an
- zeigt einen Button "Zur neuesten Nachricht", wenn man hochgescrollt hat
- zeigt nach längerer Wartezeit einen Hinweis an
- öffnet bei `response.redFlag == true` die `WarningPage`
- enthält Tastatur-Shortcuts:
  - `End`: nach unten scrollen
  - `Home`: nach oben scrollen

Diese Datei ist die wichtigste UI-Datei im Chat-Bereich.

### `chat/presentation/themes/app_colors.dart`

Pfad: `app1/lib/features/chatscreen/presentation/themes/app_colors.dart`

Diese Datei enthält zentrale Farben für die Oberfläche.

Beispiele:

- Primärfarbe
- Akzentfarbe
- Hintergrundfarbe
- Kartenfarbe
- Textfarben

Sie funktioniert wie ein kleines Design-System. Dadurch müssen Farben nicht überall hart im Code verteilt werden.

### `chat/presentation/widgets/chat_app_bar.dart`

Pfad: `app1/lib/features/chatscreen/presentation/widgets/chat_app_bar.dart`

Diese Datei baut die obere Leiste im Chat.

Sie enthält:

- Zurück-Button
- Careena-Avatar
- Name "Careena"
- Online-Status

### `chat/presentation/widgets/chat_bubble.dart`

Pfad: `app1/lib/features/chatscreen/presentation/widgets/chat_bubble.dart`

Diese Datei zeigt eine einzelne Chat-Nachricht an.

Sie entscheidet:

- ist die Nachricht vom Nutzer oder vom Bot?
- soll die Bubble links oder rechts stehen?
- welche Farbe bekommt die Bubble?
- muss ein Careena-Avatar angezeigt werden?
- ist es eine Lade-Nachricht?
- gibt es einen medizinischen Begriff, der erklärt werden soll?

Wenn `isLoading` aktiv ist, wird statt Text eine `ThinkingBubble` angezeigt.

### `chat/presentation/widgets/chat_input_field.dart`

Pfad: `app1/lib/features/chatscreen/presentation/widgets/chat_input_field.dart`

Diese Datei enthält das Eingabefeld unten im Chat.

Bestandteile:

- Textfeld für Symptome oder Beschwerden
- Mikrofon-Icon als visuelles Element
- Senden-Button
- Ladezustand während eine Nachricht verarbeitet wird
- Accessibility-/Semantics-Beschriftungen

### `chat/presentation/widgets/thinking_bubble.dart`

Pfad: `app1/lib/features/chatscreen/presentation/widgets/thinking_bubble.dart`

Diese Datei zeigt die Ladeanimation, während Careena antwortet.

Sie enthält:

- Careena-Avatar
- animierte Punkte
- Text "Careena schreibt..."
- optionalen Hinweis, wenn die Antwort länger dauert

### `chat/presentation/widgets/smart_reply_list.dart`

Pfad: `app1/lib/features/chatscreen/presentation/widgets/smart_reply_list.dart`

Diese Datei zeigt vorgeschlagene Folgefragen als klickbare Chips an.

Wenn keine Vorschläge vorhanden sind, zeigt das Widget nichts an.

### `chat/presentation/widgets/medical_term_info_box.dart`

Pfad: `app1/lib/features/chatscreen/presentation/widgets/medical_term_info_box.dart`

Diese Datei zeigt eine kleine Erklärung zu einem medizinischen Begriff.

Sie wird innerhalb einer Bot-Chat-Bubble angezeigt, wenn `MedicalTerms` einen passenden Begriff findet.

### `chat/presentation/widgets/latest_message_button.dart`

Pfad: `app1/lib/features/chatscreen/presentation/widgets/latest_message_button.dart`

Diese Datei enthält den Button "Zur neuesten Nachricht".

Er erscheint, wenn man in der Chatliste nach oben scrollt und nicht mehr am Ende des Chats ist.

### `chat/presentation/widgets/feature_tile.dart`

Pfad: `app1/lib/features/chatscreen/presentation/widgets/feature_tile.dart`

Diese Datei enthält eine wiederverwendbare Kachel mit Icon und Titel.

Aktuell wird sie vom älteren oder alternativen `FeatureGrid` im Home-Bereich genutzt, nicht direkt vom aktuellen `HomeScreen`.

---

## `features/onboardingscreen`

Der Onboarding-Bereich enthält die erste sichtbare Seite der App.

### `onboardingscreen/presentation/screens/onboarding_screen.dart`

Pfad: `app1/lib/features/onboardingscreen/presentation/screens/onboarding_screen.dart`

Aufgaben:

- zeigt Header, Hero-Card und Auth-Buttons
- öffnet über den Hero-Button direkt den `ChatScreen`
- öffnet über "Anmelden" und "Registrieren" den `HomeScreen`
- nutzt responsive Layout-Wrapper, damit die Seite auf kleinen und größeren Screens stabil bleibt

### `onboardingscreen/presentation/widgets`

Dieser Ordner enthält die Bausteine des Onboarding-Screens:

- `onboarding_header.dart`: Logo und App-Name
- `onboarding_hero_card.dart`: zentrale Einstiegskarte mit Careena und Chat-CTA
- `careena_chat_bubble.dart`: kleine Sprechblase im Hero-Bereich
- `auth_button.dart`: wiederverwendbarer Button für Anmeldung und Registrierung

---

## `features/warningscreen`

Der Warning-Bereich zeigt die Handlungsempfehlung, wenn das Backend eine medizinische Red Flag meldet.

Wichtig: Die medizinische Entscheidung passiert weiterhin im Backend. Das Frontend liest nur `ChatResponse.redFlag` und zeigt dann die passende Oberfläche an.

### `warningscreen/presentation/screens/warning_page.dart`

Pfad: `app1/lib/features/warningscreen/presentation/screens/warning_page.dart`

Diese Datei enthält nur noch die Screen-Ebene:

- `Scaffold`
- AppBar mit Zurück-Button
- responsiver Seiten-Wrapper
- Einbindung von `EmergencyCard` und `NoDiagnosisInfoBox`

### `warningscreen/presentation/widgets`

Pfad: `app1/lib/features/warningscreen/presentation/widgets/`

Dieser Ordner enthält reine UI-Bausteine:

- `emergency_card.dart`: Hauptkarte mit Notfallhinweis und Aktionen
- `warning_header.dart`: Warnsymbol, Überschrift und Erklärungstext
- `emergency_action_list.dart`: Liste der empfohlenen Sofortmaßnahmen
- `emergency_call_button.dart`: Button "Notruf 112 anrufen"
- `reason_box.dart`: Anzeige erkannter Warnzeichen
- `no_diagnosis_info_box.dart`: Hinweis, dass keine Diagnose gestellt wird
- `highlighted_text.dart`: Text mit optional hervorgehobenen Begriffen
- `emergency_divider.dart`: Trenner innerhalb der Notfallkarte
- `section_title.dart`: kleine Abschnittsüberschrift

### `warningscreen/presentation/theme`

Pfad: `app1/lib/features/warningscreen/presentation/theme/`

Dieser Ordner bündelt Präsentationskonstanten:

- `warning_copy.dart`: sichtbare Texte der Warning-UI
- `warning_layout.dart`: Maximalbreiten, Padding und Breakpoints
- `warning_theme.dart`: Farben, Textstile und Decorations

### `warningscreen/presentation/models`

Pfad: `app1/lib/features/warningscreen/presentation/models/emergency_action.dart`

`EmergencyAction` beschreibt eine einzelne Handlungsempfehlung mit Icon, Text und optional hervorgehobenem Textteil.

### `warningscreen/presentation/view_models`

Pfad: `app1/lib/features/warningscreen/presentation/view_models/emergency_reason.dart`

`EmergencyReason` bereitet die Backend-Daten aus `ChatResponse` für die Anzeige auf. Dazu gehören Regelname, Kategorie und erkannte Keywords.

---

## `features/homescreen`

Der Home-Bereich enthält die Startseite der App.

Die Startseite ist der erste Bildschirm nach App-Start. Von dort gelangt man in den Chat und sieht weitere Funktionsbereiche als Platzhalter oder Navigationselemente.

### `homescreen/data/home_feature.dart`

Pfad: `app1/lib/features/homescreen/data/home_feature.dart`

Diese Datei definiert das Modell `HomeFeature`.

Ein `HomeFeature` beschreibt eine Funktion auf der Startseite.

Eigenschaften:

- `icon`: Symbol der Funktion
- `title`: Name der Funktion
- `backgroundColor`: Hintergrundfarbe des Icons
- `onTap`: Aktion beim Antippen

Der `HomeScreen` erstellt mehrere `HomeFeature`-Objekte und gibt sie an die Funktionsliste weiter.

---

## `features/homescreen/presentation`

Dieser Bereich enthält die sichtbare Oberfläche der Startseite.

### `homescreen/presentation/screens/home_screen.dart`

Pfad: `app1/lib/features/homescreen/presentation/screens/home_screen.dart`

`HomeScreen` ist die aktuelle Startseite der App.

Aufgaben:

- zeigt den Begrüßungstext "Willkommen!"
- zeigt das Benachrichtigungs-Icon
- zeigt die Careena-Karte
- enthält eine Suchleiste
- zeigt eine Liste von Funktionen
- zeigt die untere Navigation
- öffnet den `ChatScreen`, wenn die Careena-Karte angetippt wird

Der `HomeScreen` bekommt den `ChatController` aus `main.dart`, damit derselbe Controller an den Chat weitergegeben werden kann.

### `homescreen/presentation/widgets/careena_hero_card.dart`

Pfad: `app1/lib/features/homescreen/presentation/widgets/careena_hero_card.dart`

Diese Datei zeigt die große Careena-Karte auf der Startseite.

Sie enthält:

- animierten Careena-Avatar
- kurzen Begrüßungstext
- Button "Jetzt mit Careena sprechen"

Beim Tippen auf den Button wird der Chat geöffnet.

### `homescreen/presentation/widgets/floating_avatar.dart`

Pfad: `app1/lib/features/homescreen/presentation/widgets/floating_avatar.dart`

Diese Datei zeigt ein rundes Avatar-Bild mit leichter Hoch-und-runter-Animation.

Genutzt wird sie in `CareenaHeroCard`.

### `homescreen/presentation/widgets/notification_badge_icon.dart`

Pfad: `app1/lib/features/homescreen/presentation/widgets/notification_badge_icon.dart`

Diese Datei zeigt ein Benachrichtigungs-Icon mit rotem Zähler.

Im aktuellen `HomeScreen` wird der Zähler fest mit `3` gesetzt.

### `homescreen/presentation/widgets/home_function_list.dart`

Pfad: `app1/lib/features/homescreen/presentation/widgets/home_function_list.dart`

Diese Datei zeigt die Liste der Funktionen auf der Startseite.

Sie bekommt eine Liste von `HomeFeature`-Objekten und baut daraus mehrere `FunctionMenuTile`-Einträge.

### `homescreen/presentation/widgets/function_menu_tile.dart`

Pfad: `app1/lib/features/homescreen/presentation/widgets/function_menu_tile.dart`

Diese Datei zeigt eine einzelne Funktionszeile auf der Startseite.

Sie enthält:

- Icon links
- Titel der Funktion
- Pfeil rechts
- Tap-Aktion

Aktuelle Beispiele aus dem `HomeScreen`:

- Terminplanung
- Medikamente
- Dokumente
- Präventive Angebote
- Symptomtagebuch

### `homescreen/presentation/widgets/custom_bottom_nav.dart`

Pfad: `app1/lib/features/homescreen/presentation/widgets/custom_bottom_nav.dart`

Diese Datei zeigt die untere Navigationsleiste.

Aktuelle Einträge:

- Startseite
- Kalender
- Nachrichten
- Einstellungen

Der aktuelle Index ist fest auf `0`, also Startseite. Die Navigation ist deshalb optisch vorhanden, aber noch nicht als echte Seiten-Navigation umgesetzt.

---

## Vorhandene, aktuell nicht direkt eingebundene Home-Widgets

Einige Dateien existieren im Projekt, werden aber vom aktuellen `HomeScreen` nicht direkt genutzt. Sie können ältere Varianten oder vorbereitete Bausteine sein.

### `homescreen/presentation/widgets/feature_grid.dart`

Pfad: `app1/lib/features/homescreen/presentation/widgets/feature_grid.dart`

Diese Datei zeigt eine Grid-Ansicht mit mehreren Feature-Kacheln.

Sie kann den Chat öffnen und nutzt dafür `FeatureTile`. Im aktuellen `HomeScreen` wird aber stattdessen `HomeFunctionList` verwendet.

### `homescreen/presentation/widgets/home_header.dart`

Pfad: `app1/lib/features/homescreen/presentation/widgets/home_header.dart`

Diese Datei enthält einen alternativen Header mit Farbverlauf, Text, Benachrichtigungs-Icon und optionalem Avatar.

Im aktuellen `HomeScreen` wird der Header direkt in `_buildHeader()` gebaut.

### `homescreen/presentation/widgets/home_search_bar.dart`

Pfad: `app1/lib/features/homescreen/presentation/widgets/home_search_bar.dart`

Diese Datei enthält eine alternative Suchleiste.

Im aktuellen `HomeScreen` wird die Suchleiste direkt in `_buildSearchBar()` gebaut.

---

## Welche Dateien sollte man zuerst lesen?

Für einen schnellen Einstieg empfiehlt sich diese Reihenfolge:

1. `app1/lib/main.dart`
2. `app1/lib/features/onboardingscreen/presentation/screens/onboarding_screen.dart`
3. `app1/lib/features/homescreen/presentation/screens/home_screen.dart`
4. `app1/lib/features/chatscreen/presentation/screens/chat_screen.dart`
5. `app1/lib/features/chatscreen/controllers/chat_controller.dart`
6. `app1/lib/features/warningscreen/presentation/screens/warning_page.dart`
7. `app1/lib/features/warningscreen/presentation/widgets/emergency_card.dart`
8. `app1/lib/features/chatscreen/data/chat_api.dart`
9. `app1/lib/core/network/api_client.dart`
10. `app1/lib/core/widgets/responsive_frame.dart`

Danach kann man die einzelnen Widgets lesen, wenn man verstehen möchte, wie die Oberfläche im Detail gebaut ist.

---

## Was passiert im Frontend und was im Backend?

Frontend in `app1/lib`:

- zeigt Onboarding-, Home-, Chat- und Warning-Screens
- nimmt Nutzereingaben entgegen
- sendet Nachrichten an das Backend
- zeigt Antworten an
- öffnet bei Red-Flag-Antworten die Handlungsempfehlungsseite
- simuliert Streaming
- zeigt Smart Replies
- zeigt einfache Begriffserklärungen
- nutzt gemeinsame responsive Layout-Wrapper für kompatible Screen-Größen

Backend in `server`:

- erstellt und verwaltet Chat-Sessions
- prüft, ob Eingaben gesundheitsbezogen sind
- erkennt medizinische Red Flags
- spricht mit dem LiteLLM/OpenAI-kompatiblen Modell
- gibt die Antwort an das Frontend zurück
- initialisiert Datenbanktabellen

---

## Aktuelle Hinweise

- Die App-Version steht nicht in `lib`, sondern in `app1/pubspec.yaml`.
- Die Backend-Adresse steht in `AppConfig.baseUrl`.
- Die Chat-Session wird im Backend erstellt, aber im Frontend im `ChatController` gespeichert.
- Einige UI-Elemente sind bereits sichtbar, aber noch ohne echte Funktion hinterlegt, zum Beispiel mehrere Home-Funktionen und die Bottom-Navigation.
- Manche Texte in der Terminalausgabe können wegen Encoding falsch dargestellt werden. In der Markdown-Datei selbst sind die deutschen Sonderzeichen normal gespeichert.
