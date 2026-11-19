# Group5F26-SENG71000-Backend

All Repositories:
- https://github.com/RajdeepC-20107/Group5F26-SENG71000-AndroidFrontend
- https://github.com/RajdeepC-20107/Group5F26-SENG71000-iOSFrontend
- **https://github.com/RajdeepC-20107/Group5F26-SENG71000-Backend**


# DriverKarma Backend

FastAPI backend with a Supabase (PostgreSQL) database for the driver scoring app.

## Requirements
- Python 3.10 or newer
- A Supabase project with the `Users`, `DriverScores`, `Tracks` and `Penalties` tables
- The project's `SUPABASE_URL` and secret key (ask a team member; never commit them)

## Python packages
Listed in `requirements.txt` and installed in step 2 below.

| Package             | Purpose                                 |
|---------------------|-----------------------------------------|
| `fastapi`           | Web framework for the API               |
| `uvicorn[standard]` | Server that runs the FastAPI app        |
| `supabase`          | Python client for the Supabase database |
| `python-dotenv`     | Loads secrets from the `.env` file      |
| `bcrypt`            | Hashes and checks passwords             |
| `pytest`            | Runs normal and endpoint tests          |

## Setup

### 1. Create and activate a virtual environment

Run this from the project folder. Pick your operating system.

**Windows (PowerShell)**
```powershell
python -m venv venv
venv\Scripts\activate
```
If PowerShell says scripts are disabled, run
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, then activate again.

**Windows (Command Prompt)**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**macOS**
```bash
python3 -m venv venv
source venv/bin/activate
```
If `python3` isn't found, install Python from python.org or with `brew install python`.

**Linux**
```bash
python3 -m venv venv
source venv/bin/activate
```
On Debian/Ubuntu, if you get an error about `ensurepip` or `venv`, install it first:
`sudo apt install python3-venv python3-pip`

When it works, your prompt starts with `(venv)`. Run `deactivate` to leave the environment.

### 2. Install the packages
With the environment active (same command on every OS):
```bash
pip install -r requirements.txt
```

### 3. Configure secrets
Copy the example file and fill in the real values.

macOS / Linux:
```bash
cp .env.example .env
```
Windows (PowerShell):
```powershell
copy .env.example .env
```

Then edit `.env`:
```
SUPABASE_URL=https://<your-project-ref>.supabase.co
SUPABASE_SECRET_KEY=<your-secret-key>
```
- Get both from **Project Settings → API Keys** in the Supabase dashboard.
- The URL must end at `.supabase.co`, with no extra path such as `/rest/v1/`.
- No quotes and no spaces around `=`.
- `.env` is listed in `.gitignore`. Never commit it or paste the key in chat or screenshots.

### 4. Run the server
```bash
python -m uvicorn main:app --reload
```
Open http://127.0.0.1:8000/docs in a browser to test the endpoints.
Press `Ctrl+C` in the terminal to stop the server. Restart it after changing `.env`.

> Without activating the environment, call the environment's Python directly:
> `venv/bin/python -m uvicorn main:app --reload` (macOS/Linux) or
> `venv\Scripts\python -m uvicorn main:app --reload` (Windows).

## Endpoints
| Method | Path | Description |
|---|---|---|
| POST | `/login` | Sign in with username or driver's license number and password |
| GET | `/users/{user_id}/scores` | A user's scores with tracks and penalties |
| POST | `/users/{user_id}/drives` | Upload a finished drive; the backend scores it and saves the track, score and penalties |

### Uploading a drive
The app sends the drive and the penalty events it detected. The backend calculates the score
(rules in `scoring.py`).
Times must include a timezone (e.g. `Z` for UTC), and every penalty must fall inside the drive.

```json
POST /users/1/drives
{
  "start_time": "2026-11-18T08:00:00Z",
  "end_time": "2026-11-18T08:30:00Z",
  "track_object": "tracks/sample.gpx.gz",
  "penalties": [
    {"occurred_at": "2026-11-18T08:10:00Z", "penalty_type": "hard_brake"}
  ]
}
```
Allowed `penalty_type` values: `hard_brake`, `hard_acceleration`, `sharp_turn`, `speeding`, `phone_use`.
`track_object` and `penalties` are optional.

Response (`201 Created`):
```json
{"score_id": 7, "track_id": 7, "score": 95, "scoring_notes": "1 harsh braking event", "profile_score": 81}
```
`profile_score` is the user's new average across all their drives.

## Troubleshooting

Below are some common errors that could happen on setup and how to fix them

| Problem | Fix |
|---|---|
| `getaddrinfo failed` or connection errors | `SUPABASE_URL` is wrong, still a placeholder, or you're offline |
| `KeyError: 'SUPABASE_URL'` | `.env` is missing or not in the project root |
| `Attribute "app" not found in module "main"` | `main.py` is empty, unsaved or in a different folder |
| `ModuleNotFoundError` | The environment isn't active, or `pip install -r requirements.txt` wasn't run |
| `Address already in use` | Another server is running. Stop it, or use `--port 8001` |
| `.env` changes have no effect | Restart the server, and check for old values in your shell with `echo $SUPABASE_URL` |
