# Base stage for common dependencies
FROM python:3.13-slim-bookworm AS base

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN pip install uv && uv sync --frozen --no-cache

# --- Backend Stage ---
FROM base AS backend

# Copy application source
COPY . .

# Expose backend port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV REFLEX_ENV=prod

# Command to run the backend
CMD ["uv", "run", "reflex", "run", "--env", "prod", "--backend-only"]

# --- Frontend Builder Stage ---
FROM base AS frontend-builder

# Install Node.js (required for reflex export)
RUN apt-get update && apt-get install -y curl unzip && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy application source
COPY . .

# Argument for backend URL
ARG BACKEND_URL
ENV API_URL=${BACKEND_URL}

# Export the frontend
# Note: This creates frontend.zip
RUN uv run reflex export --frontend-only

# --- Frontend (Nginx) Stage ---
FROM nginx:stable-alpine AS frontend

# Install unzip
RUN apk add --no-cache unzip

# Copy exported frontend zip from builder
COPY --from=frontend-builder /app/frontend.zip /tmp/frontend.zip

# Extract and clean up
RUN unzip /tmp/frontend.zip -d /usr/share/nginx/html && \
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

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
