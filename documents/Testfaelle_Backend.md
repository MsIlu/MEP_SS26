# Testfälle Backend

Diese Datei ordnet die Backend-Tests des Projekts nach Themen, Testdateien und einzelnen Testfällen. Die IDs werden in den Backend-Testdateien als Referenz verwendet.

## ID-System

- `T01`: Auth und Account Management
- `T02`: Profile Management
- `T03`: Chat History
- `T04`: Symptome und Input-Drafts
- `T05`: Chat Logic und Session-Kontext
- `T06`: Safety und Red Flags
- `T07`: Dialogue und Response Management
- `T08`: Katalog und STS Seed Integrity
- `Txx.y`: Testdatei oder Testgruppe
- `Txx.y.z`: einzelner Testfall

## Test-Infrastruktur

### `server/tests/conftest.py`

- Stellt eine isolierte FastAPI-Test-App bereit.
- Nutzt eine frische In-Memory-SQLite-Datenbank pro Test.
- Überschreibt die produktive Datenbank-Dependency, damit Tests nicht auf PostgreSQL schreiben.
- Bindet Auth-, Profile-, Chat-History-, Symptoms- und Input-Draft-Router ein.

## T01 Auth Und Account Management

### T01.1 `server/tests/test_auth.py`

- `T01.1.1`: Registrierung erstellt User, Hauptprofil und Account-Profile-Zugriff.
- `T01.1.2`: Registrierung lehnt doppelte E-Mail-Adressen ab.
- `T01.1.3`: Login funktioniert mit gültigen Zugangsdaten.
- `T01.1.4`: Login scheitert mit falschem Passwort.
- `T01.1.5`: `/auth/me` verlangt einen Token.
- `T01.1.6`: `/auth/me` gibt den aktuellen Account mit gültigem Token zurück.
- `T01.1.7`: Account-Löschen deaktiviert den User und blockiert späteren Login.

## T02 Profile Management

### T02.1 `server/tests/test_profiles.py`

- `T02.1.1`: Profil-Liste enthält nur zugängliche Profile.
- `T02.1.2`: Child-Profil-Erstellung erzeugt Guardian-Zugriff.
- `T02.1.3`: Profilabruf per ID verlangt Zugriff.
- `T02.1.4`: Profil-Patch aktualisiert ein Profil für erlaubte Rollen.
- `T02.1.5`: Profil-Löschen setzt Soft-Delete und blendet Profil aus.
- `T02.1.6`: Gelöschtes Profil liefert `404`.
- `T02.1.7`: Familienmitglieder und andere betreute Personen erhalten Guardian-Zugriff und können per Soft-Delete gelöscht werden.
- `T02.1.8`: Die Profil-Liste enthält zuerst das Hauptprofil und danach betreute Profile in Erstellungsreihenfolge.

## T03 Chat History

### T03.1 `server/tests/test_chat_history.py`

- `T03.1.1`: Chat-History ist profilgebunden und nach Erstellungszeit sortiert.
- `T03.1.2`: Chat-History verlangt Zugriff auf das Profil.

## T04 Symptome Und Input-Drafts

### T04.1 `server/tests/test_symptoms.py`

- `T04.1.1`: Symptom-Entry wird für ein Profil gespeichert.
- `T04.1.2`: Profil-Symptome werden abgerufen.
- `T04.1.3`: Symptom-Entry wird aus der Datenbank gelöscht.
- `T04.1.4`: Symptom-Erstellung verlangt Profilzugriff.
- `T04.1.5`: Symptom-Erstellung validiert Intensitätswerte.

### T04.2 `server/tests/test_input_drafts.py`

