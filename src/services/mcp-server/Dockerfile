FROM ghcr.io/astral-sh/uv:alpine
LABEL authors="Fontys-OpenRemote"

WORKDIR /app

# Pin Python 3.13 to avoid Pydantic V1 compatibility issues with 3.14
ENV UV_PYTHON=python3.13

# Copy dependency metadata (improves caching) and workspace layout
COPY ./src/shared/pyproject.toml /app/shared/pyproject.toml
COPY ./src/services/mcp-server/pyproject.toml /app/mcp-server/pyproject.toml

# Install dependencies without full project sources
RUN uv init

RUN uv add --no-install-project "shared @ ./shared"
RUN uv add --no-install-project "mcp-server @ ./mcp-server"

COPY ./src/shared /app/shared
COPY ./src/services/mcp-server /app/mcp-server

EXPOSE 8420

ENTRYPOINT ["uv", "run", "uvicorn", "mcp-server.app:app", "--host", "0.0.0.0", "--workers", "4", "--port", "8420"]