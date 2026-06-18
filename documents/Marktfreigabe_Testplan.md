# Careena Marktfreigabe-Testplan

Diese Datei beschreibt, was vor einer Veröffentlichung der App geprüft werden muss. Sie ergänzt die bestehenden Testfall-Dokumente:

- `documents/Testfaelle_Frontend.md`
- `documents/Testfaelle_Backend.md`

Ziel ist eine nachvollziehbare Testabdeckung über Funktion, medizinische Sicherheit, Datenschutz, Bedienbarkeit, Barrierefreiheit, Performance und Release-Stabilität.

## 1. Testziel

Die App darf erst veröffentlicht oder präsentiert werden, wenn die wichtigsten Nutzerwege zuverlässig funktionieren und keine kritischen Risiken offen sind.

Geprüft werden muss insbesondere:

- Kann ein Nutzer sicher durch Onboarding, Registrierung, Login und Profilverwaltung gehen?
- Funktioniert der Chat inklusive Symptomabfrage, Red-Flag-Erkennung und Handlungsempfehlung?
- Werden medizinisch sensible Inhalte verständlich, korrekt und verantwortungsvoll dargestellt?
- Werden Symptome, Medikamente, Termine und Einstellungen korrekt gespeichert, angezeigt und geändert?
- Sind PDF-Export, Terminempfehlung, Chat-History und Notfall-Hinweise zuverlässig?
- Ist die App auf Desktop, Tablet und Smartphone bedienbar?
- Sind Eingabefelder, Buttons und wichtige Dialoge per Tastatur und Screenreader erreichbar?
- Werden personenbezogene Gesundheitsdaten sicher behandelt?
- Gibt es keine offensichtlichen Layoutfehler, Asset-Fehler, Abstürze oder leere Zustände?

## 2. Release-Kriterien

Ein Release gilt nur als freigabefähig, wenn alle folgenden Punkte erfüllt sind:

- Alle automatisierten Frontend-Tests laufen erfolgreich.
- Alle automatisierten Backend-Tests laufen erfolgreich.
- `flutter analyze` meldet keine Issues.
- Backend-Linting und Backend-Testlauf sind erfolgreich.
- Alle kritischen manuellen Testfälle aus diesem Dokument sind bestanden.
- Alle bekannten kritischen und hohen Bugs sind behoben oder explizit begründet zurückgestellt.
- Datenschutz-, Sicherheits- und medizinische Warnhinweise sind sichtbar und korrekt.
- Die App wurde mindestens auf Chrome Desktop, einem mobilen Browser-Viewport und einem kleinen Smartphone-Viewport geprüft.
- Der komplette Hauptnutzerfluss wurde einmal mit neuem Account und einmal mit bestehendem Account getestet.
- Ein Teammitglied, das die Funktion nicht selbst implementiert hat, hat die wichtigsten Flows gegengeprüft.

## 3. Risikoklassen

| Klasse         | Bedeutung | Beispiele | Release-Regel |
|----------------|---|---|---|
| Kritisch       | Gefährdet Nutzer, Daten oder medizinische Sicherheit | Notfall wird nicht erkannt, fremde Profildaten sichtbar, App startet nicht | Release blockiert |
| Hoch           | Zentrale Funktion unbrauchbar oder falsche Empfehlung wahrscheinlich | Chat speichert falsches Profil, PDF leer, Login defekt | Release blockiert |
| Mittel         | Funktion eingeschränkt, Workaround möglich | Layout auf kleinem Display fehlerhaft, Suche findet einzelne Begriffe nicht | Release nur mit Entscheidung |
| Niedrig        | Kosmetik oder kleiner Komfortfehler | Abstand, Textumbruch, kleinere Inkonsistenz | Release möglich, Ticket anlegen |

## 4. Automatisierte Pflichtprüfungen

Diese Befehle müssen vor jeder Abnahme ausgeführt und dokumentiert werden.

| Bereich | Befehl | Erwartung |
|---|---|---|
| Flutter Analyse | `cd app1 && flutter analyze` | Keine Issues |
| Flutter Tests | `cd app1 && flutter test` | Alle Tests grün |
| Backend Tests | Backend-Testbefehl aus Projektsetup ausführen | Alle Tests grün |
| Backend API Smoke | Server starten und zentrale Endpunkte manuell/automatisiert prüfen | Keine 5xx-Fehler |
| Asset Smoke | App im Browser starten | Keine 404-Assetfehler in Konsole |
| Build Smoke | Flutter Web Build ausführen | Build erfolgreich |

Ergebnisprotokoll:

| Datum | Tester | Branch/Commit | Analyse | Frontend Tests | Backend Tests | Build | Ergebnis |
|---|---|---|---|---|---|---|---|
| | | | | | | | |

## 5. Testdaten

Für die Abnahme sollten feste Testdaten genutzt werden, damit Ergebnisse vergleichbar bleiben.

