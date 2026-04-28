# SmartFin Server

Django REST API server that receives sensor data from SmartFin surfboard devices (Apple Watch) and serves it to a frontend.

---

## Prerequisites

- Python 3.12+
- PostgreSQL 14+ **or** Docker + Docker Compose

---

## Running with Docker (recommended)

The easiest path — no local PostgreSQL install needed.

**1. Copy and configure the environment file**

```bash
cp .env.example .env   # or just edit .env directly
```

The defaults in `.env` work out of the box with Docker Compose. Change `SECRET_KEY` and `DB_PASSWORD` before deploying to production.

**2. Start everything**

```bash
docker compose up --build
```

This starts a PostgreSQL 16 container and the Django app on port `8000`. Migrations run automatically on startup.

**3. Verify it's running**

```
http://localhost:8000/admin/
```

To stop: `docker compose down`. To wipe the database volume: `docker compose down -v`.

---

## Running locally (manual setup)

**1. Createpwd and activate a virtual environment**

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows (PowerShell)
venv\Scripts\Activate.ps1

# Windows (CMD)
venv\Scripts\activate.bat
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Configure environment**

Edit `.env` and point `DB_HOST` at your local PostgreSQL instance:

```
DB_NAME=smartfin_db
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=change-this-in-production
DEBUG=True
```

**4. Create the database** (if it doesn't exist yet)

```bash
psql -U postgres -c "CREATE DATABASE smartfin_db;"
```

**5. Run migrations**

```bash
python manage.py migrate
```

**6. Create a superuser** (to access `/admin/`)

```bash
python manage.py createsuperuser
```

**7. Start the development server**

```bash
python manage.py runserver
```

The API is now available at `http://localhost:8000`.

---

## API Reference

All sensor endpoints require a Bearer token in the `Authorization` header:

```
Authorization: Token <your-token>
```

### Auth

#### Register a new user
```
POST /api/auth/register
```
```json
{
  "username": "surfer_john",
  "password": "securepassword"
}
```
Response `201`:
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user_id": 1,
  "username": "surfer_john"
}
```

#### Login
```
POST /api/auth/login
```
```json
{
  "username": "surfer_john",
  "password": "securepassword"
}
```
Response `200`:
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user_id": 1,
  "username": "surfer_john"
}
```

---

### Sensor Data Upload (Apple Watch → Server)

```
POST /api/upload
Authorization: Token <token>
Content-Type: application/json
```

**Ensemble 01** — Temperature + water status only (low power):
```json
{
  "ensemble_type": "01",
  "temperature": 19.4,
  "water_status": "in_water"
}
```

**Ensemble 11** — Full set (temperature, water, 9-axis IMU, GPS):
```json
{
  "ensemble_type": "11",
  "temperature": 19.4,
  "water_status": "in_water",
  "gps": "32.81,-117.23",
  "imu": {
    "accel": [0.1, -0.2, 9.8],
    "gyro": [0.01, -0.03, 0.02],
    "mag": [23.1, -4.5, 41.2]
  }
}
```

**Ensemble 12** — High data rate IMU only:
```json
{
  "ensemble_type": "12",
  "imu": [[0.1, -0.2, 9.8], [0.11, -0.21, 9.79]]
}
```

Response `201`:
```json
{ "status": "success", "id": 42 }
```

---

### Fetch User Data (Server → Frontend)

```
GET /api/data/
Authorization: Token <token>
```

**Optional query parameters:**

| Param | Description | Example |
|-------|-------------|---------|
| `type` | Filter by ensemble type | `?type=11` |
| `from` | Readings on or after date | `?from=2026-04-01` |
| `to` | Readings on or before date | `?to=2026-04-28` |
| `limit` | Page size (default 100, max 1000) | `?limit=50` |
| `offset` | Pagination offset (default 0) | `?offset=50` |

Response `200`:
```json
{
  "user": "surfer_john",
  "total_readings": 142,
  "limit": 100,
  "offset": 0,
  "readings": [
    {
      "id": 42,
      "ensemble_type": "11",
      "ensemble_type_label": "Full Set (Temp, Water, 9-axis IMU, GPS)",
      "temperature": 19.4,
      "water_status": "in_water",
      "geo_coordinates": "32.81,-117.23",
      "imu_data": { "accel": [0.1, -0.2, 9.8], "gyro": [0.01, -0.03, 0.02], "mag": [23.1, -4.5, 41.2] },
      "timestamp": "2026-04-28T10:32:00+00:00"
    }
  ]
}
```

---

## Django Admin

Visit `http://localhost:8000/admin/` and log in with your superuser credentials.

- Browse and filter all `EnsembleReading` records
- View the temperature heatmap at `/admin/smartfin_server/ensemblereading/heatmap/`

---

## Seed Mock Data

To populate the database with 50 sample readings (San Diego area):

```bash
python seed_mock_data.py
```

---

## Project Structure

```
smartfin_server/
├── smartfin_server/
│   ├── models.py        # EnsembleReading and Video models
│   ├── views.py         # API endpoints
│   ├── urls.py          # URL routing
│   ├── settings.py      # Django configuration
│   ├── admin.py         # Admin interface + heatmap view
│   └── migrations/      # Database migrations
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env
```
