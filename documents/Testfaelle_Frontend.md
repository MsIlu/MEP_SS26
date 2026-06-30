# Testfälle Frontend Aufgaben

Diese Datei ordnet die Frontend-Tests des Projekts nach Themen, Testdateien und einzelnen Testfällen. Die IDs werden in den Testdateien als Referenz verwendet.

## ID-System

- `T01`: Medicationbook / Medication Plan
- `T02`: Chat History
- `T03`: Symptome erkennen / Input-Drafts
- `T04`: Auth und Registrierung
- `T05`: Core Network und Shared Widgets
- `T06`: Chat Core und Chat UI
- `T07`: Home Screen
- `T08`: Profile Management
- `T09`: Symptom Diary
- `T10`: Settings
- `T11`: App Smoke / Warning Flow
- `T12`: PDF-Export
- `Txx.y`: Testdatei oder Testgruppe
- `Txx.y.z`: einzelner Testfall

## T01 Medicationbook

### T01.1 `app1/test/features/medication_plan/presentation/utils/medication_plan_builder_test.dart`

- `T01.1.1`: Keine Dosis vor dem Erstellungsdatum eines Medikaments.
- `T01.1.2`: Zweimal tägliche Einnahme wird in zwei sortierte Dosiszeilen aufgeteilt.
- `T01.1.3`: Wöchentliche und monatliche Pläne werden am Starttag verankert.
- `T01.1.4`: Werktags-Pläne erscheinen nur Montag bis Freitag.
- `T01.1.5`: Tägliche Medikamente bleiben ab dem Erstellungsdatum sichtbar.
- `T01.1.6`: Dosen aus mehreren Medikamenten werden nach Einnahmezeit sortiert.

### T01.2 `app1/test/features/medication_plan/data/medication_entry_test.dart`

- `T01.2.1`: JSON-Roundtrip erhält Einnahmeplan, zweite Dosis und Einnahmestatus.
- `T01.2.2`: Legacy-Daten ohne neue Felder werden mit sicheren Defaults geladen.
- `T01.2.3`: Wöchentliche Medikamente erscheinen nur am verankerten Wochentag.

### T01.3 `app1/test/features/medication_plan/data/medication_repository_test.dart`

- `T01.3.1`: Leerer lokaler Speicher ergibt eine leere Medikamentenliste.
- `T01.3.2`: Speichern und Laden lokaler Medikamente funktioniert als Roundtrip.
- `T01.3.3`: Geladene Medikamente werden nach erster Einnahmezeit sortiert.

### T01.4 `app1/test/features/medication_plan/presentation/widgets/medication_daily_plan_section_test.dart`

- `T01.4.1`: Tagesplan zeigt geplante Dosen mit 24-Stunden-Zeiten.
- `T01.4.2`: Checkbox für zukünftige Tage ist deaktiviert.
- `T01.4.3`: Als eingenommen markierte Dosen bleiben sichtbar.

### T01.5 `app1/test/features/medication_plan/presentation/widgets/medication_plan_content_test.dart`

- `T01.5.1`: Seite rendert Titel und Medikament-Aktionen.
- `T01.5.2`: Untere Aktionen rufen die übergebenen Callbacks auf.

## T02 Chat History

### T02.1 `app1/test/features/chat/data/chat_history_entry_test.dart`

- `T02.1.1`: UTC-Zeitstempel werden in lokale Nutzerzeit umgewandelt.
- `T02.1.2`: Backend-Zeitstempel ohne Zeitzone werden als UTC behandelt.
- `T02.1.3`: Titel wird auf ein Wort normalisiert und fällt bei Leerwert auf `Verlauf` zurück.
- `T02.1.4`: Vorschau bevorzugt die erste nicht-leere Nutzernachricht.
- `T02.1.5`: Nachrichten und PDF-Exportfelder bleiben im JSON-Roundtrip erhalten.

### T02.2 `app1/test/features/chat/data/chat_history_repository_test.dart`

- `T02.2.1`: Profilhistorie wird vom API-Endpunkt geladen und neueste Einträge stehen vorne.
- `T02.2.2`: Abgeschlossene Chats werden an den Chat-History-Endpunkt gesendet.

### T02.3 `app1/test/features/chat/controllers/chat_controller_test.dart`

