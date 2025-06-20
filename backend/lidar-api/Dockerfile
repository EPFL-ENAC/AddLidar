# Stage 1: Build dependencies
FROM python:3.12-slim-bookworm AS builder

# Copy uv binary from official UV image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set environment variables for uv
ENV UV_LINK_MODE=copy
ENV UV_COMPILE_BYTECODE=1
ENV UV_PROJECT_ENVIRONMENT=/app/.venv

# Create the app directory
WORKDIR /app

# Copy project files needed for dependency installation
COPY pyproject.toml uv.lock ./

# Install dependencies using uv sync
RUN uv sync --frozen --no-cache

# Stage 2: Final image
FROM python:3.12-slim-bookworm

# Copy the installed dependencies from the builder stage
# Copy the uv binary from builder stage to final image
COPY --from=builder /usr/local/bin/uv /usr/local/bin/uv

# Copy the installed dependencies from the builder stage
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/uv.lock /app/uv.lock

# Create the app directory
WORKDIR /app

# Copy the rest of the application code
COPY . .

# Set the path to include the virtual environment's binaries
ENV PATH="/app/.venv/bin:$PATH"

ENV PUBLIC_PORT=8000
ENV INTERNAL_PORT=8001

# Run both servers using the new main.py startup method
CMD ["uv", "run", "python", "-m", "src.main"]