### 5.1 Testaccounts

| Account | Zweck | Erwartung |
|---|---|---|
| Neuer Account | Registrierung, erster Start, Onboarding | Account und Hauptprofil werden erstellt |
| Bestehender Account | Login, Historie, gespeicherte Daten | Daten werden geladen |
| Account mit betreutem Profil | Profilwechsel, getrennte Daten | Daten bleiben profilgebunden |
| Fehleraccount | falsches Passwort, doppelte E-Mail | Klare Fehlermeldungen |

### 5.2 Medizinische Testszenarien

| Szenario | Eingabe | Erwartung |
|---|---|---|
| Niedrige Dringlichkeit | Leichte Kopfschmerzen seit 2 Tagen, kein Fieber, keine neurologischen Ausfälle | Strukturierte Handlungsempfehlung, keine Notfallseite |
| Mittlere Dringlichkeit | Anhaltende Beschwerden, Verschlechterung, aber keine Red Flags | Zeitnahe Empfehlung, Versorgungsebene plausibel |
| Notfall | Starke Brustschmerzen, Atemnot, Kaltschweißigkeit | Notfallfenster mit 112-Hinweis |
| Unklarer Fall | Sehr kurze Eingabe: "Mir ist schlecht" | Rückfragen statt voreiliger Empfehlung |
| Fieber | Temperatur 38,5 Grad, Begleitsymptome | Fieber korrekt eingeordnet, keine Schmerzskala für Fieber |
| Kinder-/Betreutes Profil | Beschwerde im verwalteten Profil | Empfehlung und Historie werden korrekt dem Profil zugeordnet |

## 6. Funktionsabdeckung Frontend

### 6.1 Onboarding

| ID | Test | Schritte | Erwartung | Priorität |
|---|---|---|---|---|
| FE-ONB-01 | App startet | App neu öffnen | Onboarding erscheint ohne Fehler | Kritisch |
| FE-ONB-02 | Careena-Bilder laden | Onboarding ansehen | Keine fehlenden Assets, keine 404-Konsole | Hoch |
| FE-ONB-03 | Start Chat | "Jetzt mit Careena sprechen" drücken | Chat oder Auth-Flow öffnet korrekt | Kritisch |
| FE-ONB-04 | Responsive Layout | Breiten 320, 390, 768, 1440 px prüfen | Keine Überlappung, Text lesbar | Hoch |
| FE-ONB-05 | Dark Mode | Darstellung wechseln | Farben, Kontraste, Bilder passen | Mittel |

### 6.2 Registrierung und Login

| ID | Test | Schritte | Erwartung | Priorität |
|---|---|---|---|---|
| FE-AUTH-01 | Registrierung mit gültigen Daten | Name, E-Mail, Passwort, Profilangaben eintragen | Account wird erstellt | Kritisch |
| FE-AUTH-02 | Pflichtfelder | Registrierung leer absenden | Klare Validierung je Feld | Hoch |
| FE-AUTH-03 | Passwortregeln | Zu schwaches Passwort eingeben | Verständliche Fehlermeldung | Hoch |
| FE-AUTH-04 | Doppelte E-Mail | Bereits registrierte E-Mail nutzen | Nutzerfreundliche Fehlermeldung | Hoch |
| FE-AUTH-05 | Login gültig | Bestehende Zugangsdaten nutzen | Home Screen öffnet | Kritisch |
| FE-AUTH-06 | Login ungültig | Falsches Passwort nutzen | Keine Anmeldung, klare Meldung | Hoch |
| FE-AUTH-07 | Tastaturbedienung | Mit Pfeiltasten/Tab durch Felder navigieren | Alle Eingaben erreichbar | Hoch |
| FE-AUTH-08 | Geburtsdatum | Ungültige und gültige Daten testen | Nur plausible Daten akzeptiert | Hoch |

### 6.3 Home Screen

| ID | Test | Schritte | Erwartung | Priorität |
|---|---|---|---|---|
| FE-HOME-01 | Home lädt | Nach Login öffnen | Begrüßung, Funktionen und Navigation sichtbar | Kritisch |
| FE-HOME-02 | Funktionsnavigation | Alle Kacheln öffnen | Zielseiten öffnen korrekt | Hoch |
| FE-HOME-03 | Suche | Nach Funktionen suchen | Passende Funktionen werden gefiltert | Mittel |
| FE-HOME-04 | Einfache Ansicht | Einstellung aktivieren | Größere, reduzierte UI | Mittel |
| FE-HOME-05 | Zurücknavigation | Von Unterseiten zurück | Keine Datenverluste, keine Abstürze | Hoch |

### 6.4 Chat und Symptomdialog