- `T02.3.1`: ChatController startet ohne Nachrichten vor der Initialisierung.
- `T02.3.2`: Aktive Profil-ID aus der Auth-Session wird an die Chat-API übergeben.
- `T02.3.3`: Profilwechsel setzt Chat-Session und Symptom-Draft zurück.
- `T02.3.4`: Normale Empfehlungen werden für angemeldete Profile gespeichert und Folgefragen blockiert.
- `T02.3.5`: Anonyme Empfehlungen werden abgeschlossen, aber nicht in der History gespeichert.
- `T02.3.6`: Red-Flag-Empfehlungen werden als Notfall-History gespeichert.
- `T02.3.7`: Notruf-Text in Empfehlungen wird als Notfall-History erkannt.
- `T02.3.8`: Dringende Red-Flag-Metadaten werden als Notfall-History erkannt.
- `T02.3.9`: Ein Konflikt beim Fortsetzen eines Chats wird ausführlich und vollständig auf Deutsch angezeigt.
- `T02.3.10`: Ein Continue-Konflikt synchronisiert den aktuellen Serverstand, ohne den Chat auf `failed` zu setzen.
- `T02.3.11`: Ein Profilkonflikt der Chat-Session wird verständlich auf Deutsch erklärt.

### T02.4 `app1/test/features/chat/presentation/chat_history_screen_test.dart`

- `T02.4.1`: Ein Resume-Konflikt wird im Verlauf als verständliche deutsche Meldung angezeigt.

## T03 Symptome Erkennen / Input-Drafts

### T03.1 `app1/test/features/chat/services/symptom_draft_service_test.dart`

- `T03.1.1`: Ohne Session-ID werden keine Symptome geladen und kein API-Call ausgeführt.
- `T03.1.2`: Symptome werden für eine Session aktualisiert und wieder geladen.
- `T03.1.3`: Draft-Daten können gelöscht werden.
- `T03.1.4`: Ladefehler werden abgefangen und als leere Symptomliste behandelt.
- `T03.1.5`: Aktualisieren ohne Session-ID wird abgelehnt.
- `T03.1.6`: Fehler beim Löschen blockieren den Chat nicht.

### T03.2 `app1/test/features/chat/data/chat_api_input_drafts_test.dart`

- `T03.2.1`: Symptome werden über `/input-drafts/{sessionId}` geladen.
- `T03.2.2`: Symptome werden per `PATCH` an den Draft-Endpunkt gesendet.
- `T03.2.3`: Drafts werden per `DELETE` am Session-Endpunkt gelöscht.

### T03.3 `app1/test/features/chatscreen/widgets/symptom_list_test.dart`

- `T03.3.1`: Symptom-Chips werden angezeigt, wenn Symptome vorhanden sind.
- `T03.3.2`: Ohne Symptome wird die Hinzufügen-Aktion angezeigt.
- `T03.3.3`: Mehr als drei Symptome werden in einer zusammengefassten Gruppe dargestellt.
- `T03.3.4`: Lange Symptom-Labels werden visuell gekürzt.

## T04 Auth Und Registrierung

### T04.1 `app1/test/features/authscreen/data/auth_api_service_test.dart`

- `T04.1.1`: Login parst Auth-Antwort und speichert den Token im `ApiClient`.
- `T04.1.2`: Registrierung sendet Profildaten, parst Auth-Antwort und speichert den Token.
- `T04.1.3`: Zweiter Registrierungsfall prüft erneut Token-Speicherung und Profilmapping.

### T04.2 `app1/test/features/authscreen/domain/models/auth_response_test.dart`

- `T04.2.1`: `AuthResponse.fromJson` parst Account, Token und Profile.

### T04.3 `app1/test/features/authscreen/presentation/registration_layout_test.dart`

- `T04.3.1`: Step-Connectoren sind auf alle Fortschrittskreise zentriert.
- `T04.3.2`: Fester Auth-Header hält den Titel zwischen gleich großen Aktionsbuttons.

### T04.4 `app1/test/features/authscreen/state/auth_session_test.dart`

