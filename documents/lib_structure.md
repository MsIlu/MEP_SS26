# Flutter lib structure

Diese Datei beschreibt die aktuelle Struktur von `app1/lib` und die wichtigsten
Verantwortlichkeiten der einzelnen Bereiche.

## Überblick

`app1/lib` enthält das Flutter-Frontend. Die App startet im Onboarding, teilt
eine Chat-Session über Onboarding, Home und Chat hinweg und öffnet bei einer
medizinischen Red-Flag-Antwort des Backends einen eigenen Warning-Flow.

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
    |-- chatscreen/
    |   |-- controllers/
    |   |-- data/
    |   |-- presentation/
    |   |-- services/
    |   `-- utils/
    |-- homescreen/
    |   |-- data/
    |   `-- presentation/
    |-- onboardingscreen/
    |   `-- presentation/
    `-- warningscreen/
        `-- presentation/
```

## App-Start

`main.dart` bleibt bewusst klein. Die Datei erstellt `MyApp`; die langlebigen
Abhängigkeiten werden in `_AppDependencyScope` gehalten.

`app/app_dependencies.dart` ist der Composition Root der App. Dort werden diese
Objekte einmal erstellt und gemeinsam verwendet:

- `http.Client`
- `ApiClient`
- `ChatApi`
- `ChatService`
- `ChatController`

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

## Home und Onboarding

`features/onboardingscreen` ist die erste Seite und routet in Chat oder Home.

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
- Warning-Page-Rendering
- `ChatService`-Transformationen
- `ChatResponse.fromJson`

Sinnvolle nächste Testziele sind Controller-Fehlerpfade, API-Exceptions und die
Red-Flag-Navigation.