| ID | Test | Schritte | Erwartung | Priorität |
|---|---|---|---|---|
| FE-CHAT-01 | Chat öffnen | Home -> Chat | Eingabefeld fokussiert, Verlauf sichtbar | Kritisch |
| FE-CHAT-02 | Nachricht senden | Freitext eingeben und senden | Nutzernachricht und Antwort erscheinen | Kritisch |
| FE-CHAT-03 | Streaming/Loading | Antwort abwarten | Thinking Bubble, keine doppelten Antworten | Hoch |
| FE-CHAT-04 | Smart Replies | Vorschlag antippen | Text wird übernommen/gesendet wie vorgesehen | Mittel |
| FE-CHAT-05 | Leere Eingabe | Senden ohne Text | Keine leere Nachricht | Mittel |
| FE-CHAT-06 | Lange Eingabe | Sehr langer Text | Layout bleibt stabil, kein Overflow | Hoch |
| FE-CHAT-07 | Tastatur | Pfeiltasten und Enter nutzen | Eingabe und Navigation funktionieren | Hoch |
| FE-CHAT-08 | Fachbegriffe | Antwort mit Fachbegriffen | Begriffe sind markiert, Tooltip erscheint | Mittel |
| FE-CHAT-09 | Glossar-Tooltip | Tooltip öffnen | Erklärung aus zentralem Glossar korrekt | Mittel |
| FE-CHAT-10 | Chat verlassen | Während laufendem Chat zurück | Sicherheitsdialog oder sauberer Abbruch | Hoch |
| FE-CHAT-11 | Netzwerkfehler | Backend nicht erreichbar | Verständliche Fehlermeldung, App bleibt nutzbar | Kritisch |

### 6.5 Handlungsempfehlung und Dringlichkeit

| ID | Test | Schritte | Erwartung | Priorität |
|---|---|---|---|---|
| FE-REC-01 | Normale Empfehlung | Nicht-akuten Fall abschließen | Empfehlung erscheint als Karte, nicht als Rohtextblock | Kritisch |
| FE-REC-02 | Zusammenfassung | Antwort enthält "Kurze Zusammenfassung" | Abschnitt wird korrekt angezeigt | Hoch |
| FE-REC-03 | Dringlichkeit niedrig | Antwort enthält `Dringlichkeit: niedrig` | Dringlichkeit sichtbar, dezente Farbe | Hoch |
| FE-REC-04 | Dringlichkeit mittel | Antwort enthält `Dringlichkeit: mittel/zeitnah` | Dringlichkeit sichtbar, gelb/orange | Hoch |
| FE-REC-05 | Dringlichkeit hoch | Antwort enthält `Dringlichkeit: hoch/sofort` | Warnfarbe oder Notfallflow je Backend-Einstufung | Kritisch |
| FE-REC-06 | Versorgungsebene | Antwort enthält Hausarzt/Facharzt/Selbstbeobachtung | Versorgungsebene korrekt in Karte | Hoch |
| FE-REC-07 | Nächster Schritt | Antwort enthält nächsten Schritt | Handlungsanweisung gut lesbar | Hoch |
| FE-REC-08 | Hinweis | Antwort enthält Hinweis | Hinweisbox sichtbar und lesbar | Hoch |
| FE-REC-09 | PDF Export | PDF exportieren drücken | PDF wird erzeugt, enthält Empfehlung | Hoch |
| FE-REC-10 | Termin vereinbaren | Empfehlung enthält Arzttermin/Hausarzt/Facharzt | Button sichtbar, Termin wird erstellt | Hoch |
| FE-REC-11 | Chatabschluss | Empfehlung erzeugt | Keine weiteren unsinnigen Folgefragen nach Abschluss | Hoch |
| FE-REC-12 | Historie | Empfehlung speichern | Chat-History enthält Empfehlung und Exportdaten | Hoch |

### 6.6 Notfall- und Red-Flag-Flow

| ID | Test | Schritte | Erwartung | Priorität |
|---|---|---|---|---|
| FE-EMG-01 | Notfall erkannt | Red-Flag-Szenario senden | Notfallseite erscheint | Kritisch |
| FE-EMG-02 | Notfallinhalt | Notfallseite prüfen | 112, Notaufnahme, nicht allein bleiben sichtbar | Kritisch |
| FE-EMG-03 | Notrufbutton | Button drücken | Telefonaktion oder fallback Hinweis | Kritisch |
| FE-EMG-04 | Erkannte Warnzeichen | Backend liefert Keywords | Warnzeichen werden angezeigt | Hoch |
| FE-EMG-05 | PDF Export Notfall | PDF exportieren | PDF enthält Notfall-Empfehlung | Hoch |
| FE-EMG-06 | Keine Diagnose | Infohinweis prüfen | Hinweis ersetzt keine ärztliche Diagnose sichtbar | Kritisch |
| FE-EMG-07 | Zurücknavigation | Zurück aus Notfallseite | Nutzer verliert nicht den Kontext | Hoch |
| FE-EMG-08 | Fehlklassifikation vermeiden | Nicht-akuter Fall | Keine Notfallseite ohne Red Flag | Kritisch |