- `T04.4.1`: Auth-Antwort wird gespeichert und erstes Profil als aktiv gesetzt.
- `T04.4.2`: Aktives Profil kann per ID gewechselt werden.
- `T04.4.3`: Auswahl eines fremden Profils wird abgelehnt.
- `T04.4.4`: Logout/Reset leert Session-Daten.
- `T04.4.5`: Das zuletzt aktive Profil wird für die nächste Anmeldung gespeichert.
- `T04.4.6`: Das eigene Profil steht vor allen betreuten Profiltypen, deren Erstellungsreihenfolge erhalten bleibt.

### T04.5 `app1/test/features/authscreen/utils/auth_error_message_test.dart`

- `T04.5.1`: Doppelte E-Mail bei Registrierung wird nutzerfreundlich erklärt.
- `T04.5.2`: Nicht erreichbarer Server bei Registrierung wird nutzerfreundlich erklärt.

## T05 Core Network Und Shared Widgets

### T05.1 `app1/test/core/network/api_client_test.dart`

- `T05.1.1`: Backend-Detail für doppelte E-Mail wird in die erwartete Fehlermeldung gemappt.
- `T05.1.2`: `GET` mappt HTTP 400 auf eine nutzerfreundliche Nachricht.
- `T05.1.3`: `GET` mappt HTTP 401 auf eine nutzerfreundliche Nachricht.
- `T05.1.4`: `GET` mappt HTTP 403 auf eine nutzerfreundliche Nachricht.
- `T05.1.5`: `GET` mappt HTTP 404 auf eine nutzerfreundliche Nachricht.
- `T05.1.6`: `GET` mappt HTTP 500 auf eine nutzerfreundliche Nachricht.
- `T05.1.7`: `getList` mappt HTTP 400 auf eine nutzerfreundliche Nachricht.
- `T05.1.8`: `getList` mappt HTTP 401 auf eine nutzerfreundliche Nachricht.
- `T05.1.9`: `getList` mappt HTTP 403 auf eine nutzerfreundliche Nachricht.
- `T05.1.10`: `getList` mappt HTTP 404 auf eine nutzerfreundliche Nachricht.
- `T05.1.11`: `getList` mappt HTTP 500 auf eine nutzerfreundliche Nachricht.
- `T05.1.12`: `GET` wirft `invalidResponse`, wenn JSON kein Objekt ist.
- `T05.1.13`: `getList` wirft `invalidResponse`, wenn JSON keine Liste ist.
- `T05.1.14`: `GET` wandelt Timeout in eine Timeout-Exception.
- `T05.1.15`: `getList` wandelt Timeout in eine Timeout-Exception.

### T05.2 `app1/test/core/widgets/careena_page_header_test.dart`

- `T05.2.1`: Header-Titel bleibt zwischen linker und rechter Seite zentriert.
- `T05.2.2`: Zentralisierter Header-Hintergrund wird ohne Divider dargestellt.

## T06 Chat Core Und UI

### T06.1 `app1/test/chat_service_test.dart`

- `T06.1.1`: Nachrichten werden hinzugefügt, ohne die Ursprungsliste zu mutieren.
- `T06.1.2`: Nur die letzte Assistant-Nachricht wird entfernt.
- `T06.1.3`: Unicode-Text wird gestreamt, ohne Emoji-Codepoints zu zerlegen.

### T06.2 `app1/test/chat_response_model_test.dart`

- `T06.2.1`: Normale Backend-Antworten werden in das ChatResponse-Modell gemappt.
- `T06.2.2`: Red-Flag-Metadaten werden gemappt.
- `T06.2.3`: Ungültige Antwort-Payloads nutzen einen lesbaren Fallback.

### T06.3 `app1/test/features/chat/services/chat_service_test.dart`

- `T06.3.1`: `addMessage` hängt an, ohne die bestehende Liste zu mutieren.
- `T06.3.2`: `removeLastBotMessage` entfernt die neueste Assistant-Bubble.

### T06.4 `app1/test/features/chat/services/chat_session_service_test.dart`

- `T06.4.1`: Session wird nur einmal erstellt und gewarmt.
- `T06.4.2`: Profilwechsel erstellt eine neue Session.
- `T06.4.3`: `clearSession` gibt die aktuelle Session-ID zurück und entfernt sie.

### T06.5 `app1/test/features/chat/utils/smart_replies_test.dart`

- `T06.5.1`: Schmerzbezogene Eingaben erzeugen passende Rückfragen.
- `T06.5.2`: Neutrale Eingaben fallen auf allgemeine Rückfragen zurück.

