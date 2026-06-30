# Reporting Stack Integration

Connects the Malawi OpenLMIS database to the [SolDevelo reporting stack](https://github.com/OpenLMIS/openlmis-reporting) via CDC (Debezium → Kafka → ClickHouse → dbt → Superset).

## Quick start

```bash
# 1. Start mw-distro with the reporting overlay
docker compose -f docker-compose.dev.yml -f docker-compose.reporting-stack.yml up -d

# 2. Start the reporting stack (separate repo)
cd /path/to/openlmis-reporting
cp /path/to/env.mw-distro .env   # see "Environment switching" below
make up
make setup
```

**Important:** Always include both compose files. Using only `docker-compose.dev.yml` starts the original PG 9.6 database without CDC support. Using only `docker-compose.reporting-stack.yml` won't work — it's an overlay, not standalone.

## Why `docker-compose.dev.yml`, not `docker-compose.yml`

The production compose (`docker-compose.yml`) does **not** include a `db` service — it expects an external, separately hosted PostgreSQL. The dev compose (`docker-compose.dev.yml`) adds a local `db` service with demo data seeding, which is what we need for local testing.

The reporting-stack overlay overrides the dev compose's `db` service (PG 9.6 → PG 14 with PostGIS and logical replication). For production deployments where the database is external, you would not need the DB image override — only the `reporting-shared` network and the CDC init.

## What the overlay does

| Change | Why |
|---|---|
| Overrides `db` image to `postgis/postgis:14-3.4-alpine` | PG 9.6 lacks `pgoutput` (required by Debezium). PG 14 has it built in. |
| Adds `wal_level=logical` and replication settings | Enables CDC logical replication. |
| Sets `password_encryption=md5` | OpenLMIS Java services use an older JDBC driver that doesn't support PG 14's default `scram-sha-256`. |
| Creates `reporting-shared` network with `olmis-db` alias | The reporting stack's `kafka-connect` joins this network to reach the database. |
| Runs `reporting-stack-init` container | Waits for Flyway migrations, then creates the CDC publication, heartbeat table, and replication role. |
| Installs `uuid-ossp`, `pgcrypto`, `postgis` extensions | Required by OpenLMIS Flyway migrations but not included in the vanilla PostGIS image. |
| Replaces `ftp` service | The original `hauptmedia/proftpd` image is no longer available on Docker Hub. |

## Fresh database required

The overlay uses PG 14 which is incompatible with PG 9.6 data directories. If you previously ran mw-distro without the overlay, wipe volumes first:

```bash
docker compose -f docker-compose.dev.yml -f docker-compose.reporting-stack.yml down -v
```

## Environment switching (reporting stack side)

The reporting stack `.env` must point to the correct distro. Pre-configured env files are saved in the workspace:

```bash
cd /path/to/openlmis-reporting

# Switch to mw-distro
cp /path/to/env.mw-distro .env
make reset && make up && make setup

# Switch back to ref-distro
cp /path/to/env.ref-distro .env
make reset && make up && make setup
```

Key differences in the mw-distro env: Malawi extension is enabled (`ANALYTICS_EXTENSIONS_PATHS=examples/olmis-analytics-malawi`), Airflow port is 8081 (avoids conflict with mw-distro's nginx on 8080).

## Files

| File | Purpose |
|---|---|
| `init-db.sql` | CDC publication (9 tables), heartbeat table, replication role |
| `wait-and-init.sh` | Waits for PG + Flyway, then runs init-db.sql |
| `init-extensions.sql` | Creates PG extensions needed by OpenLMIS migrations |
