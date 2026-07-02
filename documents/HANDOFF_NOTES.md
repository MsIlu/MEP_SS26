# Handoff Notes

Stand: 02.07.2026

## Verified

- Backend syntax check passed with `python -m compileall`.
- Backend test suite passed: `238 passed`.
- Flutter static analysis passed: `flutter analyze`.
- Flutter test suite passed: `260 passed`.
- Backend run check passed on `127.0.0.1:8001` with a disposable SQLite database:
  `GET /health/server` returned `200 OK`, and `/docs` was reachable.
- Flutter web debug build passed with `flutter build web --debug`.

## Improvements In This Handoff Pass

- Prevented main profiles from being reclassified through profile patch requests.
- Enforced symptom severity range `1..10` at the API boundary.
- Enforced five-digit numeric postal codes for appointment search.
- Made PostgreSQL-only startup migrations skip non-PostgreSQL engines.
- Fixed DST-sensitive symptom diary import date arithmetic.
- Persisted frontend profile/session mutations after login and allowed explicit
  clearing of biological sex with `Keine Angabe`.
- Fixed `MyApp` partial dependency injection so tests do not null-crash the
  dependency scope.
- Added Android release permissions for backend networking, microphone, and
  Android 13+ notifications.
- Replaced generated/template frontend metadata and README content.
- Added `server/README.md` and refreshed selected architecture/test docs.

## Residual Notes

- Backend tests still emit deprecation warnings for Pydantic class-based config,
  FastAPI `on_event`, and naive `datetime.utcnow()` usage. These are not
  immediate failures but should be scheduled before dependency upgrades.
- `flutter build web --debug` reports a WebAssembly dry-run warning from
  `flutter_timezone 4.1.1`. The normal web build succeeds; WASM support would
  require a dependency update or package fix.
- Android package identifiers and release signing still need final product
  values before store distribution. The visible Android app label is now
  `Careena`.
- The local FHIR flow is a HAPI-FHIR adapter/test setup, not a productive
  external 116117 integration.
