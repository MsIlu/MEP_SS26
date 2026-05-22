# Changelog

In dieser Datei dokumentieren wir relevante Änderungen für Review, Teamarbeit
und Abgabe.

## Aktueller App-Stand

| Bereich | Stand |
| --- | --- |
| App-Version | `1.0.0` |
| Quelle der Version | `app1/pubspec.yaml` |
| Datum | 2026-05-22 |
| Status | Entwicklungsstand / Prototyp |

## [Unreleased]

### Added

- `app/app_dependencies.dart` als zentraler Composition Root für langlebige
  Frontend-Abhängigkeiten ergänzt.
- `ApiException` und `ApiErrorType` für typisierte API-Fehler ergänzt.
- Unit-Tests für `ChatService` und `ChatResponse.fromJson` ergänzt.
- `MyApp` unterstützt injizierbare `ChatController`, damit Widget-Tests ohne
  echte Backend-Initialisierung laufen können.
- Neue Strukturdatei `documents/lib_structure.md` ergänzt.

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

### Fixed

- Sichtbare Encoding-Artefakte in den berührten deutschen UI-Texten korrigiert.
- Unicode-Streaming in `ChatService` korrigiert, damit Emoji-Codepoints nicht
  zerschnitten werden.
- Warning-Page-Test auf die korrigierte deutsche Copy angepasst.

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
