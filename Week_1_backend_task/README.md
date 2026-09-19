# ZapTek Applications API

A FastAPI service for managing programme applications. The service provides CRUD operations, application filtering, status transitions, statistics, validation, structured errors, request logging, and an in-memory data store.

## Features

- Create, read, update, and withdraw applications
- Filter and paginate application lists
- Search by applicant information
- Accept or reject applications through controlled status transitions
- View aggregate statistics by status and university
- Reset demo data through a protected admin route
- OpenAPI documentation through Swagger UI

## Requirements

- Python 3.11 or newer
- pip

## Run locally

From `Week_1_backend_task`:

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API is available at `http://127.0.0.1:8000`. Interactive documentation is available at `http://127.0.0.1:8000/docs`.

## API routes

| Method | Route                       | Description                                     |
| ------ | --------------------------- | ----------------------------------------------- |
| GET    | `/health`                   | Service health check                            |
| GET    | `/applications`             | List applications with filtering and pagination |
| GET    | `/applications/{id}`        | Get one application                             |
| POST   | `/applications`             | Create an application                           |
| PATCH  | `/applications/{id}`        | Update application fields                       |
| PATCH  | `/applications/{id}/status` | Change an application status                    |
| DELETE | `/applications/{id}`        | Withdraw an application                         |
| GET    | `/applications/stats`       | Return application statistics                   |
| POST   | `/admin/reset`              | Restore the seed data                           |

Example requests:

```bash
curl "http://127.0.0.1:8000/applications?status=accepted&limit=5"
curl "http://127.0.0.1:8000/applications/3"
curl "http://127.0.0.1:8000/applications?university=knust"
```

The list endpoint supports `status`, `university`, `track`, `search`, `limit`, and `offset` query parameters.

## Project structure

```text
app/
  main.py                         FastAPI application and middleware
  models/application.py           Request and response schemas
  data/mock_data.py               In-memory application store
  services/application_service.py Business rules and data operations
  routers/applications.py         Application HTTP routes
  core/                           Configuration, security, and exceptions
tests/                             Automated API tests
.github/workflows/tests.yml       Continuous integration workflow
```

## Tests

Install the development dependencies and run the test suite from `Week_1_backend_task`:

```bash
pip install -r requirements-dev.txt
pytest
```

## Deployment

The included `render.yaml` configures deployment on Render. The service starts with:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Configure `ADMIN_RESET_TOKEN`, `ALLOWED_HOSTS`, and `CORS_ALLOWED_ORIGINS` through the deployment environment when required.

## Current limitations

- Data is stored in memory and resets when the process restarts.
- The service is intended for a single process while using the mock store.
- The mock store should be replaced with a transactional database for production use.
