# ===================================================
# Stage 1: Use Python 3.11 slim as the base image
# "slim" means a minimal Linux + Python — no extra 
# bloat. Keeps the image small (~150MB vs ~900MB full).
# ===================================================
FROM python:3.11-slim

# ===================================================
# Set the working directory inside the container.
# All following commands run from /app.
# Think of this as doing "cd /app" inside the container.
# ===================================================
WORKDIR /app

# ===================================================
# Install system dependencies needed by psycopg2.
# psycopg2-binary sometimes still needs libpq 
# headers on slim images. gcc is needed to compile
# any C extensions. We clean up apt cache after
# to keep the image small.
# ===================================================
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# ===================================================
# Copy ONLY the requirements file first.
# Why? Docker caches each step (layer). If your code
# changes but requirements don't, Docker reuses the
# cached pip install — saving minutes on rebuilds.
# ===================================================
COPY Requirements.txt .

# ===================================================
# Install Python dependencies.
# --no-cache-dir: don't store pip's download cache 
#   (smaller image)
# --upgrade pip: ensures we have the latest pip
# ===================================================
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r Requirements.txt

# ===================================================
# Now copy the rest of the application code.
# This is separate from requirements so that code
# changes don't re-trigger pip install.
# ===================================================
COPY . .

# ===================================================
# Tell Docker this container listens on port 8000.
# This is documentation — it doesn't actually open
# the port. You still need -p 8000:8000 when running.
# ===================================================
EXPOSE 8000

# ===================================================
# The command that runs when the container starts.
# uvicorn: the ASGI server running your FastAPI app
# app.main:app — tells uvicorn to find the FastAPI 
#   instance named "app" in app/main.py
# --host 0.0.0.0 — listen on all network interfaces
#   (required inside Docker, otherwise it only 
#   listens on localhost which is unreachable)
# --port 8000 — match the EXPOSE above
# ===================================================
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]