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

# 7. Start the Backend Server

Start the local-Terminal (not bash-terminal) inside the `server` folder and start the server:

```bash
python -m uvicorn main:app --reload
```

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
