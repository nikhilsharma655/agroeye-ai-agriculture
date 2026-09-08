#!/bin/sh
# Applies any pending Alembic migrations, then starts the API server.
# This is the production-safe schema path; app.database.init_db()'s
# create_all() is only a dev-convenience fallback and never runs instead of
# this in Docker.
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Starting AgroEye API..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
