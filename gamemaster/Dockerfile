FROM python:3.12.0-alpine3.18 AS builder

WORKDIR /app

RUN apk add --no-cache gcc musl-dev postgresql-dev

COPY requirements.txt .

RUN --mount=type=cache,target=/root/.cache \
    python -m pip install -r requirements.txt

FROM python:3.12.0-alpine3.18

RUN apk add --no-cache postgresql

RUN python -m pip install uvicorn

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY ./entrypoint.sh /app/

WORKDIR /app

EXPOSE 8000
ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
