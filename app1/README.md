# Careena Flutter Frontend

This directory contains the Flutter application for Careena, the MedBitAid
prototype for guided medical first assessment.

## Responsibilities

- onboarding, login, registration, profile selection, and settings
- guided Careena chat with backend sessions and structured reply chips
- warning and recommendation views driven by backend safety decisions
- symptom diary, medication plan, appointments, document storage, and PDF export
- local persistence for frontend session state and selected profile settings

The frontend does not make medical safety decisions. It displays data returned
by the FastAPI backend and sends user edits, selected profiles, diary entries,
and recommendation actions back through API services.

## Backend URL

By default the app uses:

- `http://localhost:8000` on web, desktop, and iOS simulator
- `http://10.0.2.2:8000` on Android emulator

Override the backend for a physical device or deployed environment:

```bash
flutter run --dart-define=API_BASE_URL=http://YOUR_HOST:8000
```

## Local Run

Start the backend first, then run:

```bash
flutter pub get
flutter run -d chrome
```

For Android release builds, the main manifest declares network, microphone, and
notification permissions. Android 13+ still requires runtime notification
permission before medication reminders can be shown.

## Tests

```bash
flutter analyze
flutter test
```

The frontend test matrix is documented in
`../documents/testing/Testfaelle_Frontend.md`.

## Structure

- `lib/app`: composition root, shared dependency scope, restored-page handling
- `lib/core`: configuration, API client, themes, shared widgets, speech service
- `lib/features`: screen-level feature modules such as chat, auth, home,
  settings, documents, appointments, medication plan, symptom diary, warnings,
  calendar overview, app guide, profiles, and recommendation export
- `test`: unit and widget tests grouped by feature