- `T04.2.1`: Input-Draft-Router aktualisiert und leert eine gültige Session.
- `T04.2.2`: Input-Draft-Router lehnt unbekannte Session ab.
- `T04.2.3`: Input-Draft-Router verlangt Auth für profilgebundene Session.
- `T04.2.4`: Symptom-Draft kann aktualisiert und gelesen werden.
- `T04.2.5`: Symptom-Draft entfernt leere Werte.
- `T04.2.6`: Cancel entfernt gespeicherte Draft-Daten.
- `T04.2.7`: Fehlender Draft liefert eine leere Liste.
- `T04.2.8`: Extrahierte Symptome werden nur als neue Labels ergänzt.
- `T04.2.9`: Extrahierte Symptome werden bereinigt und dedupliziert.
- `T04.2.10`: Psychische Beschwerden bleiben beim Merge erhalten.
- `T04.2.11`: Generische Schmerzvarianten werden dedupliziert.
- `T04.2.12`: Generischer Schmerz wird nach spezifischem Schmerz übersprungen.
- `T04.2.13`: Spezifischer Schmerz ersetzt generischen Schmerz.
- `T04.2.14`: Schmerzphrasen mit Körperstelle werden dedupliziert.
- `T04.2.15`: Schmerzphrasen mit verbindendem Buchstaben werden dedupliziert.
- `T04.2.16`: Draft-Update bevorzugt spezifische Schmerzlabels.

### T04.3 `server/tests/test_symptom_draft_extraction.py`

- `T04.3.1`: Kontextbestätigung fügt nur bestätigte Symptome hinzu.
- `T04.3.2`: Ohne Confirmation-Extractor werden nur direkte Nutzersymptome gespeichert.
- `T04.3.3`: Fehler in der Kontextbestätigung behalten direkte Symptome bei.

## T05 Chat Logic Und Session-Kontext

### T05.1 `server/tests/test_chat_logic_symptom_extraction.py`

- `T05.1.1`: ChatLogic merged LLM-extrahierte Symptome in den Draft.
- `T05.1.2`: Manuell bearbeitete Symptome werden in den LLM-Kontext aufgenommen.

## T06 Safety Und Red Flags

### T06.1 `server/tests/test_raw_red_flag_detector.py`

- `T06.1.1`: Unklare Dyspnoe wird als vermutetes Red Flag erkannt.
- `T06.1.2`: Brustschmerz wird als vermutetes Red Flag erkannt.
- `T06.1.3`: Bewusstlosigkeit und keine Atmung werden als bestätigter Notfall erkannt.
- `T06.1.4`: Vages Unwohlsein wird nicht als Raw Red Flag markiert.

### T06.2 `server/tests/test_safety_clarification_builder.py`

- `T06.2.1`: Builder nutzt Fallback, wenn Katalog-Lookup fehlschlägt.
- `T06.2.2`: Builder nutzt Fallback, wenn Datenbankverbindung nicht verfügbar ist.

### T06.3 `server/tests/test_safety_clarification_resolver.py`

- `T06.3.1`: Ja bestätigt Red Flag und erlaubt Notfallpfad.
- `T06.3.2`: Nein entfernt vermutetes Red Flag.
- `T06.3.3`: Unsicher hält Safety-Clarification offen.
- `T06.3.4`: Sofortige-Hilfe-Antwort bestätigt Notfall.
- `T06.3.5`: Ungültige Antwort hält Safety-Clarification offen.
- `T06.3.6`: Sichtbares Ja-Label bestätigt Red Flag.

### T06.4 `server/tests/test_safety_manager_raw_safety.py`

- `T06.4.1`: SafetyManager nutzt Raw-Detector für vermutetes Red Flag.
- `T06.4.2`: SafetyManager lässt Nicht-Red-Flag-Nachricht frei.

### T06.5 `server/tests/test_sql_safety_catalog_repository.py`

- `T06.5.1`: Repository findet Safety-Catalog-Match über Laienbegriff.
- `T06.5.2`: Repository ignoriert Nicht-Safety-Links.

## T07 Dialogue Und Response Management

### T07.1 `server/tests/test_dialogue_state_followup_resolution.py`

- `T07.1.1`: Aufgelöste Requirement-Followup-Antwort erzeugt turn-lokale Resolution.
- `T07.1.2`: Nicht aufgelöste Followup-Antwort lässt Resolution leer.
- `T07.1.3`: Signal für zusätzliche medizinische Information bleibt erhalten.

