# MEP_SS26 – Setup Guide
Author: Ilu

## 1. Requirements

Please install the following software before starting the project.

### Required Software

* Python 3.12+ (recommended)
* Docker Desktop
* Git
* Plugin Docker in your IDE

### Windows Users

Docker Desktop usually requires:

* WSL2
* Ubuntu (recommended)


---

(You can skip step 2 - "Clone the Repository", if you have the repository and is up to date)

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

Verify Docker installation in bash-terminal:

```bash
docker --version
```

---

# 4. Add in the .env File

Add in the `.env` file, which is inside the main project folder, the database_URL:

```text
MEP_SS26/.env
```

Example content:

```env
LITELLM_BASE_URL=YOUR_URL
LITELLM_API_KEY=YOUR_API_KEY
LITELLM_MODEL=YOUR_MODEL

DATABASE_URL= Database_URL
```

### ⚠️ Warning

```text
The `.env` file contains sensitive information.
Do NOT push the `.env` file to GitHub.
The required `DATABASE_URL`, usernames, passwords, 
and API keys are shared separately within the team (e.g. Discord - Channel "code-schnipsel"; pinned).
```
---

# 5. Start PostgreSQL with Docker

Inside the main project folder (C:/StudioProjects/MEP_SS26) open the bash-Terminal and insert the following code:

```bash
docker compose up -d
```

This starts the PostgreSQL database container.

Check running (also bash-Terminal):

```bash
docker ps
```

---

# 6. Install Python Dependencies

Start the local-terminal (not bash-Terminal) and go into the server-folder:

```bash
cd server
```

Install all required packages:

```bash
pip install -r requirements.txt
```

---

# 7. Start Backend and Frontend

The normal local web setup uses HTTPS on the same computer. Use HTTP only as a
fallback if HTTPS does not work locally.

## 7.1 Create a Trusted Local HTTPS Certificate

This is required for the normal HTTPS setup.

Install `mkcert` once on your operating system:

Windows:

```powershell
winget install FiloSottile.mkcert
```

Close and reopen PowerShell after the installation, then check:

```powershell
mkcert --version
```

If PowerShell still does not recognize `mkcert`, find the installed executable:

```powershell
Get-ChildItem "$env:LOCALAPPDATA\Microsoft\WinGet\Packages" -Recurse -Filter mkcert.exe
```

Use the shown path directly in PowerShell. Replace the example path with the
path printed by the previous command:

```powershell
$mkcert = "C:\Users\<YOUR_USER>\AppData\Local\Microsoft\WinGet\Packages\FiloSottile.mkcert_Microsoft.Winget.Source_8wekyb3d8bbwe\mkcert.exe"

& $mkcert --version
```

If this works, use `& $mkcert` instead of `mkcert` in the commands below. For
example:

```powershell
& $mkcert -install
```

Important: `$mkcert` is only available in the same PowerShell session where it
was set. If you close PowerShell or open a new terminal, set `$mkcert` again
before running commands such as `& $mkcert -install`.

If `& $mkcert --version` works, continue with `& $mkcert` for the mkcert
commands in this setup.

macOS with Homebrew:

```bash
brew install mkcert
```

Linux, for example Debian/Ubuntu:

```bash
sudo apt install mkcert libnss3-tools
```

Install the local certificate authority into the operating system trust store.
Chrome uses the system trust store on Windows and macOS. On Linux, `mkcert`
also uses `libnss3-tools` so browsers such as Chrome/Chromium and Firefox can
trust the local certificate:

```bash
mkcert -install
```

On Windows, a security confirmation dialog can appear during `mkcert -install`.
This is expected: `mkcert` creates a local development certificate authority and
adds it to the trusted certificate store. Confirm it if the dialog refers to the
mkcert local development CA.

If `mkcert -install` prints a Java/keytool warning such as `Access is denied`
for a Java `cacerts` file, Chrome support can still be installed correctly. For
Flutter Web in Chrome, the important message is:

```text
The local CA is now installed in the system trust store!
```

The Java warning only means that mkcert could not add the local CA to Java's own
certificate store. This is usually not required for the local Flutter Web and
FastAPI setup.

Create the backend certificate inside the `server` folder:

```bash
cd server
mkdir certs
mkcert -key-file certs/localhost-key.pem -cert-file certs/localhost-cert.pem localhost 127.0.0.1 10.0.2.2
```

If the `certs` folder already exists, skip `mkdir certs`.

Restart Chrome after installing the certificate authority. You can also open
`chrome://restart`.

## 7.2 Start with HTTPS on the Same Computer

Start the backend inside the `server` folder:

```bash
python -m uvicorn main:app --reload --ssl-keyfile certs/localhost-key.pem --ssl-certfile certs/localhost-cert.pem
```

Start Flutter inside the `app1` folder:

```bash
cd app1
flutter run --web-hostname localhost --web-port 3000 --web-tls-cert-path "../server/certs/localhost-cert.pem" --web-tls-cert-key-path "../server/certs/localhost-key.pem"
```

Open:

```text
https://localhost:3000
```

## 7.3 HTTP Fallback for Local Development

Use this only if HTTPS does not work locally.

Start the backend inside the `server` folder:

```bash
python -m uvicorn main:app --reload
```

Start Flutter inside the `app1` folder:

```bash
cd app1
flutter run --dart-define=BACKEND_USE_HTTPS=false
```

## 7.4 Physical Phone Note

If you test on a physical phone, `localhost` does not point to your computer.
Use your computer's IPv4 address instead, start the backend with
`--host 0.0.0.0`, and run Flutter with
`--dart-define=API_BASE_URL=http://<YOUR_IPV4_ADDRESS>:8000`.

---

# 8. Verify Database Connection

Open the bash-terminal to start PostgreSQL in docker:

```bash
docker exec -it mep_postgres psql -U mep_user -d mep_server
```

To show all tables, use the following code:

```sql
\dt
```

To exit PostgreSQL, use the following code:

```sql
\q
```

---

# 9. Stop Docker

To stop the database:

```bash
docker compose down
```

---

# 10. Common Issues

## Docker command not found

Make sure Docker Desktop is installed and running.

---

## Port already in use

The project uses:

```text
5433
```

for PostgreSQL to avoid conflicts with local PostgreSQL installations.

---

## Backend cannot connect to database

Check:

* Docker container is running
* `.env` exists
* `DATABASE_URL` is correct
* PostgreSQL container started successfully

---

# Project Structure (on 15.05.2026)

```text
MEP_SS26/
├── .github/
├── app1/
├── documents
├── server/
│   ├── database/
│   │    ├── __init__.py
│   │    ├── connection.py
│   │    └── models.py
│   ├── docs/
│   ├── models/
│   ├── red_flags/
│   ├── config.py
│   ├── main.py
│   ├── medical_rules.py
│   ├── requirements.txt
│   └── topic_filter.py
├── .env
├── .env.example
├── .gitignore
├── docker-compose.yml
├── README.md
└── SETUP.md
```

---

# Database Architecture

## models.py

Defines database tables using SQLModel.

## connection.py

Handles:

* PostgreSQL connection
* table creation
* database sessions

## main.py

Starts the FastAPI backend and initializes the database.
