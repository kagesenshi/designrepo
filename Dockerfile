# Base stage for common dependencies
FROM python:3.13-slim-bookworm AS base

# Install Node.js (required for reflex export)
RUN apt-get update && apt-get install -y curl unzip && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    curl -fsSL https://bun.com/install | bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip install uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN uv sync --frozen --no-cache

COPY . .

# --- Backend Stage ---
FROM base AS backend

# Expose backend port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV REFLEX_ENV=prod

# Command to run the backend
CMD ["uv", "run", "reflex", "run", "--env", "prod", "--backend-only"]

# --- Frontend Builder Stage ---
FROM base AS frontend-builder

# Export the frontend
RUN uv run reflex export --frontend-only

# --- Frontend (Nginx) Stage ---
FROM nginx:stable-alpine AS frontend

# Install unzip
RUN apk add --no-cache unzip

# Copy exported frontend zip from builder
COPY --from=frontend-builder /app/frontend.zip /tmp/frontend.zip

# Extract and clean up
RUN unzip -o /tmp/frontend.zip -d /usr/share/nginx/html && \
    rm /tmp/frontend.zip

# Copy custom nginx config
RUN printf "server {\n\
    listen 80;\n\
    location / {\n\
    root /usr/share/nginx/html;\n\
    index index.html;\n\
    try_files \$uri \$uri/ /404.html;\n\
    }\n\
    }\n" > /etc/nginx/conf.d/default.conf

# Copy entrypoint script
COPY frontend-entrypoint.sh /usr/local/bin/frontend-entrypoint.sh
RUN chmod +x /usr/local/bin/frontend-entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/usr/local/bin/frontend-entrypoint.sh"]