### 6.7 Symptomtagebuch

| ID | Test | Schritte | Erwartung | Priorität |
|---|---|---|---|---|
| FE-SYM-01 | Symptom anlegen | Symptomtyp, Körperstelle, Details speichern | Eintrag erscheint im Tagebuch | Kritisch |
| FE-SYM-02 | Schmerzskala | Schmerzsymptom auswählen | Schmerzskala sichtbar und speicherbar | Hoch |
| FE-SYM-03 | Fiebertemperatur | Fieber auswählen | Temperaturleiste statt Schmerzskala | Hoch |
| FE-SYM-04 | Temperaturbereich | 36,0 bis 42,0 Grad prüfen | 0,5er-Schritte, korrekte Fiebergrenzen | Hoch |
| FE-SYM-05 | Body Silhouette männlich | Geschlecht männlich | Vorder-/Rückenansicht passend | Mittel |
| FE-SYM-06 | Body Silhouette weiblich | Geschlecht weiblich | Weiblichere Silhouette passend | Mittel |
| FE-SYM-07 | Körperbereiche | Kopf, Hals, Brust, Rücken, Hüfte, Knie, Füße wählen | Markierung sitzt korrekt | Hoch |
| FE-SYM-08 | Vorne/hinten | Körperbereich plus Ansicht wählen | Speicherung enthält Bereich und Ansicht | Hoch |
| FE-SYM-09 | Hinten ohne Bauch | Rückenansicht prüfen | Bauch nicht als hinten auswählbar | Hoch |
| FE-SYM-10 | Bearbeiten/Löschen | Eintrag ändern oder entfernen | Daten aktualisieren korrekt | Hoch |
| FE-SYM-11 | Leerer Zustand | Keine Einträge | Freundlicher Empty State | Mittel |
| FE-SYM-12 | Persistenz | App neu laden | Einträge bleiben erhalten | Kritisch |

### 6.8 Medikamentenplan

| ID | Test | Schritte | Erwartung | Priorität |
|---|---|---|---|---|
| FE-MED-01 | Medikament hinzufügen | Name, Dosis, Einheit, Zeit speichern | Medikament erscheint im Plan | Kritisch |
| FE-MED-02 | Autocomplete | Medikament suchen | Vorschläge erscheinen und auswählbar | Mittel |
| FE-MED-03 | Dosiseinheit | Einheit eingeben | Einheit wird korrekt gespeichert | Hoch |
| FE-MED-04 | Einnahmefrequenz täglich | Täglich wählen | Dosis erscheint täglich | Hoch |
| FE-MED-05 | Zweimal täglich | Zwei Zeiten wählen | Zwei Einträge pro Tag | Hoch |
| FE-MED-06 | Wöchentlich/monatlich | Frequenz wählen | Anzeige am richtigen Datum | Hoch |
| FE-MED-07 | Einnahme abhaken | Checkbox nutzen | Status bleibt gespeichert | Hoch |
| FE-MED-08 | Erinnerung | Reminder aktivieren/deaktivieren | Status korrekt, keine Abstürze ohne Berechtigung | Mittel |
| FE-MED-09 | Medikament bearbeiten | Daten ändern | Plan aktualisiert sich | Hoch |
| FE-MED-10 | Medikament löschen | Löschen bestätigen | Eintrag verschwindet | Hoch |

### 6.9 Termine

| ID | Test | Schritte | Erwartung | Priorität |
|---|---|---|---|---|
| FE-APT-01 | Termin manuell anlegen | Arzt, Datum, Uhrzeit, Notiz speichern | Termin erscheint | Hoch |
| FE-APT-02 | Termin aus Empfehlung | Empfehlung -> Termin vereinbaren | Terminempfehlung wird angelegt | Hoch |
| FE-APT-03 | Termin bearbeiten | Details ändern | Änderungen bleiben erhalten | Mittel |
| FE-APT-04 | Termin löschen | Löschen bestätigen | Termin entfernt | Mittel |
| FE-APT-05 | 116117-Hinweis | Terminseite prüfen | Hinweis/Verlinkung korrekt | Mittel |

### 6.10 Einstellungen und Profile

