FROM python:3.11-slim

# System dependencies including Node.js and SQLite
RUN apt-get update && apt-get install -y \
    git curl sqlite3 nodejs npm \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install uv package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uv

# Copy project files
COPY pyproject.toml README.md ./
COPY devdep ./devdep

# Install Python dependencies using uv
RUN /uv sync

# Pre-install MCP servers to speed up agent startup
RUN npm install -g @upstash/context7-mcp @modelcontextprotocol/server-github

# Create workspace directory
RUN mkdir -p /app/workspace

CMD ["python", "devdep/main.py"]