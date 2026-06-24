# NFA7.1 Datenschutzhinweise und Transparenz

## Ziel

Nutzerinnen und Nutzer sollen vor oder zu Beginn der Nutzung verständlich darüber informiert werden, welche personenbezogenen und gesundheitsbezogenen Daten Careena verarbeitet und zu welchem Zweck diese Daten genutzt werden.

Diese Dokumentation erfüllt folgende Anforderungen:

- NFA7.1.1: Datenschutzhinweis vor oder zu Beginn der Nutzung bereitstellen
- NFA7.1.2: Zweck der Datenerhebung verständlich beschreiben
- NFA7.1.3: Übersicht erstellen, welche Daten im System verarbeitet werden

## Kurztext für die App

Careena verarbeitet deine Angaben, um dich bei der ersten Einordnung deiner Beschwerden zu unterstützen und passende nächste Schritte vorzuschlagen. Dazu können Kontoangaben, Profildaten, Chatnachrichten, Symptombeschreibungen und Symptomtagebuch-Einträge verarbeitet werden.

Careena ersetzt keine ärztliche Diagnose, Behandlung oder Notfallversorgung. In akuten Notfällen ist der Notruf 112 oder medizinisches Fachpersonal zu kontaktieren.

## Zweck der Datenerhebung

Die Daten werden im Prototyp zu folgenden Zwecken verarbeitet:

1. Nutzerkonto und Anmeldung  
   E-Mail-Adresse und Passwort werden verwendet, um ein Konto zu erstellen und Nutzerinnen und Nutzer wiederzuerkennen.

2. Medizinisches Profil  
   Profildaten wie Name, Geburtsdatum und biologisches Geschlecht können genutzt werden, um die Einschätzung besser an den medizinischen Kontext anzupassen.

3. Ersteinschätzung von Beschwerden  
   Chatnachrichten und Symptombeschreibungen werden verarbeitet, um Beschwerden einzuordnen und Hinweise zu möglichen nächsten Schritten zu geben.

4. Patientensteuerung  
   Die Anwendung kann Hinweise geben, ob eher Selbstbeobachtung, ärztliche Abklärung oder dringende Hilfe notwendig ist.

5. Symptomtagebuch  
   Einträge im Symptomtagebuch werden verarbeitet, damit Nutzerinnen und Nutzer ihre Beschwerden über die Zeit dokumentieren können.

6. Chatverlauf  
   Abgeschlossene Chatverläufe können gespeichert werden, damit Empfehlungen und nächste Schritte später erneut eingesehen werden können.

7. Technische Bereitstellung  
   Session-IDs und Zugriffstoken werden verwendet, um die App technisch bereitzustellen und Anfragen korrekt zuzuordnen.

## Übersicht der verarbeiteten Daten

| Datenkategorie | Beispiele | Zweck | Speicherung |
|---|---|---|---|
| Kontoangaben | E-Mail-Adresse, Passwort-Hash | Registrierung, Login, Kontoverwaltung | Backend-Datenbank |
| Profildaten | Anzeigename, Geburtsdatum, biologisches Geschlecht | medizinischer Kontext für Einschätzung | Backend-Datenbank |
| Gesundheitsangaben | Vorerkrankungen, Medikamente, medizinische Hinweise | bessere Einordnung von Beschwerden | Backend-Datenbank / Profil |
| Chatdaten | Nutzernachrichten, erkannte Symptome, Empfehlungen | Ersteinschätzung und Patientensteuerung | Session / ggf. Chatverlauf |
| Chatverlauf | Nachrichten, Empfehlung, nächste Schritte, Notfallstatus | spätere Einsicht in abgeschlossene Empfehlungen | Backend-Datenbank |
| Symptomtagebuch | Datum, Symptom, Körperbereich, Intensität, Notiz | Dokumentation von Beschwerden | lokal und/oder Backend |
| Technische Daten | Session-ID, Profil-ID, Zugriffstoken | technische Zuordnung und Authentifizierung | App / Backend |

## Hinweise zur Abgrenzung

Careena stellt keine ärztliche Diagnose und ersetzt keine medizinische Behandlung. Die Anwendung unterstützt lediglich bei der strukturierten Erfassung von Beschwerden und bei der Orientierung zu möglichen nächsten Schritten.

Diese Dokumentation beschreibt den aktuellen Prototyp-Stand und ersetzt keine finale rechtliche Datenschutzerklärung.