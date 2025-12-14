FROM python:3.14-slim-trixie AS base
ARG SERVICE=gamemaster


FROM base AS build-prod
WORKDIR /app
COPY --from=docker.io/astral/uv:latest /uv /uvx /bin/
RUN --mount=type=cache,id=${SERVICE}-build-prod-uv,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-managed-python --no-dev


FROM build-prod AS build-test
RUN --mount=type=cache,id=${SERVICE}-build-test-uv,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-managed-python


FROM base AS prod
RUN addgroup --system app && adduser --system --ingroup app app
WORKDIR /app
RUN --mount=type=cache,id=${SERVICE}-runner-apt,target=/var/cache/apt \
    apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gettext \
    netcat-openbsd \
    postgresql-client \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
COPY ./docker/entrypoint.sh ./pyproject.toml ./manage.py /app/
COPY ./app/ /app/app/
COPY --from=build-prod /app/.venv /app/.venv
ENV DJANGO_SETTINGS_MODULE=app.settings \
    DJANGO_CONFIGURATION=Development \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
RUN python manage.py makemessages --all --exclude .venv && \
    python manage.py compilemessages --exclude .venv && \
    python manage.py collectstatic --noinput
EXPOSE 8000
ENTRYPOINT ["/app/entrypoint.sh"]
USER app
CMD ["uvicorn", "--app-dir", "/app/", "app.asgi:application", "--host", "0.0.0.0", "--port", "8000"]


FROM prod AS test
COPY --from=build-test /app/.venv /app/.venv
COPY ./tests/ /app/tests/
ENV DJANGO_CONFIGURATION=Testing
CMD ["tail", "-f", "/dev/null"]


FROM prod AS dev
ENV DJANGO_CONFIGURATION=Development
CMD ["uvicorn", "--app-dir", "/app/", "app.asgi:application", "--host", "0.0.0.0", "--port", "8000", "--reload"]