### T06.6 `app1/test/features/chatscreen/widgets/leave_chat_dialog_test.dart`

- `T06.6.1`: Dialog zeigt standardmäßig HomeScreen-Copy.
- `T06.6.2`: Dialog zeigt benutzerdefinierte Ziel-Copy.

## T07 Home Screen

### T07.1 `app1/test/features/homescreen/data/home_feature_test.dart`

- `T07.1.1`: `HomeFeature`-Konstruktor mappt alle übergebenen Attribute korrekt.

### T07.2 `app1/test/features/homescreen/presentation/home_screen_widget_test.dart`

- `T07.2.1`: HomeScreen rendert Willkommensbereich und Careena-Einstiegskarte.
- `T07.2.2`: Einfache Ansicht entfernt Ablenkungen und vergrößert Navigation.
- `T07.2.3`: HomeScreen nutzt die helle Careena-Farbpalette.
- `T07.2.4`: Feature-Karten bleiben im Dark Mode erhöht.
- `T07.2.5`: Nachrichten-Navigation öffnet gespeicherte Chat-History.

## T08 Profile Management

### T08.1 `app1/test/features/profiles/data/profile_api_service_test.dart`

- `T08.1.1`: Profile werden geladen und Authorization-Header wird gesendet.
- `T08.1.2`: Neues Profil wird gesendet und erzeugtes Profil wird geparst.
- `T08.1.3`: Profil-Löschen sendet DELETE mit Authorization-Header.

## T09 Symptom Diary

### T09.1 `app1/test/features/symptom_diary/presentation/controllers/symptom_diary_controller_test.dart`

- `T09.1.1`: Einträge werden für den gewählten Tag gespeichert und Durchschnittsintensität berechnet.

## T10 Settings

### T10.1 `app1/test/features/settings/presentation/settings_page_test.dart`

- `T10.1.1`: Display-, Rechts- und Logout-Einstellungen werden angezeigt.
- `T10.1.2`: Simple-View-Schalter aktualisiert den ThemeController.
- `T10.1.3`: Display Settings starten direkt mit Appearance-Auswahl.
- `T10.1.4`: Settings-Icons werden auf passenden Detailseiten wiederverwendet.
- `T10.1.5`: Zwischen eigenem und verwaltetem Profil kann gewechselt werden.
- `T10.1.6`: Managed-Profile-Frontend-Draft wird geöffnet.
- `T10.1.7`: Personal- und Health-Data-Settings-Seiten werden geöffnet.
- `T10.1.8`: Suche filtert Settings und lässt Logout sichtbar.
- `T10.1.9`: Logout ist zentriert und helle Settings-Panels sind hervorgehoben.
- `T10.1.10`: Familienmitglieder und andere betreute Profile werden zur Löschung angeboten.

## T11 App Smoke / Warning Flow

### T11.1 `app1/test/widget_test.dart`

- `T11.1.1`: HomeScreen rendert den authentifizierten Einstiegspunkt.
- `T11.1.2`: Sichtbarer Text kann selektiert und kopiert werden.
- `T11.1.3`: ChatScreen öffnet mit controller-gestützter UI.
- `T11.1.4`: Red-Flag-Antwort ersetzt Chat durch WarningPage.
- `T11.1.5`: WarningPage zeigt Notfall-Handlungsempfehlung.
- `T11.1.6`: ChatWarningDialog zeigt Titel, Inhalt und Button.
- `T11.1.7`: ChatWarningDialog schließt nach Akzeptieren.

## T12 PDF-Export

### T12.1 `app1/test/features/recommendation_export/data/recommendation_pdf_service_test.dart`

- `T12.1.1`: Das biologische Geschlecht wird für die PDF-Ausgabe auf Deutsch übersetzt.

## Quality-Prinzipien

- Separation of Concerns: API-Endpunkte, Services, Modelle, Repository, Controller und Widgets werden getrennt getestet.
- KISS: Tests prüfen beobachtbares Verhalten über öffentliche Schnittstellen.
- Refactoring-Sicherheit: Testdaten nutzen kleine Helper/Fakes und vermeiden Produktivcode-Aenderungen.
- Nachvollziehbarkeit: Jede Frontend-Testdatei verweist auf diese Matrix.
