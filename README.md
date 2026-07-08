# TaskDesk — Flask + MySQL Task Manager

A task manager: Flask backend (using `mysql.connector` with a cursor for
every query), a MySQL database, and a vanilla JS frontend that talks to a
JSON API for live add / edit / delete without page reloads. Any registered
user can log in.

## 1. Install dependencies

```bash
pip install -r requirements.txt
```

## 2. Create the database

```bash
mysql -u root -p < schema.sql
```

This creates the `taskmanager` database with a `users` table and a `tasks`
table.

> Already ran an older version of this project? That schema added an
> `is_admin` column that's no longer used. It's harmless to leave in place,
> or you can drop it with:
> `ALTER TABLE users DROP COLUMN is_admin;`

## 3. Set your MySQL password

Open `app.py` and replace the placeholder:

```python
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "password",   # <-- put your real MySQL password here
    "database": "taskmanager",
}
```

## 4. Run the app

```bash
python app.py
```

Visit `http://127.0.0.1:5000`, register an account, then log in with it.

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
├── app.py              # Flask app + JSON API
├── schema.sql            # MySQL schema
├── requirements.txt
├── templates/
│   ├── login.html
│   ├── register.html
│   └── dashboard.html
└── static/
    ├── css/style.css
    └── js/script.js
```
