# MEP_SS26 – Setup Guide
Author: Ilu

## 1. Requirements

Please install the following software before starting the project.

### Required Software

* Python 3.12 (recommended)
* Flutter from the stable channel
* Docker Desktop with Docker Compose v2
* Git
* Plugin Docker in your IDE

### Windows Users

Docker Desktop usually requires:

* WSL2
* Ubuntu (recommended)


---

(You can skip step 2 - "Clone the Repository", if you have the repository and it is up to date)

---

# 2. Clone the Repository

Clone the repository:

```bash
git clone <repository-url>
cd MEP_SS26
```

Or pull the newest version:

```bash
git pull
```

---

# 3. Start Docker Desktop

Make sure Docker Desktop is running before starting the database.

Verify the Docker installation:

```bash
docker --version
docker compose version
```

---

# 4. Add the `.env` File

Create `.env` in the main project folder. You can copy `.env.example` and adjust its values.

Example content for the local PostgreSQL container:

```env
LITELLM_BASE_URL=YOUR_URL
LITELLM_API_KEY=YOUR_API_KEY
LITELLM_MODEL=medgemma:27b

DATABASE_URL=postgresql+psycopg://mep_user:mep_password@127.0.0.1:5433/mep_server
SECRET_KEY=REPLACE_WITH_A_LONG_RANDOM_VALUE
SQL_ECHO=false

FHIR_BASE_URL=http://localhost:8080/fhir
FHIR_TIMEOUT_SECONDS=5
```

### ⚠️ Warning

```text
The `.env` file contains sensitive information.
Do NOT push the `.env` file to GitHub.
The required API keys are shared separately within the team.
```
---

# 5. Start PostgreSQL with Docker

Inside the main project folder, run:

```bash
docker compose up -d postgres
```

This starts the PostgreSQL database container.

Check the running services:

```bash
docker compose ps
```

### Start the Local FHIR Server

```bash
docker compose up -d fhir-server
```

The HAPI FHIR test server is then available at `http://localhost:8080/fhir`.

---

# 6. Install Python Dependencies

Go to the server folder:

```bash
cd server
```

Creating a virtual environment is recommended:

```bash
python -m venv .venv
```

Activate it with `.venv\Scripts\Activate.ps1` in PowerShell, `source .venv/Scripts/activate` in Git Bash on Windows, or `source .venv/bin/activate` on macOS/Linux.

Install all required packages:

```bash
python -m pip install -r requirements.txt
```

---

# 7. Start the Backend Server

Inside the `server` folder, start the server:

```bash
python -m uvicorn main:app --reload
```

Useful URLs:

* API: `http://localhost:8000`
* Swagger UI: `http://localhost:8000/docs`
* Server health: `http://localhost:8000/health/server`
* LLM health: `http://localhost:8000/health/llm`
* Simulierter FHIR Server: http://localhost:8000/fhir-simulator

---

# 8. Verify the Database Connection

Open PostgreSQL in Docker:

```bash
docker exec -it mep_postgres psql -U mep_user -d mep_server
```

To show all tables, use:

```sql
\dt
```

To exit PostgreSQL, use:

```sql
\q
```

---

# 9. Start the Flutter Application

Open a second terminal in the project root:

```bash
cd app1
flutter pub get
flutter run -d chrome
```

The application uses `http://localhost:8000` on web, desktop, and the iOS simulator. The Android emulator automatically uses `http://10.0.2.2:8000`.

For a physical device or another backend address, use:

```bash
flutter run --dart-define=API_BASE_URL=http://YOUR_COMPUTER_IP:8000
```

---

# 10. Run Tests

Backend tests from the `server` folder:

```bash
python -m pytest tests -q
```

Frontend tests from the `app1` folder:

```bash
flutter analyze
flutter test
```

---

# 11. Stop Docker

To stop the services:

```bash
docker compose down
```

---

# 12. Common Issues

## Docker command not found

Make sure Docker Desktop is installed and running.

---

## Port already in use

The project uses:

* `5433` for PostgreSQL
* `8000` for FastAPI
* `8080` for HAPI FHIR

Stop the conflicting service or adjust the corresponding configuration.

---

## Backend cannot connect to the database

Check:

* Docker container is running
* `.env` exists
* `DATABASE_URL` is correct and uses port `5433`
* PostgreSQL container started successfully

---

## Flutter cannot connect to the backend

Check:

* `http://localhost:8000/health/server` is reachable
* the Android emulator uses `10.0.2.2` instead of `localhost`
* a physical device uses the development computer's LAN IP
* firewall and network settings allow connections to port `8000`

---

# Project Structure

```text
MEP_SS26/
├── .github/
├── app1/
│   ├── lib/
│   └── test/
├── documents/
├── server/
│   ├── careena4/
│   ├── database/
│   ├── tests/
│   ├── main.py
│   └── requirements.txt
├── .env.example
├── docker-compose.yml
├── README.md
└── SETUP.md
```

---

# Database Architecture

## `database/models.py`

Defines the application tables using SQLModel.

## `database/connection.py`

Handles:

* PostgreSQL connection
* table creation and compatibility migrations
* database sessions

## `main.py`

Starts the FastAPI backend and initializes the database.