| ID | Test | Schritte | Erwartung | Priorität |
|---|---|---|---|---|
| FE-SET-01 | Einstellungen öffnen | Home -> Einstellungen | Alle Bereiche sichtbar | Kritisch |
| FE-SET-02 | Suche | Begriff suchen | Passende Einstellungen sichtbar | Mittel |
| FE-SET-03 | Darstellung | Dark/Light/System wechseln | App aktualisiert Theme | Mittel |
| FE-SET-04 | Einfache Ansicht | Aktivieren/deaktivieren | UI reagiert sichtbar | Mittel |
| FE-SET-05 | Profildaten | Name/Geburt/Geschlecht ändern | Daten gespeichert | Hoch |
| FE-SET-06 | Gesundheitsdaten | Größe, Gewicht, Vorerkrankungen ändern | Daten gespeichert | Hoch |
| FE-SET-07 | Betreutes Profil | Profil hinzufügen | Neues Profil auswählbar | Hoch |
| FE-SET-08 | Profilwechsel | Zwischen Profilen wechseln | Datenkontext wechselt korrekt | Kritisch |
| FE-SET-09 | Glossar | Glossar öffnen | Alphabetische Liste sichtbar | Mittel |
| FE-SET-10 | Glossarsuche | Begriff suchen | Passende Begriffe erscheinen | Mittel |
| FE-SET-11 | Datenschutzseite | Öffnen | Datenschutzinformationen sichtbar | Hoch |
| FE-SET-12 | Logout | Abmelden | Session wird gelöscht, Onboarding/Auth erscheint | Kritisch |

### 6.11 Chat-History

| ID | Test | Schritte | Erwartung | Priorität |
|---|---|---|---|---|
| FE-HIST-01 | Verlauf öffnen | Home -> Nachrichten | Gespeicherte Chats sichtbar | Hoch |
| FE-HIST-02 | Sortierung | Neueste/Älteste wechseln | Reihenfolge korrekt | Mittel |
| FE-HIST-03 | Gruppierung | Mehrere Monate | Monatsgruppen korrekt | Mittel |
| FE-HIST-04 | Verlauf öffnen | Eintrag antippen | Chatdetails sichtbar | Hoch |
| FE-HIST-05 | Notfallmarkierung | Notfallverlauf erzeugen | Eintrag als Notfall erkennbar | Hoch |
| FE-HIST-06 | Profiltrennung | Profil wechseln | Nur passende Historie sichtbar | Kritisch |

## 7. Backend-Abdeckung

### 7.1 Auth und Profile

| ID | Test | Erwartung | Priorität |
|---|---|---|---|
| BE-AUTH-01 | Registrierung erzeugt Account und Hauptprofil | Datenbank enthält korrekte Beziehungen | Kritisch |
| BE-AUTH-02 | Login mit falschem Passwort | Kein Token, korrekter Fehler | Kritisch |
| BE-AUTH-03 | Tokenpflicht | Geschützte Endpunkte ohne Token blockiert | Kritisch |
| BE-AUTH-04 | Profilzugriff | Nutzer sieht nur eigene/verwaltete Profile | Kritisch |
| BE-AUTH-05 | Soft Delete | Gelöschte Profile/Accounts nicht mehr aktiv | Hoch |

### 7.2 Chat und medizinische Logik

| ID | Test | Erwartung | Priorität |
|---|---|---|---|
| BE-CHAT-01 | Chat startet Session | Session-ID stabil und eindeutig | Kritisch |
| BE-CHAT-02 | Follow-up-Fragen | Unvollständige Eingaben führen zu Rückfragen | Hoch |
| BE-CHAT-03 | Handlungsempfehlung | Vollständige Eingaben führen zu strukturierter Empfehlung | Kritisch |
| BE-CHAT-04 | Dringlichkeitsstufen | Niedrig, mittel, hoch/Notfall korrekt abgebildet | Kritisch |
| BE-CHAT-05 | Red Flags | Kritische Symptome werden zuverlässig erkannt | Kritisch |
| BE-CHAT-06 | Keine Diagnose | Antwort vermeidet Diagnoseversprechen | Kritisch |
| BE-CHAT-07 | Kontexttrennung | Profilwechsel setzt Kontext korrekt zurück | Kritisch |
| BE-CHAT-08 | Halluzinationsschutz | Antwort bleibt bei vorhandenen Angaben | Hoch |
| BE-CHAT-09 | Fallback | LLM/API-Fehler erzeugt sichere Meldung | Kritisch |

### 7.3 Symptome, Medikamente, Termine und History

| ID | Test | Erwartung | Priorität |
|---|---|---|---|
| BE-DATA-01 | Symptom erstellen/listen/löschen | Profilgebunden korrekt | Hoch |
| BE-DATA-02 | Symptomvalidierung | Ungültige Werte abgelehnt | Hoch |
| BE-DATA-03 | Chat-History speichern | Empfehlung und Metadaten bleiben erhalten | Hoch |
| BE-DATA-04 | Chat-History abrufen | Nur profilberechtigte Daten | Kritisch |
| BE-DATA-05 | Medication API | Create/Update korrekt serialisiert | Hoch |
| BE-DATA-06 | Input Drafts | Drafts werden bereinigt und dedupliziert | Mittel |

## 8. Ende-zu-Ende-Testflows

### E2E-01 Neuer Nutzer mit normaler Empfehlung

