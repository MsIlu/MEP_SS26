# Lokaler FHIR-Server als Test- und Adapterlösung

## Ziel

Dieser lokale FHIR-Server dient als Test- und Adapterlösung für die technische Vorbereitung einer möglichen späteren FHIR-Anbindung.

Die Anwendung bindet aktuell keine produktive 116117-Schnittstelle an. Da für das Projekt keine offiziell nutzbare produktive 116117-FHIR-Schnittstelle vorliegt, wird ein lokaler HAPI-FHIR-Server verwendet, um FHIR-Ressourcen technisch erzeugen, übertragen und prüfen zu können.

Dadurch kann lokal getestet werden, ob Careena später FHIR-Ressourcen bereitstellen und an einen FHIR-Server übergeben kann, ohne eine echte externe Schnittstelle zu verwenden.

## Technische Umsetzung

Der lokale FHIR-Server wird über Docker Compose gestartet.

Dafür wurde in der bestehenden `docker-compose.yml` ein zusätzlicher Service ergänzt:

fhir-server:
  image: hapiproject/hapi:v8.10.0-1
  container_name: careena_fhir_server
  restart: unless-stopped
  ports:
    - "8080:8080"
  volumes:
    - fhir_data:/data/hapi

Für reproduzierbare lokale Tests wird ein konkreter HAPI-FHIR-Docker-Tag verwendet statt latest.

Das Volume `fhir_data` ist für eine spätere Persistenz-Konfiguration vorbereitet.

## Vorbereitung für Persistenz

In der `docker-compose.yml` ist ein benanntes Docker Volume (`fhir_data`) für den lokalen FHIR-Server vorbereitet.

Mit der aktuellen Konfiguration ist jedoch noch keine explizite HAPI-FHIR-Datenbank- oder Datasource-Konfiguration eingerichtet. Daher wird nicht garantiert, dass FHIR-Ressourcen bereits dauerhaft persistent gespeichert werden.

Das Volume dient in diesem Schritt als vorbereitende Grundlage für eine spätere Persistenz-Konfiguration. Eine konkrete Datenbank-Anbindung, z. B. über PostgreSQL, kann in einem separaten Schritt ergänzt werden.


## Starten des lokalen FHIR-Servers

```bash
docker compose up -d fhir-server
```

## Prüfen des Containers

```bash
docker compose ps
```

Der Container sollte als `careena_fhir_server` mit dem Status `Up` angezeigt werden.

## Prüfen der FHIR-Schnittstelle

PowerShell:

```powershell
(Invoke-WebRequest http://localhost:8080/fhir/metadata -UseBasicParsing).StatusCode
```

Erwartetes Ergebnis:

```text
200
```

Alternativ kann der Server im Browser geöffnet werden:

```text
http://localhost:8080/
http://localhost:8080/fhir/metadata
```

## FHIR Base URL

```text
http://localhost:8080/fhir
```

## Abgrenzung

Diese Lösung ist keine produktive 116117-Anbindung.

Der lokale FHIR-Server dient nur dazu, die technische Übergabe von FHIR-Ressourcen lokal zu testen. Eine echte Kommunikation mit der Terminservicestelle findet nicht statt.

Nicht Bestandteil dieses Schritts sind:

* produktive 116117-Anbindung
* produktive externe Terminbuchung bei der 116117
* Authentifizierung gegenüber externen Systemen
* TI-/KIM-Anbindung
* vollständige KBV-spezifische Profile
* Verarbeitung echter Patientendaten
* explizite persistente HAPI-FHIR-Datenbank-Anbindung

## Bezug zum FHIR-Mapper

Der FHIR-Mapper erzeugt FHIR-Ressourcen aus internen Careena-Test- und Analyse-Daten.

Der lokale FHIR-Server nimmt diese erzeugten FHIR-Ressourcen testweise entgegen. Dadurch kann geprüft werden, ob die technische Übertragung und Verarbeitung grundsätzlich funktioniert.

## Aktueller Careena-Ablauf

Der Backend-Endpunkt `POST /appointments/search` erzeugt für die aktuelle
Careena-Session ein FHIR-Bundle und überträgt es an HAPI. Danach fragt das
Backend FHIR-Appointment-Ressourcen aus HAPI ab und gibt diese an das Frontend
zurück.

Wenn für die konkrete Session/Profil/PLZ-Kombination noch keine passenden
Appointment-Ressourcen in HAPI liegen, legt der lokale Adapter passende
Appointment-Kandidaten in HAPI an und liest sie anschließend wieder über die
FHIR-Suche aus HAPI zurück. Dadurch läuft der technische Weg über HAPI, ohne
eine produktive 116117-Schnittstelle vorzutäuschen.

Ein ausgewählter Termin wird über
`POST /profiles/{profile_id}/appointments/recommended` zusätzlich profilbezogen
in der Careena-Datenbank gespeichert. Vor dem Speichern setzt das Backend die
zugehörige HAPI-FHIR-Appointment-Resource lokal auf `booked`, markiert die
Teilnehmer als angenommen und schreibt den buchenden Careena-Account als
FHIR-Extension. Die gespeicherte Zeile enthält die HAPI-FHIR-Appointment-ID,
den buchenden Account und den Status, damit dieselbe Empfehlung nicht doppelt
angelegt wird.

Damit entsteht folgender Ablauf:

```text
Careena-Session
→ FHIR-Mapper
→ FHIR-Bundle
→ lokaler HAPI-FHIR-Server
→ FHIR Appointment Ressourcen
→ Backend-Antwort an Flutter
→ lokale HAPI-FHIR-Buchung des ausgewählten Termins
→ profilbezogene Speicherung des gebuchten Termins in PostgreSQL
```



