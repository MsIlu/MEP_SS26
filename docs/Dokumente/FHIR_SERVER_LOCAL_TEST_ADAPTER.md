# Lokaler FHIR-Server als Test- und Adapterlösung

## Ziel

Dieser lokale FHIR-Server dient als Test- und Adapterlösung für die technische Vorbereitung einer möglichen späteren FHIR-Anbindung.

Die Anwendung bindet aktuell keine produktive 116117-Schnittstelle an. Da für das Projekt keine offiziell nutzbare produktive 116117-FHIR-Schnittstelle vorliegt, wird ein lokaler HAPI-FHIR-Server verwendet, um FHIR-Ressourcen technisch erzeugen, übertragen und prüfen zu können.

## Technische Umsetzung

Der lokale FHIR-Server wird über Docker Compose gestartet.

Der lokale FHIR-Server verwendet ein benanntes Docker Volume (`fhir_data`), damit lokale Testdaten und Serverdaten nicht nur im Container selbst liegen. Dadurch bleiben Daten bei einem normalen Neustart des Containers erhalten. Wenn der Container komplett neu erstellt wird, sind die Daten nicht direkt verloren, solange das Docker Volume bestehen bleibt.

Dafür wurde in der bestehenden `docker-compose.yml` ein zusätzlicher Service ergänzt:

```yaml
fhir-server:
  image: hapiproject/hapi:latest
  container_name: careena_fhir_server
  restart: unless-stopped
  ports:
    - "8080:8080"
```

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
* echte Terminbuchung
* Authentifizierung gegenüber externen Systemen
* TI-/KIM-Anbindung
* vollständige KBV-spezifische Profile
* Verarbeitung echter Patientendaten

## Bezug zum FHIR-Mapper

Der FHIR-Mapper erzeugt FHIR-Ressourcen aus internen Careena-Test- und Analyse-Daten.

Der lokale FHIR-Server kann später genutzt werden, um diese erzeugten FHIR-Ressourcen testweise entgegenzunehmen. Dadurch kann geprüft werden, ob die technische Übertragung und Verarbeitung grundsätzlich funktioniert.

## Nächster möglicher Schritt

In einem späteren Schritt kann ein Backend-Adapter ergänzt werden, der ein erzeugtes FHIR-Bundle an den lokalen HAPI-FHIR-Server sendet.

Damit entsteht folgender Ablauf:

```text
Careena-interne Daten
→ FHIR-Mapper
→ FHIR-Bundle
→ lokaler HAPI-FHIR-Server
```



