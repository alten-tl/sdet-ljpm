# Cloud AWS Appointments API

Local REST API for the Cloud AWS technical test. The project uses AWS SAM to define API Gateway and four AWS Lambda functions. PostgreSQL runs in Docker Compose. `sam local start-api` emulates API Gateway locally and runs Lambda functions in Docker containers.

## Architecture

`HTTP client -> API Gateway (SAM local) -> AWS Lambda function -> PostgreSQL (Docker)`

The local database network is `citas-network`. Lambda containers started by SAM must join that network by using `--docker-network citas-network`.

## Requirements

- Docker Desktop with Docker Compose.
- AWS SAM CLI.
- Git.
- PowerShell, Bash, or another terminal.

## Start PostgreSQL

```powershell
docker compose up -d db
docker compose ps
docker compose logs -f db
```

Wait until the database health status is `healthy`. The SQL schema and demo customer/vehicle are loaded on the first initialization of the PostgreSQL volume.

## Build Lambda functions

Run from the project root:

```powershell
sam validate
sam build --use-container
```

## Start the local API

Keep this terminal open:

```powershell
sam local start-api --port 3000 --docker-network citas-network --warm-containers eager
```

The local base URL is `http://127.0.0.1:3000`.

## Demo data

- Customer ID: `11111111-1111-1111-1111-111111111111`
- Vehicle ID: `22222222-2222-2222-2222-222222222222`

## API endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/appointments?date=YYYY-MM-DD` | List appointments for a date. Optional `status=HABILITADA` or `status=DESHABILITADA`. |
| POST | `/customers/{customerId}/appointments` | Create an appointment for a customer. |
| PUT | `/appointments/{appointmentId}` | Change an appointment date and time. |
| PATCH | `/appointments/{appointmentId}/cancel` | Disable an appointment and update `updated_at`. |

### Create appointment request

```json
{
  "date": "2027-01-15",
  "time": "10:30",
  "vehicle_id": "22222222-2222-2222-2222-222222222222",
  "comments": "Initial appointment"
}
```

### Reschedule appointment request

```json
{
  "date": "2027-01-15",
  "time": "11:30"
}
```

## Example API responses

The following examples were captured while testing the endpoints locally with Postman.

### Create appointment — `POST`

**Expected HTTP status:** `201 Created`

```json
{
  "message": "Appointment created successfully.",
  "data": {
    "id": "d44df93b-8dc2-4edd-93f5-7696fb7d3aca",
    "customer_id": "11111111-1111-1111-1111-111111111111",
    "vehicle_id": "22222222-2222-2222-2222-222222222222",
    "appointment_date": "2027-01-15",
    "appointment_time": "10:35:00",
    "created_at": "2026-11-21 08:01:31.718108+00:00",
    "updated_at": "2026-11-21 08:01:31.718108+00:00",
    "comments": "Initial appointment",
    "status": "HABILITADA"
  }
}
```

### Create appointment with an already reserved time — `POST`

**Expected HTTP status:** `409 Conflict`

The API rejects an appointment when an enabled appointment already reserves the same date and time.

```json
{
  "message": "The selected date and time are already reserved."
}
```

### List appointments by date — `GET`

**Expected HTTP status:** `200 OK`

Request example:

```text
GET /appointments?date=2027-01-15&status=HABILITADA
```

Response example:

```json
{
  "date": "2027-01-15",
  "count": 1,
  "data": [
    {
      "id": "e4ae1bdd-a16c-452a-8658-d0246c41784a",
      "customer_id": "11111111-1111-1111-1111-111111111111",
      "customer_name": "Alex Morgan",
      "vehicle_id": "22222222-2222-2222-2222-222222222222",
      "vehicle_plates": "ABC-123-A",
      "vehicle_model": "Honda Accord",
      "appointment_date": "2027-01-15",
      "appointment_time": "11:30:00",
      "created_at": "2026-11-21 07:47:19.793360+00:00",
      "updated_at": "2026-11-21 07:56:57.120844+00:00",
      "comments": "Initial appointment",
      "status": "HABILITADA"
    }
  ]
}
```

### Reschedule appointment — `PUT`

**Expected HTTP status:** `200 OK`

Response example:

```json
{
  "message": "Appointment rescheduled successfully.",
  "data": {
    "id": "e4ae1bdd-a16c-452a-8658-d0246c41784a",
    "customer_id": "11111111-1111-1111-1111-111111111111",
    "vehicle_id": "22222222-2222-2222-2222-222222222222",
    "appointment_date": "2027-01-15",
    "appointment_time": "11:30:00",
    "created_at": "2026-11-21 07:47:19.793360+00:00",
    "updated_at": "2026-11-21 07:56:57.120844+00:00",
    "comments": "Initial appointment",
    "status": "HABILITADA"
  }
}
```

### Cancel appointment — `PATCH`

**Expected HTTP status:** `200 OK`

The appointment remains in the database. Its status changes to `DESHABILITADA`, and `updated_at` is refreshed.

```json
{
  "message": "Appointment cancelled successfully.",
  "data": {
    "id": "e4ae1bdd-a16c-452a-8658-d0246c41784a",
    "customer_id": "11111111-1111-1111-1111-111111111111",
    "vehicle_id": "22222222-2222-2222-2222-222222222222",
    "appointment_date": "2027-01-15",
    "appointment_time": "11:30:00",
    "created_at": "2026-11-21 07:47:19.793360+00:00",
    "updated_at": "2026-11-21 08:00:06.749343+00:00",
    "comments": "Initial appointment",
    "status": "DESHABILITADA"
  }
}
```

## Database model

- One customer can have many appointments.
- One vehicle can be related to many appointments over time.
- Every appointment references one customer and one vehicle.
- An active appointment reserves its exact date/time. A partial unique index prevents two enabled appointments from using the same slot. Disabled appointments do not reserve the slot.

## Stop the services

Stop SAM with `Ctrl+C`, then run:

```powershell
docker compose down
```

The named PostgreSQL volume is preserved. To delete the database and all local data, run `docker compose down -v`.

## Important local-development note

`sam local start-api` is a local emulator; this project does not create AWS resources or deploy to an AWS account. The password in `template.yaml` is for local development only. Before a real AWS deployment, move database credentials to AWS Secrets Manager or another approved secret store and connect Lambda to a managed database or a properly networked database host.
