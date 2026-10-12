# Co-so-sys

Community Sound System Governance is a Flask application for community
decision-making and administration. It includes member accounts, proposals and
voting, real-time community chat, scheduled facility or equipment use, and a
mock treasury ledger. Application data is stored in SQLite.

## Requirements

- Python 3.10 or newer recommended
- `pip`

`requirements.txt` is currently empty. Install the runtime dependencies
explicitly:

```bash
python -m venv .venv
```

Activate the virtual environment:

```bash
# Linux/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

Then install the dependencies:

```bash
python -m pip install Flask Flask-SocketIO python-dotenv
```

## Configuration

The application loads `SECRET_KEY` from a `.env` file in the project root.
Create the file with a long, private random value:

```dotenv
SECRET_KEY=replace-this-with-a-private-random-value
```

Keep this value private and do not commit `.env`. Flask uses it to secure login
sessions.

## Database

The application database is `database/sound_system.sqlite3`, and its schema is
defined in `database/schema.sql`. To create the database tables, run this from
the project root:

```bash
python -m database.db
```

Initialization uses `CREATE TABLE IF NOT EXISTS`; it does not erase existing
data or migrate existing tables.

## Run the application

From the project root, with the virtual environment activated and `.env`
configured, run:

```bash
python run.py
```

Open [http://127.0.0.1:5000/](http://127.0.0.1:5000/) in your browser. Create an
account using the Sign Up page and then log in. Scheduling a system use requires
an authenticated session.

## Main pages

| URL | Description |
| --- | --- |
| `/` | Governance overview |
| `/proposals` | Browse and submit proposals |
| `/members` | Browse members and invite members |
| `/treasury` | View mock accounts and transactions |
| `/chat` | Community chat |
| `/events` | Events page |
| `/uses` | Schedule and view system uses and fees |
| `/login` | Sign in |
| `/signup` | Create an account |

JSON endpoints are implemented in the backend route modules. They include
`/api/chat`, `/api/proposals`, `/api/treasury`, and `/api/users`.

## Optional mock treasury data

To seed demo transactions, run this from the project root:

```bash
python seed_treasury.py
```

The script creates a mock account if none exists, adds a 500 EUR deposit, then
adds several randomly generated transactions. Each run adds more transactions
and changes the account balance. Use it only with demo data.

## Project layout

```text
run.py                       Flask and Socket.IO application entry point
backend/                     Flask blueprints and route handlers
client/templates/            Jinja HTML templates
client/static/               CSS and browser-side JavaScript
database/db.py               SQLite connection and initialization helpers
database/schema.sql          Database table definitions
database/sound_system.sqlite3 Local SQLite database
seed_treasury.py             Optional mock treasury data seeder
```

## Development and deployment note

The treasury features use mock accounts and are for development and
demonstration, not real financial transactions. Before exposing the app to a
network or using real member or financial data, review authentication,
authorization, input validation, secret management, and production deployment
configuration.
