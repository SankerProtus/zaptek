# ZapTek Applications API

Week 1 individual backend task — **Backend Engineering With FastAPI (Team 2)**.

A complete CRUD API for programme applications, built on an in-memory mock
datastore instead of a database.

---

## Run it locally

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open **http://127.0.0.1:8000/docs** for the interactive Swagger UI.

---

## Project structure

```
app/
  main.py                        app instance, error handlers, request logging, meta routes
  models/application.py          Pydantic schemas + validators
  data/mock_data.py              the in-memory store (the only file that
                                 knows data lives in a list)
  services/application_service.py  all business logic
  routers/applications.py        HTTP layer — thin handlers
  core/exceptions.py             domain exceptions
tests/                           pytest suite — one file per route group
.github/workflows/tests.yml      CI: runs the suite on every push
```

The split between `routers/` and `services/` is the point of the whole
exercise. Route handlers parse the request, call a service, return a response.
When this project moves to PostgreSQL, only `data/` and parts of `services/`
change — the routes stay exactly as they are.

---

## Endpoints

| Method   | Path                        | Purpose                                   |
| -------- | --------------------------- | ----------------------------------------- |
| `GET`    | `/applications`             | List, with filtering and pagination       |
| `GET`    | `/applications/stats`       | Aggregate counts by status and university |
| `GET`    | `/applications/{id}`        | Fetch a single application                |
| `POST`   | `/applications`             | Submit a new application → `201`          |
| `PATCH`  | `/applications/{id}`        | Partial update                            |
| `PATCH`  | `/applications/{id}/status` | Accept or reject                          |
| `DELETE` | `/applications/{id}`        | Withdraw → `204`                          |
| `GET`    | `/health`                   | Health check (used by Render)             |
| `POST`   | `/admin/reset`              | Restore seed data — useful mid-demo       |

Query parameters on the list endpoint: `status`, `university`, `track`,
`search`, `limit` (1–100), `offset`.

```bash
curl "http://127.0.0.1:8000/applications?status=accepted&limit=5"
curl "http://127.0.0.1:8000/applications/3"
curl "http://127.0.0.1:8000/applications?university=knust"
```

---

## Design decisions worth defending

**Three schemas, not one.** `ApplicationCreate` has no `id`, no `status`, no
`submittedAt`. If the client could set `status`, an applicant could accept
themselves. `ApplicationUpdate` makes every field optional for PATCH.
`ApplicationResponse` carries the full record. One shared model would break all
three use cases at once.

**Status has its own endpoint.** Accepting someone is a different operation
from correcting a typo in their phone number. It has different rules — and
later, different permissions. `PATCH /applications/{id}/status` also enforces
a transition table: `pending → accepted/rejected`, `accepted → rejected`, and
`rejected` is terminal. A plain CRUD endpoint cannot express that.

**Phone numbers are normalised, not just validated.** `+233 24 556 7812`,
`233245567812` and `0245567812` all store as `0245567812`, so the same person
cannot slip through duplicate checks behind different formatting.

**Every read returns a deep copy.** With a list as your store, handing out the
dicts themselves lets a caller mutate your "database" by accident. This bug
does not exist with a real database, which makes it a good slide.

**IDs come from a counter, not `len()`.** The seed data starts at `id: 2` with
no `id: 1`, so `len(applications) + 1` collides on the very first insert. The
counter is seeded from the highest existing id.

**One error shape everywhere.** Including FastAPI's own 422:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "One or more fields are invalid.",
    "details": {
      "fields": [
        {
          "field": "body.phone",
          "message": "must be a 10-digit Ghanaian number starting with 0"
        }
      ]
    }
  }
}
```

Error codes in use: `VALIDATION_ERROR` (422), `APPLICATION_NOT_FOUND` (404),
`DUPLICATE_EMAIL` (409), `INVALID_STATUS_TRANSITION` (409), `INTERNAL_ERROR` (500).

---

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

54 tests, 95% coverage. They cover every route, every validation rule, the
full status-transition table, and — as regression tests, not just
demonstrations — the two mock-data bugs described above: id collisions and
shared references. `tests/conftest.py` resets the in-memory store before each
test, so tests never leak state into each other.

A GitHub Actions workflow (`.github/workflows/tests.yml`) runs this suite on
every push and pull request against `main`.

## Logging

Every request is tagged with a short id and logged with method, path, status
code, and duration:

```
9bc814dd-1f6a-4d6c-8a3c GET /applications/2 -> 200 (5.0ms)
```

The same id comes back in the `X-Request-ID` response header, so a specific
request reported by a user can be found in the logs rather than guessed at.

## Deploy to Render

1. Push this folder to a GitHub repo.
2. On [render.com](https://render.com) → **New** → **Web Service** → connect the repo.
3. Render reads `render.yaml` automatically. If you configure it manually instead:
   - **Runtime:** Python 3
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Health check path:** `/health`
   - Set `ADMIN_RESET_TOKEN` to a strong secret, `ALLOWED_HOSTS` to the public
     hostname, and `CORS_ALLOWED_ORIGINS` to the trusted frontend origins.
4. Deploy, then share the live docs URL: `https://<your-service>.onrender.com/docs`

**Two things to expect on the free tier.** The service sleeps after ~15 minutes
idle, so the first request after a nap takes 30–50 seconds — warn whoever is
reviewing it. And because the data lives in memory, every restart wipes your
writes back to the seed records. Both are consequences of the mock-data
approach, so mention them in your presentation rather than letting a reviewer
discover them.

---

## Known limitations

- No persistence — data resets on restart.
- Application routes are public by design; the destructive `/admin/reset` route
  requires the `X-Admin-Token` header and is disabled when no token is configured.
- CORS is deny-by-default. Configure `CORS_ALLOWED_ORIGINS` when a browser
  frontend needs cross-origin access.
- Single-process only. Render's free tier runs one worker, so the in-memory
  store is consistent, but scaling to two workers would give each its own copy.
- Duplicate-email checking is a linear scan — fine at four records, wrong at
  forty thousand. A database index is the real answer.
- The mock store is process-local and should be replaced with a transactional
  database before running multiple workers or handling production traffic.
