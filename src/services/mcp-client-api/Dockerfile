FROM ghcr.io/astral-sh/uv:alpine
LABEL authors="Fontys-OpenRemote"

WORKDIR /app

# Copy dependency metadata (improves caching) and workspace layout
ADD ./src/shared/pyproject.toml /app/shared/pyproject.toml
ADD ./src/services/mcp-client-api/pyproject.toml /app/mcp-client-api/pyproject.toml

# Install dependencies without full project sources
RUN uv init

RUN uv add --no-install-project "shared @ ./shared"
RUN uv add --no-install-project "mcp-client-api @ ./mcp-client-api"

ADD ./src/shared /app/shared
ADD ./src/services/mcp-client-api /app/mcp-client-api

EXPOSE 8421

ENTRYPOINT ["uv", "run", "uvicorn", "mcp-client-api.app:app", "--host", "0.0.0.0", "--workers", "4", "--port", "8421"]