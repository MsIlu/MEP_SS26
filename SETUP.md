# MEP_SS26 – Setup Guide
Author: Ilu

## 1. Requirements

Please install the following software before starting the project.

### Required Software

* Python 3.12+ (recommended)
* Docker Desktop
* Git

### Windows Users

Docker Desktop usually requires:

* WSL2
* Ubuntu (recommended)

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

Verify Docker installation:

```bash
docker --version
```

---

# 4. Create the .env File

Create a `.env` file inside the main project folder:

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
```Text
The `.env` file contains sensitive information. 
Do NOT push the `.env` file to GitHub.
The required `DATABASE_URL`, usernames, passwords, and API keys are shared separately within the team (e.g. Discord). 
```
---

# 5. Start PostgreSQL with Docker

Inside the main project folder (C:/StudioProjects/MEP_SS26) open the bash-Terminal and insert the following code:

```bash
docker compose up -d
```

This starts the PostgreSQL database container.

Check running containers:

```bash
docker ps
```

---

# 6. Install Python Dependencies

Go into the backend folder:

```bash
cd server
```

Install all required packages:

```bash
pip install -r requirements.txt
```

---

# 7. Start the Backend Server

Inside the `server` folder:

```bash
python -m uvicorn main:app --reload
```

---

# 8. Verify Database Connection

Open PostgreSQL inside Docker:

```bash
docker exec -it mep_postgres psql -U username -d mep_server
```

Show all tables:

```sql
\dt
```

Exit PostgreSQL:

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

# Project Structure

```text
MEP_SS26/
│
├── docker-compose.yml
├── .env
│
├── server/
│   ├── main.py
│   ├── database.py
│   ├── db_models.py
│   ├── requirements.txt
│
└── frontend/
```

---

# Database Architecture

## db_models.py

Defines database tables using SQLModel.

## database.py

Handles:

* PostgreSQL connection
* table creation
* database sessions

## main.py

Starts the FastAPI backend and initializes the database.
