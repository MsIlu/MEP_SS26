# Changelog

In dieser Datei dokumentieren wir den aktuellen Entwicklungsstand der App und alle relevanten Änderungen pro Version.

Das Changelog dient als schneller Überblick für Team, Review und Abgabe: Welche Version ist aktuell? Was kann die App bereits? Was wurde geändert? Was ist noch offen?

---

## Aktueller App-Stand

| Bereich            | Stand |
|--------------------| --- |
| App-Version        | `1.0.0` |
| Quelle der Version | `app1/pubspec.yaml` |
| Datum              | 2026-05-19 |
| Status             | Entwicklungsstand / Prototyp |
| Aktueller Hauptbranch | `cleangit` |

### Kurzbeschreibung

Die App ist ein medizinischer Chat-Prototyp mit Flutter-Frontend und FastAPI-Backend. Nutzerinnen und Nutzer können über eine Chat-Oberfläche gesundheitsbezogene Anliegen eingeben. Das Backend verwaltet Chat-Sessions, prüft Eingaben auf medizinische Red Flags und leitet geeignete Anfragen an ein LiteLLM/OpenAI-kompatibles Sprachmodell weiter.

Der aktuelle Stand enthält außerdem einen überarbeiteten Careena-Home-Screen, eine strukturierte Frontend-Architektur, Backend-Endpunkte für Chat und Sessions sowie eine PostgreSQL-Anbindung über Docker.

---

## Pflege-Regeln

- Neue Änderungen werden immer oben unter `Unreleased` eingetragen.
- Vor einem Release wird aus `Unreleased` ein neuer Versionseintrag erstellt.
- Die App-Version muss mit `app1/pubspec.yaml` übereinstimmen.
- Einträge sollen kurz, konkret und nachvollziehbar sein.
- Kategorien:
  - `Added`: neue Funktionen
  - `Changed`: Änderungen an bestehenden Funktionen
  - `Fixed`: Fehlerbehebungen
  - `Known Issues`: bekannte offene Probleme
  - `Documentation`: reine Dokumentationsänderungen

---

## [Unreleased]

### Added
- Responsiver Seiten-Wrapper `ResponsivePageBody` für wiederverwendbare Screen-Breiten, Padding und optionales Scroll-Verhalten.
- Handlungsempfehlungsseite für Red-Flag-Fälle mit klarer Notruf-112-Empfehlung.
- Widget-Test für die Navigation vom Onboarding zum HomeScreen und ChatScreen sowie für die Handlungsempfehlungsseite.
- Chat-Eingabefeld bleibt während einer laufenden Bot-Antwort beschreibbar.
- Chat-Eingabefeld wird beim Öffnen des Chats automatisch fokussiert.
- Eingabefeld kann per Pfeiltasten aus der Nachrichtenliste wieder erreicht werden.

### Changed
- Onboarding-, Home-, Chat- und Warning-Screens nutzen ein gemeinsames responsives Layout-Verhalten.
- `features/warningscreen` wurde nach Separation of Concerns aufgeteilt in Screen, Widgets, Theme/Copy, Models und ViewModels.
- Die Handlungsempfehlungsseite wurde von der normalen Bottom-Navigation gelöst, damit Red-Flag-Hinweise eigenständig und fokussiert angezeigt werden.
- Deutsche UI-Texte auf der Handlungsempfehlungsseite verwenden wieder echte Umlaute.
- Senden bleibt während einer laufenden Bot-Antwort gesperrt, während das Sanduhr-Symbol sichtbar bleibt.
- Auto-Scroll im Chat verbessert: neue Nachrichten und gestreamte Bot-Antworten halten die Ansicht zuverlässiger am unteren Ende.
- Auto-Scroll respektiert bewusstes Hochscrollen, solange keine laufende Bot-Antwort aktiv ist.

### Fixed
- Chat-Initialisierung robuster gemacht: Senden wartet auf die Session-Erstellung und versucht bei fehlender Session erneut, eine Session anzulegen.
- Red-Flag-Antworten werden im Frontend wieder als Handlungsempfehlungsscreen angezeigt, statt im normalen Chat-Fehlerpfad zu landen.
- Mehrere responsive Darstellungsprobleme bei Onboarding-, Home-, Chat- und Warning-Screens reduziert.
- Encoding-Artefakte in den neuen Warning-UI-Texten korrigiert.

### Planned
- Tests für Chat-Controller, Backend-Endpunkte und Red-Flag-Erkennung erweitern.
- Persistente Speicherung von Chat-Sessions prüfen.
- Release-Regeln im Team festlegen, inklusive Git-Tags und Versionsnummern.
- Medizinische Sicherheitslogik weiter validieren und dokumentieren.

### Known Issues
- `flutter test` und `flutter run -d web-server` können lokal vor der App-Ausführung an einem Flutter/native-assets-Pfadproblem mit Leerzeichen in `C:\Users\Eli Hehl\...` scheitern.

---

## [1.0.0] - 2026-05-19

