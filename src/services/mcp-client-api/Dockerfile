FROM ghcr.io/astral-sh/uv:alpine AS app-builder

WORKDIR /app

# Copy dependency metadata (improves caching) and workspace layout
COPY ./src/shared/pyproject.toml /app/shared/pyproject.toml
COPY ./src/services/mcp-client-api/pyproject.toml /app/mcp-client-api/pyproject.toml

# Fix for the non existant app folder, not included for caching purposes.
RUN mkdir /app/mcp-client-api/app

# Install dependencies without full project sources
RUN uv init

RUN uv add --no-install-project "shared @ ./shared"
RUN uv add --no-install-project "mcp-client-api @ ./mcp-client-api"

# ----------------------------------------------------------------------
# This stage uses a Node image to download dependencies and compile the Vue app.
# ----------------------------------------------------------------------
FROM node:24-alpine AS ui-builder

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json first to take advantage of Docker caching.
# This step only re-runs if the dependency definitions change.
COPY ./src/services/mcp-client-api/ui/package*.json ./

# Install project dependencies
RUN npm install

# Copy the rest of the application source code
COPY ./src/services/mcp-client-api/ui .

# Build the application for production.
# The output (usually 'dist' or 'build') will contain the static HTML, CSS, and JS files.
# The command below assumes your Vue CLI/Vite configuration outputs to a directory named 'dist'.
RUN npm run build

FROM ghcr.io/astral-sh/uv:alpine AS production
LABEL authors="Fontys-OpenRemote"

WORKDIR /app

# Copy the builder outputs to current stage
COPY --from=app-builder /app .
COPY --from=ui-builder /app/dist ./static

COPY ./src/shared ./shared
COPY ./src/services/mcp-client-api/app ./mcp-client-api/app

EXPOSE 8421

ENTRYPOINT ["uv", "run", "uvicorn", "mcp-client-api.app:app", "--host", "0.0.0.0", "--workers", "4", "--port", "8421"]