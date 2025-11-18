FROM ghcr.io/astral-sh/uv:alpine
LABEL authors="Fontys-OpenRemote"

WORKDIR /app

# Copy dependency metadata (improves caching) and workspace layout
ADD ./src/shared/pyproject.toml /app/shared/pyproject.toml
ADD ./src/services/mcp-server/pyproject.toml /app/mcp-server/pyproject.toml

# Install dependencies without full project sources
RUN uv init

RUN uv add --no-install-project "shared @ ./shared"
RUN uv add --no-install-project "mcp-server @ ./mcp-server"

ADD ./src/shared /app/shared
ADD ./src/services/mcp-server /app/mcp-server

EXPOSE 8420

ENTRYPOINT ["uv", "run", "uvicorn", "mcp-server.app:app", "--host", "0.0.0.0", "--workers", "4", "--port", "8420"]