### Status
- Aktueller Entwicklungsstand der Flutter-App.
- Prototyp ist noch nicht als stabiler Release getaggt.
- Backend und Frontend sind lokal lauffähig, benötigen aber korrekte `.env`-Konfiguration und laufende Infrastruktur.

### Added
- Flutter-App `app1` als aktuelle Haupt-App.
- Home-Screen mit Careena-Branding, Header, Suchleiste, Feature-Kacheln, Bottom-Navigation und Avatar-Elementen.
- Chat-Screen für medizinische Nutzeranfragen.
- Begrüßungsnachricht beim Start einer Chat-Session.
- Simuliertes Streaming der Bot-Antworten im Frontend.
- Smart Replies und UI-Elemente für Chat-Interaktionen.
- Wiederverwendbare Frontend-Struktur mit:
  - `ApiClient`
  - `ChatApi`
  - `ChatController`
  - `ChatService`
  - `Message`-Modell
- FastAPI-Backend mit Endpunkten für:
  - Chat-Anfragen
  - Session-Erstellung
  - Modellabfrage
  - Modell-Warmup
- LiteLLM/OpenAI-kompatible Backend-Anbindung über Umgebungsvariablen.
- Session-basierte Chat-Verwaltung im Backend.
- Red-Flag-Erkennung für medizinische Notfallsituationen.
- Themenfilter für gesundheitsbezogene Eingaben.
- Begrenzung von Smalltalk und fachfremden Anfragen.
- PostgreSQL-Setup über Docker Compose.
- Automatische Tabellenerstellung beim Start des Backends.
- Datenmodelle für:
  - Patientendaten
  - klinische Fakten
  - Empfehlungen
  - Sicherheitsereignisse
  - Red Flags
  - Sessions
- Setup-Dokumentation für lokale Entwicklung, Docker, Backend und Datenbank.
- Beispielkonfiguration über `.env.example`.

### Changed
- Chat-Frontend wurde in eine klarere Feature-Struktur refaktoriert.
- Chat-Logik wurde aus UI-Komponenten in Controller- und Service-Klassen verschoben.
- Backend sendet für LLM-Anfragen nur einen begrenzten Verlauf weiter.
- Vollständiger Chat-Verlauf bleibt pro Session im Backend gespeichert, solange der Server läuft.
- Homescreen-Layout wurde optisch überarbeitet.
- Funktionskacheln auf dem Homescreen wurden kompakter angeordnet.
- Farben, Avatar-Bilder und Chat-Eingabefeld-Beschriftung wurden angepasst.
- Smart Replies und Thinking Bubble wurden visuell überarbeitet.
- Datenbankdateien und Setup-Anleitung wurden bereinigt.
- Projektstruktur wurde um Backend-, Frontend- und Dokumentationsbereiche geschärft.

### Fixed
- Import- und Pfadprobleme im Backend behoben.
- Dummy-Datenbank-URL für CI- oder Testkontexte ergänzt.
- Darstellungsprobleme bei Smart Replies korrigiert.
- Thinking Bubble mit Profilbild angepasst.
- Farbe des Buttons zur neuesten Nachricht angepasst.
- Chat-Eingabefeld optisch korrigiert.
- Mehrere kleinere UI-Probleme auf dem Homescreen behoben.

### Documentation
- Setup-Anleitung für lokale Entwicklung erweitert.
- Docker- und Datenbankstart dokumentiert.
- Hinweise zur `.env`-Datei ergänzt.
- Projektstruktur im Setup dokumentiert.
- Changelog grundlegend überarbeitet.

### Known Issues
- Chat-Sessions werden aktuell nur im Arbeitsspeicher gehalten und gehen bei einem Server-Neustart verloren.
- Es gibt noch keinen Git-Release-Tag für `1.0.0`.
- Die medizinische Red-Flag-Erkennung muss weiter getestet und validiert werden.
- Backend-Kommentare enthalten noch Hinweise auf Prototyp-Status und temporäre Einschränkungen.
- Automatisierte Tests decken den aktuellen Funktionsumfang noch nicht vollständig ab.
- Einige Dokumente enthalten noch Encoding-Artefakte bei Sonderzeichen, wenn sie in bestimmten Terminals angezeigt werden.

---

## [0.5.0] - 2026-05-19

### Status
- Zwischenstand vor der vollständigen Angleichung an die aktuelle Flutter-Version.

### Added
- Erste dokumentierte Changelog-Struktur.
- KI-Chat-Grundfunktion mit Backend-Kommunikation.
- Clean-Architecture-nahe Ordnerstruktur im Flutter-Frontend.
- Wiederverwendbarer API-Client.

### Changed
- Chat-Controller refaktoriert.
- Homescreen-Layout verbessert.

### Fixed
- Fehlerhafte Ladezustände im Chat korrigiert.
- Keyboard-Overflow-Probleme im Chat reduziert.

---

## [0.4.0] - 2026-05-10

### Status
- Früher Prototypenstand.

### Added
- Erste Chatbot-Integration.
- Erste Darstellung strukturierter Chat-Antworten.

### Changed
- UI-Animationen und Chat-Darstellung verbessert.
