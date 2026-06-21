# NFA7.4 Datensicherheit und technische Begrenzung

## Ziel

Sensible personenbezogene und gesundheitsbezogene Daten sollen bei der Uebertragung geschuetzt und beim Zugriff technisch begrenzt werden.

## NFA7.4.1 Gesicherte Uebertragung sensibler Daten

Der Prototyp ist fuer lokalen Betrieb vorgesehen. Die Kommunikation zwischen Flutter-Frontend und FastAPI-Backend erfolgt lokal ueber HTTPS/TLS.

Fuer diese lokale HTTPS-Nutzung wird `mkcert` verwendet. Damit wird pro Geraet ein lokal vertrauenswuerdiges Zertifikat erzeugt, das vom Browser fuer `localhost` akzeptiert werden kann. Die Zertifikatsdateien liegen lokal unter `server/certs/` und werden nicht ins Repository aufgenommen.

HTTP ist fuer die lokale Frontend-Backend-Kommunikation nicht der vorgesehene Betriebsmodus. Externe API-Verbindungen, zum Beispiel zu einem LLM-Gateway, muessen ebenfalls ueber HTTPS erfolgen, sofern sensible Daten uebertragen werden.

CORS ist nicht pauschal fuer alle Origins freigegeben. Fuer die lokale Flutter-Web-Nutzung erlaubt `CORS_ALLOWED_ORIGIN_REGEX` nur lokale Origins wie `localhost` und `127.0.0.1` mit beliebigem Port. Eine separate `CORS_ALLOWED_ORIGINS`-Liste wird fuer den lokalen Betrieb nicht benoetigt.

## NFA7.4.2 Zugriff auf verarbeitete Daten technisch begrenzen

Der Zugriff auf geschuetzte Daten wird technisch ueber Authentifizierung, Zugriffstoken und Profilberechtigungen begrenzt.

Aktueller Stand:

- Passwoerter werden nicht im Klartext gespeichert, sondern als Hash abgelegt.
- Geschuetzte Backend-Endpunkte nutzen Bearer-Token.
- Profilbezogene Daten und Chat-Sessions pruefen die Profilberechtigung.
- Ein Wechsel einer bestehenden Chat-Session auf ein anderes Profil wird technisch verhindert.

## Bewertung

NFA7.4 ist fuer den lokalen Prototyp angemessen beruecksichtigt. Die Frontend-Backend-Kommunikation ist auf HTTPS mit lokal vertrauenswuerdigem `mkcert`-Zertifikat ausgelegt. CORS ist lokal begrenzt und nicht pauschal mit `*` freigegeben. Zugriffsschutz ist fuer authentifizierte und profilbezogene Funktionen technisch angelegt.

Da das System lokal betrieben wird und kein oeffentlich erreichbarer Server vorgesehen ist, ist kein oeffentliches TLS-Zertifikat erforderlich. Die umgesetzten Massnahmen sind auf den lokalen Prototyp und dessen Schutzbedarf ausgelegt.
