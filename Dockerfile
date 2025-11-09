ARG PYTHON_VERSION=3.13
LABEL authors="SpiderFrog"

FROM python:${PYTHON_VERSION}-alpine

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

# Copy the project into the image
ADD ./app /app

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

EXPOSE 8000

ENTRYPOINT ["uvicorn", "--host", "0.0.0.0", "--workers", "4"]