1. App öffnen.
2. Neuen Account registrieren.
3. Gesundheitsdaten eintragen.
4. Chat starten.
5. Nicht-akute Beschwerden eingeben.
6. Rückfragen beantworten.
7. Handlungsempfehlung prüfen.
8. PDF exportieren.
9. Falls empfohlen, Termin vereinbaren.
10. Chat-History öffnen und gespeicherten Verlauf prüfen.

Erwartung: Der komplette Flow funktioniert ohne Absturz, Empfehlung ist verständlich, History ist gespeichert.

### E2E-02 Bestehender Nutzer mit Notfall

1. Mit bestehendem Account einloggen.
2. Chat starten.
3. Red-Flag-Symptom eingeben.
4. Notfallseite prüfen.
5. Notrufhinweise und Warnzeichen prüfen.
6. PDF exportieren.
7. History prüfen.

Erwartung: Notfall wird sofort und eindeutig angezeigt. Keine normale Empfehlung versteckt den Notfall.

### E2E-03 Betreutes Profil

1. Ein betreutes Profil erstellen.
2. Profil wechseln.
3. Symptomtagebuch-Eintrag erfassen.
4. Chatempfehlung erzeugen.
5. History prüfen.
6. Zurück zum eigenen Profil wechseln.

Erwartung: Daten des betreuten Profils erscheinen nicht im eigenen Profil und umgekehrt.

### E2E-04 Fieber und Symptomtagebuch

1. Symptomtagebuch öffnen.
2. Fieber auswählen.
3. Temperatur 37,5, 38,0, 38,5 und 42,0 prüfen.
4. Eintrag speichern.
5. App neu laden.

Erwartung: Temperatursteuerung ist medizinisch korrekt und gespeichert.

### E2E-05 Offline/Backend-Fehler

1. Backend stoppen oder Netzwerkfehler simulieren.
2. Login, Chat und Datenspeicherung versuchen.
3. App weiter bedienen.

Erwartung: Nutzer erhält verständliche Fehlermeldungen, App bleibt stabil.

## 9. Medizinische Sicherheitsprüfung

Diese Prüfung ist besonders wichtig, weil die App gesundheitsbezogene Empfehlungen erzeugt.

| ID | Test | Erwartung | Priorität |
|---|---|---|---|
| MED-01 | Notfallhinweise | 112/Notaufnahme werden bei Red Flags klar angezeigt | Kritisch |
| MED-02 | Kein Diagnoseversprechen | Texte sagen nicht "Sie haben Krankheit X" als sichere Diagnose | Kritisch |
| MED-03 | Grenzen der App | Hinweis "ersetzt keine ärztliche Untersuchung" sichtbar | Kritisch |
| MED-04 | Fieberwerte Erwachsene | 36,7-37,4 normal, 37,5-38,0 erhöht, über 38,0 Fieber | Hoch |
| MED-05 | Dringlichkeitslogik | Niedrig/mittel/hoch plausibel und konsistent | Kritisch |
| MED-06 | Red-Flag-Abdeckung | Brustschmerz, Atemnot, neurologische Ausfälle, starke Blutung, Bewusstlosigkeit | Kritisch |
| MED-07 | Unklare Eingaben | App fragt nach, statt falsche Sicherheit zu geben | Hoch |
| MED-08 | Medikamentenhinweise | Keine gefährlichen Dosierungsempfehlungen ohne Kontext | Kritisch |
| MED-09 | Psychische Krise | Selbstgefährdung wird sicher eskaliert | Kritisch |
| MED-10 | Kinder/Schwangerschaft | Falls nicht unterstützt, klare Vorsichtshinweise | Hoch |

## 10. Datenschutz und Sicherheit

| ID | Test | Schritte | Erwartung | Priorität |
|---|---|---|---|---|
| SEC-01 | Tokenpflicht | API ohne Token aufrufen | Zugriff verweigert | Kritisch |
| SEC-02 | Profilisolierung | Profil-ID eines fremden Nutzers verwenden | Zugriff verweigert | Kritisch |
| SEC-03 | Logout | Abmelden und zurück navigieren | Geschützte Seiten nicht nutzbar | Kritisch |
| SEC-04 | Lokaler Speicher | Nach Logout prüfen | Keine sensiblen Daten offen sichtbar | Hoch |
| SEC-05 | Fehlerausgaben | Backendfehler provozieren | Keine Stacktraces/Secrets im UI | Hoch |
| SEC-06 | `.env` | Repo prüfen | Keine echten Secrets committed | Kritisch |
| SEC-07 | HTTPS/Deployment | Produktivumgebung prüfen | Keine unsicheren API-URLs | Kritisch |
| SEC-08 | PDF | PDF exportieren | Enthält nur relevante Nutzerdaten | Hoch |
| SEC-09 | Account löschen | Löschung testen | Login danach blockiert, Datenzugriff entfernt | Hoch |
| SEC-10 | Datenschutztext | Einstellungen prüfen | Verständliche Datenschutzinfos vorhanden | Hoch |

