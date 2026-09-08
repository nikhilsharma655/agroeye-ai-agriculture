FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

# Build context is the project root (see docker-compose.yml) so that the
# ml/ folder — a sibling of backend/, not inside it — can also be copied in.
# That means every COPY source here must be prefixed with backend/.
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

# The ml/ package (models, inference code) is copied in from the project
# root at build time via the docker-compose build context.
COPY ml /ml

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
