# TaskDesk — Flask + MySQL Task Manager

A task manager: Flask backend (using `mysql.connector` with a cursor for
every query), a MySQL database, and a vanilla JS frontend that talks to a
JSON API for live add / edit / delete without page reloads. Any registered
user can log in.

## 1. Install dependencies

```bash
pip install -r requirements.txt
```

## 2. Configure your connection

Connection details live in a `.env` file, so nothing needs to be hand-edited
in the code. A `.env` file is already included, pre-filled for MySQL running
on **port 3307** — you just need to add your MySQL password:

```
FLASK_SECRET_KEY=f5dcfbafb5c344223f9ffe45288684e65a1a49eb7d9881e430fab51197d4c750
MYSQL_HOST=localhost
MYSQL_PORT=3307
MYSQL_USER=root
MYSQL_PASSWORD=        <-- put your MySQL password here
MYSQL_DATABASE=taskmanager
```

Open `.env`, fill in `MYSQL_PASSWORD`, save it. `app.py` loads this file
automatically on startup via `python-dotenv`.

**If someone else runs this with MySQL on the default port (3306):**
copy `.env.example` to `.env` instead (it defaults to `MYSQL_PORT=3306`),
generate their own secret key, and fill in their own password:

```bash
cp .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"   # paste into FLASK_SECRET_KEY
```

`.env` is listed in `.gitignore` so it never gets committed — `.env.example`
is the shareable template.

## 3. Create the database

Point the `mysql` client at the same host/port you put in `.env`:

```bash
mysql -u root -p -h localhost -P 3307 < schema.sql
```

(use `-P 3306` if you're on the default port). This creates the
`taskmanager` database with a `users` table and a `tasks` table.

> Already ran an older version of this project? That schema used to add an
> `is_admin` column that's no longer used. Harmless to leave, or drop it
> with: `ALTER TABLE users DROP COLUMN is_admin;`

## 4. Run the app

```bash
python app.py
```

Visit `http://127.0.0.1:5000`, register an account, then log in with it.

## About the secret key

Flask requires a secret key to cryptographically sign session cookies —
that's what keeps you logged in between page loads; the app won't start a
session without one. A random one is already generated in `.env` for you.
If you ever need a new one:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
Paste the output into `FLASK_SECRET_KEY` in `.env`. Note: changing it logs
everyone out, since it invalidates existing session cookies.

## Login / register fields

- **Register**: username, email, password, confirm password.
- **Login**: username, email, password.
- Any account created through Register can log in immediately — there's no
  approval step.

## Task manager page

- Fields: Employee ID, Employee name, Task (dropdown of predefined task
  names, editable in `TASK_OPTIONS` in `app.py`), Completed (Yes/No
  dropdown).
- Full CRUD via `/api/tasks` (GET, POST, PUT `/api/tasks/<id>`, DELETE
  `/api/tasks/<id>`), all using `mysql.connector` cursors.
- Frontend: add, inline edit, delete, live search filter, and running
  totals (total / completed / pending) — all updated instantly via
  `fetch()` calls, no full-page reloads.

## Project structure

```
taskmanager/
├── app.py               # Flask app + JSON API
├── schema.sql            # MySQL schema
├── requirements.txt
├── .env                   # your real config (not committed)
├── .env.example           # template for others to copy
├── .gitignore
├── templates/
│   ├── login.html
│   ├── register.html
│   └── dashboard.html
└── static/
    ├── css/style.css
    └── js/script.js
```