## 11. Barrierefreiheit und Bedienbarkeit

| ID | Test | Erwartung | Priorität |
|---|---|---|---|
| A11Y-01 | Tastaturbedienung | Alle Eingabefelder per Pfeiltasten/Tab erreichbar | Hoch |
| A11Y-02 | Fokus sichtbar | Aktuelles Element ist visuell erkennbar | Hoch |
| A11Y-03 | Screenreader Labels | Buttons, Felder, Notfallaktionen haben sinnvolle Labels | Hoch |
| A11Y-04 | Kontrast Light Mode | Text und Buttons erfüllen gute Lesbarkeit | Hoch |
| A11Y-05 | Kontrast Dark Mode | Text und Buttons erfüllen gute Lesbarkeit | Hoch |
| A11Y-06 | Große Schrift | TextScaler/große Schrift prüfen | Keine Überläufe | Hoch |
| A11Y-07 | Kleine Displays | 320 px Breite prüfen | Alle Aktionen erreichbar | Hoch |
| A11Y-08 | Touch-Ziele | Buttons groß genug und nicht zu nah | Mittel |
| A11Y-09 | Fehlermeldungen | Fehler nicht nur farblich markiert | Hoch |
| A11Y-10 | Tooltips | Fachbegriffe per Tap/Keyboard zugänglich | Mittel |

## 12. Responsive Design und visuelle QA

Zu prüfen in mindestens diesen Viewports:

- 320 x 568
- 390 x 844
- 768 x 1024
- 1366 x 768
- 1920 x 1080

| Bereich | Erwartung |
|---|---|
| Onboarding | Keine Bild-/Textüberlappung |
| Home | Kacheln und Suche bleiben bedienbar |
| Chat | Eingabefeld, Nachrichten, Empfehlungskarte und Buttons sichtbar |
| Notfallseite | Karte ist zentriert, kein Inhalt abgeschnitten |
| Symptomtagebuch | Silhouetten und Auswahlchips passen |
| Einstellungen | Suche, Listen und Detailseiten lesbar |
| PDF Export | Button erreichbar und keine Layoutverschiebung |

Visuelle Abnahme:

- Keine gelben/schwarzen Flutter-Overflow-Balken.
- Keine roten Asset-Platzhalter.
- Keine abgeschnittenen Buttons.
- Keine unlesbaren Texte auf farbigem Hintergrund.
- Keine UI-Karten in Karten, falls nicht bewusst als Dialog/Item genutzt.
- Einheitliche Abstände und Rundungen.
- App wirkt im Light und Dark Mode konsistent.

## 13. Performance und Stabilität

| ID | Test | Erwartung | Priorität |
|---|---|---|---|
| PERF-01 | App-Start | Start ohne lange weiße/leere Fläche | Mittel |
| PERF-02 | Chatantwort | Loading sichtbar, keine blockierte UI | Hoch |
| PERF-03 | Lange History | Viele Chatverläufe laden | Scrollen bleibt flüssig | Mittel |
| PERF-04 | Viele Symptome | Tagebuch mit vielen Einträgen | Suche/Anzeige bleibt nutzbar | Mittel |
| PERF-05 | PDF Export | Export großer Empfehlung | Keine App-Blockade oder leerer Export | Hoch |
| PERF-06 | Speicher | Mehrere Navigationen/Chats | Keine auffälligen Leaks oder Abstürze | Mittel |
| PERF-07 | Hot Restart/Reload Smoke | App neu laden | Zustand verhält sich erwartbar | Mittel |

## 14. Fehler- und Edge-Case-Abdeckung

| ID | Test | Erwartung |
|---|---|
| EDGE-01 | Sehr lange Wörter im Chat | Kein horizontaler Overflow |
| EDGE-02 | Emojis und Sonderzeichen | Keine kaputte Darstellung |
| EDGE-03 | Umlaute in Suche | Treffer funktionieren |
| EDGE-04 | Leere API-Antwort | Sicherer Fallback |
| EDGE-05 | Ungültiges JSON | Nutzerfreundliche Fehlermeldung |
| EDGE-06 | Doppelklick auf Senden | Keine doppelten Nachrichten |
| EDGE-07 | Browser Refresh im Chat | Kein Absturz, Zustand klar |
| EDGE-08 | Zurückbutton während Dialog | Dialog/Navigation konsistent |
| EDGE-09 | Scrollposition | Neue Nachrichten erreichbar |
| EDGE-10 | Keine Daten | Empty States statt leerer Screens |

## 15. Deployment- und Release-Checkliste

Vor dem Markt-/Präsentationsrelease:

