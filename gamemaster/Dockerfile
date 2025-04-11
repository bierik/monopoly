FROM python:3.13-slim-bookworm AS poetry
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libffi-dev libpq-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
RUN --mount=type=cache,id=poetry-pip,target=/root/.cache \
    python -m pip install -U --no-cache-dir poetry
COPY poetry.lock pyproject.toml /app/
RUN --mount=type=cache,id=poetry,target=/root/.cache \
    poetry self add poetry-plugin-export && \
    poetry lock && \
    poetry export -o requirements.txt --without-hashes

FROM python:3.13-alpine3.21 AS builder

WORKDIR /app

RUN apk add --no-cache gcc build-base libpq-dev postgresql-dev

COPY --from=poetry /app/requirements.txt .

RUN --mount=type=cache,target=/root/.cache \
    python -m pip install -r requirements.txt

FROM python:3.13-alpine3.21

RUN apk add --no-cache libpq postgresql

RUN python -m pip install uvicorn

COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY ./entrypoint.sh /app/

WORKDIR /app

EXPOSE 8000
ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