### T07.2 `server/tests/test_dialogue_manager_followup_resolution.py`

- `T07.2.1`: DialogueManager wiederholt beantwortete Followup-Frage nicht.

### T07.3 `server/tests/test_dialogue_state_safety_clarification.py`

- `T07.3.1`: DialogueManager speichert offene Safety-Clarification.

### T07.4 `server/tests/test_response_manager_followup_resolution.py`

- `T07.4.1`: Followup-Slot-Update nutzt statische Bestätigung.
- `T07.4.2`: Gemischte Followup-Resolution bleibt auf LLM-Continue-Pfad.
- `T07.4.3`: Offenes Pending-Followup fragt weiter nach.

### T07.5 `server/tests/test_careena4_llm_paths_unittest.py`

- `T07.5.1`: Der Hinweis auf die Handlungsempfehlung wird mit deutschen Umlauten ausgegeben.
- `T07.5.2`: Rückfragen verwenden deutsche Umlaute.
- `T07.5.3`: Strukturierte Handlungsempfehlungen verwenden deutsche Umlaute.

## T08 Katalog Und STS Seed Integrity

### T08.1 `server/tests/test_catalog_seed_integrity.py`

- `T08.1.1`: Assessment-Criteria-Seed nutzt aktuelle Input-Model-Felder.
- `T08.1.2`: Assessment-Criteria-Keys sind eindeutig.
- `T08.1.3`: Consultation-Reason-Source-IDs sind eindeutig.
- `T08.1.4`: Consultation-Reason-Criteria-Links referenzieren existierende Seed-Items.
- `T08.1.5`: Consultation-Reason-Criteria-Links sind eindeutig.
- `T08.1.6`: User-Provided-Measurements nutzen Measurement-Value-Type.
- `T08.1.7`: STS 1001 nutzt laienbeobachtbares primäres Safety-Kriterium.
- `T08.1.8`: Kardiovaskulär/Respiratorisch hat primäre Criterion-Links.
- `T08.1.9`: Neurologie/Psychiatrie hat primäre Criterion-Links.
- `T08.1.10`: Traumatologie hat primäre Criterion-Links.
- `T08.1.11`: Gastrointestinal/Gynäkologie hat primäre Criterion-Links.
- `T08.1.12`: Urologie/Nephrologie hat primäre Criterion-Links.
- `T08.1.13`: Infektionssymptome hat primäre Criterion-Links.
- `T08.1.14`: HNO hat primäre Criterion-Links.
- `T08.1.15`: Dermatologie hat primäre Criterion-Links.
- `T08.1.16`: Rheumatologie hat primäre Criterion-Links.
- `T08.1.17`: Sonstige Konsultationsmotive haben primäre oder source-only Links.

### T08.2 `server/tests/test_sts_source_alignment_review.py`

- `T08.2.1`: Review-Samples referenzieren existierende STS-Reasons.
- `T08.2.2`: Review-Samples passen zu aktuellem Seed-Label und Kategorie.
- `T08.2.3`: Review-Samples haben primäre Criterion-Links.
- `T08.2.4`: Source-Alignment-Review deckt Mindestanzahl Kategorien ab.
- `T08.2.5`: Review enthält risikobasierte Samples pro Kategorie.
- `T08.2.6`: Sonstige Kategorie hat zusätzliche Review-Samples.
- `T08.2.7`: Als OK markierte Samples haben abgeschlossene Checklist.
- `T08.2.8`: Review-Samples verstecken bekannte Revision-Needs nicht.

## Quality-Prinzipien

- Separation of Concerns: Router-, Service-, Repository-, Manager- und Seed-Integritätstests sind getrennt dokumentiert.
- KISS: Testfälle beschreiben beobachtbares Verhalten statt interne Implementierungsdetails.
- Refactoring-Sicherheit: IDs bleiben stabil, auch wenn Testnamen später präzisiert werden.
- Datenbankschutz: Tests nutzen isolierte Testdatenbank/Fakes und sollen keine produktive PostgreSQL-Datenbank berühren.