- [ ] Branch ist aktuell und basiert auf dem richtigen Zielbranch.
- [ ] Keine ungeprüften Debug-Kommentare oder Testbuttons sichtbar.
- [ ] Keine echten Secrets in `.env`, Code oder Dokumentation.
- [ ] `pubspec.yaml` enthält alle Assets korrekt.
- [ ] Keine 404-Assets in Browser-Konsole.
- [ ] Version/Buildnummer ist gesetzt.
- [ ] Datenschutz- und Impressums-/Kontaktinformationen sind erreichbar.
- [ ] Notfallhinweise sind im Notfallflow sichtbar.
- [ ] PDF-Export wurde auf Inhalt und Format geprüft.
- [ ] Chat-History wurde mit normaler und Notfall-Empfehlung geprüft.
- [ ] Profilwechsel wurde mit Gesundheitsdaten, Symptomen und History geprüft.
- [ ] App wurde in Light und Dark Mode geprüft.
- [ ] App wurde auf kleiner und großer Bildschirmgröße geprüft.
- [ ] Review durch mindestens eine zweite Person erfolgt.
- [ ] Bekannte Restfehler sind dokumentiert und bewertet.

## 16. Abnahmematrix

| Bereich | Automatisiert | Manuell | Kritisch bestanden | Tester | Datum | Bemerkung |
|---|---|---|---|---|---|---|
| Onboarding | | | | | | |
| Auth/Login | | | | | | |
| Profile | | | | | | |
| Home | | | | | | |
| Chat | | | | | | |
| Handlungsempfehlung | | | | | | |
| Notfallflow | | | | | | |
| Symptomtagebuch | | | | | | |
| Medikamente | | | | | | |
| Termine | | | | | | |
| Einstellungen | | | | | | |
| Glossar/Tooltips | | | | | | |
| Datenschutz | | | | | | |
| Barrierefreiheit | | | | | | |
| Responsive Design | | | | | | |
| Performance | | | | | | |
| Deployment | | | | | | |

## 17. Bug-Protokoll

| ID | Bereich | Beschreibung | Schwere | Status | Verantwortlich | Entscheidung |
|---|---|---|---|---|---|---|
| BUG-001 | | | | Offen | | |

Statuswerte:

- Offen
- In Arbeit
- Behoben
- Retest bestanden
- Akzeptiertes Restrisiko
- Verschoben

## 18. Mindest-Testcoverage je Release

Für jeden Release müssen mindestens diese Bereiche grün sein:

- Auth und Profilzugriff: automatisiert und manuell.
- Chat-Service, Chat-Controller und Chat-UI: automatisiert und manuell.
- Red-Flag-/Notfalllogik: automatisiert und manuell.
- Handlungsempfehlung inklusive PDF und Terminvereinbarung: manuell.
- Symptomtagebuch inklusive Fieber und Body-Silhouette: manuell.
- Settings inklusive Glossar und Datenschutz: manuell.
- API-Client-Fehlerbehandlung: automatisiert.
- Backend Auth/Profile/Chat/Safety Tests: automatisiert.
- Responsive Smoke auf mindestens drei Größen: manuell.
- Tastaturbedienung und Fokus: manuell.

## 19. Traceability zu bestehenden Testdokumenten

| Thema | Frontend-Testdokument | Backend-Testdokument | Manuelle Ergänzung in diesem Plan |
|---|---|---|---|
| Auth | `T04` | `T01` | FE-AUTH, SEC |
| Profile | `T08`, `T10` | `T02` | FE-SET, E2E-03 |
| Chat | `T02`, `T03`, `T06`, `T11` | `T05`, `T07` | FE-CHAT, FE-REC |
| Red Flags | `T11` | `T06`, `T08` | FE-EMG, MED |
| Symptome | `T09` | `T04` | FE-SYM |
| Medikamente | `T01` | teilweise API/Service Tests | FE-MED |
| Termine | Widget-/manuelle Tests ergänzen | falls vorhanden ergänzen | FE-APT |
| Settings | `T10` | Profile/Auth | FE-SET |
| Netzwerk | `T05` | Router-/Service-Tests | SEC, EDGE |

## 20. Finale Freigabe

Ein Release darf freigegeben werden, wenn:

- Alle kritischen Tests bestanden sind.
- Keine offenen kritischen oder hohen Bugs existieren.
- Alle medizinischen Sicherheitsprüfungen bestanden sind.
- Datenschutz- und Profiltrennung geprüft wurden.
- Mindestens eine Person außer dem Implementierer die Hauptflows getestet hat.
- Die Abnahmematrix ausgefüllt wurde.

Freigabeentscheidung:

| Rolle | Name | Datum | Entscheidung | Unterschrift/Bestätigung |
|---|---|---|---|---|
| Product Owner | | | | |
| Scrum Master | | | | |
| Entwicklung | | | | |
| QA/Tester | | | | |
