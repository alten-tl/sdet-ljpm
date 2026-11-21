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
